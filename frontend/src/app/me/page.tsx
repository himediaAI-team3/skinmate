'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Heart, Mail, User2, Info, Calendar, ChevronRight } from 'lucide-react';
import { useMemo, useState } from 'react';

type DiagnoseItem = {
  id: number;      // analysis id
  date: string;    // YYYY-MM-DD
  summary: string; // 진단명(예: 지복합성, 민감성)
};

type LikedItem = {
  id: number;
  brand: string;
  name: string;
  price: number;
  image: string;
  href: string;
};

type UserProfile = {
  avatar: string;
  name: string;
  email: string;
  info: Array<{ label: string; value: string }>;
};

const MOCK_USER: UserProfile = {
  avatar: 'https://placehold.co/160x160/png?text=YOU',
  name: '홍길동',
  email: 'gildong@example.com',
  info: [
    { label: '피부타입', value: '지복합성' },
    { label: '민감도', value: '민감성' },
    { label: '주요 고민', value: '여드름/홍조' },
    { label: '선호 성분', value: '시카, 판테놀' },
  ],
};

const MOCK_HISTORY: DiagnoseItem[] = [
  { id: 54, date: '2025-10-22', summary: '여드름' },
  { id: 53, date: '2025-10-15', summary: '건선' },
];

const MOCK_LIKES: LikedItem[] = [
  { id: 2, brand: 'Rayderm', name: '오일프리 선스크린 SPF50+', price: 15800, image: 'https://placehold.co/320x320/B2DFDB/00796B?text=Sun', href: '/cosmetics/2' },
  { id: 1, brand: 'SKNM', name: '수딩 시카 크림', price: 19800, image: 'https://placehold.co/320x320/FFE0B2/FF6B6B?text=Cica', href: '/cosmetics/1' },
  { id: 3, brand: 'HyaLab', name: '히알루론산 토너 500ml', price: 12900, image: 'https://placehold.co/320x320/E1BEE7/6A1B9A?text=Toner', href: '/cosmetics/3' },
];

export default function MyPage() {
  const router = useRouter();
  const TAB_H = 56;
  const tabSpacerStyle = { height: `calc(${TAB_H}px + env(safe-area-inset-bottom))` };

  // 좋아요 목록 상태
  const [likes, setLikes] = useState<LikedItem[]>(MOCK_LIKES);
  const likedIds = useMemo(() => new Set(likes.map(l => l.id)), [likes]);

  const toggleLike = (e: React.MouseEvent, item: LikedItem) => {
    e.preventDefault();
    e.stopPropagation();
    setLikes(prev => {
      const exists = prev.some(p => p.id === item.id);
      return exists ? prev.filter(p => p.id !== item.id) : [...prev, item];
    });
  };

  return (
    <div className="max-w-md mx-auto bg-white">
      {/* 헤더 */}
      <header className="p-4 flex items-center h-16">
        <button
          onClick={() => router.back()}
          aria-label="뒤로가기"
          className="w-10 h-10 flex items-center justify-center"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24" height="24" viewBox="0 0 24 24"
            fill="none" stroke="currentColor"
            strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          >
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <h1 className="text-xl font-bold text-gray-800 absolute left-1/2 -translate-x-1/2">
          마이페이지
        </h1>
      </header>

      <main className="px-5 pb-2">
        {/* 프로필 섹션 */}
        <section className="mt-1">
          <div className="relative overflow-hidden rounded-2xl border border-white/60 bg-white/80 backdrop-blur shadow-sm">
            <div className="p-4">
              <div className="flex items-center gap-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={MOCK_USER.avatar}
                  alt={`${MOCK_USER.name} 프로필`}
                  className="w-16 h-16 rounded-2xl object-cover border border-gray-200"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <User2 size={16} className="text-gray-500" />
                    <p className="text-base font-bold text-gray-900">{MOCK_USER.name}</p>
                  </div>
                  <div className="mt-1 flex items-center gap-2">
                    <Mail size={16} className="text-gray-500" />
                    <p className="text-sm text-gray-700">{MOCK_USER.email}</p>
                  </div>
                </div>
                
              </div>

              {/* 추가 info (chips) */}
              <div className="mt-4 flex flex-wrap gap-2">
                {MOCK_USER.info.map((it, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 rounded-full border border-white/60 bg-white/80 backdrop-blur px-3 py-1 text-[11px] font-semibold text-gray-700"
                  >
                    <Info size={12} className="text-gray-500" />
                    <span className="text-gray-500">{it.label}</span>
                    <span className="text-gray-900">· {it.value}</span>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* 진단 이력 — 요약 리스트 (진단명 + 날짜만) */}
        <section className="mt-6">
          <h2 className="text-lg font-bold text-gray-900">분석 이력</h2>
          <div className="mt-3 divide-y divide-gray-100 rounded-2xl border border-gray-100 bg-white overflow-hidden">
            {MOCK_HISTORY.map((h) => (
              <Link
                key={h.id}
                href={`/result/${h.id}`}
                className="flex items-center gap-3 p-4 hover:bg-gray-50 transition"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">{h.summary}</p>
                  <p className="mt-0.5 inline-flex items-center gap-1 text-xs text-gray-500">
                    <Calendar size={14} />
                    <span>{h.date}</span>
                  </p>
                </div>
                <ChevronRight size={18} className="text-gray-400" aria-hidden />
              </Link>
            ))}

            {MOCK_HISTORY.length === 0 && (
              <div className="p-4 text-sm text-gray-500 text-center">진단 이력이 없습니다.</div>
            )}
          </div>
        </section>

        {/* 좋아요한 화장품 리스트 (하트로 즉시 취소 가능) */}
        <section className="mt-6">
          <h2 className="text-lg font-bold text-gray-900">좋아요한 화장품</h2>
          <div className="mt-3 grid grid-cols-2 gap-3">
            {likes.map((p) => {
              const isLiked = likedIds.has(p.id);
              return (
                <article
                  key={p.id}
                  className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:shadow-md"
                >
                  <Link href={p.href} className="block">
                    <div className="relative aspect-square w-full">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={p.image} alt={p.name} className="h-full w-full object-cover" />

                      {/* 우측 상단 하트 버튼 (즉시 취소/복구) */}
                      <button
                        type="button"
                        aria-label={isLiked ? '저장 취소' : '저장'}
                        onClick={(e) => toggleLike(e, p)}
                        className={[
                          'absolute right-2 top-2 inline-flex items-center gap-1 rounded-full px-2 py-1 text-[10px] font-semibold shadow-sm',
                          'backdrop-blur border',
                          isLiked
                            ? 'bg-white/95 border-white/80 text-pink-600 hover:bg-white'
                            : 'bg-white/80 border-white/60 text-gray-700 hover:bg-white',
                        ].join(' ')}
                      >
                        <Heart
                          size={12}
                          className={isLiked ? 'fill-pink-500 stroke-pink-500' : 'stroke-gray-700'}
                        />
                        {isLiked ? '저장됨' : '저장'}
                      </button>
                    </div>

                    <div className="p-3">
                      <p className="text-[11px] font-medium text-gray-500">{p.brand}</p>
                      <h3 className="mt-0.5 line-clamp-2 text-sm font-semibold text-gray-900">{p.name}</h3>
                      <p className="mt-1 text-[15px] font-extrabold tracking-tight text-gray-900">
                        {p.price.toLocaleString()}원
                      </p>
                    </div>
                  </Link>
                </article>
              );
            })}
            {likes.length === 0 && (
              <div className="col-span-2 rounded-2xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500">
                아직 저장한 제품이 없어요.
              </div>
            )}
          </div>
        </section>

        {/* 탭바 스페이서 */}
        <div aria-hidden style={tabSpacerStyle} />
      </main>
    </div>
  );
}
