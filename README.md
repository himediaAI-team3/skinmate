## SkinMate

## Backend
0. 가상환경 설정
    - conda create -n "이름" python==3.12 -y
    - conda activate "이름"

1. 의존성 설치
    - cd backend
    - pip install -r requirements.txt

2. 개발 서버 실행
    2-1. VS Code 내 "Python(ms-python)" 확장 프로그램 설치 
    2-2. Ctrl + F5 (launch.json 설정대로 서버 실행됨)

3. Swagger 문서 확인
    - 브라우저에서 `http://127.0.0.1:8000/docs`

4. 로컬에 `.env` 생성
- env.example 에서 필요한 값을 `.env`에 채워 넣기