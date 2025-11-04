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
    gender VARCHAR(10),
    age_group INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

-- 2. skin_analysis 테이블
CREATE TABLE skin_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    skin_type VARCHAR(50), 
    min_price INT,
    max_price INT, 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT
);

-- 3. file 테이블
CREATE TABLE file (
    file_id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(50),
    entity_id INT,
    file_path VARCHAR(255),
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

-- 5. cosmetic 테이블 (image_url 제외 버전)
CREATE TABLE cosmetic (
    cosmetic_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200),
    brand VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2),
    ingredients TEXT,
    short_description TEXT COMMENT '한줄설명',
    description TEXT COMMENT '상세설명',
    buy_url VARCHAR(2048),
    skin_type VARCHAR(50) COMMENT '피부타입',
    skin_disease VARCHAR(50) COMMENT '관련 피부질환',
    main_effect VARCHAR(100) COMMENT '주요효능',
    care_symptom VARCHAR(100) COMMENT '케어증상',
    key_ingredient VARCHAR(200) COMMENT '핵심성분',
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

-- 8. like 테이블 (행 존재=좋아요, 행 없음=취소)
CREATE TABLE like (
    like_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    cosmetic_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_id INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_id INT,
    UNIQUE KEY unique_member_cosmetic (member_id, cosmetic_id),
    INDEX idx_cosmetic_id (cosmetic_id),
    INDEX idx_member_id (member_id)
) COMMENT='좋아요 규칙: INSERT(좋아요) → UNIQUE 위반 시 DELETE(취소) / COUNT(cosmetic_id)=총 좋아요 수';

-- 9. analysis_result_view (분석 결과 조회용 VIEW)
CREATE VIEW analysis_result_view AS
SELECT 
    sa.analysis_id,
    sa.member_id,
    sa.created_at as analysis_created_at,
    f.file_id as skin_file_id,
    d.disease_name,
    d.summary as diagnosis_summary,
    r.cosmetic_id,
    c.name as cosmetic_name,
    c.brand,
    c.price,
    c.buy_url,
    cf.file_path as cosmetic_file_path,
    r.reason,
    r.ranking
FROM skin_analysis sa
LEFT JOIN file f ON f.entity_type = 'skin_analysis' AND f.entity_id = sa.analysis_id
LEFT JOIN diagnosis d ON sa.analysis_id = d.analysis_id
LEFT JOIN recommendation r ON sa.analysis_id = r.analysis_id
LEFT JOIN cosmetic c ON r.cosmetic_id = c.cosmetic_id
LEFT JOIN file cf ON cf.entity_type = 'cosmetic' AND cf.entity_id = c.cosmetic_id
ORDER BY r.ranking;

