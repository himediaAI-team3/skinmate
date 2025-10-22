'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

type Item = {
  href: string;
  label: string;
  icon: (active: boolean) => JSX.Element;
};

const items: Item[] = [
  {
    href: '/',
    label: '홈',
    icon: (active) => (
      <svg viewBox="0 0 24 24" className={`w-6 h-6 ${active ? 'fill-gray-900' : 'fill-none'} stroke-current`}>
        <path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-9.5Z" strokeWidth="1.8" />
      </svg>
    ),
  },
  {
    href: '/scan',
    label: '스캔',
    icon: (active) => (
      <svg viewBox="0 0 24 24" className={`w-6 h-6 ${active ? 'fill-gray-900' : 'fill-none'} stroke-current`}>
        <rect x="3" y="3" width="7" height="7" rx="2" strokeWidth="1.8" />
        <rect x="14" y="14" width="7" height="7" rx="2" strokeWidth="1.8" />
        <rect x="14" y="3" width="7" height="7" rx="2" strokeWidth="1.8" />
        <rect x="3" y="14" width="7" height="7" rx="2" strokeWidth="1.8" />
      </svg>
    ),
  },
  {
    href: '/routine',
    label: '루틴',
    icon: (active) => (
      <svg viewBox="0 0 24 24" className={`w-6 h-6 ${active ? 'fill-gray-900' : 'fill-none'} stroke-current`}>
        <path d="M4 6h16M4 12h16M4 18h10" strokeWidth="1.8" />
      </svg>
    ),
  },
  {
    href: '/me',
    label: '내 정보',
    icon: (active) => (
      <svg viewBox="0 0 24 24" className={`w-6 h-6 ${active ? 'fill-gray-900' : 'fill-none'} stroke-current`}>
        <circle cx="12" cy="8" r="4" strokeWidth="1.8" />
        <path d="M20 21a8 8 0 0 0-16 0" strokeWidth="1.8" />
      </svg>
    ),
  },
];

export default function TabBar() {
  const pathname = usePathname();

  return (
    <nav
      className="
        fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md
        border-t border-gray-200 bg-white/95 backdrop-blur
        shadow-[0_-6px_12px_rgba(0,0,0,0.04)]
        safe-area-bottom
      "
      style={{
        paddingBottom: 'max(env(safe-area-inset-bottom), 8px)',
      }}
    >
      <ul className="grid grid-cols-4 h-14 items-center">
        {items.map(({ href, label, icon }) => {
          const active = pathname === href || (href !== '/' && pathname.startsWith(href));
          return (
            <li key={href} className="flex justify-center">
              <Link
                href={href}
                className="flex flex-col items-center gap-1 text-xs"
                aria-current={active ? 'page' : undefined}
              >
                {icon(active)}
                <span className={active ? 'text-gray-900 font-semibold' : 'text-gray-500'}>{label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
