// /src/app/login/oauth2/code/kakao/page.tsx
'use client';

import { useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { saveTokens } from '@/features/auth';

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

      const apiBase = ENV_API_BASE ?? 'http://127.0.0.1:8080';
      const redirectUri =
        ENV_REDIRECT ??
        (typeof window !== 'undefined'
          ? `${window.location.origin}/login/oauth2/code/kakao`
          : 'https://skinmate.site/login/oauth2/code/kakao');

      const usedKey = `oauth:kakao:code:used:${code}`;
      if (sessionStorage.getItem(usedKey) === '1') {
        router.replace('/login?error=code_already_used');
        return;
      }

      if (inFlight.current) return;
      inFlight.current = true;

      const expectedState = sessionStorage.getItem('oauth:kakao:state') || '';
      if (expectedState && expectedState !== returnedState) {
        router.replace('/login?error=bad_state');
        return;
      }

      try {
        const res = await fetch(`${apiBase}/auth/kakao-login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
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

        // 토큰 저장 (auth-changed 이벤트 발행 포함)
        saveTokens({
          accessToken: data.data.accessToken,
          refreshToken: data.data.refreshToken,
        });

        // 사용 처리 & state 정리
        sessionStorage.setItem(usedKey, '1');
        sessionStorage.removeItem('oauth:kakao:state');

        // 로그인 완료 알림
        alert('로그인되었습니다.');

        // 홈으로 이동
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
