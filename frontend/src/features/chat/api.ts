import { http } from '@/lib/http';

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
 * AI 챗봇과 대화하기
 * @param message 사용자 메시지
 * @param threadId 이전 대화 스레드 ID (선택사항)
 * @returns AI 응답과 thread_id
 */
export async function sendChatMessage(
  message: string,
  threadId?: string
): Promise<ChatResponse> {
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

