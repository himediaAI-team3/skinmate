'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { Heart } from 'lucide-react';
import {
  fetchLikedProducts,
  toggleProductLike,
} from '@/features/likes/api';
import type { LikedItem } from '@/app/entities/likes';

export default function LikesPage() {
  const [likes, setLikes] = useState<LikedItem[]>([]);
  const [cursor, setCursor] = useState<string | null | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [moreLoading, setMoreLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const likedIds = useMemo(() => new Set(likes.map((l) => l.id)), [likes]);

  // 최초 로드
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        // TODO: 실제 로그인 사용자의 member_id를 가져오는 로직 필요
        const memberId = 1; // 임시 하드코딩
        const res = await fetchLikedProducts(memberId);
        if (!alive) return;
        setLikes(res.data.items);
        setCursor(res.data.next_cursor ?? null);
        setError(null);
      } catch (e: any) {
        if (!alive) return;
        setError(e?.message || '좋아요 목록을 불러오지 못했습니다.');
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  // 더 보기(커서)
  const onLoadMore = async () => {
    if (!cursor) return;
    try {
      setMoreLoading(true);
      // TODO: 실제 로그인 사용자의 member_id를 가져오는 로직 필요
      const memberId = 1; // 임시 하드코딩
      const res = await fetchLikedProducts(memberId, cursor);
      setLikes((prev) => [...prev, ...res.data.items]);
      setCursor(res.data.next_cursor ?? null);
    } catch (e: any) {
      setError(e?.message || '더 불러오는 중 문제가 발생했습니다.');
    } finally {
      setMoreLoading(false);
    }
  };

  // 토글 (낙관적 업데이트)
  const toggleLike = async (e: React.MouseEvent, item: LikedItem) => {
    e.preventDefault();
    e.stopPropagation();

    const isLiked = likedIds.has(item.id);
    const prev = likes;

    // 낙관적 반영
    setLikes((curr) =>
      isLiked ? curr.filter((p) => p.id !== item.id) : [item, ...curr]
    );

    try {
      // TODO: 실제 로그인 사용자의 member_id를 가져오는 로직 필요
      const memberId = 1; // 임시 하드코딩
      const result = await toggleProductLike(memberId, item.id);
      
      // 백엔드 응답에 따라 상태 재조정 (낙관적 업데이트가 틀렸을 경우 대비)
      if (result.isLiked) {
        // 좋아요가 추가된 경우 - 이미 낙관적으로 추가했으므로 그대로 유지
        if (!likedIds.has(item.id)) {
          setLikes((curr) => [item, ...curr]);
        }
      } else {
        // 좋아요가 취소된 경우 - 이미 낙관적으로 제거했으므로 그대로 유지
        setLikes((curr) => curr.filter((p) => p.id !== item.id));
      }
      
      console.log(`✅ 좋아요 ${result.isLiked ? '추가' : '취소'} 완료! 총 ${result.likeCount}개`);
    } catch (err: any) {
      // 실패 시 롤백
      setLikes(prev);
      alert(err?.message || '요청에 실패했습니다.');
    }
  };

  return (
    <section className="mt-2">
      <h2 className="text-lg font-bold text-gray-900">좋아요한 화장품</h2>
      <p className="text-xs text-gray-500 mt-0.5">하트 버튼으로 즉시 취소할 수 있어요.</p>

      {/* 에러 */}
      {error && (
        <div className="mt-3 rounded-2xl border border-red-200 bg-red-50 text-red-700 px-4 py-3">
          <p className="text-sm font-semibold">불러오기 실패</p>
          <p className="text-xs mt-0.5">{error}</p>
        </div>
      )}

      {/* 로딩 스켈레톤 */}
      {loading && (
        <ul className="mt-3 space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <li key={i} className="h-24 rounded-2xl bg-gray-100 animate-pulse" />
          ))}
        </ul>
      )}

      {/* 리스트 */}
      {!loading && (
        <div className="mt-3 space-y-3">
          {likes.map((p) => {
            const isLiked = likedIds.has(p.id);

            return (
              <article
                key={p.id}
                className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:shadow-md"
              >
                {/* 링크를 relative로: 우측 상단 하트 오버레이 */}
                <Link href={p.href} className="block relative">
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
                      <div className="flex items-center gap-2">
                        <p className="text-[11px] font-medium text-gray-500">{p.brand}</p>
                      </div>

                      <h3 className="mt-0.5 line-clamp-2 text-sm font-semibold text-gray-900">
                        {p.name}
                      </h3>

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
      )}

      {/* 더 보기 */}
      {!loading && cursor && (
        <div className="mt-3 flex justify-center">
          <button
            onClick={onLoadMore}
            disabled={moreLoading}
            className="inline-flex items-center justify-center rounded-full border px-4 py-2 text-sm font-semibold hover:bg-gray-50 disabled:opacity-50"
          >
            {moreLoading ? '불러오는 중…' : '더 보기'}
          </button>
        </div>
      )}
    </section>
  );
}
