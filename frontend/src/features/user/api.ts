// src/features/user/api.ts
import { http } from '@/lib/http';

export const AUTH_CHANGED_EVENT = 'auth-changed';
export const ACCESS_TOKEN_KEY = 'ACCESS_TOKEN';

/** 현재 Access Token 조회(여러 키 호환) */
export const getAccessToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return (
    localStorage.getItem(ACCESS_TOKEN_KEY) ||   // 표준(이 파일)
    localStorage.getItem('accessToken') ||      // 다른 모듈 표준
    localStorage.getItem('access_token') ||     // 과거 호환
    localStorage.getItem('token') ||            // 과거 호환
    null
  );
};

/** 전체 스토리지 정리 + 같은 탭 즉시 갱신 이벤트 */
export const clearAuthStorage = () => {
  try {
    if (typeof window !== 'undefined') {
      localStorage.clear();
      if (typeof sessionStorage !== 'undefined') sessionStorage.clear();
      window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
    }
  } catch {}
};

export const authApi = {
  /**
   * Optimistic 로그아웃:
   * - UI는 즉시 로그아웃 상태로 (토큰 먼저 삭제)
   * - 서버 호출은 이어서 수행(실패해도 UI는 유지)
   * - 알림은 여기서 하지 않고, 호출하는 쪽(AppHeader)에서 1회만 띄워 제어
   */
  logout: async (): Promise<void> => {
    const token = getAccessToken();

    // 1) 즉시 로컬 정리 -> UI 즉각 반영
    clearAuthStorage();

    // 2) 서버 로그아웃 호출(성공/실패 무시)
    try {
      if (token) {
        await http('/api/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch (e) {
      console.warn('logout API failed (ignored):', e);
    }
  },
};
