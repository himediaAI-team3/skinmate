# AI Agent 추가 Tool 구현 계획

## 개요

AI Agent에 3개의 추가 Tool을 구현하여 채팅 기능을 확장합니다.

---

## Tool 목록

1. **recommend_by_symptom()**: 특정 증상에 맞는 화장품 재추천
2. **request_rediagnosis()**: 재진단 요청 안내
3. **get_product_detail()**: 특정 제품 상세 정보 조회

---

## 1. recommend_by_symptom() - 증상별 화장품 재추천

### 목적

사용자가 피부 분석 없이 증상명만으로 화장품을 추천받을 수 있는 Tool입니다.

### Tool 시그니처

```python
@tool
def recommend_by_symptom(
    symptom: str,
    skin_type: str = None,
    detail: str = None,
    use_my_profile: bool = False,
    min_price: int = None,
    max_price: int = None,
    price_range: str = None
) -> str:
    """특정 증상에 맞는 화장품을 추천합니다.
    
    Args:
        symptom: 피부 증상 (필수) - 예: "여드름", "아토피", "건선", "주사", "지루"
        skin_type: 피부 타입 (선택) - 예: "지성", "건성", "복합성", "민감성"
        detail: 상세 증상 설명 (선택) - 예: "볼과 턱에 붉은 여드름이 많음, 진정 효과 필요"
        use_my_profile: 내 회원 정보 활용 여부 (선택) - True면 DB 저장된 스킨타입만 활용 (가격대 제외)
        min_price: 최소 가격 (선택) - 단위: 원
        max_price: 최대 가격 (선택) - 단위: 원
        price_range: 가격대 범위 (선택) - 예: "2만원대", "3-5만원", "5만원 이상"
    """
```

### 핵심 설계 원칙

#### 1. DB 저장 안함
- 채팅으로 입력받은 정보는 일회성 조회용
- 추천 결과를 DB에 저장하지 않음
- 기존 `recommendation` 테이블과 독립적

#### 2. 필터 우선순위
```
기본: 증상명만 (필터 없음)
  ↓
사용자 입력: skin_type, detail, price_range
  ↓
프로필 활용: use_my_profile=True → 스킨타입만 활용 (가격대 제외)
```

#### 3. 가격대 처리
- **기본**: 가격대 필터 없음
- **사용자 입력**: `price_range`, `min_price`, `max_price` 파라미터로 받음
- **프로필 활용**: `use_my_profile=True`일 때도 가격대는 **제외**
- **이유**: 가격대는 선호도 정보이므로 진단 정보와 별개로 취급

---

### 시나리오별 처리 로직

#### 시나리오 1: 증상명만 입력 (기본)

**사용자 입력**:
```
"여드름에 맞는 화장품 추천해줘"
```

**Tool 호출**:
```python
recommend_by_symptom(symptom="여드름")
```

**처리 로직**:
```python
# 1. 필터 구성
filters = {"skin_disease": "여드름"}
query = "여드름 케어"

# 2. 벡터 검색
search_results = VectorStoreService.search_cosmetics(
    query=query,
    filters=filters,
    limit=10
)

# 3. LLM으로 최종 3개 선정
recommendations = RecommendationService._select_top3_with_llm(
    diagnosis={"disease_name": "여드름", "summary": ""},
    cosmetics=cosmetics,
    search_scores=scores
)

# 4. 응답 포맷팅
return f"""
**여드름 증상에 적합한 화장품 TOP 3**

1. {product1.name} ({product1.brand})
   - 가격: {product1.price:,}원
   - 추천 이유: {reason1}

2. {product2.name} ({product2.brand})
   - 가격: {product2.price:,}원
   - 추천 이유: {reason2}

3. {product3.name} ({product3.brand})
   - 가격: {product3.price:,}원
   - 추천 이유: {reason3}

💡 **더 정확한 추천을 원하시나요?**
- 피부 타입을 알려주시면 더 적합한 제품을 추천해드려요
- 가격대를 지정해주시면 원하는 가격대의 제품을 찾아드려요 (예: "2만원대로", "3-5만원")
- 증상을 구체적으로 설명해주시면 맞춤 추천이 가능합니다
- 이전 진단 정보를 활용하려면 "내 피부 타입으로 추천해줘"라고 말씀해주세요
"""
```

---

#### 시나리오 2: 증상 + 피부타입

**사용자 입력**:
```
"지성 피부인데 여드름에 좋은 제품 추천해줘"
```

**Tool 호출** (Agent가 자동 파싱):
```python
recommend_by_symptom(
    symptom="여드름",
    skin_type="지성"
)
```

**처리 로직**:
```python
filters = {
    "skin_disease": "여드름",
    "skin_type": "지성"  # 사용자가 입력한 값
}
query = "여드름 지성 케어"

search_results = VectorStoreService.search_cosmetics(
    query=query,
    filters=filters,
    limit=10
)

# 응답 안내문구는 간소화
return f"""
**지성 피부의 여드름 증상에 적합한 화장품 TOP 3**

1. ...

💡 증상을 더 자세히 설명해주시면 맞춤 추천이 가능합니다.
"""
```

---

#### 시나리오 3: 증상 + 상세 설명 (자연어)

**사용자 입력**:
```
"턱과 볼에 붉은 여드름이 많은데 진정 효과 좋은 제품 알려줘"
```

**Tool 호출**:
```python
recommend_by_symptom(
    symptom="여드름",
    detail="턱과 볼에 붉은 여드름이 많음, 진정 효과 필요"
)
```

**처리 로직**:
```python
# 자연어를 벡터 검색 쿼리에 활용
vector_query = f"{symptom} {detail}"
# "여드름 턱과 볼에 붉은 여드름이 많음, 진정 효과 필요"

filters = {"skin_disease": symptom}

search_results = VectorStoreService.search_cosmetics(
    query=vector_query,
    filters=filters,
    limit=10
)

# LLM 선정 시 detail을 summary처럼 활용
recommendations = RecommendationService._select_top3_with_llm(
    diagnosis={
        "disease_name": symptom,
        "summary": detail  # 상세 증상을 summary처럼 활용
    },
    cosmetics=cosmetics,
    search_scores=scores
)
```

---

#### 시나리오 4: 가격대 재검색

**사용자 입력**:
```
"여드름에 맞는 화장품 추천해줘"
→ 추천 결과 반환

"이것들 말고 좀 더 싼 가격대로 보여줘"
```

**Tool 호출** (Agent가 "싼 가격대"를 파싱):
```python
recommend_by_symptom(
    symptom="여드름",
    max_price=30000  # Agent가 "싼 가격대"를 최대 3만원 이하로 파싱
)
```

**처리 로직**:
```python
filters = {
    "skin_disease": "여드름",
    "price_range": [0, 30000]  # 최대 3만원 이하
}

search_results = VectorStoreService.search_cosmetics(
    query="여드름 케어",
    filters=filters,
    limit=10
)
```

---

#### 시나리오 5: 가격대 직접 입력

**사용자 입력**:
```
"2만원대 여드름 화장품 추천해줘"
```

**Tool 호출**:
```python
recommend_by_symptom(
    symptom="여드름",
    price_range="2만원대"
)
```

**처리 로직** (price_range 파싱):
```python
def parse_price_range(price_range: str) -> tuple:
    """가격대 문자열을 (min_price, max_price)로 변환"""
    import re
    
    if not price_range:
        return (None, None)
    
    # "2만원대" → 20000~29999
    if "만원대" in price_range:
        match = re.search(r'(\d+)만원대', price_range)
        if match:
            base = int(match.group(1)) * 10000
            return (base, base + 9999)
    
    # "3-5만원" 또는 "3~5만원" → 30000~50000
    elif "~" in price_range or "-" in price_range:
        parts = re.findall(r'(\d+)', price_range)
        if len(parts) >= 2:
            return (int(parts[0]) * 10000, int(parts[1]) * 10000)
    
    # "5만원 이상" → 50000 이상
    elif "이상" in price_range:
        match = re.search(r'(\d+)만원', price_range)
        if match:
            base = int(match.group(1)) * 10000
            return (base, 999999)
    
    # "5만원 이하" → 5만원 이하
    elif "이하" in price_range:
        match = re.search(r'(\d+)만원', price_range)
        if match:
            base = int(match.group(1)) * 10000
            return (0, base)
    
    return (None, None)

# 사용
min_price, max_price = parse_price_range("2만원대")
# (20000, 29999)

filters = {
    "skin_disease": "여드름",
    "price_range": [min_price, max_price]
}
```

---

#### 시나리오 6: 프로필 활용 (스킨타입만)

**사용자 입력**:
```
"저번에 진단했던 정보대로 여드름 화장품 추천해줘"
또는
"내 피부 타입으로 여드름 화장품 추천해줘"
```

**Tool 호출** (Agent가 자동 판단):
```python
recommend_by_symptom(
    symptom="여드름",
    use_my_profile=True
)
```

**처리 로직**:
```python
if use_my_profile:
    # 회원 정보 조회
    member = MemberRepository.get_by_id(db, member_id)
    
    filters = {
        "skin_disease": symptom,
        "skin_type": member.skin_type  # 스킨타입만 활용
        # 가격대 필터 제외!
    }
    
    query = f"{symptom} {member.skin_type} 케어"
else:
    filters = {"skin_disease": symptom}
    query = f"{symptom} 케어"

search_results = VectorStoreService.search_cosmetics(
    query=query,
    filters=filters,
    limit=10
)

# 응답
return f"""
**귀하의 피부 타입({member.skin_type})에 맞는 여드름 화장품 TOP 3**

(이전 진단 정보 활용: {member.skin_type} 피부)

1. ...
"""
```

---

#### 시나리오 7: 모든 정보 입력

**사용자 입력**:
```
"지성 피부인데 2만원대 여드름 화장품 추천해줘"
```

**Tool 호출**:
```python
recommend_by_symptom(
    symptom="여드름",
    skin_type="지성",
    price_range="2만원대"
)
```

**처리 로직**:
```python
min_price, max_price = parse_price_range("2만원대")
# (20000, 29999)

filters = {
    "skin_disease": "여드름",
    "skin_type": "지성",
    "price_range": [min_price, max_price]
}

query = f"여드름 지성 케어"
```

---

### 구현 세부사항

#### 1. VectorStoreService 확장

**기존 메서드**:
```python
VectorStoreService.search_by_analysis(
    db, analysis_id, member_id, limit=10
)
```

**새 메서드 추가**:
```python
@staticmethod
def search_cosmetics(
    db: Session,
    query: str,           # 자연어 쿼리
    filters: dict,        # 필터 조건
    limit: int = 10
) -> List[dict]:
    """자연어 쿼리로 화장품 검색
    
    Args:
        query: 자연어 검색 쿼리 (예: "여드름 지성 케어")
        filters: 필터 조건
            - skin_disease: 증상명
            - skin_type: 피부 타입 (선택)
            - price_range: [min_price, max_price] (선택)
        limit: 검색 결과 개수
        
    Returns:
        List[dict]: 검색 결과 리스트
    """
    # 1. 쿼리 임베딩
    # 2. Qdrant 벡터 검색
    # 3. 필터 적용 (skin_type, price_range)
    # 4. 결과 반환
```

**구현 위치**: `backend/app/services/vector_store.py`

---

#### 2. chat_tools.py에 Tool 추가

**파일**: `backend/app/services/chat_tools.py`

**추가 내용**:
```python
def create_recommend_by_symptom_tool(db: Session, member_id: int):
    """증상별 화장품 재추천 Tool 생성"""
    
    @tool
    def recommend_by_symptom_impl(
        symptom: str,
        skin_type: str = None,
        detail: str = None,
        use_my_profile: bool = False,
        min_price: int = None,
        max_price: int = None,
        price_range: str = None
    ) -> str:
        """특정 증상에 맞는 화장품을 추천합니다."""
        
        # 1. 필터 구성
        filters = {"skin_disease": symptom}
        query_parts = [symptom]
        
        # 2. 프로필 활용 (스킨타입만)
        if use_my_profile:
            member = MemberRepository.get_by_id(db, member_id)
            filters["skin_type"] = member.skin_type
            query_parts.append(member.skin_type)
        
        # 3. 사용자 입력 정보
        if skin_type:
            filters["skin_type"] = skin_type  # 덮어쓰기
        
        if detail:
            query_parts.append(detail)
        
        # 4. 가격대 처리
        if price_range:
            min_price, max_price = parse_price_range(price_range)
            if min_price is not None and max_price is not None:
                filters["price_range"] = [min_price, max_price]
        elif min_price is not None or max_price is not None:
            filters["price_range"] = [
                min_price or 0,
                max_price or 999999
            ]
        
        # 5. 벡터 검색
        query = " ".join(query_parts) + " 케어"
        search_results = VectorStoreService.search_cosmetics(
            db=db,
            query=query,
            filters=filters,
            limit=10
        )
        
        # 6. LLM 선정
        # 7. 응답 포맷팅
        return formatted_response
    
    return recommend_by_symptom_impl

def parse_price_range(price_range: str) -> tuple:
    """가격대 문자열 파싱"""
    # 위 시나리오 5의 로직 구현
    pass
```

---

#### 3. get_chat_tools() 수정

**파일**: `backend/app/services/chat_tools.py`

**수정 내용**:
```python
def get_chat_tools(db: Session, member_id: int) -> list:
    """Agent에 전달할 Tool 리스트 생성"""
    return [
        create_diagnosis_history_tool(db, member_id),
        create_recommended_products_tool(db, member_id),
        create_recommend_by_symptom_tool(db, member_id),  # 추가
        # ... 나머지 Tool들
    ]
```

---

### 응답 안내문구 가이드

#### 최소 정보 입력 시
```
💡 **더 정확한 추천을 원하시나요?**
- 피부 타입을 알려주시면 더 적합한 제품을 추천해드려요
- 가격대를 지정해주시면 원하는 가격대의 제품을 찾아드려요 (예: "2만원대로", "3-5만원")
- 증상을 구체적으로 설명해주시면 맞춤 추천이 가능합니다
- 이전 진단 정보를 활용하려면 "내 피부 타입으로 추천해줘"라고 말씀해주세요
```

#### 가격대 재검색 안내
```
💡 다른 가격대를 원하시나요?
- "좀 더 싼 가격대로 보여줘"
- "2만원대 제품으로 보여줘"
- "3-5만원 제품 추천해줘"
```

---

## 2. request_rediagnosis() - 재진단 요청 안내

### 목적

사용자가 재진단을 원할 때 안내 메시지를 제공하는 Tool입니다.

### Tool 시그니처

```python
@tool
def request_rediagnosis() -> str:
    """재진단을 요청합니다. 새로운 얼굴 사진 업로드 페이지로 안내합니다."""
```

### 구현 내용

**파일**: `backend/app/services/chat_tools.py`

```python
def create_request_rediagnosis_tool():
    @tool
    def request_rediagnosis_impl() -> str:
        """재진단을 요청합니다."""
        return """
🔄 재진단을 원하시는군요!

피부 상태는 계속 변화하므로 정기적인 진단이 중요합니다.

**다음 단계:**
1. 앱에서 '피부 분석' 메뉴로 이동
2. 새로운 얼굴 사진 촬영
3. AI 진단 결과 확인

📱 피부 분석 페이지로 이동해주세요!

💡 **재진단이 필요한 경우:**
- 피부 상태가 변화했을 때
- 새로운 증상이 나타났을 때
- 약 2-4주 주기로 권장
"""
    
    return request_rediagnosis_impl
```

### 사용 시나리오

**사용자 입력**:
```
"피부 상태가 달라진 것 같아, 다시 진단받고 싶어"
또는
"재진단 받고 싶어"
또는
"다시 진단해줘"
```

**Agent 판단**: 재진단 요청 → `request_rediagnosis()` 호출

**응답**: 안내 메시지 반환

---

## 3. get_product_detail() - 제품 상세 정보 조회

### 목적

사용자가 특정 화장품의 상세 정보를 조회할 수 있는 Tool입니다.

### Tool 시그니처

```python
@tool
def get_product_detail(product_name: str) -> str:
    """특정 화장품의 상세 정보를 조회합니다.
    
    Args:
        product_name: 화장품 이름 (예: "아이디플라코스메틱 엑소브이 플러스 앰플")
    """
```

### 구현 내용

**파일**: `backend/app/services/chat_tools.py`

```python
def create_get_product_detail_tool(db: Session, member_id: int):
    @tool
    def get_product_detail_impl(product_name: str) -> str:
        """특정 화장품의 상세 정보를 조회합니다."""
        
        # 1. DB에서 제품명으로 검색
        cosmetics = db.query(Cosmetic).filter(
            Cosmetic.name.like(f"%{product_name}%")
        ).all()
        
        if not cosmetics:
            return f"'{product_name}' 제품을 찾을 수 없습니다.\n\n다른 제품명으로 검색해주세요."
        
        # 2. 여러 결과가 있으면 첫 번째 선택 (또는 Agent에게 선택 요청)
        if len(cosmetics) > 1:
            # 여러 결과 반환 (Agent가 선택하도록)
            result = f"'{product_name}'로 검색한 결과 {len(cosmetics)}개가 있습니다:\n\n"
            for i, cosmetic in enumerate(cosmetics[:5], 1):  # 최대 5개
                result += f"{i}. {cosmetic.name} ({cosmetic.brand})\n"
            result += "\n더 정확한 제품명을 알려주시면 상세 정보를 제공하겠습니다."
            return result
        
        cosmetic = cosmetics[0]
        
        # 3. 상세 정보 포맷팅
        return f"""
**{cosmetic.name}**

🏷️ **브랜드**: {cosmetic.brand}
💰 **가격**: {int(cosmetic.price):,}원
📦 **카테고리**: {cosmetic.category}

✨ **주요 효능**: {cosmetic.main_effect or "정보 없음"}
🧪 **핵심 성분**: {cosmetic.key_ingredient or "정보 없음"}
💊 **케어 증상**: {cosmetic.care_symptom or "정보 없음"}
👤 **피부 타입**: {cosmetic.skin_type or "정보 없음"}
🏥 **관련 질환**: {cosmetic.skin_disease or "정보 없음"}

📝 **한줄 설명**: {cosmetic.short_description or "정보 없음"}

📄 **상세 설명**:
{cosmetic.description or "상세 설명이 없습니다."}

🔗 **구매하기**: {cosmetic.buy_url or "구매 링크가 없습니다."}

💡 추가 정보가 필요하시면 질문해주세요!
"""
    
    return get_product_detail_impl
```

### 사용 시나리오

**사용자 입력**:
```
"아이디플라 앰플 자세히 알려줘"
또는
"엑소브이 플러스 앰플 정보 보여줘"
```

**Agent 판단**: 제품명 인식 → `get_product_detail()` 호출

**응답**: 제품 상세 정보 반환

---

## 구현 작업 순서

### 1단계: VectorStoreService 확장
- [ ] `search_cosmetics()` 메서드 추가
- [ ] 자연어 쿼리 임베딩 기능
- [ ] 필터 로직 (skin_type, price_range) 구현

### 2단계: price_range 파싱 함수
- [ ] `parse_price_range()` 함수 구현
- [ ] 다양한 가격대 형식 지원 ("2만원대", "3-5만원", "5만원 이상" 등)

### 3단계: chat_tools.py에 Tool 추가
- [ ] `create_recommend_by_symptom_tool()` 구현
- [ ] `create_request_rediagnosis_tool()` 구현
- [ ] `create_get_product_detail_tool()` 구현
- [ ] `get_chat_tools()`에 Tool 추가

### 4단계: 테스트
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] Swagger UI에서 테스트

---

## 참고사항

### DB 저장 정책
- **저장 안함**: `recommend_by_symptom()` 추천 결과
- **저장 안함**: 채팅으로 입력받은 정보 (skin_type, price_range 등)
- **저장됨**: 기존 `member` 테이블 정보 (조회용)

### 성능 고려사항
- 벡터 검색 시 필터 적용 순서 최적화
- 가격대 파싱 함수 효율성
- 제품명 검색 시 LIKE 검색 성능 (인덱스 확인)

### 확장 가능성
- 추천 결과를 임시 저장하는 옵션 (캐시)
- 제품 상세 정보에 이미지 포함
- 여러 제품 비교 기능

---

## 완료 기준

- [ ] 3개 Tool 모두 구현 완료
- [ ] 모든 시나리오 테스트 통과
- [ ] Swagger UI에서 정상 작동 확인
- [ ] 에러 핸들링 구현
- [ ] 응답 안내문구 명확히 작성

