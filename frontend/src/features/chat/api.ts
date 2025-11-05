import { http } from '@/lib/http';
import { getAccessToken, saveTokens } from '@/features/auth';

export interface ChatRequest {
  message: string;
  thread_id?: string;
}

export interface ChatResponse {
  response: string;
  thread_id: string;
}

interface ApiResponse<T> {
  code: number;
  success: boolean;
  message: string;
  data: T;
  timestamp?: string;
}

/**
 * 개발용: 토큰이 없으면 기본 토큰 설정
 */
function ensureToken() {
  const token = getAccessToken();
  if (!token) {
    // 개발용 기본 토큰 (운영 환경에서는 제거해야 함)
    const defaultToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6IlVTRVIiLCJ0eXBlIjoiYWNjZXNzIiwiaWF0IjoxNzYyMjc2NDQ2LCJleHAiOjE3NjIyNzczNDZ9.EkBRUNOMwbg_G-cUdh5cs4d4ByI2R4Qxdxua4qi4hW0";
    saveTokens({ accessToken: defaultToken });
  }
}

/**
 * AI 챗봇과 대화하기
 * @param message 사용자 메시지
 * @param threadId 이전 대화 스레드 ID (선택사항)
 * @returns AI 응답과 thread_id
 */
export async function sendChatMessage(
  message: string,
  threadId?: string
): Promise<ChatResponse> {
  // 토큰 확인 및 설정 (개발용)
  ensureToken();
  
  const response = await http<ApiResponse<ChatResponse>>(
    '/api/chat',
    {
      method: 'POST',
      json: {
        message,
        thread_id: threadId,
      },
    }
  );

  if (!response.success || !response.data) {
    throw new Error(response.message || '채팅 요청에 실패했습니다.');
  }

  return response.data;
}

