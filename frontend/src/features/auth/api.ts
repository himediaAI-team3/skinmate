// /features/auth/api.ts
import type { SocialProvider } from '@/entities/auth';
import { OAUTH_PROVIDERS } from '@/entities/auth';
import { http } from '@/lib/http';

/**
 * Kakao 인가 URL을 프론트에서 직접 생성 (프론트 콜백 경로로 복귀)
 * - 필요 env:
 *   NEXT_PUBLIC_KAKAO_REST_KEY
 *   NEXT_PUBLIC_FRONT_BASE   (예: http://192.168.0.249:3000)
 */
function buildKakaoAuthorizeUrl(): string {
  const clientId  = process.env.NEXT_PUBLIC_KAKAO_REST_KEY!;
  const frontBase = process.env.NEXT_PUBLIC_FRONT_BASE!;
  const redirectUri = `${frontBase}/login/oauth2/code/kakao`;

  // CSRF 방지용 state
  const state = Math.random().toString(36).slice(2);
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('oauth:kakao:state', state);
  }

  const url = new URL('https://kauth.kakao.com/oauth/authorize');
  url.searchParams.set('client_id', clientId);
  url.searchParams.set('redirect_uri', redirectUri);
  url.searchParams.set('response_type', 'code');
  url.searchParams.set('state', state);
  // scope 필요 시:
  // url.searchParams.set('scope', 'account_email profile_nickname');

  return url.toString();
}

/**
 * 1) 인가 URL 생성
 *  - Kakao: kauth로 직접
 *  - 그 외: 메타에 등록된 경로(현재는 미사용/준비중)
 */
export function buildAuthorizeUrl(provider: SocialProvider): string {
  // Kakao는 그대로 백엔드 시작점 사용
  return OAUTH_PROVIDERS[provider].authorizePath;
}

/**
 * 2) 공급자 인가 엔드포인트로 브라우저 이동
 */
export function redirectToProvider(p: SocialProvider) {
  const url = buildAuthorizeUrl(p);
  window.location.href = url; // 백엔드로 이동
}

/**
 * 3) 아직 미구현 공급자 가드
 */
export function ensureProviderEnabled(provider: SocialProvider): boolean {
  const meta = OAUTH_PROVIDERS[provider];
  if (!meta?.enabled) {
    alert('해당 간편 로그인은 준비중입니다');
    return false;
  }
  return true;
}

/* ------------------------------ */
/*          토큰 유틸들           */
/* ------------------------------ */

const ACCESS_KEY = 'accessToken';
const REFRESH_KEY = 'refreshToken';

export type Tokens = { accessToken: string; refreshToken?: string };

export function saveTokens(tokens: Tokens) {
  if (typeof window === 'undefined') return;
  if (tokens.accessToken) localStorage.setItem(ACCESS_KEY, tokens.accessToken);
  if (tokens.refreshToken) localStorage.setItem(REFRESH_KEY, tokens.refreshToken);
}

export function getAccessToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem(ACCESS_KEY) : null;
}

export function getRefreshToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem(REFRESH_KEY) : null;
}

export function clearTokens() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

/**
 * 4) URL(hash 혹은 query)에 포함된 토큰을 파싱하여 localStorage에 저장
 */
export function persistTokensFromLocation(): boolean {
  if (typeof window === 'undefined') return false;

  const { location, history } = window;
  const hash = location.hash?.startsWith('#') ? location.hash.slice(1) : '';
  const hashParams = new URLSearchParams(hash);
  const hAT = hashParams.get('accessToken');
  const hRT = hashParams.get('refreshToken');

  const search = location.search?.startsWith('?') ? location.search.slice(1) : '';
  const searchParams = new URLSearchParams(search);
  const qAT = searchParams.get('accessToken');
  const qRT = searchParams.get('refreshToken');

  const accessToken = hAT ?? qAT ?? undefined;
  const refreshToken = hRT ?? qRT ?? undefined;

  if (accessToken) {
    saveTokens({ accessToken, refreshToken });
    history.replaceState(null, '', location.pathname);
    return true;
  }
  return false;
}

/**
 * 5) Authorization 헤더 자동 첨부 fetch
 */
export async function authFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  const headers = new Headers(init.headers || {});
  const at = getAccessToken();
  if (at) headers.set('Authorization', `Bearer ${at}`);
  return fetch(input, { ...init, headers });
}

/**
 * 로그아웃: 서버 RT 삭제 요청 후 로컬 토큰 클리어
 */
export async function logout(): Promise<void> {
  try {
    await http('/auth/logout', { method: 'POST' }); // withAuth 기본값 true → Authorization 자동 첨부
  } catch (e) {
    console.warn('logout API failed, clearing local tokens anyway.', e);
  } finally {
    clearTokens();
  }
}
