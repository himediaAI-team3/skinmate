# Skinmate Auth Server (Spring Boot 기반 OAuth2 인증/인가 서버)

## 1. 기술 스택
  - **Spring Boot 2.7.13**
  - **Spring Security + OAuth2 Client**
  - **Spring Data JPA**
  - **MySQL**
  - **JWT (JJWT)**
  - **Lombok**

## 2. 기능
## 2-1. OAuth2 소셜 로그인
  - Google 로그인
  - Kakao 로그인
  - OAuth2 인증 후 JWT 토큰 발급

## 2-2. JWT 토큰 관리
  - **Access Token**: 15분 유효
  - **Refresh Token**: 7일 유효, DB 저장
  - **Bearer Token**
  - **Refresh Token 회전**

## 3. 설정
## 3-1. 환경 변수 설정
  - .env 에서 환경변수 로드

## 3-2. CORS 설정

## 4. 엔드포인트
## 4-1. OAuth2 로그인
- **GET** `/oauth2/authorization/google` - Google 로그인
- **GET** `/oauth2/authorization/kakao` - Kakao 로그인

## 4-2. 토큰 갱신
```
POST /auth/refresh
Content-Type: application/json

RequestBody
{
  "refreshToken": "eyJhbGciOiJIUzI1NiJ9..."
}
```

**응답:**
```json
{
  "success": true,
  "code": 200,
  "message": "토큰 갱신 성공",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiJ9..."
  }
}
```

## 4-3. 로그아웃
```
POST /auth/logout
Authorization: Bearer {accessToken}
```

**응답:**
```json
{
  "success": true,
  "code": 200,
  "message": "로그아웃 성공",
  "data": null
}
```

## 5. ResponseCode

| 코드 | HTTP 상태 | 설명 |
|------|-----------|------|
| SUCCESS | 200 | 성공 |
| INVALID_REQUEST | 400 | 잘못된 요청 |
| INVALID_TOKEN | 400 | 유효하지 않은 토큰 |
| UNAUTHORIZED | 401 | 인증 필요 |
| OAUTH2_LOGIN_FAILED | 401 | OAuth2 로그인 실패 |
| TOKEN_EXPIRED | 401 | 토큰 만료 |
| FORBIDDEN | 403 | 권한 없음 |
| MEMBER_NOT_FOUND | 404 | 회원 없음 |
| REFRESH_TOKEN_NOT_FOUND | 404 | Refresh Token 없음 |
| INTERNAL_SERVER_ERROR | 500 | 서버 오류 |

## 6. 실행 방법
```bash
# 프로젝트 디렉토리로 이동
cd auth

# Maven 빌드
mvn clean install

# 애플리케이션 실행
mvn spring-boot:run
```

서버가 `http://localhost:8080`에서 실행됩니다.