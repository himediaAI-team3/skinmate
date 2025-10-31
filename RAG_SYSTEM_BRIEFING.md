# RAG 기반 화장품 추천 시스템 브리핑

## 개요
피부 진단 결과(질환명 + summary)를 입력받아 사용자 맞춤 화장품을 Top 3 추천하는 RAG(Retrieval-Augmented Generation) 파이프라인입니다.

---

## 전체 아키텍처

```
[진단 데이터] → [LLM 쿼리 생성] → [하이브리드 벡터 검색] → [점수 계산 & 소프트 부스팅] → [Top 3 저장]
```

### 주요 구성 요소
1. **지식 DB 구축 파이프라인** (1회 실행)
   - Vocabulary 생성 → Qdrant 컬렉션 생성 → 제품 인덱싱
2. **추천 생성 파이프라인** (API 호출 시마다 실행)
   - 진단 조회 → LLM 쿼리 생성 → 검색 → 점수 계산 → 저장

---

## 1. 지식 DB 구축 단계

### 1.1 Vocabulary 생성 (`1_build_vocabulary.py`)
**목적**: 제품의 주요 효능(`main_effect`)과 증상(`care_symptom`)에서 고유 키워드를 추출하여 인덱스 사전을 만듭니다.

**로직**:
- MySQL에서 `cosmetic` 테이블의 `main_effect`, `care_symptom` 컬럼 조회
- 각 값을 쉼표(`,`)로 분리 → 공백 제거 → 중복 제거
- 정렬 후 인덱스 부여: `{ "보습": 0, "진정": 1, ... }`
- `data/vocabulary.json`에 저장

**결과**: 키워드 → 인덱스 매핑 사전 (예: 101개 키워드)

---

### 1.2 Qdrant 컬렉션 생성 (`2_create_collection.py`)
**목적**: 벡터 검색을 위한 컬렉션을 생성하고, 필터링에 필요한 인덱스를 설정합니다.

**컬렉션 구조**:
- **Dense Vector**: `jhgan/ko-sroberta-multitask` 임베딩 (768차원, COSINE 거리)
- **Sparse Vector**: 키워드 기반 빈도 벡터
- **Payload**: 제품 메타데이터 (cosmetic_id, name, brand, price, skin_type, skin_disease, main_effect, care_symptom, description 등)

**인덱스 설정**:
- `price` 필드에 FLOAT 타입 인덱스 생성 (가격 필터링용)

**특징**:
- 기존 컬렉션이 있으면 삭제하지 않고 인덱스만 추가/확인
- 데이터 보존 우선

---

### 1.3 제품 데이터 인덱싱 (`3_index_products.py`)
**목적**: 화장품 데이터를 벡터화하여 Qdrant에 저장합니다.

**Dense Vector 생성**:
```
입력 텍스트 = "{name}는 {brand}의 {category} 제품입니다.
              주요 효능: {main_effect}
              케어 증상: {care_symptom}
              피부 타입: {skin_type}
              
              {description}"
→ SentenceTransformer로 임베딩 (768차원 벡터)
```

**Sparse Vector 생성**:
```
1. main_effect + care_symptom에서 키워드 추출 (쉼표 분리)
2. 키워드 빈도 계산 (Counter 사용)
3. vocabulary에서 인덱스 찾기 → SparseVector 생성
   - indices: [vocabulary[keyword] for keyword in keywords]
   - values: [count for keyword in keywords]
```

**저장**:
- 각 제품을 하나의 Point로 저장
- ID = `cosmetic_id`
- Vector = `{"dense": dense_vector, "sparse": sparse_vector}`
- Payload = 제품 메타데이터 전체

---

## 2. 추천 생성 파이프라인

### 2.1 사용자 정보 로드
**소스**: `member` 테이블에서 `skin_type`, `min_price`, `max_price` 조회

**경로**: 
```
analysis_id → SkinAnalysis.member_id → Member 조회
```

**활용**:
- 가격: 하드 필터 (검색 범위 축소)
- 피부타입: 소프트 부스팅 (점수 가산)

---

### 2.2 LLM 기반 검색 쿼리 생성 (`query_generator.py`)

**입력**: 
- `disease_name`: 진단 질환명 (예: "아토피")
- `summary`: 진단 요약 (예: "피부 건조/가려움, 장벽 약화")

**프로세스**:
1. **브리지 사전 참조**: 질환 → 효능/성분 매핑 테이블 사용
   ```python
   "아토피" → {
       "keywords": ["보습", "진정", "피부장벽강화", "가려움완화"],
       "ingredients": ["세라마이드", "판테놀", ...]
   }
   ```

2. **LLM 호출** (OpenAI GPT):
   - System Prompt: "화장품 효능 기반 검색 질의 생성기"
   - User Input: 질환명, summary, 브리지 힌트
   - 출력 형식: JSON
     ```json
     {
       "dense_text": "아토피 피부염에 적합한 보습과 진정 효과가 있는 화장품...",
       "keywords": ["보습", "진정", "피부장벽강화", "가려움완화"],
       "must_keywords": ["세라마이드", "판테놀", ...],
       "avoid_ingredients": ["강한 향료"],
       "notes": "..."
     }
     ```

3. **폴백 처리**: LLM 실패 시 브리지 사전 기반 규칙 생성

**출력**: 
- `dense_text`: 자연어 검색 쿼리 (의미 기반)
- `keywords`: 효능 키워드 리스트 (키워드 기반)

---

### 2.3 벡터 검색 (`recommendation.py`)

**Dense Vector 검색**:
```
입력: dense_text (LLM 생성)
→ SentenceTransformer.encode(dense_text)
→ NamedVector(name="dense", vector=dense_vector)
→ Qdrant search (limit=20)
```

**Sparse Vector 검색**:
```
입력: keywords (LLM 생성)
→ create_search_sparse_vector(keywords, vocabulary)
  - 각 키워드를 vocabulary에서 인덱스로 변환
  - 값은 1.0 (검색 쿼리는 빈도 고려 안 함)
→ NamedSparseVector(name="sparse", vector=sparse_vector)
→ Qdrant search (limit=20)
```

**필터 적용**:
- 가격 필터 (하드 필터):
  ```python
  Filter(must=[
      FieldCondition(key="price", range=Range(gte=min_price, lte=max_price))
  ])
  ```
- 필터가 없으면 전체 검색

**특징**:
- Dense: 의미 유사도 검색 (문맥 이해)
- Sparse: 키워드 정확 매칭 검색 (효능 중심)

---

### 2.4 점수 계산: RRF (Reciprocal Rank Fusion)

**기본 RRF**:
```
각 검색 결과의 순위(r)에 대해:
RRF_score = 1 / (k + r)

여기서 k = 60 (안정화 상수)
```

**가중 결합**:
```
각 제품의 최종 점수 = 
  1.0 × RRF_dense + 
  1.2 × RRF_sparse

(Sparse를 1.2배 강조 → 효능 정확도 우선)
```

**예시**:
- Dense 검색에서 1위 → RRF_dense = 1/(60+1) = 0.0164
- Sparse 검색에서 3위 → RRF_sparse = 1/(60+3) = 0.0159
- 최종 = 1.0 × 0.0164 + 1.2 × 0.0159 = 0.0375

---

### 2.5 소프트 부스팅 (Soft Boosting)

**질환 동의어 부스트**:
```
if payload.skin_disease in disease_synonyms:
    score += 0.1

예: 
- 진단: "아토피"
- 제품 skin_disease: "아토피" or "아토피 피부염" → +0.1
```

**피부타입 부스트**:
```
if payload.skin_type == user.skin_type:
    score += 0.1

elif payload.skin_type in compatible_types[user.skin_type]:
    score += 0.05

예:
- 사용자: "건성"
- 제품: "건성" → +0.1
- 제품: "중건성" (호환) → +0.05
```

**호환 매핑**:
- 건성 ↔ 중건성, 민감성
- 지성 ↔ 복합성, 민감성
- 복합성 ↔ 지성, 건성
- 민감성 ↔ 건성, 복합성

**최종 점수**:
```
최종_점수 = 
    RRF_가중합 + 
    질환_부스트(0~0.1) + 
    피부타입_부스트(0~0.1)
```

---

### 2.6 Top 3 저장

**랭킹**:
1. 최종 점수로 내림차순 정렬
2. 상위 3개 추출
3. `recommendation` 테이블에 저장
   - `ranking`: 1, 2, 3
   - `reason`: "{질환명}에 적합: {제품_효능}"

**중복 방지**:
- 저장 전 기존 추천 삭제 (같은 `analysis_id`)

**폴백 처리**:
- 예외 발생 시 기본 추천 3개 저장 (cosmetic_id: 1, 2, 3)

---

## 3. 핵심 기법 및 설계 원칙

### 3.1 하이브리드 검색
- **Dense**: 의미 유사도 (문맥 이해, LLM 생성 쿼리 활용)
- **Sparse**: 키워드 매칭 (효능 정확도, vocabulary 기반)

**장점**: 의미적 유연성 + 정확한 효능 매칭의 균형

---

### 3.2 RRF (Reciprocal Rank Fusion)
**목적**: 여러 검색 결과를 단일 순위로 통합

**특징**:
- 순위 기반 점수 (절대 점수 의존 없음)
- 안정화 상수 k=60 사용
- 가중치 적용 가능 (dense: 1.0, sparse: 1.2)

**장점**: 다양한 검색 결과를 공정하게 결합

---

### 3.3 소프트 부스팅 (Soft Boosting)
**철학**: "필터로 제외" 대신 "매칭되면 가점"

**적용 대상**:
- 질환 일치
- 피부타입 일치/호환

**장점**:
- 검색 결과 0건 방지
- 사용자 선호도를 점수로 반영

---

### 3.4 질환-효능 브리지 사전
**목적**: 질환 도메인 → 화장품 효능 도메인 간 의미 거리 축소

**구조**:
```
질환명 → {
    "keywords": [효능 키워드],
    "ingredients": [추천 성분]
}
```

**활용**:
1. LLM 프롬프트에 힌트 제공
2. LLM 실패 시 폴백 규칙

---

### 3.5 하드 필터 vs 소프트 부스트

| 구분 | 대상 | 방식 | 효과 |
|------|------|------|------|
| 하드 필터 | 가격 | Range 필터 | 검색 범위 축소, 속도↑ |
| 소프트 부스트 | 질환, 피부타입 | 점수 가산 | 결과 다양성 유지, 선호도 반영 |

---

## 4. 데이터 흐름 요약

```
[진단] 
  ↓
[사용자 정보 로드] (skin_type, price range)
  ↓
[LLM 쿼리 생성] (dense_text, keywords)
  ↓
[Dense 벡터 변환] ─┐
[Sparse 벡터 변환] ─┤
[가격 필터 적용] ──┤
  ↓                 ↓
[Qdrant 검색] (각각 20개)
  ↓
[RRF 점수 계산] (가중 합산)
  ↓
[소프트 부스팅] (질환, 피부타입)
  ↓
[랭킹 정렬] (상위 3개)
  ↓
[DB 저장]
```

---

## 5. 주요 파일 구조

```
backend/app/
├── core/config/
│   ├── qdrant.py          # Qdrant 클라이언트 싱글톤
│   ├── embedding.py       # 임베딩 모델 싱글톤
│   └── openai.py          # LLM 클라이언트 싱글톤
├── rag/
│   ├── 1_build_vocabulary.py    # Vocabulary 생성
│   ├── 2_create_collection.py   # 컬렉션 + 인덱스 생성
│   ├── 3_index_products.py      # 제품 인덱싱
│   ├── 4_test_search.py         # 검색 테스트 스크립트
│   ├── query_generator.py       # LLM 쿼리 생성
│   ├── vector_builder.py        # 벡터 생성 유틸
│   └── vocabulary.py            # Vocabulary 로더
└── services/
    └── recommendation.py  # RAG 추천 서비스 (핵심 로직)
```

---

## 6. 성능 및 최적화

### 6.1 검색 속도
- 가격 하드 필터 → 검색 범위 축소
- Dense/Sparse 병렬 검색
- 상위 20개만 조회 후 RRF 결합

### 6.2 정확도
- 하이브리드 검색 → 의미 + 키워드 양쪽 활용
- 소프트 부스팅 → 사용자 선호도 반영
- RRF 가중치 조정 → 효능 정확도 강조

### 6.3 안정성
- LLM 실패 시 폴백 규칙
- 검색 결과 0건 시 폴백 추천
- 예외 로깅으로 디버깅 용이

---

## 7. 향후 개선 가능 사항

1. **BM25 적용**: Sparse 벡터 가중치를 TF 수준에서 BM25로 개선 (DF, IDF 반영)
2. **사용자 입력 반영**: LLM 쿼리 생성 시 피부타입, 가격대를 프롬프트에 명시적으로 포함
3. **회피 성분 필터링**: 현재는 미적용, 필요 시 페널티 방식으로 추가 가능
4. **개인화 가중치**: 사용자 히스토리 기반 선호도 학습

---

## 8. 실행 순서

### 초기 구축 (1회)
```bash
# 1. Vocabulary 생성
python backend/app/rag/1_build_vocabulary.py

# 2. 컬렉션 생성 및 인덱스 설정
python backend/app/rag/2_create_collection.py

# 3. 제품 데이터 인덱싱
python backend/app/rag/3_index_products.py
```

### 추천 생성 (API 호출)
```bash
POST /api/skin-analysis/{analysis_id}/recommendations/rag
```

---

## 요약

**RAG 시스템의 핵심**:
1. **하이브리드 검색**: Dense(의미) + Sparse(키워드)
2. **RRF 결합**: 공정한 순위 통합
3. **소프트 부스팅**: 사용자 선호도를 점수로 반영
4. **질환-효능 브리지**: 도메인 간 거리 축소

**결과**: 사용자 맞춤 화장품 Top 3 추천

