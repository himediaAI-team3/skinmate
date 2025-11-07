// /src/app/login/oauth2/code/kakao/page.tsx
'use client';

import { useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { saveTokens } from '@/features/auth';

// 빌드타임 ENV(있으면 사용), 없으면 로컬 기본값 사용
const ENV_API_BASE = process.env.NEXT_PUBLIC_API_AUTH as string | undefined;
const ENV_REDIRECT = process.env.NEXT_PUBLIC_KAKAO_REDIRECT_URI as string | undefined;

export default function KakaoCallbackPage() {
  const router = useRouter();
  const params = useSearchParams();
  const inFlight = useRef(false);

  useEffect(() => {
    const run = async () => {
      const code = params.get('code');
      const returnedState = params.get('state') || '';
      if (!code) {
        router.replace('/login?error=no_code');
        return;
      }

      // 기본값 보정: ENV 없으면 로컬 기본값
      const apiBase = ENV_API_BASE ?? 'http://127.0.0.1:8080';
      const redirectUri =
        ENV_REDIRECT ??
        (typeof window !== 'undefined'
          ? `${window.location.origin}/login/oauth2/code/kakao`
          : 'https://skinmate.site/login/oauth2/code/kakao');

      // 같은 code 재사용 방지(뒤로가기/새로고침)
      const usedKey = `oauth:kakao:code:used:${code}`;
      if (sessionStorage.getItem(usedKey) === '1') {
        router.replace('/login?error=code_already_used');
        return;
      }

      // StrictMode 중복 방지
      if (inFlight.current) return;
      inFlight.current = true;

      // CSRF state 확인 (리다이렉트 직전에 저장한 값과 동일해야 함)
      const expectedState = sessionStorage.getItem('oauth:kakao:state') || '';
      if (expectedState && expectedState !== returnedState) {
        router.replace('/login?error=bad_state');
        return;
      }

      try {
        const res = await fetch(`${apiBase}/auth/kakao-login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          // credentials: 'include', // 백엔드가 세션/쿠키면 필요
          body: JSON.stringify({ code, state: returnedState, redirectUri }),
        });

        const text = await res.text();
        let data: any = null;
        try { data = JSON.parse(text); } catch {}

        if (!res.ok) {
          const msg = (data?.message || text || `exchange_failed_${res.status}`).slice(0, 200);
          router.replace(`/login?error=${encodeURIComponent(msg)}`);
          return;
        }

        if (!data?.data?.accessToken) {
          const msg = data?.message || 'no_access_token';
          router.replace(`/login?error=${encodeURIComponent(msg)}`);
          return;
        }

        // 토큰 저장
        saveTokens({
          accessToken: data.data.accessToken,
          refreshToken: data.data.refreshToken,
        });

        // 사용 처리 & state 정리
        sessionStorage.setItem(usedKey, '1');
        sessionStorage.removeItem('oauth:kakao:state');

        router.replace('/');
      } catch (e: any) {
        const msg = e?.message || 'exchange_exception';
        router.replace(`/login?error=${encodeURIComponent(msg)}`);
      } finally {
        inFlight.current = false;
      }
    };

    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  return (
    <main className="p-6">
      <h1 className="text-xl font-bold">로그인 처리 중…</h1>
      <p className="mt-2 text-sm text-gray-500">잠시만 기다려 주세요.</p>
    </main>
  );
}
