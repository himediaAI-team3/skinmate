// (mypage)/layout.tsx
'use client';
import AppHeader, { type Me } from '@/components/AppHeader';
import TabBar from '@/components/TabBar';
import { logout } from '@/features/auth';
import { useRouter } from 'next/navigation';
import { useCallback } from 'react';

export default function MyPageLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  const tempMe: Me = {
    id: 1,
    name: 'jinwoo',
    email: 'jinwoopz@naver.com',
    image_url: '/images/1.webp',
  };

  // 실제 로그아웃 핸들러
  const handleLogout = useCallback(async () => {
    await logout();          // 서버 /auth/logout 호출 + 로컬 토큰 삭제
    router.replace('/login'); // 로그인 페이지로 이동(원하면 '/' 등으로 변경 가능)
  }, [router]);

  return (
    <div className="max-w-md mx-auto min-h-screen bg-white">
      <AppHeader me={tempMe} onLogout={handleLogout} /> {/* ✅ 교체 */}
      <main className="px-5 pb-5">{children}</main>
      <TabBar />
    </div>
  );
}
