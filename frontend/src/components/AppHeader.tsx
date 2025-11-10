'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { LogOut, User2, Menu, User, History, Heart, LogIn } from 'lucide-react';
import { authApi } from '@/features/user/api';
import { getAccessToken, AUTH_CHANGED_EVENT } from '@/features/auth/api';

export type Me = { id: number | string; name?: string; email?: string; image_url?: string };

type Props = {
  me?: Me | null;
  loading?: boolean;
  onLogout?: () => Promise<void> | void;
};

const hasToken = () => !!getAccessToken();

export default function AppHeader({ me = null, loading = false, onLogout }: Props) {
  const DEMO_ME: Me = { id: '1', name: '박진우', email: 'jinwoopz@naver.com', image_url: '/images/2.webp' };
  const ver = '20251103';

  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [isAuthed, setIsAuthed] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);     // ✅ 로딩 상태
  const busyRef = useRef(false);                            // ✅ 중복 클릭 락
  const alertedRef = useRef(false);                         // ✅ 알림 1회 보장
  const rootRef = useRef<HTMLDivElement>(null);

  // 최초 마운트
  useEffect(() => setIsAuthed(hasToken()), []);

  // 라우트 변경 시 토큰 재평가
  useEffect(() => setIsAuthed(hasToken()), [pathname]);

  // 메뉴 열릴 때 최신 상태 반영
  useEffect(() => { if (open) setIsAuthed(hasToken()); }, [open]);

  // 다른 탭(storage) + 같은 탭(auth-changed) 반응
  useEffect(() => {
    const refresh = () => setIsAuthed(hasToken());
    window.addEventListener('storage', refresh);
    window.addEventListener('auth-changed', refresh);
    return () => {
      window.removeEventListener('storage', refresh);
      window.removeEventListener('auth-changed', refresh);
    };
  }, []);

  // AUTH_CHANGED_EVENT 상수 리스너(선택적; 위와 중복 방지용으로 유지)
  useEffect(() => {
    const onAuthChanged = () => setIsAuthed(!!getAccessToken());
    window.addEventListener(AUTH_CHANGED_EVENT, onAuthChanged);
    return () => window.removeEventListener(AUTH_CHANGED_EVENT, onAuthChanged);
  }, []);

  // 바깥 클릭/ESC 닫기
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

  const userForDisplay = isAuthed ? (me ?? DEMO_ME) : null;

  const handleLogout = async () => {
    // ✅ 중복 방지: 이미 진행 중이면 무시
    if (busyRef.current) return;
    busyRef.current = true;
    setLoggingOut(true);

    // ✅ 즉시 UX 반영: 메뉴 닫고 헤더 상태 false로 (optimistic)
    setOpen(false);
    setIsAuthed(false);

    try {
      if (onLogout) {
        await onLogout();
      } else {
        await authApi.logout(); // 내부에서 토큰 즉시 삭제 + 서버 호출
      }
      // ✅ 알림은 한 번만
      if (!alertedRef.current) {
        alertedRef.current = true;
        alert('로그아웃되었습니다.');
      }
    } catch {
      // 실패해도 optimistic으로 이미 로그아웃 처리됨
    } finally {
      setLoggingOut(false);
      busyRef.current = false;
      router.push('/');
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
            type="button"
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
                    <img src={`${userForDisplay.image_url}?v=${ver}`} alt="avatar" className="w-10 h-10 rounded-full object-cover" />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                      <User2 size={18} />
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">
                      {userForDisplay.name || userForDisplay.email || '사용자'}
                    </p>
                    {userForDisplay.email && <p className="text-xs text-gray-500 truncate">{userForDisplay.email}</p>}
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3 text-sm text-gray-600">
                  <User2 size={16} />
                  <span>로그인이 필요합니다.</span>
                </div>
              )}
            </div>

            {!isAuthed ? (
              <div className="p-2">
                <Link href="/login" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-gray-900" role="menuitem" onClick={() => setOpen(false)}>
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
                    type="button"
                    disabled={loggingOut}                                   // ✅ 비활성화
                    aria-busy={loggingOut}
                    className={[
                      'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left',
                      loggingOut
                        ? 'bg-gray-50 text-gray-400 cursor-not-allowed'
                        : 'hover:bg-red-50 text-red-600',
                    ].join(' ')}
                    role="menuitem"
                    data-e2e="logout-btn"
                    title={loggingOut ? '로그아웃 중…' : '로그아웃'}
                  >
                    <LogOut size={18} />
                    {loggingOut ? '로그아웃 중…' : '로그아웃'}
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
