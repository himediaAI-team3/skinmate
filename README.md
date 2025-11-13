# SkinMate

> **사진 한 장으로 AI가 피부 질환을 분석하고, 내게 딱 맞는 화장품을 추천해주는 서비스**

## 📋 목차

- [프로젝트 소개](#프로젝트-소개)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [시작하기](#시작하기)
  - [데이터베이스 설정](#데이터베이스-설정)
  - [Backend 설정](#backend-설정)
  - [Auth Server 설정](#auth-server-설정)
  - [Frontend 설정](#frontend-설정)
- [API 문서](#api-문서)

## 프로젝트 소개

SkinMate는 AI 기반 피부 질환 분석 및 맞춤형 화장품 추천 서비스입니다. 사용자가 업로드한 얼굴 사진을 분석하여 피부 상태를 진단하고, 개인 맞춤형 화장품을 추천합니다.

## 주요 기능

### 1. AI 피부 질환 분석
- 사용자가 얼굴 사진을 업로드하면 파인튜닝된 VLM 모델이 피부 질환을 분석하고 소견을 제공합니다.
- Qwen2.5-VL 7B 모델을 LoRA 기반으로 파인튜닝하여 정확한 진단을 수행합니다.

### 2. RAG 맞춤 화장품 추천
- 분석된 피부 질환과 사용자의 피부 타입, 선호 가격대를 기반으로 개인 맞춤 화장품을 추천합니다.
- Qdrant 벡터DB와 Hybrid Search(Dense/Sparse 임베딩, RRF)를 활용하여 정확한 추천을 제공합니다.

### 3. AI 상담 챗봇
- 과거 진단 이력 및 추천 제품 조회 Tool을 통한 개인 맞춤형 상담을 제공합니다. 
- 피부 질환 지식베이스 RAG를 결합한 전문적 상담이 가능합니다. 
- LangChain과 LangGraph를 활용한 지능형 대화 시스템을 구현했습니다.

## 기술 스택

### AI/ML
- **VLM**: Qwen2.5-VL 7B 파인튜닝 (LoRA), RunPod GPU
- **RAG**: Qdrant 벡터DB, Hybrid Search (Dense/Sparse 임베딩, RRF)
- **LLM**: OpenAI GPT-4o-mini, LangChain, LangGraph

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy ORM
- **RDBMS**: MySQL

### Auth Server
- **Framework**: Spring Boot 2.7.13
- **Security**: Spring Security, OAuth2, JWT
- **Language**: Java 17

### Frontend
- **Framework**: Next.js 14.2.3
- **Styling**: Tailwind CSS
- **Language**: TypeScript

## 프로젝트 구조

```
skinmate/
├── backend/          # FastAPI 백엔드 서버
│   ├── app/
│   │   ├── core/     # 설정 및 미들웨어
│   │   ├── models/   # SQLAlchemy 모델
│   │   ├── router/   # API 라우터
│   │   ├── services/ # 비즈니스 로직
│   │   └── db/       # 데이터베이스 스크립트
│   └── requirements.txt
├── auth/             # Spring Boot 인증 서버
│   └── src/main/java/com/skinmate/
└── frontend/         # Next.js 프론트엔드
    └── src/
```

## 시작하기

### 데이터베이스 설정

1. **MySQL 설치 및 실행**
   - MySQL 8.0 이상 버전 설치
   - MySQL 서버 실행

2. **데이터베이스 생성**
   ```sql
   CREATE DATABASE skinmate CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **DDL 실행**
   - `backend/app/db/ddl.sql` 파일을 실행하여 테이블 생성
   - `analysis_result_view` VIEW는 수동으로 실행 필요

4. **초기 데이터 삽입 (선택사항)**
   - `backend/app/db/init.sql` 파일을 실행하여 더미 데이터 삽입

### Backend 설정

1. **Python 가상환경 설정**
   ```bash
   # Conda 사용 시
   conda create -n skinmate python=3.12 -y
   conda activate skinmate
   
   # 또는 venv 사용 시
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **의존성 설치**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **환경 변수 설정**
   - `backend/env.example` 파일을 참고하여 `backend/.env` 파일 생성
   - 필요한 값들을 채워넣기:
     ```env
     # 데이터베이스 설정
     DB_HOST=localhost
     DB_PORT=3306
     DB_NAME=skinmate
     DB_USER=root
     DB_PASSWORD=your_password
     
     # RunPod AI 모델 설정
     RUNPOD_MODEL_NAME=your_model_name
     RUNPOD_API_KEY=your_api_key
     RUNPOD_BASE_URL=your_base_url
     
     # JWT 설정 (Auth 서버와 동일한 secret 사용)
     JWT_SECRET=your_jwt_secret_key_here
     
     # OpenAI API 설정
     OPENAI_API_KEY=your_openai_api_key_here
     ```

4. **서버 실행**
   ```bash
   # 개발 서버 실행
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # 또는 VS Code에서 실행
   # Python 확장 프로그램 설치 후 Ctrl + F5
   ```

5. **API 문서 확인**
   - 브라우저에서 `http://localhost:8000/docs` 접속하여 Swagger UI 확인

### Auth Server 설정

1. **Java 17 설치**
   - JDK 17 이상 버전 설치 확인
   ```bash
   java -version
   ```

2. **Maven 설치 (선택사항)**
   - 프로젝트에 `mvnw`(Maven Wrapper)가 포함되어 있어 별도 설치 불필요
   - Windows: `mvnw.cmd` 사용
   - Linux/Mac: `mvnw` 사용

3. **환경 변수 설정**
   - `auth/` 디렉토리에 `.env` 파일 생성
   ```env
   # 데이터베이스 설정
   DB_URL=jdbc:mysql://localhost:3306/skinmate?useSSL=false&serverTimezone=Asia/Seoul&characterEncoding=UTF-8
   DB_USERNAME=root
   DB_PASSWORD=your_password
   
   # JWT 설정
   JWT_SECRET=your_jwt_secret_key_here
   
   # Kakao OAuth 설정
   KAKAO_CLIENT_ID=your_kakao_client_id
   KAKAO_CLIENT_SECRET=your_kakao_client_secret
   ```

4. **애플리케이션 빌드 및 실행**
   ```bash
   cd auth
   
   # Windows
   .\mvnw.cmd clean install
   .\mvnw.cmd spring-boot:run
   
   # Linux/Mac
   ./mvnw clean install
   ./mvnw spring-boot:run
   ```

5. **서버 확인**
   - 기본 포트: `http://localhost:8080`
   - OAuth 로그인 엔드포인트: `http://localhost:8080/oauth2/authorization/kakao`

### Frontend 설정

1. **Node.js 설치**
   ```powershell
   # Windows (PowerShell)
   winget install -e --id CoreyButler.NVMforWindows
   # 설치 후 PowerShell 재시작
   ```

2. **Node.js 버전 설정**
   ```bash
   # NVM 사용 시
   nvm install 22.20.0
   nvm use 22.20.0
   
   # 버전 확인
   node -v  # v22.20.0
   npm -v   # 10.x
   ```

3. **의존성 설치**
   ```bash
   cd frontend
   npm ci
   ```

4. **환경 변수 설정 (필요시)**
   - API 엔드포인트 등 필요한 환경 변수를 설정
   - Next.js는 `.env.local` 파일 사용

5. **개발 서버 실행**
   ```bash
   # 개발 모드 (핫 리로드)
   npm run dev
   # http://localhost:3000
   
   # 프로덕션 빌드 및 실행
   npm run build
   npm run start
   # http://localhost:3000
   ```

## API 문서

### Backend API
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 주요 엔드포인트
- `POST /api/analysis` - 피부 분석 요청
- `GET /api/analysis/{analysis_id}` - 분석 결과 조회
- `GET /api/cosmetics` - 화장품 목록 조회
- `POST /api/chat` - AI 챗봇 대화

## 주의사항

1. **JWT Secret**: Backend와 Auth Server에서 동일한 `JWT_SECRET` 값을 사용해야 합니다.
2. **CORS 설정**: Frontend와 Backend 간 통신을 위해 CORS 설정이 필요합니다.
3. **벡터 DB**: Qdrant 벡터DB가 별도로 실행되어 있어야 RAG 기능이 정상 작동합니다.
4. **RunPod API**: VLM 모델을 사용하기 위해 RunPod API 키가 필요합니다.

## 라이선스

이 프로젝트는 개인 프로젝트입니다.
