'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { LogOut, User2, Menu, User, History, Heart, LogIn } from 'lucide-react';

// 외부에서 사용할 사용자 타입 export
export type Me = { id: number | string; name?: string; email?: string; image_url?: string };

type Props = {
  me?: Me | null;                 // 외부에서 주입 가능
  loading?: boolean;
  onLogout?: () => Promise<void> | void;
};

// 로컬스토리지 토큰 조회 헬퍼 (키 후보 몇 가지 지원)
const getAccessToken = () =>
  (typeof window !== 'undefined' &&
    (localStorage.getItem('access_token') ||
     localStorage.getItem('ACCESS_TOKEN') ||
     localStorage.getItem('token'))) || null;

export default function AppHeader({ me = null, loading = false, onLogout }: Props) {
  // 데모 사용자 (로그인 상태에서 me가 없을 때만 보조로 사용)
  const DEMO_ME: Me = {
    id: '1',
    name: '박진우',
    email: 'jinwoopz@naver.com',
    image_url: '/images/2.webp',
  };
  const ver = '20251103'; // 캐시 무력화용

  const [open, setOpen] = useState(false);
  const [isAuthed, setIsAuthed] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  // 최초 마운트 시 토큰 확인
  useEffect(() => {
    setIsAuthed(!!getAccessToken());
  }, []);

  // 메뉴 열릴 때마다 최신 토큰 상태 재확인 (로그인/로그아웃 직후 반영)
  useEffect(() => {
    if (open) setIsAuthed(!!getAccessToken());
  }, [open]);

  // 외부에서 storage 변경 시(다른 탭 등) 반영
  useEffect(() => {
    const onStorage = () => setIsAuthed(!!getAccessToken());
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  // 바깥 클릭/ESC로 닫기
  useEffect(() => {
    if (!open) return;
    const onClickOutside = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onEsc = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('click', onClickOutside);
    window.addEventListener('keydown', onEsc);
    return () => {
      window.removeEventListener('click', onClickOutside);
      window.removeEventListener('keydown', onEsc);
    };
  }, [open]);

  // 표시용 사용자(로그인 상태에서만 보임)
  const userForDisplay = isAuthed ? (me ?? DEMO_ME) : null;

  const handleLogout = async () => {
    try {
      if (onLogout) {
        await onLogout();
      } else {
        // onLogout 미제공 시, 일반적인 키들을 제거 (필요 없으면 지워도 됨)
        localStorage.removeItem('access_token');
        localStorage.removeItem('ACCESS_TOKEN');
        localStorage.removeItem('token');
      }
    } finally {
      setIsAuthed(!!getAccessToken());
      setOpen(false);
    }
  };

  return (
    <header className="sticky top-0 z-20 bg-white/90 backdrop-blur border-b">
      <div className="h-16 px-7 max-w-md mx-auto flex items-center justify-between relative">
        <a href="/" className="flex items-center space-x-2">
          <h1 className="text-3xl font-bold font-gmarket text-gray-800 tracking-tighter">SkinMate</h1>
        </a>

        <div ref={rootRef} className="relative">
          <button
            onClick={(e) => { e.stopPropagation(); setOpen(v => !v); }}
            className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition"
            aria-haspopup="menu" aria-expanded={open} aria-controls="appheader-menu" aria-label="메뉴 열기" title="메뉴"
          >
            <Menu size={20} />
          </button>

          <div
            id="appheader-menu" role="menu"
            className={[
              'absolute right-2 top-full mt-2 w-64 max-w-[calc(100vw-16px)]',
              'origin-top-right rounded-2xl border bg-white shadow-xl',
              'transition-transform transition-opacity duration-150',
              open ? 'opacity-100 scale-100' : 'pointer-events-none opacity-0 scale-95',
              'z-50',
            ].join(' ')}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-4 py-3 border-b">
              {loading ? (
                <div className="h-10 bg-gray-100 rounded animate-pulse" />
              ) : userForDisplay ? (
                <div className="flex items-center gap-3">
                  {userForDisplay.image_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={`${userForDisplay.image_url}?v=${ver}`}
                      alt="avatar"
                      className="w-10 h-10 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                      <User2 size={18} />
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">
                      {userForDisplay.name || userForDisplay.email || '사용자'}
                    </p>
                    {userForDisplay.email && (
                      <p className="text-xs text-gray-500 truncate">{userForDisplay.email}</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <User2 size={16} />
                  <span>로그인이 필요합니다.</span>
                </div>
              )}
            </div>

            {/* 메뉴 본문: 로그인 여부로 분기 */}
            {!isAuthed ? (
              <div className="p-2">
                <Link
                  href="/login"
                  className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-gray-900"
                  role="menuitem"
                  onClick={() => setOpen(false)}
                >
                  <LogIn size={18} /> 로그인 하러 가기
                </Link>
              </div>
            ) : (
              <>
                <nav className="p-2">
                  <Link href="/account" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50" role="menuitem" onClick={() => setOpen(false)}>
                    <User size={18} /><span>내 정보</span>
                  </Link>
                  <Link href="/history" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50" role="menuitem" onClick={() => setOpen(false)}>
                    <History size={18} /><span>분석 이력</span>
                  </Link>
                  <Link href="/likes" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50" role="menuitem" onClick={() => setOpen(false)}>
                    <Heart size={18} /><span>좋아요 이력</span>
                  </Link>
                </nav>
                <div className="px-2 pb-2 border-t">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-red-50 text-left text-red-600"
                    role="menuitem"
                  >
                    <LogOut size={18} /> 로그아웃
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
