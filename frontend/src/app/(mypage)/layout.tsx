'use client';
import AppHeader, { type Me } from '@/components/AppHeader';

export default function MyPageLayout({ children }: { children: React.ReactNode }) {
  const tempMe: Me = {
    id: 1,
    name: 'jinwoo',
    email: 'jinwoopz@naver.com',
    image_url: 'https://placehold.co/80x80?text=JW',
  };

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white">
      <AppHeader me={tempMe} onLogout={() => alert('임시 로그아웃')} />
      <main className="px-5 pb-5">{children}</main>
    </div>
  );
}
