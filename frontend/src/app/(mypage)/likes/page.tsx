'use client';

import Link from 'next/link';
import { Heart } from 'lucide-react';
import { useMemo, useState } from 'react';
import { MOCK_LIKES } from '@/lib/mypage.mock';
import type { LikedItem } from '@/lib/mypage.types';

export default function LikesPage() {
  const [likes, setLikes] = useState<LikedItem[]>(MOCK_LIKES);
  const likedIds = useMemo(() => new Set(likes.map((l) => l.id)), [likes]);

  const toggleLike = (e: React.MouseEvent, item: LikedItem) => {
    e.preventDefault();
    e.stopPropagation();
    setLikes((prev) => {
      const exists = prev.some((p) => p.id === item.id);
      return exists ? prev.filter((p) => p.id !== item.id) : [...prev, item];
    });
  };

  return (
    <section className="mt-2">
      <h2 className="text-lg font-bold text-gray-900">좋아요한 화장품</h2>
      <p className="text-xs text-gray-500 mt-0.5">하트 버튼으로 즉시 취소할 수 있어요.</p>

      <div className="mt-3 space-y-3">
        {likes.map((p) => {
          const isLiked = likedIds.has(p.id);

          return (
            <article
              key={p.id}
              className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:shadow-md"
            >
              {/* 링크 자체를 relative로: 우측 상단 하트 오버레이 */}
              <Link href={p.href} className="block relative">
                {/* 우측 최상단 하트 토글 버튼 (코스메틱 페이지와 동일한 감성) */}
                <button
                  type="button"
                  aria-label={isLiked ? '저장 취소' : '저장'}
                  onClick={(e) => toggleLike(e, p)}
                  className="absolute right-2 top-2 rounded-full bg-white/95 p-1.5 shadow-sm backdrop-blur transition hover:bg-white border border-white/60"
                >
                  <Heart
                    size={18}
                    className={isLiked ? 'fill-pink-500 stroke-pink-500' : 'stroke-gray-700'}
                  />
                </button>

                <div className="flex items-stretch gap-4 p-3">
                  {/* 썸네일 */}
                  <div className="relative w-20 h-20 rounded-xl overflow-hidden flex-shrink-0">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={p.image} alt={p.name} className="w-full h-full object-cover" />
                  </div>

                  {/* 우측 정보 */}
                  <div className="flex-1 min-w-0">
                    {/* 1행: 브랜드 (카테고리 태그는 LikedItem에 없으므로 제외) */}
                    <div className="flex items-center gap-2">
                      <p className="text-[11px] font-medium text-gray-500">{p.brand}</p>
                    </div>

                    {/* 제품명 */}
                    <h3 className="mt-0.5 line-clamp-2 text-sm font-semibold text-gray-900">
                      {p.name}
                    </h3>

                    {/* 하단: 좌측 가격 (우측 좋아요 수는 데이터 없어서 제외) */}
                    <div className="mt-2 flex items-center justify-between">
                      <span
                        className="text-[15px] font-extrabold tracking-tight text-gray-900"
                        style={{
                          background: 'linear-gradient(90deg, #111 0%, #444 100%)',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                      >
                        {p.price.toLocaleString()}원
                      </span>
                      {/* 우측 공간은 비움 (필요 시 배지/라벨 등 추가 가능) */}
                      <span />
                    </div>
                  </div>
                </div>
              </Link>
            </article>
          );
        })}

        {likes.length === 0 && (
          <div className="rounded-2xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500">
            아직 저장한 제품이 없어요.
          </div>
        )}
      </div>
    </section>
  );
}
