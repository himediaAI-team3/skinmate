'use client';

import { usePathname } from 'next/navigation';
import AppHeader, { type Me } from '@/components/AppHeader';
import TabBar from '@/components/TabBar';

const TEMP_ME: Me = {
  id: 999,
  name: 'Test User',
  email: 'test@example.com',
  image_url: 'https://placehold.co/80x80?text=TU',
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
