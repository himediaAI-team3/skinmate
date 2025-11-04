# 최종 수정 사항 정리

## 🎯 수정 개요

사용자 요청에 따라 다음 두 가지를 수정했습니다:

1. **하이브리드 검색 메서드 구분**: 기존 RAG 파이프라인과 챗봇 추천을 별도 메서드로 분리
2. **LLM 추천 로직 개선**: 3개 강제 → LLM 자율 판단 (0~3개)

---

## 📝 수정된 파일 및 내용

### 1️⃣ `backend/app/services/vector_store.py`

#### ✅ 변경 사항

**기존 문제점:**
- 챗봇 추천 기능 수정 시 `search_hybrid()` 메서드를 수정하여 기존 RAG 파이프라인(`test_openai_diagnosis.py`)에 영향 가능성

**해결 방법:**
- `search_hybrid()`: 기존 RAG용 (Prefetch 방식 유지)
- `search_hybrid_chat()`: 챗봇용 (수동 RRF 병합 방식 - Prefetch 오류 회피)

#### 코드 구조

```python
@staticmethod
def search_hybrid(...):
    """
    하이브리드 검색: Prefetch(dense+sparse) + 필터링
    
    ⚠️ 주의: 이 메서드는 기존 RAG 파이프라인(test_openai_diagnosis.py)에서 사용됩니다.
    챗봇 증상별 추천은 search_hybrid_chat()을 사용하세요.
    """
    # Prefetch 방식 (기존 방식 유지)
    prefetch = [
        Prefetch(query=dense_query_list, using="dense", limit=20),
        Prefetch(query=sparse_query_obj, using="bm25", limit=20),
    ]
    
    results = client.query_points(
        collection_name=QDRANT_HYBRID_COLLECTION,
        prefetch=prefetch,
        query=dense_query_list,
        using="dense",
        query_filter=query_filter,
        limit=limit,
        with_payload=True
    )
    # ...

@staticmethod
def search_hybrid_chat(...):
    """
    하이브리드 검색 (챗봇용): Dense + Sparse 병렬 검색 후 RRF 수동 병합
    
    Prefetch indices 중복 오류를 피하기 위해 별도 검색 후 RRF로 병합합니다.
    챗봇의 증상별 화장품 추천 Tool에서 사용됩니다.
    """
    # Dense 검색
    dense_results = client.search(...)
    
    # Sparse 검색
    sparse_results = client.search(...)
    
    # RRF 수동 병합
    rrf_scores = defaultdict(float)
    k = 60
    
    for rank, result in enumerate(dense_results, 1):
        rrf_scores[result.id] += 1 / (k + rank)
    
    for rank, result in enumerate(sparse_results, 1):
        rrf_scores[result.id] += 1 / (k + rank)
    
    # 정렬 및 반환
    # ...
```

#### `search_cosmetics()` 메서드 수정

```python
@staticmethod
def search_cosmetics(...):
    """자연어 쿼리로 화장품 검색 (챗봇용)"""
    # ...
    
    # 챗봇용 search_hybrid_chat() 메서드 사용 (Prefetch 오류 회피)
    return VectorStoreService.search_hybrid_chat(
        query_dense_text=query_data["dense_query"],
        query_sparse_text=query_data["sparse_keywords"],
        min_price=min_price,
        max_price=max_price,
        skin_type=skin_type,
        disease_name=skin_disease,
        limit=limit
    )
```

---

### 2️⃣ `backend/app/core/prompt/recommendation.yaml`

#### ✅ 변경 사항

**기존 프롬프트 (수정 전):**
```yaml
**중요: 반드시 정확히 3개의 화장품을 선정해야 합니다.**

주의사항:
- 반드시 3개를 선정해야 합니다 (2개 이하 불가)
- JSON 형식 외 다른 텍스트 출력 금지
```

**수정된 프롬프트 (현재):**
```yaml
instruction: |
  당신은 피부과 전문의이자 화장품 추천 전문가입니다.
  
  사용자의 개인 정보(피부타입, 나이대), 피부 진단 결과, 추천 후보 화장품 10개를 분석하여,
  사용자에게 가장 적합한 화장품을 선정하고 각각의 추천 이유를 작성하세요.
  
  **선정 기준:**
  1. 진단된 피부 질환과의 관련성 (가장 중요)
  2. 사용자의 피부타입과의 적합성
  3. 사용자의 나이대에 적합한 제품 선택
  4. 브랜드 다양성
  5. 주요 효능 및 케어 증상의 적합성
  6. 핵심 성분의 효과
  
  **주의사항:**
  - 적합한 제품이 있다면 최대 3개까지 선정하세요
  - 적합한 제품이 없다면 빈 배열 []을 반환하세요
  - 동일한 cosmetic_id 중복 불가
  - 가능한 한 서로 다른 브랜드를 선택하세요
  - ranking은 1부터 시작하여 순서대로
  - JSON 형식을 정확히 지켜주세요
  - 추가 설명 없이 JSON만 출력하세요
```

**변경 내용:**
- ❌ 제거: "반드시 3개 선정" 강제 요구
- ✅ 추가: "최대 3개까지" 유연한 선정
- ✅ 추가: "적합한 제품이 없다면 빈 배열 [] 반환" → LLM이 자율 판단

---

### 3️⃣ `backend/app/services/recommendation.py`

#### ✅ 변경 1: Temperature 복원

```python
# LLM 초기화
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,  # LLM이 자율적으로 판단하도록 원래대로 복구 (0.3 → 0.7)
)
```

#### ✅ 변경 2: 파싱 로직 개선 (0~3개 유연하게 처리)

**기존 로직 (수정 전):**
```python
# 검증
if len(recommendations) != 3:
    raise ValueError(f"LLM이 3개가 아닌 {len(recommendations)}개를 반환했습니다.")

return recommendations
```

**수정된 로직 (현재):**
```python
# 유연한 검증: 0~3개 모두 허용
if len(recommendations) == 0:
    logger.warning(f"LLM이 적합한 제품이 없다고 판단했습니다.")
elif len(recommendations) > 3:
    logger.warning(f"LLM이 {len(recommendations)}개 반환. 상위 3개만 사용합니다.")
    recommendations = recommendations[:3]
else:
    logger.info(f"LLM이 {len(recommendations)}개 제품을 선정했습니다.")

return recommendations
```

**파싱 실패 시 처리:**
```python
except Exception as e:
    logger.error(f"LLM 응답 파싱 실패: {e}")
    logger.error(f"LLM 응답 원문: {response.content}")
    
    # 파싱 실패 시: Vector 검색 결과는 있으나 LLM 파싱 오류
    # 명확한 에러 메시지로 원인 구분
    raise ValueError(
        f"LLM 응답 파싱 실패. Vector 검색 결과는 {len(cosmetics)}개 있으나 "
        f"LLM이 올바른 JSON 형식을 반환하지 않았습니다."
    )
```

#### ✅ 변경 3: `create_recommendations` 메서드 - 0개 처리

```python
# 6. 결과 처리
if len(final_recommendations) == 0:
    logger.warning("LLM이 적합한 제품이 없다고 판단했습니다.")
    logger.info(f"========== RAG 파이프라인 완료 (추천 제품 0개) ==========")
    return []  # 빈 리스트 반환

logger.info(f"LLM 최종 선정 완료 ({len(final_recommendations)}개):")
for rec in final_recommendations:
    logger.info(f"  {rec['ranking']}. cosmetic_id={rec['cosmetic_id']} - {rec['reason'][:50]}...")

# 7. MySQL recommendation 테이블 저장
# ...
```

---

## 🎯 수정 결과 정리

### ✅ 해결된 문제

1. **하이브리드 검색 메서드 분리**
   - 기존 RAG 파이프라인(`test_openai_diagnosis.py`)과 챗봇 추천 기능이 독립적으로 동작
   - 챗봇: `search_hybrid_chat()` → Prefetch 오류 회피 (수동 RRF)
   - RAG: `search_hybrid()` → 기존 방식 유지 (Prefetch)

2. **LLM 추천 로직 유연화**
   - LLM이 0~3개를 자율적으로 판단하여 반환
   - 적합한 제품이 없으면 빈 배열 반환 가능
   - 에러 메시지 개선: Vector 검색 실패 vs LLM 파싱 실패 구분

### 📊 추천 개수 시나리오

| 상황 | Vector 검색 결과 | LLM 판단 | 최종 반환 | 로그 메시지 |
|-----|---------------|---------|---------|----------|
| **정상** | 10개 | 3개 | 3개 | ✅ "LLM이 3개 제품을 선정했습니다." |
| **일부 선정** | 10개 | 2개 | 2개 | ✅ "LLM이 2개 제품을 선정했습니다." |
| **일부 선정** | 10개 | 1개 | 1개 | ✅ "LLM이 1개 제품을 선정했습니다." |
| **부적합** | 10개 | 0개 | 0개 | ⚠️ "LLM이 적합한 제품이 없다고 판단했습니다." |
| **과다 선정** | 10개 | 5개 | 3개 | ⚠️ "LLM이 5개 반환. 상위 3개만 사용합니다." |
| **검색 실패** | 0개 | - | 에러 | 🔴 "Vector 검색 결과가 없습니다." |
| **파싱 실패** | 10개 | 파싱 오류 | 에러 | 🔴 "LLM 응답 파싱 실패. Vector 검색 결과는 10개 있으나..." |

### 🧪 테스트 방법

#### 1. 기존 RAG 파이프라인 테스트
```bash
cd C:\Users\201\dev\skinmate\backend
python scripts\test_openai_diagnosis.py
```
- `search_hybrid()` 메서드 사용 (Prefetch 방식)
- 3개 추천 정상 동작 확인

#### 2. 챗봇 추천 테스트
```bash
cd C:\Users\201\dev\skinmate\backend
python scripts\test_chat.py
```
- `search_hybrid_chat()` 메서드 사용 (수동 RRF 방식)
- 시나리오 6-1 ~ 6-7 정상 동작 확인
- Prefetch 오류 없음 확인

---

## 📋 체크리스트

- [x] `search_hybrid()` 메서드 기존 방식 유지 (RAG용)
- [x] `search_hybrid_chat()` 메서드 추가 (챗봇용, 수동 RRF)
- [x] `search_cosmetics()` → `search_hybrid_chat()` 호출
- [x] `recommendation.yaml` 프롬프트 "3개 강제" 제거
- [x] `recommendation.yaml` 프롬프트 "0~3개 자율" 추가
- [x] `recommendation.py` Temperature 0.7로 복원
- [x] `recommendation.py` 파싱 로직 0~3개 허용
- [x] `recommendation.py` 에러 메시지 개선 (원인 명확화)
- [x] `create_recommendations()` 0개 처리 추가

---

## 🚀 다음 단계

1. **테스트 실행**
   ```bash
   # 기존 RAG 테스트
   cd backend
   python scripts\test_openai_diagnosis.py
   
   # 챗봇 테스트
   python scripts\test_chat.py
   ```

2. **확인 사항**
   - 기존 RAG 파이프라인 정상 동작
   - 챗봇 증상별 추천 정상 동작
   - Prefetch 오류 없음
   - LLM이 0~3개 자율 선정
   - 에러 메시지 명확성

3. **추가 개선 제안**
   - 챗봇 응답에서 "Vector 검색 결과 없음" vs "LLM이 부적합 판단" 구분하여 안내
   - 0개 추천 시 사용자에게 다른 조건(가격대, 피부타입 등) 변경 제안

---

**수정 완료 일시**: 2025-11-03  
**수정자**: AI Assistant  
**검토 필요**: 두 테스트 파일 모두 실행 후 정상 동작 확인

