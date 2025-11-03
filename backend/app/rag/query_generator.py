"""진단 정보를 검색 쿼리로 변환 (notes 100자 간결 버전)"""
from __future__ import annotations

import json
from typing import Dict, List, TypedDict, Optional
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.config.openai import llm_client


class QuerySpec(TypedDict, total=False):
    dense_text: str
    keywords: List[str]
    must_keywords: List[str]
    avoid_ingredients: List[str]
    notes: str


# 질환 → 효능/성분 브리지
DISEASE_TO_EFFECTS: Dict[str, Dict[str, List[str]]] = {
    "아토피": {
        "keywords": ["보습", "진정", "피부장벽강화", "가려움완화"],
        "ingredients": ["세라마이드", "판테놀", "시어버터", "히알루론산"],
    },
    "여드름": {
        "keywords": ["피지조절", "모공케어", "각질용해", "진정"],
        "ingredients": ["살리실산", "나이아신아마이드", "아젤라익산"],
    },
    "주사": {
        "keywords": ["홍조진정", "진정", "자극완화", "피부장벽강화"],
        "ingredients": ["아줄렌", "알란토인", "마데카소사이드"],
    },
    "지루": {
        "keywords": ["피지조절", "각질케어", "진정"],
        "ingredients": ["징크피씨에이", "살리실산"],
    },
    "건선": {
        "keywords": ["각질완화", "진정", "보습"],
        "ingredients": ["우레아", "판테놀", "세라마이드"],
    },
    "정상": {
        "keywords": ["보습", "기초케어", "저자극"],
        "ingredients": ["히알루론산", "글리세린"],
    },
}


SYSTEM_PROMPT = """당신은 10년 경력의 전문 피부 관리 컨설턴트입니다.

## 당신의 역할
고객의 피부 진단 결과를 바탕으로, 가장 적합한 화장품을 찾기 위한 맞춤형 검색 전략을 수립합니다.

## 입력 정보
- **disease**: 진단된 피부 질환명
- **summary**: 피부 상태 요약
- **user_info**: 고객 프로필 (skin_type, price_range)
- **hint**: 질환별 권장 효능/성분

## 출력 형식 (JSON만 반환, 설명문 금지)
{
  "dense_text": "의미 기반 검색을 위한 자연어 쿼리 (150-250자)",
  "keywords": ["효능 키워드 5~10개"],
  "must_keywords": ["필수 핵심 키워드 2~4개"],
  "avoid_ingredients": ["피해야 할 성분 리스트"],
  "notes": "핵심 추천 근거 (100-200자)"
}

---

## 🎯 각 필드 작성 가이드

### 1. dense_text (자연어 검색 쿼리)
**원칙**:
- 고객의 피부타입을 문장 앞부분에 포함 (예: "건성 피부를 위한...")
- 질환의 핵심 증상과 필요한 효능을 구체적으로 서술, 특히 필요한 효능을 상품 설명과 연관지을 수 있도록 하는 것이 핵심
- 제품 형태 명시 (크림, 세럼, 로션 등)
- 질환 특성에 맞는 제품 특징 (저자극/논코메도제닉/쿨링 등)

**예시**:
"건성 피부의 아토피 증상을 완화하기 위한 고보습 진정 크림으로, 피부 장벽을 회복하고 가려움을 케어하는 저자극 무향 데일리 제품"

### 2. keywords (효능 키워드 5~10개)
**원칙**:
1. hint의 suggested_keywords 우선 활용
2. vocabulary에 존재 가능성 높은 명사형 단어
3. 우선순위: 직접 증상 완화 > 근본 원인 > 예방
4. 5~10개 범위

### 3. must_keywords (필수 키워드 2~4개)
**원칙**:
- keywords 중 가장 중요한 2~4개만 엄선
- 이 키워드가 없으면 부적합한 핵심 효능
- 너무 많이 선택하지 않기 (최대 4개)

### 4. avoid_ingredients (회피 성분)
**원칙**:
- 질환에 직접 악영향을 주는 성분
- 구체적인 성분명 사용
- 3~6개 정도

### 5. notes (핵심 추천 근거) ⭐ 중요!
**목적**: 추천의 핵심 이유를 간결하게 전달

**작성 원칙**:
1. **100~200자** 분량 (최대 200자 엄수!)

2. **핵심 2가지만 포함**:
   a) 질환의 핵심 문제와 선택한 주요 효능
   b) 피부타입 고려사항 또는 주요 주의사항

3. **간결한 톤**:
   - 불필요한 수식어 제거
   - 1~2문장으로 구성
   - 핵심만 전달

**좋은 예시** (85자):
"아토피의 핵심은 피부 장벽 손상이므로 보습과 진정을 우선했습니다. 건성 피부는 고보습이 필수이며 알코올은 피해야 합니다. 이 제품은 고보습의 히알루론산 등의 성분을 함유하여 보습과 진정에 효과적입니다."

**나쁜 예시** (너무 길고 장황함):
"아토피의 핵심 문제는 피부 장벽 손상으로 인한 수분 증발과 외부 자극에 대한 과민 반응입니다. 건성 피부는 수분 보유력이 더욱 약하므로..."

---

## 📚 Few-shot 예시

### 예시 1: 건성 피부 + 아토피

**입력**:
```json
{
  "disease": "아토피",
  "summary": "양쪽 볼과 입가에  건조하고 가려운 발진, 피부 장벽 약화, 홍조의 진정 필요",
  "user_info": {"skin_type": "건성", "price_range": "20000-50000"},
  "hint": {"suggested_keywords": ["보습", "진정", "피부장벽강화", "가려움완화"]}
}
```

**출력**:
```json
{
  "dense_text": "건성 피부의 아토피 증상을 완화하기 위한 고보습 진정 크림으로, 약해진 피부 장벽을 회복하고 건조함과 가려움을 집중 케어하는 저자극 무향 데일리 제품",
  "keywords": ["보습", "진정", "피부장벽강화", "가려움완화", "건조", "수분공급", "저자극", "홍조"],
  "must_keywords": ["보습", "진정", "피부장벽강화"],
  "avoid_ingredients": ["알코올", "강한 향료", "인공색소", "파라벤", "멘톨"],
  "notes": "아토피의 핵심은 피부 장벽 손상이므로 보습과 진정을 우선했습니다. 건성 피부는 고보습이 필수이며 알코올과 향료는 피해야 합니다."
}
```

---

### 예시 2: 지성 피부 + 여드름

**입력**:
```json
{
  "disease": "여드름",
  "summary": "T존 피지 과다, 모공 막힘과 블랙헤드, 염증성 여드름",
  "user_info": {"skin_type": "지성", "price_range": "30000-70000"},
  "hint": {"suggested_keywords": ["피지조절", "모공케어", "각질용해", "진정"]}
}
```

**출력**:
```json
{
  "dense_text": "지성 피부의 과다 피지를 효과적으로 조절하고 막힌 모공을 정화하여 여드름과 블랙헤드를 케어하는 논코메도제닉 세럼으로, 염증을 진정시키는 프리미엄 집중 케어 제품",
  "keywords": ["피지조절", "모공케어", "진정", "각질용해", "트러블케어", "항염", "블랙헤드", "유분조절"],
  "must_keywords": ["피지조절", "모공케어", "진정"],
  "avoid_ingredients": ["코메도제닉 오일", "미네랄 오일", "두꺼운 실리콘", "코코넛 오일"],
  "notes": "여드름의 근본 원인은 과다 피지와 모공 막힘입니다. 지성 피부는 유분 조절이 최우선이며 코메도제닉 오일은 피해야 합니다."
}
```

---

### 예시 3: 민감성 피부 + 주사

**입력**:
```json
{
  "disease": "주사",
  "summary": "양 볼과 코 주변 지속적인 홍조, 열감과 따끔거림",
  "user_info": {"skin_type": "민감성", "price_range": "40000-80000"},
  "hint": {"suggested_keywords": ["홍조진정", "진정", "자극완화", "피부장벽강화"]}
}
```

**출력**:
```json
{
  "dense_text": "민감성 피부의 주사로 인한 지속적인 붉은기와 열감을 효과적으로 진정시키고 외부 자극을 완화하는 쿨링 세럼으로, 손상된 피부 장벽을 회복하는 저자극 프리미엄 제품",
  "keywords": ["홍조진정", "진정", "자극완화", "피부장벽강화", "열감", "예민함", "보습"],
  "must_keywords": ["홍조진정", "진정", "자극완화"],
  "avoid_ingredients": ["알코올", "멘톨", "유칼립투스", "민트", "강한 향료", "레티놀"],
  "notes": "주사의 특징은 혈관 확장으로 인한 홍조입니다. 홍조진정이 최우선이며 멘톨과 알코올은 혈관을 자극해 악화시킬 수 있습니다."
}
```

---

## ⚠️ 주의사항

1. **출력은 반드시 유효한 JSON 형식**
   - 마크다운 코드 블록 사용 금지
   - 오직 JSON 객체만 반환

2. **notes는 반드시 100~200자 이내**
   - 간결함이 핵심
   - 1~2문장만 사용

3. **vocabulary 용어 준수**
   - 제품 DB에 실제 등록된 효능 키워드 우선

4. **피부타입 일치**
   - 지성 피부에 "건조" 키워드 ❌
   - 건성 피부에 "피지조절" 키워드 ❌

당신의 전문성으로 고객에게 가장 도움이 되는 검색 전략을 수립해주세요.
"""


def _fallback_query(disease: str, summary: str, user_info: Optional[Dict] = None) -> QuerySpec:
    """폴백 쿼리 생성"""
    bridge = DISEASE_TO_EFFECTS.get(disease, {"keywords": ["보습"], "ingredients": []})
    keywords = bridge.get("keywords", [])
    
    skin_type_prefix = f"{user_info.get('skin_type')} 피부의 " if user_info and user_info.get('skin_type') else ""
    dense = f"{skin_type_prefix}{disease}로 인한 증상을 완화하기 위한 {','.join(keywords[:2])} 중심의 저자극 케어 제품"
    
    notes = f"{disease}의 주요 증상 완화를 위해 {', '.join(keywords[:2])} 효능을 우선했습니다."
    if user_info and user_info.get('skin_type'):
        notes += f" {user_info['skin_type']} 피부 특성을 고려했습니다."
    
    return QuerySpec(
        dense_text=dense,
        keywords=keywords,
        must_keywords=keywords[:2] if keywords else [],
        avoid_ingredients=["강한 향료", "알코올"],
        notes=notes[:120],
    )


def generate_query_from_diagnosis(
    disease: str, 
    summary: str, 
    user_info: Optional[Dict] = None
) -> QuerySpec:
    """진단 정보를 바탕으로 LLM을 사용해 검색 쿼리를 생성"""
    bridge = DISEASE_TO_EFFECTS.get(disease, {"keywords": [], "ingredients": []})
    bridge_hint = {
        "disease": disease,
        "suggested_keywords": bridge.get("keywords", []),
        "suggested_ingredients": bridge.get("ingredients", []),
    }
    
    formatted_user_info = {}
    if user_info:
        if user_info.get('skin_type'):
            formatted_user_info['skin_type'] = user_info['skin_type']
        
        min_p = user_info.get('min_price')
        max_p = user_info.get('max_price')
        if min_p is not None or max_p is not None:
            price_range = f"{min_p or 0}-{max_p or '무제한'}"
            formatted_user_info['price_range'] = price_range

    user_content = {
        "disease": disease,
        "summary": summary,
        "user_info": formatted_user_info,
        "hint": bridge_hint,
    }

    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=json.dumps(user_content, ensure_ascii=False, indent=2)),
        ]
        resp = llm_client.invoke(messages)
        text = resp.content if isinstance(resp.content, str) else str(resp.content)
        
        if "```" in text:
            if "```json" in text:
                text = text.split("```json")[-1].split("```")[0].strip()
            else:
                text = text.split("```")[-2].strip() if text.count("```") >= 2 else text
        
        data = json.loads(text)

        if not isinstance(data, dict):
            return _fallback_query(disease, summary, user_info)

        dense_text = data.get("dense_text") or _fallback_query(disease, summary, user_info)["dense_text"]
        keywords = data.get("keywords") or bridge.get("keywords", [])
        must_keywords = data.get("must_keywords") or (keywords[:2] if keywords else [])
        avoid_ingredients = data.get("avoid_ingredients") or ["강한 향료", "알코올"]
        notes = data.get("notes") or "기본 추천 전략을 적용했습니다."
        
        if len(notes) > 120:
            notes = notes[:117] + "..."

        return QuerySpec(
            dense_text=dense_text,
            keywords=keywords,
            must_keywords=must_keywords,
            avoid_ingredients=avoid_ingredients,
            notes=notes,
        )
    except Exception as e:
        print(f"[WARN] LLM 쿼리 생성 실패: {e}")
        return _fallback_query(disease, summary, user_info)


# ============================================================
# ⭐ 신규 추가: Top 2, 3용 제품별 reason 생성 함수
# ============================================================

def generate_product_reason(
    disease: str,
    product_info: Dict,
    rank: int,
    user_info: Optional[Dict] = None
) -> str:
    """
    개별 제품의 추천 이유를 LLM으로 생성 (제품 중심)
    
    Args:
        disease: 질환명 (예: "아토피")
        product_info: 제품 정보
            - brand: 브랜드명
            - name: 제품명
            - main_effect: 주요 효능
            - key_ingredient: 핵심 성분
            - description: 상세 설명
            - care_symptom: 케어 증상
            - price: 가격
            - category: 카테고리
        rank: 순위 (1, 2, 또는 3)
        user_info: 사용자 정보 (skin_type 등)
    
    Returns:
        추천 이유 (200자 이내)
    """
    # 제품 정보 추출
    brand = product_info.get('brand', '미상')
    name = product_info.get('name', '제품')
    main_effect = product_info.get('main_effect', '') or '케어'
    key_ingredient = product_info.get('key_ingredient', '') or ''
    description = product_info.get('description', '') or ''
    care_symptom = product_info.get('care_symptom', '') or ''
    price = product_info.get('price', 0)
    category = product_info.get('category', '제품')
    
    # 사용자 정보
    skin_type = ''
    if user_info and user_info.get('skin_type'):
        skin_type = user_info['skin_type']
    
    # 가격대 표현
    if price:
        if price <= 30000:
            price_desc = '합리적인 가격대'
        elif price <= 50000:
            price_desc = '적정 가격대'
        else:
            price_desc = '프리미엄 가격대'
    else:
        price_desc = ''
    
    # 상세 설명 요약 (너무 길면 자름)
    desc_summary = description[:200] + "..." if len(description) > 200 else description
    
    # LLM 프롬프트 (제품 중심)
    prompt = f"""당신은 화장품 추천 전문가입니다.

{disease} 증상이 있는 고객에게 "{brand} {name}"을 추천하는 이유를 **제품의 고유한 특성을 중심으로** 200자 이내로 작성하세요.

## 제품 정보
- 브랜드: {brand}
- 제품명: {name}
- 주요 효능: {main_effect}
- 핵심 성분: {key_ingredient if key_ingredient else '(정보 없음)'}
- 케어 증상: {care_symptom if care_symptom else '(정보 없음)'}
- 카테고리: {category}
- 가격: {price:,.0f}원{f' ({price_desc})' if price_desc else ''}
{f'- 상세 설명: {desc_summary}' if desc_summary else ''}

## 고객 정보
- 피부타입: {skin_type if skin_type else '미상'}
- 질환: {disease} (참고용 - 질환 설명보다는 제품 특성에 집중)

## 작성 원칙
1. **200자 이내** (반드시 지킬 것!)
2. **제품 중심으로 작성**: 질환 설명("{disease}의 주요 증상은...")보다는 제품의 성분/효능/특징을 먼저 언급
3. 제품의 **고유한 장점**을 구체적으로 강조:
   - 핵심 성분이 있다면 그 성분의 효능과 질환과의 연관성
   - 주요 효능이 질환에 어떻게 도움이 되는지
   - 브랜드나 제품명의 특별한 점
4. {rank}순위 제품이므로 간결하게
5. 자연스러운 문장 구조 (예: "~성분의 효능으로", "~효능이 뛰어나", "~특징을 가진")
6. **매번 다른 표현** 사용 (다양한 어휘와 문장 구조)

## 좋은 예시 (제품 중심)
- "진정과 항염 효과가 뛰어난 {brand} {name}은 건선 피부의 불편함을 완화하고, 피부 장벽을 강화하여 건강한 상태로 회복하는 데 도움을 줍니다."
- "{key_ingredient if key_ingredient else '핵심 성분'}의 효능으로 피부장벽 강화와 진정 효과를 제공하여 건선 증상 완화에 적합합니다. 복합성 피부에 적합한 보습력으로 건강한 피부를 유지할 수 있습니다."
- "{brand}의 피지 조절과 모공 케어 효능이 여드름 피부에 최적화되어 있습니다. 각질 제거 기능으로 깨끗한 피부를 만들어줍니다."

## 나쁜 예시 (질환 중심 - 피해야 함)
- "{disease}의 핵심은 피지와 모공 막힘이므로..." (질환 설명으로 시작)
- "{disease} 케어에 적합한 제품입니다. 주요 효능: {main_effect}" (너무 일반적)

**출력**: 추천 이유 문장만 반환 (JSON이나 마크다운 없이 문장만!)
"""
    
    try:
        messages = [HumanMessage(content=prompt)]
        resp = llm_client.invoke(messages)
        reason = resp.content.strip() if isinstance(resp.content, str) else str(resp.content).strip()
        
        # 200자 강제 제한
        if len(reason) > 200:
            reason = reason[:197] + "..."
            print(f"[WARN] Rank {rank} reason이 200자 초과하여 자름: {reason[:50]}...")
        
        return reason
        
    except Exception as e:
        print(f"[WARN] Rank {rank} reason 생성 실패: {e}")
        # 폴백 - 제품 정보 중심
        if brand and brand != '미상' and main_effect:
            return f"{brand} {name}은 {main_effect.split(',')[0]} 효능으로 {disease} 케어에 적합합니다."
        elif key_ingredient:
            return f"{key_ingredient} 성분이 함유된 {name}으로 {disease} 증상 완화에 도움을 줍니다."
        elif main_effect:
            return f"{main_effect.split(',')[0]} 효능이 {disease} 케어에 효과적입니다."
        else:
            return f"{disease} 증상 완화에 효과적인 제품입니다."






