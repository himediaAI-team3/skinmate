'use client';

import { usePathname } from 'next/navigation';
import AppHeader, { type Me } from '@/components/AppHeader';
import TabBar from '@/components/TabBar';

const TEMP_ME: Me = {
  id: 1,
  name: '박진우',
  email: 'jinwoopz@naver.com',
  image_url: '/images/2.webp',
};

const MY_PREFIXES = ['/account', '/history', '/likes', '/me', '/mypage'];

export default function HeaderGate() {
  const pathname = usePathname() || '';
  const isMyPage = MY_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`));

  if (isMyPage) return null;

  return (
    <>
      <AppHeader me={TEMP_ME} />
      <TabBar />
    </>
  );
}
