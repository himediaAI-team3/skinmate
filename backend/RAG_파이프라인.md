# RAG 파이프라인 구현 가이드

## 📋 목차

1. [개요](#개요)
2. [시스템 구조](#시스템-구조)
3. [구현 완료 현황](#구현-완료-현황)
4. [실행 가이드](#실행-가이드)
5. [테스트 전략](#테스트-전략)
6. [성능 및 비용](#성능-및-비용)
7. [문제 해결](#문제-해결)
8. [향후 계획](#향후-계획)

---

## 개요

Qdrant Cloud 기반 RAG(Retrieval-Augmented Generation) 파이프라인이 성공적으로 구축되었습니다!

### 핵심 기능

- ✅ **Vector 검색**: multilingual-e5-large (1024-dim) 임베딩
- ✅ **Hybrid 필터링**: 가격, 피부 질환, 피부 타입 기반
- ✅ **LLM 추천**: GPT-4o-mini로 최종 3개 선정 + 추천 이유 생성
- ✅ **개인화**: 회원별 맞춤 추천

### 기술 스택

| 구성 요소 | 기술 |
|----------|------|
| Vector DB | Qdrant Cloud (Free Tier) |
| 임베딩 모델 | multilingual-e5-large |
| LLM | OpenAI GPT-4o-mini |
| 백엔드 | FastAPI + SQLAlchemy |
| 데이터베이스 | MySQL |

---

## 시스템 구조

### RAG 파이프라인 흐름

```
사용자 이미지 업로드
    ↓
[1] AI 피부 진단 (RunPod Vision Model)
    ↓ (disease_name, summary)
[2] 진단 결과 + 회원 정보 조회
    ↓ (질환, 피부타입, 가격대)
[3] Query 텍스트 생성
    ↓
[4] Qdrant Vector 검색 (Top 10)
    ├─ 임베딩: multilingual-e5-large
    ├─ 필수 필터: 가격 범위
    └─ 가점: 질환 매칭, 피부타입 매칭
    ↓ (10개 후보)
[5] LLM 최종 선정 (GPT-4o-mini)
    └─ Top 10 → 최종 3개 선정 + 추천 이유 생성
    ↓
[6] MySQL recommendation 테이블 저장
    └─ (cosmetic_id, ranking, reason)
    ↓
[7] 사용자에게 결과 반환
```

### 세부 단계 설명

#### 1️⃣ Vector 검색 (Qdrant)

**목적**: 진단 결과 및 사용자 정보와 유사한 화장품 10개를 빠르게 검색

**입력**:
- 진단 질환: "여드름"
- 피부 타입: "지성"
- 가격대: 15,000원 ~ 50,000원

**처리**:
```python
# Query 텍스트 구성
query_text = f"{disease_name} 피부입니다. {summary}"

# 임베딩
query_vector = EmbeddingService.embed_query(query_text)

# Vector 검색 (Hybrid Filtering)
results = VectorStoreService.search_similar(
    query_text=query_text,
    disease_name=disease_name,  # 선호도 (가중치)
    min_price=min_price,        # 필수 필터
    max_price=max_price,        # 필수 필터
    skin_type=skin_type,        # 선호도 (가중치)
    limit=10
)
```

**Score Boosting**:
```python
# 질환 매칭: +0.01
if disease_name in cosmetic.skin_disease:
    score += 0.01

# 피부타입 매칭: +0.005
if skin_type in cosmetic.skin_type:
    score += 0.005
```

**출력**: 10개 후보 화장품 (cosmetic_id, name, brand, score)

---

#### 2️⃣ LLM 최종 선정

**목적**: 10개 중 최종 3개 선정 및 추천 이유 생성

**입력**:
- 진단 정보 (disease_name, summary)
- 10개 후보 화장품 상세 정보
- 회원 정보 (피부타입, 가격대)

**LLM 프롬프트** (recommendation.yaml):
```yaml
당신은 피부과 전문의이자 화장품 추천 전문가입니다.

사용자의 피부 진단 결과와 추천 후보 화장품 10개를 분석하여,
사용자에게 가장 적합한 화장품 3개를 선정하고 각각의 추천 이유를 작성하세요.

선정 기준:
1. 진단된 피부 질환과의 관련성 (가장 중요)
2. 브랜드 다양성 (최대한 서로 다른 브랜드 선택)
3. 주요 효능 및 케어 증상의 적합성
4. 핵심 성분의 효과

출력 형식 (JSON):
{
  "recommendations": [
    {"ranking": 1, "cosmetic_id": 숫자, "reason": "추천 이유 (50-100자)"},
    {"ranking": 2, "cosmetic_id": 숫자, "reason": "추천 이유"},
    {"ranking": 3, "cosmetic_id": 숫자, "reason": "추천 이유"}
  ]
}
```

**출력**:
```json
[
  {
    "ranking": 1,
    "cosmetic_id": 5,
    "reason": "민감한 여드름 피부에 적합한 저자극 포뮬러로 시카 성분이 진정 효과를 제공합니다."
  },
  {
    "ranking": 2,
    "cosmetic_id": 12,
    "reason": "티트리 성분이 여드름 균 억제와 피지 조절에 효과적입니다."
  },
  {
    "ranking": 3,
    "cosmetic_id": 23,
    "reason": "pH 밸런스를 유지하며 과도한 피지를 제거해 여드름 예방에 도움을 줍니다."
  }
]
```

---

#### 3️⃣ DB 저장

**recommendation 테이블**:
```sql
INSERT INTO recommendation (analysis_id, cosmetic_id, ranking, reason)
VALUES
  (123, 5, 1, '민감한 여드름 피부에 적합한...'),
  (123, 12, 2, '티트리 성분이 여드름 균...'),
  (123, 23, 3, 'pH 밸런스를 유지하며...');
```

**사용자 결과 조회**:
```bash
GET /api/skin-analysis/{analysis_id}
```

**응답**:
```json
{
  "analysis_id": 123,
  "disease_name": "여드름",
  "diagnosis_summary": "이마와 뺨 부위에 다수의...",
  "products": [
    {
      "name": "시카페어 진정 크림",
      "brand": "브랜드A",
      "price": 28000,
      "reason": "민감한 여드름 피부에 적합한 저자극 포뮬러로..."
    },
    ...
  ]
}
```

---

## 구현 완료 현황

### 생성된 파일

#### 1. 핵심 서비스
- ✅ `app/core/config/qdrant.py` - Qdrant Cloud 클라이언트 설정
- ✅ `app/services/embedding.py` - multilingual-e5-large 임베딩 서비스
- ✅ `app/services/vector_store.py` - Qdrant CRUD 작업
- ✅ `app/services/recommendation.py` - RAG 파이프라인 통합
- ✅ `app/services/diagnosis.py` - RunPod Vision 모델 진단

#### 2. Repository 레이어
- ✅ `app/repository/cosmetic.py` - `get_by_ids()`, `get_all()` 메서드 추가
- ✅ `app/repository/member.py` - `get_by_id()` 메서드
- ✅ `app/repository/diagnosis.py` - `get_by_analysis_id()` 메서드

#### 3. 프롬프트
- ✅ `app/core/prompt/diagnosis.yaml` - Vision 모델 진단 프롬프트
- ✅ `app/core/prompt/recommendation.yaml` - LLM 추천 프롬프트

#### 4. 스크립트
- ✅ `scripts/init_qdrant.py` - 초기 데이터 적재
- ✅ `scripts/check_data.py` - 데이터 검증 및 검색 테스트
- ✅ `scripts/test_openai_diagnosis.py` - End-to-End 통합 테스트

#### 5. 설정 파일
- ✅ `requirements.txt` - 의존성 (qdrant-client, sentence-transformers, tqdm)
- ✅ `env.example` - Qdrant, OpenAI, RunPod 환경 변수

---

## 실행 가이드

### Step 1: 환경 설정

#### 1.1. Qdrant Cloud 설정
1. https://cloud.qdrant.io 접속하여 계정 생성
2. Cluster 생성 (Free Tier 선택)
3. API Key 발급
4. Cluster URL 복사

#### 1.2. .env 파일 생성
```bash
# backend/.env 파일 생성
cp env.example .env

# 다음 값들을 실제 값으로 수정:
QDRANT_URL=https://your-cluster.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_api_key_here
OPENAI_API_KEY=sk-your-openai-api-key-here

# RunPod 설정 (Vision 모델)
RUNPOD_MODEL_NAME=your-model-name
RUNPOD_API_KEY=your-runpod-key
RUNPOD_BASE_URL=https://api.runpod.ai/v2/.../openai/v1
```

#### 1.3. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

---

### Step 2: 초기 데이터 적재

#### 2.1. MySQL 화장품 데이터 확인
```sql
-- cosmetic 테이블에 데이터가 있는지 확인
SELECT COUNT(*) FROM cosmetic;
```

#### 2.2. Qdrant에 데이터 적재
```bash
python scripts/init_qdrant.py
```

**예상 출력**:
```
============================================================
Qdrant 초기 데이터 적재 시작
============================================================

[Step 1] Qdrant Collection 생성 중...
Collection 'skinmate_cosmetics' 생성 완료
Payload 인덱스 생성 중...
Payload 인덱스 생성 완료

[Step 2] MySQL에서 화장품 데이터 조회 중...
✅ 190개의 화장품 데이터 조회 완료

[Step 3] 임베딩 텍스트 및 메타데이터 생성 중...
데이터 준비: 100%|██████████| 190/190 [00:02<00:00]
✅ 190개의 데이터 준비 완료

[Step 4] Qdrant에 배치 업로드 중...
[임베딩 모델 로딩 중] intfloat/multilingual-e5-large
[임베딩 모델 로딩 완료] 벡터 차원: 1024
Batches: 100%|██████████| 6/6 [01:45<00:00]
✅ Qdrant에 190개 업로드 완료

[Step 5] 업로드 검증 중...
✅ Collection 정보:
   - 이름: skinmate_cosmetics
   - 벡터 개수: 190
   - 상태: green

============================================================
Qdrant 초기 데이터 적재 완료! 🎉
============================================================
```

---

### Step 3: 테스트 실행

#### 3.1. 데이터 검증
```bash
python scripts/check_data.py
```

**확인 사항**:
- MySQL 데이터 개수
- Qdrant 벡터 개수
- Vector 검색 테스트 (필터 없음/가격 필터/모든 필터)

#### 3.2. End-to-End 테스트
```bash
python scripts/test_openai_diagnosis.py
```

**테스트 흐름**:
1. 실제 이미지 로드
2. OpenAI Vision API로 진단
3. MySQL에 진단 결과 저장
4. RAG 파이프라인 실행 (Vector 검색 → LLM 추천)
5. MySQL에 추천 결과 저장
6. 결과 출력

---

### Step 4: FastAPI 서버 실행

#### 4.1. 서버 시작
```bash
uvicorn app.main:app --reload
```

#### 4.2. API 테스트
```bash
# 피부 분석 생성
curl -X POST http://localhost:8000/api/skin-analysis \
  -F "member_id=1" \
  -F "image=@test_image.jpg"

# 응답
{
  "code": 201,
  "success": true,
  "message": "이미지 업로드 성공",
  "data": {
    "analysis_id": 123
  }
}

# 결과 조회
curl http://localhost:8000/api/skin-analysis/123

# 응답
{
  "code": 200,
  "success": true,
  "data": {
    "analysis_id": 123,
    "file_id": 456,
    "disease_name": "여드름",
    "diagnosis_summary": "이마와 뺨 부위에 다수의 홍반성 구진과 농포가 관찰됩니다...",
    "products": [
      {
        "name": "제로이드 인텐시브 크림",
        "brand": "제로이드",
        "price": 32000,
        "file_id": 789,
        "buy_url": "https://...",
        "reason": "아토피와 건선으로 인한 손상된 피부 장벽을 복원하고 수분 손실을 방지합니다."
      },
      ...
    ],
    "created_at": "2024-01-15T10:30:00"
  }
}
```

---

## 테스트 전략

### 테스트 스크립트 구성

```
backend/scripts/
├── init_qdrant.py              # 초기 데이터 적재
├── check_data.py               # 데이터 검증 (필수)
└── test_openai_diagnosis.py    # End-to-End 테스트 (필수)
```

### 단계별 검증 체크리스트

#### 기능 검증
- [x] Qdrant Cloud 연결 성공
- [x] 임베딩 벡터 1024-dim 생성
- [x] 190개 데이터 Qdrant 적재 완료
- [x] Vector 검색 Top 10 반환
- [x] 가격 필터링 정상 작동
- [x] 질환 매칭 정상 (가점 부여)
- [x] 피부 타입 매칭 정상 (가점 부여)
- [x] LLM 최종 3개 선정
- [x] 추천 이유 생성 완료
- [x] MySQL recommendation 테이블 저장

#### 품질 검증
- [ ] 추천 제품이 진단 질환과 관련성 있음
- [ ] 다양한 브랜드 믹스 (1개 브랜드 독점 방지)
- [ ] 추천 이유가 구체적이고 설득력 있음
- [ ] 가격대가 회원 선호도와 일치
- [ ] 피부 타입이 회원과 매칭
- [ ] 추천 제품 간 중복 없음
- [ ] ranking 순서 정상 (1, 2, 3)

---

## 성능 및 비용

### 성능 지표

| 단계 | 소요 시간 |
|------|-----------|
| 임베딩 (Query) | 0.5초 |
| Vector 검색 | < 200ms |
| LLM 추천 | < 5초 |
| **전체 파이프라인** | **< 10초** |

### 비용 분석

#### Qdrant Cloud (Free Tier)
- ✅ **무료** (1GB 제한)
- 190개 × 1024-dim ≈ 0.8MB → 충분

#### OpenAI API (GPT-4o-mini)
- 입력: $0.15 / 1M 토큰
- 출력: $0.60 / 1M 토큰
- **추천 1회당 약 $0.0004** (매우 저렴)

#### 임베딩 (multilingual-e5-large)
- ✅ **무료** (자체 호스팅)
- CPU로도 충분히 빠름

**월 예상 비용** (일 100회 추천 기준):
- OpenAI API: 100회/일 × 30일 × $0.0004 ≈ **$1.2/월**
- Qdrant Cloud: **$0** (Free Tier)
- **총 비용: 약 $1.2/월** 🎉

---

## 문제 해결

### Q1: Qdrant 연결 실패
```bash
❌ Could not connect to Qdrant Cloud
```

**해결 방법**:
1. `.env` 파일에서 `QDRANT_URL`, `QDRANT_API_KEY` 확인
2. Qdrant Cloud Dashboard에서 Cluster 상태 확인
3. 네트워크/방화벽 확인
4. URL에 포트 번호(`:6333`) 포함 확인

---

### Q2: 임베딩 모델 로딩 실패
```bash
❌ Model 'intfloat/multilingual-e5-large' not found
```

**해결 방법**:
1. 인터넷 연결 확인
2. `sentence-transformers` 버전 확인: `pip install sentence-transformers==2.7.0`
3. 수동 다운로드:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('intfloat/multilingual-e5-large')
```

---

### Q3: Vector 검색 결과 없음
```bash
⚠️ Vector 검색 결과가 없습니다
```

**해결 방법**:
1. Qdrant에 데이터가 적재되었는지 확인:
```bash
python scripts/check_data.py
```

2. 가격 범위가 너무 좁은지 확인:
```python
# member 테이블 확인
SELECT min_price, max_price FROM member WHERE member_id = 1;
```

3. 필터 조건 완화 테스트:
```python
# vector_store.py - should 조건 제거
```

---

### Q4: LLM 응답 파싱 실패
```bash
❌ LLM 응답 파싱 실패
```

**해결 방법**:
1. OpenAI API Key 확인
2. `recommendation.yaml` 프롬프트 확인
3. Fallback 로직 확인 (자동으로 상위 3개 반환)
4. OpenAI API 할당량 확인

---

### Q5: Vector 검색 실패 시 추천 없음
```bash
ValueError: '여드름' 질환에 적합한 화장품을 찾을 수 없습니다
```

**현재 동작**:
- Vector 검색 실패 시 `ValueError` 발생
- 진단 결과는 DB에 보존됨
- 추천 결과는 생성되지 않음

**의도된 설계**:
- 사용자는 진단 결과는 확인 가능
- 프론트엔드에서 "적합한 제품이 없습니다" 메시지 표시
- 가격대 조정 후 재시도 가능

---

## 향후 계획

### 1. 추천 시스템 고도화

#### 협업 필터링
```python
# "이 제품을 좋아한 사람들이 좋아한 다른 제품"
similar_users = find_similar_users(member_id)
popular_products = get_popular_products(similar_users)
```

#### 멀티모달 임베딩 (CLIP)
```python
# 화장품 이미지 임베딩
image_embedding = CLIPModel.encode_image(cosmetic_image)
text_embedding = CLIPModel.encode_text(cosmetic_description)
combined_embedding = (image_embedding + text_embedding) / 2
```

#### 성분 기반 필터링
```python
# 알레르기 성분 자동 제외
if cosmetic.ingredients.contains(member.allergy_ingredients):
    exclude_from_results()
```

---

### 2. 성능 최적화

#### Redis 캐싱
```python
# Vector 검색 결과 캐싱 (5분)
@cache(ttl=300)
def search_similar(query_text, ...):
    ...
```

#### GPU 활용
```python
# 임베딩 속도 향상 (0.5초 → 0.1초)
model = SentenceTransformer('intfloat/multilingual-e5-large', device='cuda')
```

---

### 3. 모니터링 및 로깅

#### 추천 품질 지표
- 클릭률 (CTR)
- 구매 전환율
- 사용자 피드백 (좋아요/싫어요)

#### 성능 모니터링
- 응답 시간 분포
- Vector 검색 속도
- LLM 호출 비용

---

### 4. 외래키 제약조건 추가

현재는 개발 편의를 위해 FK 없이 운영 중. 프로덕션 배포 시 추가:

```sql
ALTER TABLE recommendation
  ADD CONSTRAINT fk_recommendation_analysis
  FOREIGN KEY (analysis_id) REFERENCES skin_analysis(analysis_id) ON DELETE CASCADE;

ALTER TABLE recommendation
  ADD CONSTRAINT fk_recommendation_cosmetic
  FOREIGN KEY (cosmetic_id) REFERENCES cosmetic(cosmetic_id) ON DELETE CASCADE;
```

---

## 참고 자료

### 공식 문서
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Sentence Transformers](https://www.sbert.net/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### 코드 예시
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)

---

## 요약

### ✅ 구현 완료
- Qdrant Cloud 기반 Vector 검색
- multilingual-e5-large 임베딩 (1024-dim)
- GPT-4o-mini 기반 LLM 추천
- Hybrid 필터링 (가격, 질환, 피부타입)
- Score Boosting (질환 +0.01, 피부타입 +0.005)
- 개인화 추천

### 🚀 빠른 시작
1. `.env` 파일 설정 (Qdrant, OpenAI, RunPod)
2. `pip install -r requirements.txt`
3. `python scripts/init_qdrant.py` (초기 데이터 적재)
4. `python scripts/check_data.py` (검증)
5. `uvicorn app.main:app --reload` (서버 실행)

### 💰 비용
- 거의 무료 (OpenAI API만 약 $1.2/월)
- Qdrant Cloud Free Tier 충분

### 📊 성능
- 전체 파이프라인: < 10초
- Vector 검색: < 200ms
- LLM 추천: < 5초

---

**작성일**: 2024년  
**버전**: 2.0  
**최종 업데이트**: RAG 파이프라인 구현 완료

🎉 성공!

