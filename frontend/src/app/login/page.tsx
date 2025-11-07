'use client';

import Link from 'next/link';
import type { SocialProvider } from '@/entities/auth';
import { OAUTH_PROVIDERS } from '@/entities/auth';
import { ensureProviderEnabled, redirectToProvider } from '@/features/auth';

const PageHeader = ({ title, backHref }: { title: string; backHref: string }) => (
  <header className="p-4 flex items-center h-16">
    <Link href={backHref} className="w-10 h-10 flex items-center justify-center" aria-label="뒤로가기">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </Link>
    <h1 className="text-xl font-bold text-gray-800 absolute left-1/2 -translate-x-1/2">{title}</h1>
  </header>
);

export default function LoginPage() {
  const handleSocialLogin = (provider: SocialProvider) => {
    if (!ensureProviderEnabled(provider)) return;
    redirectToProvider(provider);
  };

  return (
    <div>
      <PageHeader title="로그인" backHref="/" />
      <main className="p-6 pb-24 flex flex-col items-center">
        <h2 className="text-2xl font-bold text-gray-800 text-center mt-8">
          시작하기 전에<br />로그인해주세요.
        </h2>
        <p className="text-gray-500 mt-2 text-center">간편 로그인을 통해 바로 시작할 수 있어요.</p>
        <div className="w-full mt-12 space-y-3">
{/*
          <button
            onClick={() => handleSocialLogin('google')}
            disabled={!OAUTH_PROVIDERS.google.enabled}
            className="w-full bg-gray-800 text-white font-bold py-4 px-8 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Google로 시작하기
          </button>

          <button
            onClick={() => handleSocialLogin('naver')}
            disabled={!OAUTH_PROVIDERS.naver.enabled}
            className="w-full bg-green-500 text-white font-bold py-4 px-8 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            네이버로 시작하기
          </button>
*/}
          <button
            onClick={() => handleSocialLogin('kakao')}
            disabled={!OAUTH_PROVIDERS.kakao.enabled}
            className="w-full bg-yellow-400 text-black font-bold py-4 px-8 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            카카오로 시작하기
          </button>
        </div>
      </main>
    </div>
  );
}
