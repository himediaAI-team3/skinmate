'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { User2, Info, Heart, History, Sparkles } from 'lucide-react';
import { MOCK_USER, MOCK_HISTORY, MOCK_LIKES } from '@/lib/mypage.mock';
import type { MemberResponse } from '@/entities/account';
import { getMe, getDefaultAvatar } from '@/features/account/api';

// 서버 MemberResponse -> 화면용 profile 형태로 매핑
function toProfileFromServer(me: MemberResponse | null | undefined) {
  if (!me) return null;
  return {
    name: me.name ?? '이름 미입력',
    email: me.email ?? '',
    avatar: getDefaultAvatar(me.gender),
    info: [
      { label: '피부타입', value: me.skin_type ?? '미입력' },
      { label: '성별', value: me.gender ?? '미입력' },
      { label: '나이', value: me.age_group ? `${me.age_group}대` : '미입력' },
    ],
  };
}

export default function AccountPage() {
  const [profile, setProfile] = useState<any>(MOCK_USER);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const me = await getMe();
        const fromServer = toProfileFromServer(me);
        if (fromServer) setProfile(fromServer);
      } catch {
        setProfile(MOCK_USER);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // 정보 맵 (라벨 → 값)
  const infoMap = useMemo<Record<string, string>>(
    () => Object.fromEntries((profile.info || []).map((i: any) => [i.label, i.value])),
    [profile]
  );

  // 프로필 완성도 (피부타입/성별/나이)
  const completeness = useMemo(() => {
    const fields = ['피부타입', '성별', '나이'];
    const filled = fields.filter((f) => {
      const v = infoMap[f];
      return v && v !== '미입력';
    }).length;
    return Math.round((filled / fields.length) * 100);
  }, [infoMap]);

  const recentHistory = (MOCK_HISTORY || []).slice(0, 2);
  const recentLikes = (MOCK_LIKES || []).slice(0, 2);

  return (
    <main className="max-w-md mx-auto px-7">
      {/* 프로필 카드 */}
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
            <div className="flex items-center gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={profile.avatar}
                alt={`${profile.name} 프로필`}
                className="w-20 h-20 rounded-2xl object-cover ring-4 ring-white border border-gray-200 shadow"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <User2 size={16} className="text-gray-500" />
                  <p className="text-[15px] font-extrabold tracking-tight text-gray-900">
                    {loading ? '로딩 중…' : profile.name}
                  </p>
                </div>
              </div>

              <Link
                href="/account/edit"
                className="rounded-full px-3 py-1.5 text-xs font-semibold bg-gray-900 text-white shadow-sm hover:opacity-95"
              >
                정보 수정
              </Link>
            </div>
          </div>

          {/* 내 정보 + 완성도(한 줄) + 빠른 메뉴 */}
          <div className="px-5 pb-5">
            {/* 내 정보 */}
            <h2 className="text-sm font-bold text-gray-900">내 정보</h2>

            {/* 피부타입/성별/나이 → 2열 그리드 */}
            <div className="mt-3 grid grid-cols-2 gap-3">
              {/* 피부타입 */}
              <div className="rounded-xl border border-gray-100 bg-white p-3 shadow-[0_1px_0_rgba(0,0,0,0.03)]">
                <div className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-500">
                  <Info size={12} className="text-gray-400" />
                  피부타입
                </div>
                <div className="mt-1 text-sm font-medium text-gray-900">
                  {infoMap['피부타입'] ?? '미입력'}
                </div>
              </div>

              {/* 성별 */}
              <div className="rounded-xl border border-gray-100 bg-white p-3 shadow-[0_1px_0_rgba(0,0,0,0.03)]">
                <div className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-500">
                  <Info size={12} className="text-gray-400" />
                  성별
                </div>
                <div className="mt-1 text-sm font-medium text-gray-900">
                  {infoMap['성별'] ?? '미입력'}
                </div>
              </div>

              {/* 나이 */}
              <div className="rounded-xl border border-gray-100 bg-white p-3 shadow-[0_1px_0_rgba(0,0,0,0.03)]">
                <div className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-500">
                  <Info size={12} className="text-gray-400" />
                  나이
                </div>
                <div className="mt-1 text-sm font-medium text-gray-900">
                  {infoMap['나이'] ?? '미입력'}
                </div>
              </div>

              {/* 빈 칸 맞춤(2열 균형) */}
              <div className="hidden sm:block" />
            </div>

            {/* 구분선 */}
            <div className="mt-5 border-t border-gray-100 pt-4" />

            {/* ▶ 프로필 완성도: 한 줄(풀 너비) */}
            <div className="mt-4">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-500">
                <Sparkles size={12} className="text-gray-400" />
                프로필 완성도
              </div>
              <div className="mt-2">
                <div className="h-2 w-full rounded-full bg-gray-100 overflow-hidden">
                  <div
                    className="h-full bg-gray-900 transition-all"
                    style={{ width: `${completeness}%` }}
                  />
                </div>
                <p className="mt-1.5 text-xs text-gray-600">{completeness}% 완료</p>
              </div>
            </div>

            {/* 구분선 */}
            <div className="mt-5 border-t border-gray-100 pt-4" />

            {/* 빠른 메뉴 */}
            <div className="mt-4 grid grid-cols-2 gap-3">
              <Link
                href="/history"
                className="rounded-xl border border-gray-100 bg-white p-3 shadow-[0_1px_0_rgba(0,0,0,0.03)] hover:bg-gray-50 transition"
              >
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-gray-100 flex items-center justify-center">
                    <History size={16} className="text-gray-700" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900">분석 이력</p>
                    <p className="text-[11px] text-gray-500">최근 기록 확인</p>
                  </div>
                </div>
              </Link>

              <Link
                href="/likes"
                className="rounded-xl border border-gray-100 bg-white p-3 shadow-[0_1px_0_rgba(0,0,0,0.03)] hover:bg-gray-50 transition"
              >
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-gray-100 flex items-center justify-center">
                    <Heart size={16} className="text-gray-700" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900">좋아요</p>
                    <p className="text-[11px] text-gray-500">찜한 제품 보기</p>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </section>

      <div className="h-8" />
    </main>
  );
}
