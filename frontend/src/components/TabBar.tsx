// src/app/_components/TabBar.tsx (사용 중인 경로에 맞춰 저장)
'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { getAccessToken, AUTH_CHANGED_EVENT } from '@/features/auth/api';

type Item = {
  href: string;
  label: string;
  icon: (active: boolean) => JSX.Element;
};

const DIAG_GROUP = ['/info', '/upload', '/loading', '/result'];

// ✅ 로그인 필요한 메뉴만 명시
const REQUIRES_AUTH = new Set<string>(['/info', '/cosmetics']);

// ← items는 3개만 유지
const items: Item[] = [
  {
    href: '/',
    label: '홈',
    icon: (active) => (
      <svg viewBox="0 0 24 18" className={`w-6 h-6 ${active ? 'fill-gray-900' : 'fill-none'} stroke-current`} aria-hidden>
        <path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-9.5Z" strokeWidth="1.8" />
      </svg>
    ),
  },
  {
    href: '/info',
    label: '분석',
    icon: (active) => (
      <svg viewBox="0 0 24 18" className="w-6 h-6 stroke-current" aria-hidden>
        <path
          d="M4 7.5a2.5 2.5 0 0 1 2.5-2.5h2.2c.5 0 1-.22 1.32-.6l.72-.84A1.8 1.8 0 0 1 12.9 3h2.6c.8 0 1.5.5 1.8 1.2l.35.75H19.5A2.5 2.5 0 0 1 22 7.5v8A2.5 2.5 0 0 1 19.5 18h-15A2.5 2.5 0 0 1 2 15.5v-8Z"
          className={active ? 'fill-gray-900' : 'fill-none'}
          strokeWidth="1.6"
        />
        <circle cx="12" cy="12" r="3.5" strokeWidth="1.8" className={active ? 'fill-white' : 'fill-none'} />
      </svg>
    ),
  },
  {
    href: '/cosmetics',
    label: '화장품',
    icon: (active) => (
      <svg viewBox="0 0 24 18" className="w-9 h-9 stroke-current" fill="none" aria-hidden>
        <circle cx="8" cy="9" r="4.5" strokeWidth="1.2" className={active ? 'fill-gray-900' : 'fill-none'} />
        <path d="M6.6 7.6c.9-1 2.4-1.1 3.4-.2" strokeWidth="1.2" />
        <rect x="14" y="9" width="4.8" height="8" rx="1.2" strokeWidth="1.2" className={active ? 'fill-gray-900' : 'fill-none'} />
        <path
          d="M16.4 5.2c.6 0 1.1.3 1.4.8l.9 1.7c.2.4.1.9-.2 1.2l-.6.6h-3.2l-.6-.6a1 1 0 0 1-.2-1.2l.9-1.7c.3-.5.8-.8 1.4-.8Z"
          strokeWidth="1.6"
          className={active ? 'fill-gray-900' : 'fill-none'}
        />
        <path d="M5 13.8h6" strokeWidth="1.6" />
      </svg>
    ),
  },
];

export default function TabBar() {
  const pathname = usePathname();
  const router = useRouter();

  const [isAuthed, setIsAuthed] = useState<boolean>(!!getAccessToken());
  const warnRef = useRef(false); // 알림 중복 방지(1초 rate-limit)

  // 로그인 상태 동기화: 같은 탭(AUTH_CHANGED_EVENT), 다른 탭(storage)
  useEffect(() => {
    const refresh = () => setIsAuthed(!!getAccessToken());
    window.addEventListener('storage', refresh);
    window.addEventListener(AUTH_CHANGED_EVENT, refresh);
    return () => {
      window.removeEventListener('storage', refresh);
      window.removeEventListener(AUTH_CHANGED_EVENT, refresh);
    };
  }, []);

  // 라우트 변동 시에도 재확인(로그인 콜백 → 홈 이동 상황 반영)
  useEffect(() => {
    setIsAuthed(!!getAccessToken());
  }, [pathname]);

  const isActive = (href: string) => {
    if (href === '/info') {
      return DIAG_GROUP.some((p) => pathname === p || pathname.startsWith(`${p}/`));
    }
    if (href === '/') return pathname === '/';
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  // 보호 탭 클릭 가드
  const guardNav = (e: React.MouseEvent, href: string) => {
    if (!REQUIRES_AUTH.has(href)) return; // 보호 안하면 통과
    if (isAuthed) return;                 // 로그인됨 → 통과

    // 미로그인 → 이동 막고 로그인 페이지로
    e.preventDefault();

    if (!warnRef.current) {
      warnRef.current = true;
      alert('로그인이 필요합니다. 로그인 페이지로 이동합니다.');
      setTimeout(() => (warnRef.current = false), 1000); // 1초 내 중복 알림 방지
    }

    router.push('/login');
  };

  const TAB_H = 56;
  const tabHeightStyle = { height: `calc(${TAB_H}px + env(safe-area-inset-bottom))` };
  const tabPaddingStyle = { paddingBottom: 'max(env(safe-area-inset-bottom), 8px)' };

  return (
    <>
      {/* 컨텐츠가 탭에 가려지지 않도록 스페이서 */}
      <div aria-hidden className="w-full" style={tabHeightStyle} />

      <nav
        className="
          fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md
          border-t border-gray-200 bg-white/95 backdrop-blur
          shadow-[0_-6px_12px_rgba(0,0,0,0.04)]
          z-40
          flex items-center justify-center
        "
        style={tabHeightStyle}
        aria-label="하단 메뉴"
      >
        <ul className="flex items-center justify-center gap-8 sm:gap-10 md:gap-12 h-full">
          {items.map(({ href, label, icon }) => {
            const active = isActive(href);
            return (
              <li key={href} className="h-full flex">
                <Link
                  href={href}
                  className="h-full px-6 sm:px-7 md:px-8 flex flex-col items-center justify-center gap-1 text-xs"
                  aria-current={active ? 'page' : undefined}
                  aria-label={label}
                  style={tabPaddingStyle}
                  onClick={(e) => guardNav(e, href)}
                >
                  {icon(active)}
                  <span className={active ? 'text-gray-900 font-semibold' : 'text-gray-500'}>{label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </>
  );
}
