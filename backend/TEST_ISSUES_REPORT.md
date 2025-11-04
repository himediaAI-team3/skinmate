# Test Chat 실행 문제 보고서

## 테스트 실행 환경
- **가상환경**: `(skin_nunu) C:\Users\201\dev\skinmate>`
- **테스트 파일**: `backend/scripts/test_chat.py`
- **실행 방법**: `cd backend && python scripts\test_chat.py`

## 발견된 문제 목록

### ✅ 문제 1: 작업 디렉토리 (Working Directory) 이슈
**심각도**: ⚠️ 중간 (해결됨)

**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'app/core/prompt\\summary_refine_chat.yaml'
```

**원인**:
- `backend/app/utils/prompt.py`의 `load_prompt()` 함수가 상대 경로 `"app/core/prompt"`를 사용
- 프로젝트 루트에서 실행 시 경로를 찾을 수 없음

**해결 방법**:
```bash
# 잘못된 실행 (프로젝트 루트에서)
cd C:\Users\201\dev\skinmate
python backend\scripts\test_chat.py  # ❌ 파일 경로 에러

# 올바른 실행 (backend 디렉토리에서)
cd C:\Users\201\dev\skinmate\backend
python scripts\test_chat.py  # ✅ 정상 동작
```

**영구적 수정 제안**:
`backend/app/utils/prompt.py` 파일을 수정하여 절대 경로 사용:
```python
import os
import yaml

def load_prompt(file_name: str) -> str:
    """프롬프트 파일을 로드하여 instruction을 반환"""
    # 현재 파일의 위치를 기준으로 절대 경로 계산
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(current_dir))  # backend/app 상위
    path = os.path.join(base_dir, "app", "core", "prompt", file_name)
    
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["instruction"]
```

---

### 🔴 문제 2: Qdrant Prefetch 검증 오류 (심각)
**심각도**: 🔴 높음 (미해결)

**증상**:
```
2025-11-03 17:09:34,425 - app.services.chat_tools - ERROR - 증상 추천 실패: Unexpected Response: 422 (Unprocessable Entity)
b'{"status":{"error":"Validation error in JSON body: [internal.prefetch[1].query.indices: Validation error: must be unique [{}]]"},"time":0.0}'
```

**발생 위치**:
- `backend/app/services/vector_store.py` → `search_hybrid()` 메서드
- 라인 119-122: Prefetch 구성 부분

**원인 분석**:
Qdrant의 `query_points()` API에서 여러 Prefetch를 사용할 때 `indices` 필드가 중복되면 발생하는 오류입니다.

현재 코드:
```python
# 2. Prefetch 구성
prefetch = [
    Prefetch(query=dense_query_list, using="dense", limit=20),
    Prefetch(query=sparse_query_obj, using="bm25", limit=20),
]

# 4. 하이브리드 검색 (RRF 자동 병합)
results = client.query_points(
    collection_name=QDRANT_HYBRID_COLLECTION,
    prefetch=prefetch,
    query=dense_query_list,  # 메인 쿼리도 dense 사용
    using="dense",
    query_filter=query_filter,
    limit=limit,
    with_payload=True
)
```

**문제점**:
1. Qdrant v1.12.1의 `query_points()` API는 `prefetch` 파라미터에서 여러 named vector를 사용할 때 각각 고유한 `indices`가 필요
2. 현재 코드는 `Prefetch` 객체에 `indices` 명시 없이 사용하여 내부적으로 충돌 발생
3. 메인 `query` 파라미터도 `dense_query_list`를 사용하여 prefetch[0]과 중복 가능성

**해결 방법 (권장)**:

**옵션 1**: Qdrant `query_batch_points()` 사용 (선호)
```python
@staticmethod
def search_hybrid(
    query_dense_text: str,
    query_sparse_text: str,
    min_price: int = None,
    max_price: int = None,
    skin_type: str = None,
    disease_name: str = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """하이브리드 검색: Dense + Sparse 병렬 검색 후 RRF 병합"""
    client = get_qdrant_client()
    
    # 1. 쿼리 임베딩
    from fastembed import TextEmbedding, SparseTextEmbedding
    dense_model = TextEmbedding("intfloat/multilingual-e5-large")
    sparse_model = SparseTextEmbedding("Qdrant/bm25")
    
    dense_query = list(dense_model.query_embed(query_dense_text))[0]
    sparse_query = list(sparse_model.query_embed(query_sparse_text))[0]
    
    dense_query_list = dense_query.tolist() if hasattr(dense_query, 'tolist') else list(dense_query)
    sparse_query_obj = sparse_query.as_object()
    
    # 2. 필터 구성
    must_conditions = []
    should_conditions = []
    
    if min_price is not None and max_price is not None:
        must_conditions.append(
            FieldCondition(key="price", range=Range(gte=min_price, lte=max_price))
        )
    
    if disease_name:
        should_conditions.append(
            FieldCondition(key="skin_disease", match=MatchValue(value=disease_name))
        )
    
    if skin_type:
        should_conditions.append(
            FieldCondition(key="skin_type", match=MatchValue(value=skin_type))
        )
    
    query_filter = None
    if must_conditions or should_conditions:
        query_filter = Filter(must=must_conditions, should=should_conditions)
    
    # 3. Dense 검색
    dense_results = client.search(
        collection_name=QDRANT_HYBRID_COLLECTION,
        query_vector=("dense", dense_query_list),
        query_filter=query_filter,
        limit=limit * 2,  # RRF를 위해 더 많이 가져옴
        with_payload=True
    )
    
    # 4. Sparse 검색
    sparse_results = client.search(
        collection_name=QDRANT_HYBRID_COLLECTION,
        query_vector=("bm25", sparse_query_obj),
        query_filter=query_filter,
        limit=limit * 2,
        with_payload=True
    )
    
    # 5. RRF (Reciprocal Rank Fusion) 수동 병합
    from collections import defaultdict
    rrf_scores = defaultdict(float)
    k = 60  # RRF 상수
    
    for rank, result in enumerate(dense_results, 1):
        point_id = result.id
        rrf_scores[point_id] += 1 / (k + rank)
    
    for rank, result in enumerate(sparse_results, 1):
        point_id = result.id
        rrf_scores[point_id] += 1 / (k + rank)
    
    # 6. 점수 순으로 정렬
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:limit]
    
    # 7. 최종 결과 구성
    id_to_point = {}
    for result in dense_results + sparse_results:
        if result.id not in id_to_point:
            id_to_point[result.id] = result
    
    output = []
    for point_id in sorted_ids:
        if point_id in id_to_point:
            r = id_to_point[point_id]
            output.append({
                "cosmetic_id": r.payload["cosmetic_id"],
                "score": rrf_scores[point_id],
                "name": r.payload["name"],
                "brand": r.payload["brand"],
                "category": r.payload["category"],
                "price": r.payload["price"],
                "skin_type": r.payload["skin_type"],
                "skin_disease": r.payload["skin_disease"],
            })
    
    return output
```

**옵션 2**: Prefetch에 명시적 인덱스 지정 (복잡)
```python
# Prefetch 구성 시 명시적으로 인덱스 지정
prefetch = [
    Prefetch(
        query=dense_query_list, 
        using="dense", 
        limit=20
    ),
    Prefetch(
        query=sparse_query_obj, 
        using="bm25", 
        limit=20
    ),
]

# 메인 쿼리를 RRF fusion으로 변경
results = client.query_points(
    collection_name=QDRANT_HYBRID_COLLECTION,
    prefetch=prefetch,
    query=FusionQuery(fusion=Fusion.RRF),  # RRF로 병합
    query_filter=query_filter,
    limit=limit,
    with_payload=True
)
```

**영향 범위**:
- ✅ 시나리오 6-1 ~ 6-7: 증상별 화장품 추천 (모두 실패)
- 영향받는 파일:
  - `backend/app/services/vector_store.py` (수정 필요)
  - `backend/app/services/chat_tools.py` (호출부)
  - `backend/app/services/recommendation.py` (호출부)

**우선순위**: 🔴 최우선 (핵심 기능 작동 불가)

---

### ⚠️ 문제 3: LLM 추천 결과 파싱 오류
**심각도**: ⚠️ 중간 (간헐적)

**증상**:
```
2025-11-03 17:11:14,584 - app.services.recommendation - ERROR - LLM 응답 파싱 실패: LLM이 3개가 아닌 2개를 반환했습니다.
2025-11-03 17:11:14,584 - app.services.recommendation - ERROR - LLM 응답 원문: ```json
```

**발생 위치**:
- `backend/app/services/recommendation.py` → `_select_top3_with_llm()` 메서드
- 라인 195-196: 검증 로직

**원인**:
1. LLM(GPT-4o-mini)이 프롬프트 지시를 정확히 따르지 않음
2. JSON 파싱 실패 또는 빈 응답 반환
3. `recommendations` 배열이 2개 이하로 반환됨

**현재 코드**:
```python
# 검증
if len(recommendations) != 3:
    raise ValueError(f"LLM이 3개가 아닌 {len(recommendations)}개를 반환했습니다.")

return recommendations
```

**Fallback 동작**:
```python
except Exception as e:
    logger.error(f"LLM 응답 파싱 실패: {e}")
    logger.error(f"LLM 응답 원문: {response.content}")
    
    # 실패 시 상위 3개 반환 (fallback)
    return [
        {
            "ranking": i + 1,
            "cosmetic_id": cosmetic.cosmetic_id,
            "reason": f"{cosmetic.main_effect} 효과로 {diagnosis.disease_name} 케어에 적합합니다."
        }
        for i, cosmetic in enumerate(cosmetics[:3])
    ]
```

**해결 방법**:

**1) 프롬프트 개선** (`backend/app/core/prompt/recommendation.yaml`)
```yaml
instruction: |
  당신은 피부과 전문의이자 화장품 성분 전문가입니다.
  
  **중요**: 반드시 정확히 3개의 화장품을 선정해야 합니다.
  
  아래 조건을 고려하여 Top 10 중 최종 3개를 선정하고 추천 이유를 작성하세요:
  
  1. 사용자의 피부 질환과 증상에 가장 적합한 제품
  2. 성분의 과학적 근거 (key_ingredient, main_effect)
  3. 피부 타입과의 호환성
  4. 가격 대비 효과
  5. Similarity Score (유사도) 참고
  
  **출력 형식 (반드시 이 JSON 형식만 출력):**
  ```json
  {
    "recommendations": [
      {
        "ranking": 1,
        "cosmetic_id": 123,
        "reason": "구체적인 추천 이유 (100자 이상)"
      },
      {
        "ranking": 2,
        "cosmetic_id": 456,
        "reason": "구체적인 추천 이유 (100자 이상)"
      },
      {
        "ranking": 3,
        "cosmetic_id": 789,
        "reason": "구체적인 추천 이유 (100자 이상)"
      }
    ]
  }
  ```
  
  **주의사항:**
  - 반드시 3개를 선정해야 합니다 (2개 이하 불가)
  - JSON 형식 외 다른 텍스트 출력 금지
  - cosmetic_id는 제공된 Top 10 리스트에서만 선택
```

**2) 파싱 로직 개선** (더 관대한 검증)
```python
# 검증
if len(recommendations) < 3:
    logger.warning(f"LLM이 {len(recommendations)}개만 반환. Fallback으로 상위 3개 사용")
    # Fallback: 부족한 개수만큼 채우기
    existing_ids = {r["cosmetic_id"] for r in recommendations}
    for i, cosmetic in enumerate(cosmetics):
        if len(recommendations) >= 3:
            break
        if cosmetic.cosmetic_id not in existing_ids:
            recommendations.append({
                "ranking": len(recommendations) + 1,
                "cosmetic_id": cosmetic.cosmetic_id,
                "reason": f"{cosmetic.main_effect} 효과로 {diagnosis.disease_name} 케어에 적합합니다."
            })

return recommendations[:3]  # 최대 3개만 반환
```

**3) Temperature 조정**
```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.3,  # 0.7 → 0.3으로 낮춤 (더 일관된 출력)
)
```

**영향 범위**:
- 진단 후 추천 생성 시 간헐적 실패
- Fallback이 있어 치명적이진 않지만, 추천 품질 저하

**우선순위**: ⚠️ 중간 (Fallback 동작하지만 개선 필요)

---

## 테스트 결과 요약

### ✅ 정상 동작한 시나리오
1. **시나리오 1**: 진단 이력 조회 ✅
   - Tool: `get_recent_diagnosis`
   - 응답: 정상 (진단 결과 반환)

2. **시나리오 8**: 제품 상세 정보 조회 ✅
   - Tool: `get_cosmetic_detail`
   - 응답: 정상 (제품 리스트 반환)

### ❌ 실패한 시나리오
3. **시나리오 6-1 ~ 6-7**: 증상별 화장품 추천 (모두 실패) ❌
   - Tool: `recommend_by_symptom`
   - 원인: Qdrant Prefetch 검증 오류 (문제 2)
   - 영향: AI 에이전트가 화장품 추천 불가

## 권장 조치사항

### 🔴 긴급 (즉시 수정 필요)
1. **Qdrant Prefetch 오류 수정** (문제 2)
   - `backend/app/services/vector_store.py` 수정
   - 옵션 1 (수동 RRF) 또는 옵션 2 (FusionQuery) 적용
   - 수정 후 전체 시나리오 재테스트

### ⚠️ 중요 (단기 내 수정)
2. **작업 디렉토리 이슈 해결** (문제 1)
   - `backend/app/utils/prompt.py` 절대 경로로 수정
   - 어느 위치에서 실행해도 정상 동작하도록 개선

3. **LLM 추천 로직 개선** (문제 3)
   - 프롬프트 명확화
   - 파싱 로직 관대화
   - Temperature 조정

### 📝 추가 권장사항
4. **통합 테스트 자동화**
   - GitHub Actions CI/CD 파이프라인 구축
   - pytest 기반 자동 테스트 추가

5. **로깅 개선**
   - Qdrant 요청/응답 상세 로그 추가
   - LLM 응답 전체 내용 로그 저장

6. **에러 핸들링 강화**
   - Qdrant 오류 시 재시도 로직 추가
   - LLM 오류 시 더 나은 Fallback 전략

## 다음 단계
1. ✅ 문제 파악 완료
2. 🔴 Qdrant Prefetch 오류 수정 (최우선)
3. ⚠️ 작업 디렉토리 이슈 수정
4. ⚠️ LLM 추천 로직 개선
5. ✅ 전체 시나리오 재테스트
6. 📝 문서화 및 배포

---

**보고서 작성일**: 2025-11-03  
**테스트 환경**: Windows 10, Python 3.x, 가상환경 skin_nunu  
**작성자**: AI Assistant

