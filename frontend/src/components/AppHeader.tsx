'use client';

import { useEffect, useState, useRef } from 'react';
import { LogOut, ChevronDown, User2, UserRound } from 'lucide-react';

type Me = {
  id: number | string;
  name?: string;
  email?: string;
  image_url?: string;
};

const API = process.env.NEXT_PUBLIC_API_URL; // 예: "https://api.example.com"

export default function AppHeader() {
  const [me, setMe] = useState<Me | null>(null);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const menuRef = useRef<HTMLDivElement>(null);

  // 백엔드의 /api/me에서 로그인 사용자 정보 조회 (JWT 쿠키 기반)
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const res = await fetch(`${API}/api/me`, {
          credentials: 'include', // HttpOnly 쿠키 전송
        });
        if (!alive) return;
        if (res.ok) {
          const data = await res.json();
          setMe(data ?? null);
        } else {
          setMe(null);
        }
      } catch {
        setMe(null);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  // 바깥 클릭 시 드롭다운 닫기
  useEffect(() => {
    const onClickOutside = (e: MouseEvent) => {
      if (!menuRef.current) return;
      if (!menuRef.current.contains(e.target as Node)) setOpen(false);
    };
    if (open) window.addEventListener('click', onClickOutside);
    return () => window.removeEventListener('click', onClickOutside);
  }, [open]);

  const onLogout = async () => {
    try {
      await fetch(`${API}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      location.reload(); // 상태 초기화
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <header className="sticky top-0 z-20 bg-white/90 backdrop-blur border-b">
      <div className="h-16 px-7 max-w-md mx-auto flex items-center justify-between">
        {/* 좌측: 로고 */}
        <a href="/" className="flex items-center space-x-2">
          <h1 className="text-3xl font-bold font-gmarket text-gray-800 tracking-tighter">SkinMate</h1>
        </a>

        {/* 우측: 유저 영역 */}
        <div className="relative" ref={menuRef}>
          {loading ? (
            <div className="w-10 h-10 bg-gray-100 rounded-full animate-pulse" />
          ) : me ? (
            // ✅ 로그인 상태: 아바타 버튼 클릭 시 드롭다운 토글
            <button
              onClick={() => setOpen(v => !v)}
              className="h-10 pl-3 pr-2 bg-gray-100 rounded-full flex items-center gap-2 hover:bg-gray-200 transition"
              aria-haspopup="menu"
              aria-expanded={open}
            >
              {me.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={me.image_url}
                  alt="avatar"
                  className="w-7 h-7 rounded-full object-cover"
                />
              ) : (
                <div className="w-7 h-7 rounded-full bg-white flex items-center justify-center">
                  <User2 size={18} />
                </div>
              )}
              <span className="text-sm font-semibold text-gray-800 max-w-[110px] truncate">
                {me.name || me.email || '사용자'}
              </span>
              <ChevronDown size={16} />
            </button>
          ) : (
            // ✅ 로그아웃 상태(비로그인): 로그인 버튼(아이콘 교체)
            <a
              href="/login"
              className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition"
              aria-label="로그인"
              title="로그인"
            >
              <UserRound size={20} />
            </a>
          )}

          {/* 드롭다운 메뉴 */}
          {open && me && (
            <div
              role="menu"
              className="absolute right-0 mt-2 w-48 bg-white border rounded-xl shadow-lg py-1"
            >
              <div className="px-3 py-2">
                <p className="text-sm font-semibold text-gray-800 truncate">
                  {me.name || me.email || '사용자'}
                </p>
                {me.email && (
                  <p className="text-xs text-gray-500 truncate">{me.email}</p>
                )}
              </div>
              <hr />
              <a
                href="/me"
                role="menuitem"
                className="block px-3 py-2 text-sm hover:bg-gray-50"
              >
                내 정보
              </a>
              <button
                role="menuitem"
                onClick={onLogout}
                className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
              >
                <LogOut size={16} /> 로그아웃
              </button>
            </div>
          )}

          {/*
          // (옵션) 아이콘만으로 바로 로그아웃하는 초간단 버튼을 헤더에 쓰고 싶다면:
          // <button
          //   onClick={onLogout}
          //   className="ml-2 w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center hover:bg-gray-200 transition"
          //   aria-label="로그아웃"
          //   title="로그아웃"
          // >
          //   <LogOut size={18} />
          // </button>
          */}
        </div>
      </div>
    </header>
  );
}