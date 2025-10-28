'use client';

import Link from 'next/link';
import { Heart, ChevronLeft, ChevronRight } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import type { UiLikedItem as LikedItem } from '@/entities/likes/model/schemas';
import { fetchMemberLikedCosmeticsPage, toggleProductLike } from '@/features/likes/api';

export default function LikesPage() {
  const PAGE_SIZE = 10;
  const IS_ZERO_BASED_API = true; // ← 백엔드가 0-based면 true, 1-based면 false
  const memberId = 1;

  const [likes, setLikes] = useState<LikedItem[]>([]); // 현재 페이지에 실제로 그릴 아이템
  const [total, setTotal] = useState<number | undefined>(undefined);
  const [page, setPage] = useState(1); // 항상 UI는 1-based
  const [loading, setLoading] = useState(false);
  const [pending, setPending] = useState<Set<number>>(new Set());

  const likedIds = useMemo(() => new Set(likes.map((l) => l.id)), [likes]);

  // 총합이 없을 때도 버튼이 뜨도록 총합 추정 보정
  const totalForUi = Math.max(total ?? 0, likes.length ?? 0);
  const totalPages = Math.max(1, Math.ceil(totalForUi / PAGE_SIZE));

  // 숫자 버튼 계산(최대 5개)
  const visibleCount = 5;
  const startPage = Math.max(
    1,
    Math.min(page - Math.floor(visibleCount / 2), totalPages - visibleCount + 1)
  );
  const endPage = Math.min(totalPages, startPage + visibleCount - 1);
  const pages = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        // 1-based 그대로 전송
        const resp = await fetchMemberLikedCosmeticsPage({
          memberId,
          page,               // ← 1-based
          size: PAGE_SIZE,
        });
        if (!alive) return;
  
        const serverItems = resp.items ?? [];
        const serverTotal = typeof resp.total === 'number' ? resp.total : undefined;
  
        // 서버가 size=10 요청에 딱 10개 줬는지
        const filledPage = serverItems.length === PAGE_SIZE;
  
        // ---- 핵심 보정 로직 ----
        // 규칙:
        // 1) total이 존재하고 합리적(>= page*size 이거나 > (page-1)*size) 이면 그걸 믿음
        // 2) total이 없거나 모순(예: total < page*size 인데 10개 꽉 채워줌)이면 hasMore로 추정
        let uiTotal: number;
        if (typeof serverTotal === 'number') {
          const expectedMin = (page - 1) * PAGE_SIZE + serverItems.length;
          if (serverTotal < expectedMin && filledPage) {
            // total이 모순인데, 현재 페이지가 꽉 찼다면 다음 페이지가 더 있다고 판단
            uiTotal = page * PAGE_SIZE + 1; // 2페이지 버튼이 뜨도록 최소 11로 올림
          } else {
            uiTotal = Math.max(serverTotal, expectedMin);
          }
        } else {
          // total이 없다면: 꽉 찼으면 다음 페이지 존재 가정
          uiTotal = (page - 1) * PAGE_SIZE + serverItems.length + (filledPage ? 1 : 0);
        }
        // ----------------------
  
        setLikes(serverItems.length <= PAGE_SIZE ? serverItems
                                                 : serverItems.slice(0, PAGE_SIZE));
        setTotal(uiTotal);
      } catch (err) {
        if (!alive) return;
        console.error('[likes] fetch error:', err);
        setLikes([]);
        setTotal(0);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, [memberId, page]);

  // 버튼 공통
  function IconButton({
    onClick, disabled, label, children,
  }: { onClick: () => void; disabled?: boolean; label: string; children: React.ReactNode }) {
    return (
      <button
        aria-label={label}
        onClick={onClick}
        disabled={disabled}
        title={label}
        className={[
          'h-9 w-9 inline-flex items-center justify-center rounded-full',
          'border border-white/60 bg-white/70 backdrop-blur',
          'shadow-sm hover:shadow transition hover:scale-[1.03] active:scale-[0.98]',
          'focus:outline-none focus:ring-2 focus:ring-orange-200',
          'disabled:opacity-45 disabled:hover:scale-100 disabled:shadow-none',
        ].join(' ')}
      >
        {children}
        <span className="sr-only">{label}</span>
      </button>
    );
  }

  // 하트 토글(좋아요 취소 중심)
  const onToggle = async (e: React.MouseEvent, item: LikedItem) => {
    e.preventDefault();
    e.stopPropagation();

    if (pending.has(item.id)) return;
    setPending(prev => new Set(prev).add(item.id));

    const before = likes;
    // 낙관적으로 제거
    setLikes(prev => prev.filter(p => p.id !== item.id));
    setTotal(t => {
      const cur = t ?? 0;
      return Math.max(0, cur - 1);
    });

    try {
      const res = await toggleProductLike(memberId, item.id);
      if (res.isLiked) {
        // 서버가 다시 좋아요(true)라고 하면 롤백
        setLikes(prev => [item, ...prev]);
        setTotal(t => (t ?? 0) + 1);
      } else {
        // 정상적으로 취소. 현재 페이지가 비면 이전 페이지로
        if (before.length === 1 && page > 1) {
          setPage(p => Math.max(1, p - 1));
        }
      }
    } catch (err) {
      console.error('[likes] toggle error:', err);
      // 실패 롤백
      setLikes(before);
      setTotal(t => (t ?? 0) + 1);
      alert('좋아요 변경에 실패했습니다. 네트워크 상태를 확인해주세요.');
    } finally {
      setPending(prev => {
        const next = new Set(prev);
        next.delete(item.id);
        return next;
      });
    }
  };

  return (
    <section className="mt-2">
      <h2 className="text-lg font-bold text-gray-900">좋아요한 화장품</h2>
      <p className="text-xs text-gray-500 mt-0.5">하트 버튼으로 즉시 취소할 수 있어요.</p>

      {/* 리스트 */}
      <div className="mt-3 space-y-3">
        {loading && (
          <div className="rounded-2xl border border-gray-100 bg-white p-6 text-center text-sm text-gray-500">
            불러오는 중…
          </div>
        )}

        {!loading && likes.map((p) => {
          const isLiked = likedIds.has(p.id);
          const isBusy = pending.has(p.id);
          return (
            <article
              key={p.id}
              className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:shadow-md"
            >
              <Link href={p.href} className="block relative">
                {/* 우측 상단 하트 토글 */}
                <button
                  type="button"
                  aria-label={isLiked ? '저장 취소' : '저장'}
                  onClick={(e) => onToggle(e, p)}
                  disabled={isBusy}
                  className="absolute right-2 top-2 rounded-full bg-white/95 p-1.5 shadow-sm backdrop-blur transition hover:bg-white border border-white/60 disabled:opacity-60 disabled:cursor-not-allowed"
                  title={isBusy ? '처리 중...' : isLiked ? '저장 취소' : '저장'}
                >
                  <Heart
                    size={18}
                    className={isLiked ? 'fill-pink-500 stroke-pink-500' : 'stroke-gray-700'}
                  />
                </button>

                <div className="flex items-stretch gap-4 p-3">
                  <div className="relative w-20 h-20 rounded-xl overflow-hidden flex-shrink-0">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={p.image} alt={p.name} className="w-full h-full object-cover" />
                  </div>

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
                        {Number(p.price).toLocaleString()}원
                      </span>
                      <span />
                    </div>
                  </div>
                </div>
              </Link>
            </article>
          );
        })}

        {!loading && likes.length === 0 && (
          <div className="rounded-2xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500">
            아직 저장한 제품이 없어요.
          </div>
        )}
      </div>

      {/* 페이지네이션: 총합이 없어도 hasMore 추정으로 버튼 노출 */}
      {Number.isFinite(totalPages) && totalPages > 1 && (
        <section className="mt-4 flex items-center justify-center gap-2">
          {/* 이전 */}
          <IconButton
            label="이전 페이지"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            <ChevronLeft size={18} className="text-gray-800" aria-hidden />
          </IconButton>

          {/* 숫자 버튼 */}
          {pages.map((pNum) => {
            const active = pNum === page;
            return (
              <button
                key={pNum}
                onClick={() => setPage(pNum)}
                aria-current={active ? 'page' : undefined}
                className={[
                  'h-9 min-w-9 px-3 inline-flex items-center justify-center rounded-full text-xs font-medium tabular-nums',
                  'transition focus:outline-none focus:ring-2 focus:ring-orange-200',
                  active
                    ? 'border border-gray-900 bg-gray-900 text-white shadow-sm'
                    : 'border border-white/60 bg-white/70 backdrop-blur hover:shadow hover:scale-[1.02]',
                ].join(' ')}
              >
                {pNum}
              </button>
            );
          })}

          {/* 다음 */}
          <IconButton
            label="다음 페이지"
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= totalPages}
          >
            <ChevronRight size={18} className="text-gray-800" aria-hidden />
          </IconButton>
        </section>
      )}
    </section>
  );
}
