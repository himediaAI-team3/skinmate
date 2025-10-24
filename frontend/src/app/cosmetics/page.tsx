// src/app/cosmetics/page.tsx
'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { Search, SlidersHorizontal, Heart, Tag } from 'lucide-react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

type Product = {
  id: number;
  brand: string;
  name: string;
  price: number;
  image: string;
  category:
    | '로션/크림/올인원'
    | '에센스/세럼'
    | '스킨/토너'
    | '아이크림'
    | '미스트/오일'
    | '패드';
  tags?: string[];
  rating?: number;
  likes: number;
};

const ALL_PRODUCTS: Product[] = [
  { id: 1, brand: 'SKNM',    name: '수딩 시카 크림',            price: 19800, image: 'https://placehold.co/640x640/FFE0B2/FF6B6B?text=Soothing+Cica', category: '로션/크림/올인원', tags: ['민감', '진정'],   rating: 4.6, likes: 124 },
  { id: 2, brand: 'Rayderm', name: '오일프리 선스크린 SPF50+', price: 15800, image: 'https://placehold.co/640x640/B2DFDB/00796B?text=Oil-free+Sun',  category: '로션/크림/올인원', tags: ['지성', '자외선'], rating: 4.8, likes: 231 },
  { id: 3, brand: 'HyaLab',  name: '히알루론산 토너 500ml',     price: 12900, image: 'https://placehold.co/640x640/E1BEE7/6A1B9A?text=Hyaluronic+Toner', category: '스킨/토너',      tags: ['수분', '모든피부'], rating: 4.4, likes: 98  },
  { id: 4, brand: 'Clearup', name: '트러블 패드 70매',           price: 17900, image: 'https://placehold.co/640x640/F8BBD0/C2185B?text=Acne+Pad',       category: '패드',             tags: ['지성', '각질'],   rating: 4.2, likes: 67  },
  { id: 5, brand: 'Calmia',  name: '시카 수분 앰플',             price: 24900, image: 'https://placehold.co/640x640/FFF3E0/FB8C00?text=Cica+Ampoule',   category: '미스트/오일',      tags: ['민감', '수분'],   rating: 4.7, likes: 174 },
  { id: 6, brand: 'Lite',    name: '라이트 젤 크림',             price: 15400, image: 'https://placehold.co/640x640/E0F7FA/006064?text=Gel+Cream',      category: '아이크림',         tags: ['지성', '가벼움'], rating: 4.1, likes: 52  },
];

const CATEGORIES = [
  '전체',
  '로션/크림/올인원',
  '에센스/세럼',
  '스킨/토너',
  '아이크림',
  '미스트/오일',
  '패드',
] as const;

type Category = typeof CATEGORIES[number];

export default function CosmeticsPage() {
  const [q, setQ] = useState('');
  const [cat, setCat] = useState<Category>('전체');
  const [sort, setSort] = useState<'rec' | 'price-asc' | 'price-desc' | 'rating' | 'likes'>('rec');
  const [liked, setLiked] = useState<Record<number, boolean>>({});
  const [likeCounts, setLikeCounts] = useState<Record<number, number>>(
    Object.fromEntries(ALL_PRODUCTS.map((p) => [p.id, p.likes]))
  );

  // 페이지네이션
  const PAGE_SIZE = 10;
  const [page, setPage] = useState(1);

  // 테스트용 고정 페이지네이션 스위치
  const TEST_PAGINATION = true;
  const TEST_PAGE_COUNT = 5;

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

  // 검색/필터/정렬 결과
  const filtered = useMemo(() => {
    let list = ALL_PRODUCTS.filter(
      (p) =>
        (cat === '전체' || p.category === cat) &&
        (q.trim() === '' ||
          p.name.toLowerCase().includes(q.toLowerCase()) ||
          p.brand.toLowerCase().includes(q.toLowerCase()))
    );

    switch (sort) {
      case 'price-asc':
        list = list.slice().sort((a, b) => a.price - b.price);
        break;
      case 'price-desc':
        list = list.slice().sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        list = list.slice().sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0));
        break;
      case 'likes':
        list = list.slice().sort((a, b) => (likeCounts[b.id] ?? 0) - (likeCounts[a.id] ?? 0));
        break;
      default:
        break;
    }
    return list;
  }, [q, cat, sort, likeCounts]);

  // 필터/검색/정렬 변경 시 1페이지로
  useEffect(() => {
    setPage(1);
  }, [q, cat, sort]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const maxPage = TEST_PAGINATION ? TEST_PAGE_COUNT : totalPages;

  // 숫자 페이지 버튼(최대 5개) 계산
  const visibleCount = 5;
  let pages: number[];

  if (TEST_PAGINATION) {
    // ✅ 항상 1~5 고정 노출
    pages = Array.from({ length: TEST_PAGE_COUNT }, (_, i) => i + 1);
  } else {
    const startPage = Math.max(
      1,
      Math.min(page - Math.floor(visibleCount / 2), totalPages - visibleCount + 1)
    );
    const endPage = Math.min(totalPages, startPage + visibleCount - 1);
    pages = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
  }

  const start = (page - 1) * PAGE_SIZE;
  const paged = filtered.slice(start, start + PAGE_SIZE);

  const toggleLike = (id: number) => {
    setLiked((s) => {
      const next = !s[id];
      setLikeCounts((c) => ({
        ...c,
        [id]: (c[id] ?? 0) + (next ? 1 : -1),
      }));
      return { ...s, [id]: next };
    });
  };

  return (
    <main className="px-5 pt-4">
      <section className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-extrabold tracking-tight text-gray-900">상점</h1>
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
      <section className="mt-2 space-y-3">
        {paged.map((p) => {
          const isLiked = !!liked[p.id];
          const likeNum = likeCounts[p.id] ?? p.likes;
        
          return (
            <article
              key={p.id}
              className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:shadow-md"
            >
              {/* 링크 컨테이너를 relative로 만들어 하트를 우측 상단에 배치 */}
              <Link href={`/cosmetics/${p.id}`} className="block relative">
                {/* 우측 최상단 하트 토글 버튼 */}
                <button
                  type="button"
                  aria-label={isLiked ? '좋아요 취소' : '좋아요'}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    toggleLike(p.id);
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
                    <img src={p.image} alt={p.name} className="w-full h-full object-cover" />
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
                        {p.price.toLocaleString()}원
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
          onClick={() => setPage((p) => Math.min(maxPage, p + 1))}
          disabled={page >= maxPage}
        >
          <ChevronRight size={18} className="text-gray-800" aria-hidden />
        </IconButton>
      </section>
    </main>
  );
}
