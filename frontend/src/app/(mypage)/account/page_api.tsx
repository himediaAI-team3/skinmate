'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { Mail, User2, Info } from 'lucide-react';
import { fetchMyProfile } from '@/app/features/account';
import type { MeProfile } from '@/app/entities/account';

export default function AccountPage() {
  const [me, setMe] = useState<MeProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        const res = await fetchMyProfile();
        if (!alive) return;
        setMe(res.data);
        setError(null);
      } catch (e: any) {
        if (!alive) return;
        setError(e?.message || '내 정보를 불러오지 못했습니다.');
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  return (
    <section className="mt-2">
      <div className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
        {/* 상단 비주얼 배너 */}
        <div
          className="h-24 w-full"
          style={{
            background:
              'radial-gradient(1000px 200px at -10% -40%, rgba(255,152,0,.18), transparent 60%), radial-gradient(800px 200px at 110% -40%, rgba(236,64,122,.18), transparent 60%), linear-gradient(135deg, rgba(255,255,255,1) 0%, rgba(255,255,255,.6) 100%)',
          }}
        />

        {/* 헤더 블록 (아바타 오버랩) */}
        <div className="px-5 pb-5 -mt-10">
          {loading ? (
            <div className="flex items-end gap-4">
              <div className="w-20 h-20 rounded-2xl bg-gray-100 ring-4 ring-white border animate-pulse" />
              <div className="flex-1 min-w-0 space-y-2">
                <div className="h-4 w-40 bg-gray-100 rounded animate-pulse" />
                <div className="h-4 w-56 bg-gray-100 rounded animate-pulse" />
              </div>
            </div>
          ) : error ? (
            <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">
              <p className="text-sm font-semibold">불러오기 실패</p>
              <p className="text-xs mt-1">{error}</p>
            </div>
          ) : me ? (
            <div className="flex items-end gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={me.avatar}
                alt={`${me.name} 프로필`}
                className="w-20 h-20 rounded-2xl object-cover ring-4 ring-white border border-gray-200 shadow"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <User2 size={16} className="text-gray-500" />
                  <p className="text-[15px] font-extrabold tracking-tight text-gray-900">{me.name}</p>
                </div>
                <div className="mt-1 flex items-center gap-2 text-gray-700">
                  <Mail size={16} className="text-gray-500" />
                  <p className="text-sm truncate">{me.email}</p>
                </div>
              </div>

              {/* 필요 시 수정 라우트 노출 */}
              {/* <Link
                href="/mypage/edit"
                className="rounded-full px-3 py-1.5 text-xs font-semibold bg-gray-900 text-white shadow-sm hover:opacity-95"
              >
                정보 수정
              </Link> */}
            </div>
          ) : null}
        </div>

        {/* 정보 타일 섹션 */}
        <div className="px-5 pb-5">
          <h2 className="text-sm font-bold text-gray-900">내 정보</h2>

          {loading ? (
            <div className="mt-3 grid grid-cols-2 gap-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="h-16 rounded-xl bg-gray-100 animate-pulse" />
              ))}
            </div>
          ) : me && me.info.length > 0 ? (
            <div className="mt-3 grid grid-cols-2 gap-3">
              {me.info.map((it, i) => (
                <div
                  key={`${it.label}-${i}`}
                  className="rounded-xl border border-gray-100 bg-white p-3 shadow-[0_1px_0_rgba(0,0,0,0.03)]"
                >
                  <div className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-500">
                    <Info size={12} className="text-gray-400" />
                    {it.label}
                  </div>
                  <div className="mt-1 text-sm font-medium text-gray-900">{it.value}</div>
                </div>
              ))}
            </div>
          ) : !loading && !error ? (
            <div className="mt-3 rounded-xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500">
              등록된 추가 정보가 없습니다.
            </div>
          ) : null}

          <div className="mt-5 border-t border-gray-100 pt-3" />
        </div>
      </div>
    </section>
  );
}
