// /src/app/features/auth/api.ts
'use client';

import type { SocialProvider } from '@/entities/auth';
import { OAUTH_PROVIDERS } from '@/entities/auth';
import { http } from '@/lib/http';

/* ================================
 * 백엔드 authorize URL (구글/네이버 등 확장용)
 * ================================ */
function getApiBase(): string {
  const apiBase = process.env.NEXT_PUBLIC_API_AUTH;
  if (!apiBase) throw new Error('NEXT_PUBLIC_API_AUTH 누락');
  return apiBase.replace(/\/+$/, '');
}

function buildBackendAuthorizeUrl(provider: SocialProvider): string {
  const apiBase = getApiBase();
  const meta = OAUTH_PROVIDERS[provider];
  if (!meta) throw new Error(`알 수 없는 provider: ${provider}`);
  return `${apiBase}/oauth2/authorization/${meta.registrationId}`;
}

export function buildAuthorizeUrl(provider: SocialProvider): string {
  return buildBackendAuthorizeUrl(provider);
}

/* ================================
 * URL 유틸리티 (state 주입)
 * ================================ */
function withQuery(urlStr: string, patch: Record<string, string>) {
  const u = new URL(urlStr);
  Object.entries(patch).forEach(([k, v]) => u.searchParams.set(k, v));
  return u.toString();
}

/**
 * accounts.kakao.com/login?continue=<kauth_url>
 * 의 "continue" 안쪽(kauth 쿼리)의 state를 교체한다.
 */
function patchAccountsContinueState(accountsUrl: string, state: string): string {
  const u = new URL(accountsUrl);
  const cont = u.searchParams.get('continue');
  if (!cont) return accountsUrl; // 방어적

  // continue는 인코딩된 kauth URL → 디코드 → state 교체 → 다시 인코드하여 반영
  const decodedKauth = decodeURIComponent(cont);
  const patchedKauth = withQuery(decodedKauth, { state });
  u.searchParams.set('continue', encodeURIComponent(patchedKauth));
  return u.toString();
}

/* ================================
 * 공급자 준비 여부 검사
 * ================================ */
export function ensureProviderEnabled(provider: SocialProvider): boolean {
  const meta = OAUTH_PROVIDERS[provider];
  if (!meta) {
    console.warn('[auth] Unknown provider:', provider, 'valid=', Object.keys(OAUTH_PROVIDERS));
    alert('해당 간편 로그인은 준비중입니다');
    return false;
  }
  if (!meta.enabled) {
    alert('해당 간편 로그인은 준비중입니다');
    return false;
  }
  return true;
}

/* ================================
 * 리다이렉트 진입점
 * - Kakao: 긴 URL 사용 + 매 로그인마다 난수 state 생성/주입
 * - 그 외: 필요 시 buildAuthorizeUrl 사용(현재는 카카오만)
 * ================================ */
export function redirectToProvider(provider: SocialProvider) {
  if (!ensureProviderEnabled(provider)) return;

  // 긴 URL 원본: ENV 우선, 없으면 하드코드(성공했던 URL로 교체 가능)
  const BASE_LONG_URL =
    process.env.NEXT_PUBLIC_FULL_KAKAO_LOGIN_URL ??
    "https://accounts.kakao.com/login/?continue=https%3A%2F%2Fkauth.kakao.com%2Foauth%2Fauthorize%3Fresponse_type%3Dcode%26client_id%3Da7c27574c30bb99e563d2b584d58de73%26redirect_uri%3Dhttps%253A%252F%252Fskinmate.site%252Flogin%252Foauth2%252Fcode%252Fkakao%26scope%3Dprofile_nickname%26state%3Dskinmate%26through_account%3Dtrue#login";

  // 1) 매번 난수 state 생성 + 세션 저장 → 콜백에서 동일 값 비교
  const state = Math.random().toString(36).slice(2);
  if (typeof window !== 'undefined') {
    sessionStorage.setItem('oauth:kakao:state', state);
  }

  // 2) 긴 URL 내부(continue=kauth...)의 state 값을 방금 만든 state로 교체
  const finalUrl =
    provider === 'kakao'
      ? patchAccountsContinueState(BASE_LONG_URL, state)
      : buildAuthorizeUrl(provider);

  // 페이지 이동 (fetch 금지)
  window.location.assign(finalUrl);
}

/* ================================
 * 토큰 유틸
 * ================================ */
export const AUTH_CHANGED_EVENT = 'auth-changed';   // 같은 탭 갱신용 이벤트
const ACCESS_KEY = 'accessToken';
const REFRESH_KEY = 'refreshToken';

export type Tokens = { accessToken: string; refreshToken?: string };

/** 토큰 저장(+ 같은 탭 즉시 반영을 위한 이벤트 발행) */
export function saveTokens(tokens: Tokens) {
  if (typeof window === 'undefined') return;
  if (tokens.accessToken) localStorage.setItem(ACCESS_KEY, tokens.accessToken);
  if (tokens.refreshToken) localStorage.setItem(REFRESH_KEY, tokens.refreshToken);
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

export function getAccessToken() {
  return typeof window !== 'undefined' ? localStorage.getItem(ACCESS_KEY) : null;
}

export function getRefreshToken() {
  return typeof window !== 'undefined' ? localStorage.getItem(REFRESH_KEY) : null;
}

/** 전체 토큰 정리(+ 이벤트 발행) */
export function clearTokens() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  window.dispatchEvent(new Event(AUTH_CHANGED_EVENT));
}

/** URL(hash|query)에 토큰이 있으면 저장 후 URL 정리 */
export function persistTokensFromLocation(): boolean {
  if (typeof window === 'undefined') return false;
  const { location, history } = window;

  const h = location.hash?.startsWith('#') ? location.hash.slice(1) : '';
  const hp = new URLSearchParams(h);
  const s = location.search?.startsWith('?') ? location.search.slice(1) : '';
  const sp = new URLSearchParams(s);

  const accessToken = hp.get('accessToken') ?? sp.get('accessToken') ?? undefined;
  const refreshToken = hp.get('refreshToken') ?? sp.get('refreshToken') ?? undefined;

  if (accessToken) {
    saveTokens({ accessToken, refreshToken: refreshToken ?? undefined });
    history.replaceState(null, '', location.pathname);
    return true;
  }
  return false;
}

/** Authorization 자동 주입 fetch */
export async function authFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  const headers = new Headers(init.headers || {});
  const at = getAccessToken();
  if (at) headers.set('Authorization', `Bearer ${at}`);
  return fetch(input, { ...init, headers });
}

/** 서버 로그아웃 + 로컬 토큰 정리 */
export async function logout(): Promise<void> {
  try {
    const at = getAccessToken();
    await http('/api/auth/logout', {
      method: 'POST',
      headers: at ? { Authorization: `Bearer ${at}` } : undefined,
    });
  } catch (e) {
    console.warn('logout API failed, clearing local tokens anyway.', e);
  } finally {
    clearTokens(); // 항상 로컬 정리 + 이벤트 발행
  }
}
