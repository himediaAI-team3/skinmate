-- SkinMate Database DDL
-- SQLAlchemy Models 기반 생성

-- 1. member 테이블
CREATE TABLE member (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(100),
    name VARCHAR(100),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'USER',
    skin_type VARCHAR(50),
    min_price INT,
    max_price INT,
    gender VARCHAR(10),
    age_group VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

-- 2. skin_analysis 테이블
CREATE TABLE skin_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

-- 3. file 테이블
CREATE TABLE file (
    file_id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT,
    file_url VARCHAR(255),
    file_name VARCHAR(255),
    mime_type VARCHAR(100),
    size INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

-- 4. diagnosis 테이블
CREATE TABLE diagnosis (
    diagnosis_id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT,
    disease_name VARCHAR(100),
    summary TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

-- 5. cosmetic 테이블
CREATE TABLE cosmetic (
    cosmetic_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200),
    brand VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2),
    image_url VARCHAR(255),
    ingredients TEXT,
    buy_url VARCHAR(2048),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

-- 6. recommendation 테이블
CREATE TABLE recommendation (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id INT,
    cosmetic_id INT,
    reason VARCHAR(255),
    ranking INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

