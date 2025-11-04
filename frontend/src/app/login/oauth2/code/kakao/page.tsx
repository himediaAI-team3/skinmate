'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { saveTokens } from '@/features/auth';

export default function KakaoCallbackPage() {
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    (async () => {
      const code = params.get('code');
      const returnedState = params.get('state') || '';
      if (!code) {
        router.replace('/login?error=no_code');
        return;
      }

      // CSRF 방지: 로그인 시작 전에 저장했던 state와 비교(권장)
      const expectedState = sessionStorage.getItem('oauth:kakao:state') || '';
      if (expectedState && expectedState !== returnedState) {
        router.replace('/login?error=bad_state');
        return;
      }

      try {
        // 일부 백엔드는 redirectUri 검증을 요구함
        const origin = typeof window !== 'undefined' ? window.location.origin : '';
        const redirectUri = `${origin}/login/oauth2/code/kakao`;

        const res = await fetch(`/auth/kakao-login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          // 백엔드 스펙에 맞춰 전달: code (필수), state/redirectUri(옵션)
          body: JSON.stringify({ code, state: returnedState, redirectUri }),
          // 쿠키 기반 세션이면 credentials: 'include' 필요
          // credentials: 'include',
        });

        // JSON 파싱 시도
        const data = await res.json().catch(() => null);

        if (!res.ok || !data?.success || !data?.data?.accessToken) {
          const msg = data?.message || `exchange_failed_${res.status}`;
          router.replace(`/login?error=${encodeURIComponent(msg)}`);
          return;
        }

        // 토큰 저장
        saveTokens({
          accessToken: data.data.accessToken,
          refreshToken: data.data.refreshToken,
        });

        // state 정리
        sessionStorage.removeItem('oauth:kakao:state');

        // 홈(또는 원하는 경로)로 이동
        router.replace('/');
      } catch (err) {
        router.replace('/login?error=exchange_exception');
      }
    })();
  }, [router, params]);

  return <div className="p-6">로그인 처리 중…</div>;
}
