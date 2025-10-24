// 서버 원본 DTO (예시)
export type MeProfileDTO = {
    id: number | string;
    name: string;
    email: string;
    avatar_url?: string | null;
    info?: Array<{ label: string; value: string }>;
  };
  
  // 앱 UI에서 쓰는 정규화 타입
  export type MeProfile = {
    id: number | string;
    name: string;
    email: string;
    avatar: string; // 없으면 placeholder 대체
    info: Array<{ label: string; value: string }>;
  };
  
  // 공통 응답 래퍼
  export type ApiResponse<T> = {
    success: boolean;
    message?: string;
    data: T;
  };
  