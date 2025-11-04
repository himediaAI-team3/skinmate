## SkinMate

## Backend
0. 가상환경 설정
    - conda create -n "이름" python==3.12 -y
    - conda activate "이름"

1. 의존성 설치
    - cd backend
    - pip install -r requirements.txt

2. 로컬에 `.env` 생성
    - env.example 에서 필요한 값을 `.env`에 채워 넣기

3. DB 이니셜 데이터 실행
    - backend/app/db/ddl.sql에서 "analysis_result_view"만 DB에 수동 실행
    - init.sql 더미데이터 전체 실행

4. 개발 서버 실행
   - VS Code 내 "Python(ms-python)" 확장 프로그램 설치
   - Ctrl + F5 (launch.json 설정대로 서버 실행됨)

    or

   - uvicorn 서버 지정 실행
       - cd backend
       - uvicorn app.main:app --host 192.168.0.235 --port 8000 (자신 IP 입력)

5. Swagger 문서 확인
    - 브라우저에서 `http://127.0.0.1:8000/docs`

## Frontend
0. Node/NPM 준비
	- PowerShell
		- winget install -e --id CoreyButler.NVMforWindows
		- (설치 후 PowerShell 재시작)
		- nvm version (설치 확인)

1. Node 버전 고정 및 의존성 설치
	- CMD
		- nvm install 22.20.0
		- nvm use 22.20.0
		- node -v (예: v22.20.0)
		- npm -v (예: 10.x)

2. Git에서 프론트엔드 코드 받기
		- cd frontend
		- npm ci (lockfile 기반 클린 설치)

3 .실행 방법
	- 실행(운영환경 — 빌드 후 실행)
		- npm run build
		- npm run start (기본: http://localhost:3000)
	- 실행(개발환경 — 저장 시 바로 적용)
		- npm run dev (http://localhost:3000)