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
    image_url,
    ingredients,
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
    '/images/cosmetic1.jpg',
    '센텔라아시아티카추출물, 나이아신아마이드, 판테놀',
    'https://example.com/product1',
    NOW(),
    NOW()
),
(
    2,
    '모공 타이트닝 세럼',
    '이니스프리',
    '세럼',
    25000.00,
    '/images/cosmetic2.jpg',
    '녹차추출물, 티트리오일, 살리실산',
    'https://example.com/product2',
    NOW(),
    NOW()
),
(
    3,
    '수분 보습 토너',
    '라네즈',
    '토너',
    22000.00,
    '/images/cosmetic3.jpg',
    '히알루론산, 글리세린, 베타글루칸',
    'https://example.com/product3',
    NOW(),
    NOW()
);
