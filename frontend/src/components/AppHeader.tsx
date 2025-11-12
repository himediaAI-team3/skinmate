'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { LogOut, User2, Menu, User, History, Heart, LogIn } from 'lucide-react';
import { authApi } from '@/features/user/api';
import { getAccessToken, AUTH_CHANGED_EVENT } from '@/features/auth/api';
import type { MemberResponse } from '@/entities/account';
import { getMe, getDefaultAvatar } from '@/features/account/api'; // ★ 추가

export type Me = { id: number | string; name?: string; email?: string; image_url?: string };

type Props = {
  me?: Me | null;
  loading?: boolean;
  onLogout?: () => Promise<void> | void;
};

const hasToken = () => !!getAccessToken();

export default function AppHeader({ me = null, loading = false, onLogout }: Props) {
  const ver = '20251103';
  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [isAuthed, setIsAuthed] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const busyRef = useRef(false);
  const alertedRef = useRef(false);
  const rootRef = useRef<HTMLDivElement>(null);

  // ★ 추가: 실사용자 스테이트
  const [meServer, setMeServer] = useState<MemberResponse | null>(null);
  const [meLoading, setMeLoading] = useState(false);

  // 최초/라우트 변경/메뉴 오픈 때 토큰 평가
  useEffect(() => setIsAuthed(hasToken()), []);
  useEffect(() => setIsAuthed(hasToken()), [pathname]);
  useEffect(() => { if (open) setIsAuthed(hasToken()); }, [open]);

  // 스토리지/커스텀 이벤트로 로그인 상태 동기화
  useEffect(() => {
    const refresh = () => setIsAuthed(hasToken());
    window.addEventListener('storage', refresh);
    window.addEventListener('auth-changed', refresh);
    return () => {
      window.removeEventListener('storage', refresh);
      window.removeEventListener('auth-changed', refresh);
    };
  }, []);
  useEffect(() => {
    const onAuthChanged = () => setIsAuthed(!!getAccessToken());
    window.addEventListener(AUTH_CHANGED_EVENT, onAuthChanged);
    return () => window.removeEventListener(AUTH_CHANGED_EVENT, onAuthChanged);
  }, []);

  // ★ 핵심: 로그인되어 있으면 /api/members/me 호출해서 meServer 로딩
  const fetchMe = async () => {
    if (!hasToken()) { setMeServer(null); return; }
    setMeLoading(true);
    try {
      const data = await getMe();
      setMeServer(data ?? null);
    } catch {
      setMeServer(null);
    } finally {
      setMeLoading(false);
    }
  };

  // 메뉴가 열릴 때마다 최신 me 가져오기 + 경로 변경 시에도 갱신
  useEffect(() => { if (isAuthed) fetchMe(); }, [isAuthed]);
  useEffect(() => { if (open && isAuthed) fetchMe(); }, [open, isAuthed]);
  useEffect(() => { if (isAuthed) fetchMe(); }, [pathname]); // 페이지 이동 시 리프레시

  const handleLogout = async () => {
    if (busyRef.current) return;
    busyRef.current = true;
    setLoggingOut(true);
    setOpen(false);
    setIsAuthed(false);
    setMeServer(null);

    try {
      if (onLogout) await onLogout();
      else await authApi.logout();
      if (!alertedRef.current) {
        alertedRef.current = true;
        alert('로그아웃되었습니다.');
      }
    } catch { /* noop */ } finally {
      setLoggingOut(false);
      busyRef.current = false;
      router.push('/');
    }
  };

  // ★ 표시용 사용자(백엔드 응답 → 헤더용)
  const userForDisplay: Me | null = isAuthed && meServer
    ? {
        id: meServer.member_id,
        name: meServer.name ?? undefined,
        email: meServer.email ?? undefined,
        image_url: getDefaultAvatar(meServer.gender), // 서버에 이미지가 없으므로 gender 기반 기본값
      }
    : null;

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
              {(loading || meLoading) ? (
                <div className="h-10 bg-gray-100 rounded animate-pulse" />
              ) : userForDisplay ? (
                <div className="flex items-center gap-3">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={`${userForDisplay.image_url}?v=${ver}`}
                    alt="avatar"
                    className="w-10 h-10 rounded-full object-cover"
                  />
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
                    disabled={loggingOut}
                    aria-busy={loggingOut}
                    className={[
                      'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left',
                      loggingOut ? 'bg-gray-50 text-gray-400 cursor-not-allowed' : 'hover:bg-red-50 text-red-600',
                    ].join(' ')}
                    role="menuitem"
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
