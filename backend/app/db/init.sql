-- 더미 회원 데이터 삽입
INSERT INTO member (
    member_id, 
    oauth_provider, 
    oauth_id, 
    name, 
    email, 
    role,
    skin_type,
    min_price,
    max_price,
    gender,
    age_group,
    created_at,
    updated_at,
    created_id,
    updated_id
) VALUES (
    1,                              -- member_id
    'kakao',                        -- oauth_provider (카카오 로그인)
    'kakao_123456789',              -- oauth_id
    '김지수',                       -- name
    'jisoo.kim@gmail.com',        -- email
    'USER',                         -- role
    '복합성',                       -- skin_type (복합성 피부)
    15000,                          -- min_price (1만5천원)
    50000,                          -- max_price (5만원)
    '여성',                         -- gender
    '20',                           -- age_group (20대)
    '2025-01-15 10:30:00',          -- created_at
    '2025-01-15 10:30:00',          -- updated_at
    NULL,                           -- created_id
    NULL                            -- updated_id
);

-- 더미 화장품 데이터 삽입
-- recommendation service에서 cosmetic_id 1, 2, 3 사용
INSERT INTO cosmetic (
    cosmetic_id,
    name,
    brand,
    category,
    price,
    ingredients,
    description,
    buy_url,
    created_at,
    updated_at
) VALUES
(
    1,
    '센텔라 진정 크림',
    '닥터자르트',
    '크림',
    28000.00,
    '센텔라아시아티카추출물, 나이아신아마이드, 판테놀',
    '여드름과 트러블로 자극받은 피부를 진정시켜주는 크림입니다. 센텔라 추출물이 염증을 완화하고 피부를 부드럽게 케어해줍니다.',
    'https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000209418&dispCatNo=1000001000800130001&trackingCd=Cat1000001000800130001_Small&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%A1%9C%EC%85%98/%ED%81%AC%EB%A6%BC/%EC%98%AC%EC%9D%B8%EC%9B%90_%EC%A0%84%EC%B2%B4_%EC%A0%9C%EB%A1%9C%EC%9D%B4%EB%93%9C_%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=7',
    NOW(),
    NOW()
),
(
    2,
    '모공 타이트닝 세럼',
    '이니스프리',
    '세럼',
    25000.00,
    '녹차추출물, 티트리오일, 살리실산',
    '확대된 모공을 타이트하게 조여주는 세럼입니다. 녹차 추출물과 살리실산이 모공을 깨끗하게 정리하고 탄력을 개선해줍니다.',
    'https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000209747&dispCatNo=1000001000800130001&trackingCd=Cat1000001000800130001_Small&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%A1%9C%EC%85%98/%ED%81%AC%EB%A6%BC/%EC%98%AC%EC%9D%B8%EC%9B%90_%EC%A0%84%EC%B2%B4_%EC%A0%9C%EB%A1%9C%EC%9D%B4%EB%93%9C_%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=9',
    NOW(),
    NOW()
),
(
    3,
    '수분 보습 토너',
    '라네즈',
    '토너',
    22000.00,
    '히알루론산, 글리세린, 베타글루칸',
    '깊은 수분 공급과 보습력을 제공하는 토너입니다. 히알루론산이 피부 깊숙이 수분을 공급하여 촉촉하고 탄력 있는 피부로 만들어줍니다.',
    'https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000209906&dispCatNo=1000001000800130001&trackingCd=Cat1000001000800130001_Small&t_page=%EC%B9%B4%ED%85%8C%EA%B3%A0%EB%A6%AC%EA%B4%80&t_click=%EB%A1%9C%EC%85%98/%ED%81%AC%EB%A6%BC/%EC%98%AC%EC%9D%B8%EC%9B%90_%EC%A0%84%EC%B2%B4_%EC%A0%9C%EB%A1%9C%EC%9D%B4%EB%93%9C_%EC%83%81%ED%92%88%EC%83%81%EC%84%B8&t_number=8',
    NOW(),
    NOW()
);
