# AI Agent 채팅 기능 가이드

## 개요

LangGraph 기반 AI Agent를 활용하여 사용자와 대화하며 진단 이력, 추천 제품 조회 등의 기능을 제공하는 채팅 API입니다.

## 주요 특징

### 1. 보안
- **thread_id 권한 검증**: 각 thread_id는 `thread_{member_id}_{random}` 형식으로 생성되어 고유성 보장
- **크로스 사용자 접근 차단**: 다른 사용자의 대화 이력에 접근 불가
- **검증 로직**: thread_id의 member_id prefix를 검증하여 권한 확인

### 2. 기능
- **진단 이력 조회**: 최근 피부 진단 결과 확인
- **추천 제품 조회**: AI가 추천한 화장품 3개 확인
- **일반 대화**: 피부 관리 팁 등 자유로운 대화
- **대화 이력 유지**: thread_id를 통한 컨텍스트 유지

### 3. 아키텍처
- **InMemorySaver**: 서버 메모리에 대화 이력 저장 (재시작 시 초기화)
- **Tool 기반**: LangChain Tool을 활용한 확장 가능한 구조
- **기존 코드 재사용**: Repository 패턴 유지

## API 사용법

### 엔드포인트
```
POST /api/chat
```

### Request Body
```json
{
  "member_id": 1,
  "message": "내 최근 진단 결과 뭐였지?",
  "thread_id": "thread_1_abc123"  // 선택사항: 이전 대화 이어가기
}
```

### Response
```json
{
  "code": 200,
  "success": true,
  "message": "채팅 성공",
  "data": {
    "response": "최근 진단 결과는 다음과 같습니다:\n- 진단일: 2025년 11월 03일\n- 진단명: 주사\n...",
    "thread_id": "thread_1_abc123"
  }
}
```

### 사용 예시

#### 1. 새로운 대화 시작
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": 1,
    "message": "안녕하세요"
  }'
```

#### 2. 진단 이력 조회
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": 1,
    "message": "내 최근 진단 결과 뭐였지?",
    "thread_id": "thread_1_abc123"
  }'
```

#### 3. 추천 제품 조회
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": 1,
    "message": "추천받은 화장품 보여줘",
    "thread_id": "thread_1_abc123"
  }'
```

## 보안 검증

### thread_id 형식
- **형식**: `thread_{member_id}_{random_hex}`
- **예시**: `thread_1_499277988`

### 권한 검증 로직
```python
# 사용자 1이 생성한 thread_id
thread_id = "thread_1_abc123"

# ✅ 사용자 1이 사용 → 허용
AgentService.chat(db, member_id=1, thread_id="thread_1_abc123")

# ❌ 사용자 2가 사용 → 차단 (ValueError 발생)
AgentService.chat(db, member_id=2, thread_id="thread_1_abc123")
# ValueError: 유효하지 않은 thread_id입니다. 다른 사용자의 대화에 접근할 수 없습니다.
```

## 구현 구조

### 파일 구조
```
backend/
├── app/
│   ├── services/
│   │   ├── chat_tools.py          # Tool 정의 (진단 이력, 추천 제품 조회)
│   │   └── agent_service.py       # Agent 초기화 및 대화 처리
│   └── router/
│       └── chat.py                 # Chat API 엔드포인트
└── scripts/
    ├── test_agent.py               # langgraph 호환성 테스트
    ├── test_chat.py                # 통합 테스트
    └── test_security.py            # 보안 테스트
```

### Tool 목록

#### 1. get_my_diagnosis_history_impl()
- **기능**: 최근 진단 이력 조회
- **반환**: 진단일, 진단명, 증상 요약
- **DB 쿼리**: `AnalysisRepository.get_by_member_id_with_pagination()`

#### 2. get_recommended_products_impl()
- **기능**: 추천 제품 3개 조회
- **반환**: 제품명, 브랜드, 가격, 추천 이유
- **DB 쿼리**: `RecommendationRepository.get_by_analysis_id()`

### Agent 설정

```python
# LLM 설정
model: "gpt-4o-mini"
temperature: 0.7  # 대화형이므로 약간 높게

# System Prompt
"""당신은 피부 관리 전문가 AI 어시스턴트입니다.
사용자의 피부 진단 결과와 추천 화장품에 대해 친절하게 안내합니다."""

# Checkpointer
InMemorySaver()  # 서버 재시작 시 초기화
```

## 테스트

### 1. 호환성 테스트
```bash
cd backend
python scripts/test_agent.py
```

### 2. 통합 테스트
```bash
cd backend
python scripts/test_chat.py
```

### 3. 보안 테스트
```bash
cd backend
python scripts/test_security.py
```

### 테스트 시나리오
1. ✅ 진단 이력 조회 (Tool 호출)
2. ✅ 추천 제품 조회 (Tool 호출)
3. ✅ 일반 대화 (Tool 없이)
4. ✅ 대화 이력 기억 (같은 thread_id)
5. ✅ 새로운 대화 (다른 thread_id)
6. ✅ 다른 사용자의 thread 접근 차단

## 환경 변수

```bash
# .env 파일
OPENAI_API_KEY=sk-...
```

## 의존성

```txt
# LangChain & LangGraph
langchain==0.3.14
langchain-openai==0.2.14
langchain-core==0.3.79
langgraph==0.2.45
```

## 확장 가능성

### 추가 Tool 구현 (예정)
1. `recommend_by_symptom()`: 특정 증상에 맞는 화장품 재추천
2. `request_rediagnosis()`: 재진단 요청 안내
3. `get_product_detail()`: 특정 제품 상세 정보 조회

### 영구 저장소 전환 (선택사항)
- **현재**: InMemorySaver (메모리)
- **전환 옵션**:
  - PostgreSQL + LangGraph CheckpointSaver
  - Redis + Custom CheckpointSaver
  - MySQL 테이블 추가

### 기존 파이프라인 Agent 전환 (선택사항)
- 진단/추천 파이프라인을 Agent Tool로 변환
- 자동으로 순서 판단 및 에러 핸들링
- 작업량: 2-3시간

## 주의사항

### 1. 메모리 관리
- `InMemorySaver` 사용으로 서버 재시작 시 대화 이력 초기화
- 대화가 많아지면 메모리 사용량 증가
- 프로덕션 환경에서는 영구 저장소 사용 권장

### 2. thread_id 관리
- 프론트엔드에서 thread_id를 로컬 스토리지에 저장
- 같은 대화를 이어가려면 thread_id 전달 필수
- thread_id는 사용자별로 고유해야 함 (보안)

### 3. API 키 관리
- OPENAI_API_KEY를 .env에 안전하게 보관
- 프로덕션 환경에서는 환경변수로 관리

## 트러블슈팅

### 1. "유효하지 않은 thread_id" 오류
- **원인**: 다른 사용자의 thread_id 사용 시도
- **해결**: 사용자별로 독립적인 thread_id 사용

### 2. Tool이 호출되지 않음
- **원인**: 질문이 Tool 설명과 맞지 않음
- **해결**: 명확한 질문 사용 (예: "내 진단 결과 보여줘")

### 3. 대화 이력이 유지되지 않음
- **원인**: thread_id를 전달하지 않음
- **해결**: 이전 대화의 thread_id를 다음 요청에 포함

## 라이선스

이 프로젝트는 SkinMate 서비스의 일부입니다.

