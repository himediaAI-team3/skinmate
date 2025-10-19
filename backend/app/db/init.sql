- 더미 회원 데이터 삽입
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