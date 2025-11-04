[최종 검색 전략 구조]
**핵심 원칙**

정확도 우선: DB 정확 매칭 → 하이브리드 보완
단계적 Fallback: 결과 수에 따라 전략 변경
명시적 동의: 프로필/가격 필터는 사용자 요청 시만
Hallucination 방지: DB 데이터만 사용

**구현 플로우**
입력: "에스트라 크림"
  ↓
[1단계] 파싱 & 정규화
  ↓
[2단계] DB 정확 매칭 (LIKE AND)
  ↓
├─ 1개 → 상세 정보 즉시 반환
├─ 2~10개 → 목록 제시 + 선택 유도
└─ 0개 → [3단계] 하이브리드 검색
     ↓
  [4단계] 결과 렌더링 & UX 처리

**세부 구현 설계**
1단계: 파싱 & 정규화
# 카테고리 동의어 사전
CATEGORY_SYNONYMS = {
    "크림": ["크림", "모이스처라이저", "cream", "moisturizer"],
    "세럼": ["세럼", "에센스", "앰플", "serum", "essence", "ampoule"],
    "토너": ["토너", "스킨", "toner", "skin"],
    # ...
}

# 브랜드 마스터 (다단어 처리)
BRAND_LIST = [
    "에스트라", "더페이스샵", "라로슈포제", 
    "이니스프리", "설화수", ...
]

def parse_and_normalize(query):
    # 1. 한글 정규화 (공백/특수문자 제거, 대소문자 통일)
    normalized = normalize_korean(query)
    
    # 2. 브랜드 추출 (N-gram 매칭)
    brand = extract_brand(normalized, BRAND_LIST)
    
    # 3. 카테고리 추출 (동의어 매핑)
    category = extract_category(normalized, CATEGORY_SYNONYMS)
    
    # 4. 나머지 → name 키워드
    name_tokens = remove_matched_tokens(normalized, [brand, category])
    
    return {
        "brand": brand,           # "에스트라"
        "category": category,     # "크림"
        "name_tokens": name_tokens,
        "original": query
    }


2단계: DB 정확 매칭
def db_exact_search(parsed):
    """
    브랜드 AND (카테고리 OR 제품명) 정확 매칭
    """
    query = """
        SELECT * FROM cosmetics
        WHERE brand LIKE %s
        AND (category LIKE %s OR name LIKE %s)
    """
    
    brand_pattern = f"%{parsed['brand']}%"
    category_pattern = f"%{parsed['category']}%"
    
    results = execute_query(query, [
        brand_pattern, 
        category_pattern, 
        category_pattern
    ])
    
    return results

# 결과 처리
results = db_exact_search(parsed)

if len(results) == 1:
    return render_detail(results[0])
    
elif 2 <= len(results) <= 10:
    return render_list(results) + "\n어떤 제품을 원하시나요?"
    
elif len(results) == 0:
    # 3단계로 이동
    return hybrid_search(parsed)
    
else:  # 10개 초과
    return render_list(results[:10]) + "\n더 구체적인 제품명을 알려주세요."


3단계: 하이브리드 검색 (Fallback)
# 카테고리별 Dense 프리셋 (임베딩 캐싱)
CATEGORY_PRESETS = {
    "크림": "크림 보습 진정 장벽케어 수분공급",
    "세럼": "세럼 집중케어 영양 탄력 미백",
    "토너": "토너 각질제거 pH밸런스 진정 수렴",
    # ...
}

def hybrid_search(parsed, user_profile=None, filters=None):
    """
    BM25 + Dense + 조건부 필터
    """
    
    # BM25 쿼리 구성
    bm25_query = {
        "query": parsed["original"],  # "에스트라 크림"
        "fields": {
            "brand": {"boost": 2.5, "fuzzy": 1},    # 편집거리 1 허용
            "category": {"boost": 1.5},
            "name": {"boost": 1.2}
        }
    }
    
    # Dense 쿼리 (카테고리 프리셋 사용)
    dense_text = CATEGORY_PRESETS.get(
        parsed["category"], 
        parsed["original"]
    )
    dense_query = {
        "query_vector": get_cached_embedding(dense_text),
        "fields": ["main_effect", "care_symptom", "description", "key_ingredient"]
    }
    
    # 메타데이터 필터 (조건부)
    metadata_filter = {"must": [], "should": []}
    
    # 브랜드/카테고리 강제 (노이즈 최소화)
    if parsed["brand"]:
        metadata_filter["must"].append({"brand": parsed["brand"]})
    if parsed["category"]:
        metadata_filter["must"].append({"category": parsed["category"]})
    
    # 사용자 요청 시만 적용
    if filters and filters.get("price"):
        metadata_filter["must"].append({"price": filters["price"]})
    
    if filters and filters.get("use_profile") and user_profile:
        metadata_filter["should"].append({
            "skin_type": user_profile["skin_type"],
            "skin_condition": user_profile["skin_condition"]
        })
    
    # 하이브리드 검색 실행
    results = vector_db.hybrid_search(
        bm25=bm25_query,
        dense=dense_query,
        filter=metadata_filter,
        rank_weights={"dense": 0.6, "bm25": 0.4},  # λMix
        top_k=10
    )
    
    # 중복 제거 (동일 브랜드/제품명)
    results = deduplicate(results)
    
    return results

4단계: 결과 렌더링 & UX
def render_response(results, parsed):
    if len(results) == 0:
        # 부분 일치 제안
        brand_only = db_search(brand=parsed["brand"])
        category_only = db_search(category=parsed["category"])
        
        suggestions = []
        if brand_only:
            suggestions.append(f"'{parsed['brand']}' 브랜드의 다른 제품")
        if category_only:
            suggestions.append(f"'{parsed['category']}' 카테고리의 다른 제품")
        
        return f"검색 결과가 없습니다. {', '.join(suggestions)}을 찾았습니다. 확인하시겠어요?"
    
    elif len(results) == 1:
        # 단일 결과 → 상세 정보
        return render_product_detail(results[0])
    
    elif 2 <= len(results) <= 5:
        # 소수 목록
        return render_product_list(results) + "\n\n어떤 제품의 상세 정보를 원하시나요?"
    
    else:
        # 다수 목록 (상위 5개)
        return (
            render_product_list(results[:5]) 
            + "\n\n더 많은 결과가 있습니다. 정확한 제품명을 알려주시면 더 도움이 됩니다."
        )

def render_product_detail(product):
    """
    DB 필드만 사용 (Hallucination 방지)
    """
    return f"""
제품명: {product['name']}
브랜드: {product['brand']}
카테고리: {product['category']}
가격: {product['price']:,}원
주요 효능: {product['main_effect']}
적합 피부: {', '.join(product['skin_type'])}
주요 성분: {', '.join(product['key_ingredient'])}
"""

**보조 기능**
임베딩 캐시
EMBEDDING_CACHE = {}

def get_cached_embedding(text):
    if text not in EMBEDDING_CACHE:
        EMBEDDING_CACHE[text] = embed_model.encode(text)
    return EMBEDDING_CACHE[text]

# 앱 시작 시 프리셋 캐싱
for category, preset in CATEGORY_PRESETS.items():
    get_cached_embedding(preset)

로깅
def log_search(parsed, bm25_top3, dense_top3, filters, final_results):
    logger.info({
        "parsed_brand": parsed["brand"],
        "parsed_category": parsed["category"],
        "parsed_keywords": parsed["name_tokens"],
        "bm25_top3_scores": bm25_top3,
        "dense_top3_scores": dense_top3,
        "applied_filters": filters,
        "result_count": len(final_results)
    })

에러 처리
@retry(tries=3, delay=1, backoff=2)
def safe_vector_search(query):
    try:
        return vector_db.search(query, timeout=5)
    except TimeoutError:
        return fallback_response("검색 시간이 초과되었습니다. 다시 시도해주세요.")
    except Exception as e:
        logger.error(f"Search error: {e}")
        return fallback_response("검색 중 오류가 발생했습니다.")
    