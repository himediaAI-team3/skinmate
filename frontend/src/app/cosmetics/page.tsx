// src/app/cosmetics/page.tsx
'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { Search, SlidersHorizontal, Heart, Tag } from 'lucide-react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import type { CosmeticItem, CosmeticCategory } from '@/entities/cosmetics';
import { fetchCosmetics } from '@/features/cosmetics';
import { toggleProductLike } from '@/features/likes/api';

// 백엔드에서 데이터를 가져오므로 하드코딩된 데이터 제거

const CATEGORIES: ('전체' | CosmeticCategory)[] = [
  '전체',
  '로션/크림/올인원',
  '에센스/세럼',
  '스킨/토너',
  '아이크림',
  '미스트/오일',
  '패드',
];

type Category = typeof CATEGORIES[number];

export default function CosmeticsPage() {
  const [q, setQ] = useState('');
  const [cat, setCat] = useState<Category>('전체');
  const [sort, setSort] = useState<'rec' | 'price-asc' | 'price-desc' | 'rating' | 'likes'>('rec');
  const [liked, setLiked] = useState<Record<number, boolean>>({});
  const [likeCounts, setLikeCounts] = useState<Record<number, number>>({});
  
  // 백엔드 데이터 상태
  const [products, setProducts] = useState<CosmeticItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  // 페이지네이션
  const PAGE_SIZE = 10;
  const [page, setPage] = useState(1);

  // API 데이터 로딩
  useEffect(() => {
    async function loadCosmetics() {
      try {
        setLoading(true);
        setError(null);
        
        // TODO: 실제 로그인 사용자의 member_id를 가져오는 로직 필요
        const memberId = 1; // 임시 하드코딩
        
        const response = await fetchCosmetics({
          page: page,
          size: PAGE_SIZE,
          category: cat === '전체' ? undefined : cat,
          name: q.trim() || undefined,
          member_id: memberId, // 사용자 좋아요 상태 조회를 위해 추가
        });
        
        if (response.success && response.data) {
          setProducts(response.data.items || []);
          setTotalCount(response.data.total || 0);
          
          // 좋아요 수 및 좋아요 상태 초기화
          const initialLikeCounts: Record<number, number> = {};
          const initialLikedStates: Record<number, boolean> = {};
          
          response.data.items?.forEach(item => {
            initialLikeCounts[item.cosmetic_id] = item.like_count || 0;
            initialLikedStates[item.cosmetic_id] = item.is_liked || false; // 백엔드에서 받은 좋아요 상태
          });
          
          setLikeCounts(initialLikeCounts);
          setLiked(initialLikedStates); // 초기 좋아요 상태 설정
        }
      } catch (err) {
        console.error('화장품 목록 로딩 실패:', err);
        setError(err instanceof Error ? err.message : '데이터 로딩에 실패했습니다.');
      } finally {
        setLoading(false);
      }
    }
    
    loadCosmetics();
  }, [page, cat, q]); // 페이지, 카테고리, 검색어 변경시 재호출

  function IconButton({
    onClick,
    disabled,
    label,
    children,
  }: {
    onClick: () => void;
    disabled?: boolean;
    label: string;
    children: React.ReactNode;
  }) {
    return (
      <button
        aria-label={label}
        onClick={onClick}
        disabled={disabled}
        title={label}
        className={[
          // 크기/레이아웃
          'h-9 w-9 inline-flex items-center justify-center rounded-full',
          // 유리 버튼 + 경계
          'border border-white/60 bg-white/70 backdrop-blur',
          // 그림자/호버 인터랙션
          'shadow-sm hover:shadow transition',
          'hover:scale-[1.03] active:scale-[0.98]',
          // 포커스 링
          'focus:outline-none focus:ring-2 focus:ring-orange-200',
          // 비활성화
          'disabled:opacity-45 disabled:hover:scale-100 disabled:shadow-none',
        ].join(' ')}
      >
        {children}
        <span className="sr-only">{label}</span>
      </button>
    );
  }

  // 정렬 처리 (백엔드에서 가져온 데이터 기준)
  const sortedProducts = useMemo(() => {
    let list = [...products];

    switch (sort) {
      case 'price-asc':
        list = list.sort((a, b) => (a.price || 0) - (b.price || 0));
        break;
      case 'price-desc':
        list = list.sort((a, b) => (b.price || 0) - (a.price || 0));
        break;
      case 'rating':
        list = list.sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0));
        break;
      case 'likes':
        list = list.sort((a, b) => (likeCounts[b.cosmetic_id] ?? 0) - (likeCounts[a.cosmetic_id] ?? 0));
        break;
      default:
        break;
    }
    return list;
  }, [products, sort, likeCounts]);

  // 필터/검색/정렬 변경 시 1페이지로
  useEffect(() => {
    setPage(1);
  }, [q, cat, sort]);

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  // 숫자 페이지 버튼(최대 5개) 계산
  const visibleCount = 5;
  const startPage = Math.max(
    1,
    Math.min(page - Math.floor(visibleCount / 2), totalPages - visibleCount + 1)
  );
  const endPage = Math.min(totalPages, startPage + visibleCount - 1);
  const pages = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);

  // 현재 페이지의 제품들 (이미 백엔드에서 페이징 처리됨)
  const paged = sortedProducts;

  const toggleLike = async (cosmetic_id: number) => {
    try {
      // TODO: 실제 로그인 사용자의 member_id를 가져오는 로직 필요
      const memberId = 1; // 임시 하드코딩
      
      const result = await toggleProductLike(memberId, cosmetic_id);
      
      // 백엔드 응답으로 상태 업데이트
      setLiked((s) => ({ ...s, [cosmetic_id]: result.isLiked }));
      setLikeCounts((c) => ({ ...c, [cosmetic_id]: result.likeCount }));
      
      console.log(`✅ 좋아요 ${result.isLiked ? '추가' : '취소'} 완료! 총 ${result.likeCount}개`);
    } catch (error) {
      console.error('좋아요 토글 실패:', error);
      // TODO: 사용자에게 에러 메시지 표시
    }
  };

  return (
    <main className="px-5 pt-4">
      <section className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-extrabold tracking-tight text-gray-900">화장품</h1>
      </section>

      <section className="mb-5 space-y-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="브랜드, 제품명, 피부타입 검색"
              className="w-full rounded-xl border border-gray-200 bg-white py-2.5 pl-9 pr-3 text-sm outline-none placeholder:text-gray-400 focus:border-orange-300 focus:ring-2 focus:ring-orange-200"
            />
          </div>
          {/*
          <div className="relative">
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as any)}
              className="appearance-none rounded-xl border border-gray-200 bg-white py-2.5 pl-3 pr-9 text-sm focus:border-orange-300 focus:ring-2 focus:ring-orange-200"
              aria-label="정렬"
            >
              <option value="name-asc">이름순</option>
              <option value="likes">인기(좋아요)순</option>
              <option value="price-asc">가격낮은순</option>
              <option value="price-desc">가격높은순</option>
            </select>
            <SlidersHorizontal
              size={16}
              className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400"
            />
          </div>
           */}
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">
          {CATEGORIES.map((c) => {
            const active = c === cat;
            return (
              <button
                key={c}
                onClick={() => setCat(c)}
                className={`whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-semibold ring-1 transition
                  ${
                    active
                      ? 'bg-gray-900 text-white ring-gray-900'
                      : 'bg-white text-gray-700 ring-gray-200 hover:bg-gray-50'
                  }`}
              >
                {c}
              </button>
            );
          })}
        </div>
      </section>

      {/* 세로 리스트 (브랜드 오른쪽=태그, 우측=하트버튼 + 좋아요 수) */}
      {loading && (
        <section className="mt-4 text-center py-8">
          <div className="text-sm text-gray-500">로딩 중...</div>
        </section>
      )}
      
      {error && (
        <section className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-center">
          <div className="text-sm text-red-600">{error}</div>
        </section>
      )}
      
      {!loading && !error && paged.length === 0 && (
        <section className="mt-4 text-center py-8">
          <div className="text-sm text-gray-500">검색 결과가 없습니다.</div>
        </section>
      )}

      <section className="mt-2 space-y-3">
        {paged.map((p) => {
          const isLiked = !!liked[p.cosmetic_id];
          const likeNum = likeCounts[p.cosmetic_id] ?? p.like_count ?? 0;
        
          return (
            <article
              key={p.cosmetic_id}
              className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:shadow-md"
            >
              {/* 링크 컨테이너를 relative로 만들어 하트를 우측 상단에 배치 */}
              <Link href={`/cosmetics/${p.cosmetic_id}`} className="block relative">
                {/* 우측 최상단 하트 토글 버튼 */}
                <button
                  type="button"
                  aria-label={isLiked ? '좋아요 취소' : '좋아요'}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    toggleLike(p.cosmetic_id);
                  }}
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
                    <img 
                      src={p.image_url || 'https://placehold.co/640x640/E5E7EB/9CA3AF?text=No+Image'} 
                      alt={p.name || '제품 이미지'} 
                      className="w-full h-full object-cover" 
                    />
                  </div>
                
                  {/* 우측 텍스트/액션 */}
                  <div className="flex-1 min-w-0">
                    {/* 1행: 브랜드 + 카테고리 태그(브랜드 오른쪽) */}
                    <div className="flex items-center gap-2">
                      <p className="text-[11px] font-medium text-gray-500">{p.brand}</p>
                      <span className="inline-flex items-center gap-1 rounded-full bg-white/90 px-2 py-0.5 text-[10px] font-semibold text-gray-700 ring-1 ring-gray-200 backdrop-blur">
                        <Tag size={12} /> {p.category}
                      </span>
                    </div>
                
                    {/* 제품명 */}
                    <h3 className="mt-0.5 line-clamp-2 text-sm font-semibold text-gray-900">
                      {p.name}
                    </h3>
                
                    {/* 하단 행: (좌) 가격  |  (우) 좋아요 수(오른쪽 끝) */}
                    <div className="mt-2 flex items-center justify-between">
                      {/* 가격 */}
                      <span
                        className="text-[15px] font-extrabold tracking-tight text-gray-900"
                        style={{
                          background: 'linear-gradient(90deg, #111 0%, #444 100%)',
                          WebkitBackgroundClip: 'text',
                          WebkitTextFillColor: 'transparent',
                        }}
                      >
                        {Math.floor(p.price || 0).toLocaleString()}원
                      </span>
                      
                      {/* 좋아요 수 */}
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-gray-600">
                        <Heart size={12} className="stroke-pink-500 fill-pink-500" />
                        {likeNum.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            </article>
          );
        })}
      </section>


      {/* 페이지네이션 */}
      <section className="mt-4 flex items-center justify-center gap-2">
        {/* 이전 */}
        <IconButton
          label="이전 페이지"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1}
        >
          <ChevronLeft size={18} className="text-gray-800" aria-hidden />
        </IconButton>

        {/* 숫자 버튼들 */}
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
                  ? // 활성: 딥 그라데이션 텍스트 느낌
                    'border border-gray-900 bg-gray-900 text-white shadow-sm'
                  : // 비활성: 글래스 버튼
                    'border border-white/60 bg-white/70 backdrop-blur hover:shadow hover:scale-[1.02]',
              ].join(' ')}
            >
              {pNum}
            </button>
          );
        })}

        {/* 다음 */}
        <IconButton
          label="다음 페이지"
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page >= totalPages}
        >
          <ChevronRight size={18} className="text-gray-800" aria-hidden />
        </IconButton>
      </section>
    </main>
  );
}
