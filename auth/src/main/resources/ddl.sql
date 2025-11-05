-- Member 테이블 (인증서버에서 생성 및 관리)
CREATE TABLE IF NOT EXISTS member (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(100),
    name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'USER',
    skin_type VARCHAR(50),
    -- min_price INT,
    -- max_price INT,
    gender VARCHAR(10),
    age_group INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

-- RefreshToken 테이블 (JWT 토큰 관리)
CREATE TABLE IF NOT EXISTS refresh_token (
    refresh_token_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    refresh_token VARCHAR(500) UNIQUE,
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT
);
