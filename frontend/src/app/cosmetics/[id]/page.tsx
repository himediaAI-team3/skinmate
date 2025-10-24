// src/app/cosmetics/[id]/page.tsx
'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Heart, Tag, ExternalLink, ChevronLeft } from 'lucide-react';

type ProductDetail = {
  id: number;
  brand: string;
  name: string;
  price: number;
  image: string;
  category: '클렌징' | '토너' | '크림' | '선크림' | '패드' | '앰플' | '젤';
  oliveyoungUrl: string;
  ingredients: string;
  description: string;
  likes: number;
  liked?: boolean;

  // 적합 피부/질병
  suitableSkinTypes?: string[] | string;  // 예: "건성, 민감성" 또는 ["건성","민감성"]
  suitableDiseases?: string[] | string;   // 예: "아토피, 건선" 또는 ["아토피","건선"]
};

const MOCK: ProductDetail[] = [
  {
    id: 1,
    brand: 'SKNM',
    name: '수딩 시카 크림',
    price: 19800,
    image: 'https://placehold.co/800x800/FFE0B2/FF6B6B?text=Soothing+Cica',
    category: '크림',
    oliveyoungUrl: 'https://www.oliveyoung.co.kr/',
    ingredients:
      '정제수, 병풀추출물, 글리세린, 부틸렌글라이콜, 메틸프로판다이올, 카보머, 트로메타민, 판테놀, 1,2-헥산다이올, 초피나무열매추출물',
    description:
    '[제품유형: 크림][피부타입: 건성, 민감성][관련 피부질환: 아토피, 건선][주요 효능: 보습, 피부장벽강화, 진정, 수분공급][케어 증상: 건조, 인설, 가려움, 피부장벽손상, 당김][핵심 성분: 미리스토일/팔미토일옥소스테아라마이드/아라카마이드엠이에이, 피토스테롤, 소듐하이알루로네이트, 비사보롤]아토피와 건선으로 인한 손상된 피부 장벽을 복원하고 극건조한 피부에 집중 보습을 제공하는 데 도움을 줍니다. 세라마이드 유사 성분과 피토스테롤이 피부 장벽을 강화하고 수분 손실을 방지하며, 히알루론산이 깊은 수분 공급을 통해 건조와 인설을 완화합니다. 비사보롤 성분이 민감해진 피부를 진정시키고 가려움을 달래주어 예민한 피부에도 안전하게 사용할 수 있습니다.',
    likes: 124,
    liked: false,
    suitableSkinTypes: '건성, 민감성',
    suitableDiseases: '아토피, 건선',
  },
  {
    id: 2,
    brand: 'Rayderm',
    name: '오일프리 선스크린 SPF50+',
    price: 15800,
    image: 'https://placehold.co/800x800/B2DFDB/00796B?text=Oil-free+Sun',
    category: '선크림',
    oliveyoungUrl: 'https://www.oliveyoung.co.kr/',
    ingredients:
      '정제수, 에칠헥실메톡시신나메이트, 티타늄디옥사이드, 글리세린, 사이클로펜타실록세인, 트리에탄올아민, 디메치콘',
    description:
      '[제품유형: 크림][피부타입: 건성, 민감성][관련 피부질환: 아토피, 건선][주요 효능: 보습, 피부장벽강화, 진정, 수분공급][케어 증상: 건조, 인설, 가려움, 피부장벽손상, 당김][핵심 성분: 미리스토일/팔미토일옥소스테아라마이드/아라카마이드엠이에이, 피토스테롤, 소듐하이알루로네이트, 비사보롤]아토피와 건선으로 인한 손상된 피부 장벽을 복원하고 극건조한 피부에 집중 보습을 제공하는 데 도움을 줍니다. 세라마이드 유사 성분과 피토스테롤이 피부 장벽을 강화하고 수분 손실을 방지하며, 히알루론산이 깊은 수분 공급을 통해 건조와 인설을 완화합니다. 비사보롤 성분이 민감해진 피부를 진정시키고 가려움을 달래주어 예민한 피부에도 안전하게 사용할 수 있습니다.',
    likes: 231,
    suitableSkinTypes: ['건성', '민감성'],
    suitableDiseases: ['아토피', '건선'],
  },
  {
    id: 3,
    brand: 'HyaLab',
    name: '히알루론산 토너 500ml',
    price: 12900,
    image: 'https://placehold.co/800x800/E1BEE7/6A1B9A?text=Hyaluronic+Toner',
    category: '토너',
    oliveyoungUrl: 'https://www.oliveyoung.co.kr/',
    ingredients:
      '정제수, 글리세린, 부틸렌글라이콜, 소듐하이알루로네이트, 베타인, 판테놀, 알란토인, 하이드록시에틸셀룰로오스',
    description:
      '[제품유형: 크림][피부타입: 건성, 민감성][관련 피부질환: 아토피, 건선][주요 효능: 보습, 피부장벽강화, 진정, 수분공급][케어 증상: 건조, 인설, 가려움, 피부장벽손상, 당김][핵심 성분: 미리스토일/팔미토일옥소스테아라마이드/아라카마이드엠이에이, 피토스테롤, 소듐하이알루로네이트, 비사보롤]아토피와 건선으로 인한 손상된 피부 장벽을 복원하고 극건조한 피부에 집중 보습을 제공하는 데 도움을 줍니다. 세라마이드 유사 성분과 피토스테롤이 피부 장벽을 강화하고 수분 손실을 방지하며, 히알루론산이 깊은 수분 공급을 통해 건조와 인설을 완화합니다. 비사보롤 성분이 민감해진 피부를 진정시키고 가려움을 달래주어 예민한 피부에도 안전하게 사용할 수 있습니다.',
    likes: 98,
    suitableSkinTypes: '모든 피부',
    suitableDiseases: '',
  },
];

export default function CosmeticDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();

  const product = useMemo(() => {
    const idNum = Number(params.id);
    return MOCK.find((p) => p.id === idNum) || null;
  }, [params.id]);

  const [liked, setLiked] = useState<boolean>(!!product?.liked);
  const [likeCount, setLikeCount] = useState<number>(product?.likes ?? 0);

  if (!product) {
    return (
      <main className="px-5 pt-4 pb-6">
        <header className="relative flex h-16 items-center px-4">
          <button
            onClick={() => router.back()}
            aria-label="뒤로가기"
            className="absolute left-4 inline-flex h-9 w-9 items-center justify-center rounded-full border hover:bg-gray-50 transition"
          >
            <ChevronLeft size={18} />
          </button>
          <h1 className="mx-auto text-xl font-bold text-gray-800">제품 상세</h1>
          <div className="absolute right-4 h-9 w-9" aria-hidden />
        </header>

        <div className="mt-6 rounded-2xl border p-6 text-center text-sm text-gray-600">
          존재하지 않는 상품입니다.
        </div>
      </main>
    );
  }

  const onToggleLike = () => {
    const next = !liked;
    setLiked(next);
    setLikeCount((c) => c + (next ? 1 : -1));
    // TODO: 서버 반영
  };

  // 설명 전처리: \n, <br>, ][ → 개행
  const prettyDescription = useMemo(() => {
    return (product.description ?? '')
      .replace(/\\n/g, '\n')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/]\s*\[/g, ']\n[');
  }, [product.description]);

  // "건성, 민감성" 같은 문자열도 배열로 변환
  const toList = (v?: string[] | string) =>
    Array.isArray(v)
      ? v
      : (v ?? '')
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean);

  const skinChips = toList(product.suitableSkinTypes);
  const diseaseChips = toList(product.suitableDiseases);

  const TAB_H = 56;
  const tabSpacerStyle = { height: `calc(${TAB_H}px + env(safe-area-inset-bottom))` };

  return (
    <main className="px-5 pt-0 pb-2">
      {/* 헤더: 업로드 페이지와 유사한 뒤로가기 버튼 스타일 */}
      <section className="mb-3">
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
            상품 상세
          </h1>
        </header>
      </section>

      {/* 사진 */}
      <section className="overflow-hidden rounded-2xl border bg-white">
        <div className="relative aspect-square w-full">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={product.image} alt={product.name} className="h-full w-full object-cover" />
        </div>
      </section>

      {/* 기본 정보 */}
      <section className="mt-4 space-y-2 rounded-2xl border bg-white p-4">
        <p className="text-xs font-medium text-gray-500">{product.brand}</p>
        <h1 className="text-lg font-extrabold tracking-tight text-gray-900">{product.name}</h1>

        {/* 카테고리 배지 */}
        <div className="mt-1">
          <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-[11px] font-semibold text-gray-700">
            <Tag size={12} /> {product.category}
          </span>
        </div>

        {/* 적합 피부/질병 섹션 */}
        {(skinChips.length > 0 || diseaseChips.length > 0) && (
          <div className="mt-3 rounded-xl border bg-gray-50 p-3">
            <div className="flex items-start gap-2">
              <span className="mt-1 text-[11px] font-bold text-gray-600 w-16 shrink-0">피부타입</span>
              <div className="flex flex-wrap gap-1.5">
                {skinChips.length > 0 ? (
                  skinChips.map((s) => (
                    <span
                      key={s}
                      className="rounded-full bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700 ring-1 ring-blue-200"
                    >
                      #{s}
                    </span>
                  ))
                ) : (
                  <span className="text-[11px] text-gray-400">정보 없음</span>
                )}
              </div>
            </div>

            <div className="mt-2 flex items-start gap-2">
              <span className="mt-1 text-[11px] font-bold text-gray-600 w-16 shrink-0">적합 질병</span>
              <div className="flex flex-wrap gap-1.5">
                {diseaseChips.length > 0 ? (
                  diseaseChips.map((d) => (
                    <span
                      key={d}
                      className="rounded-full bg-rose-50 px-2 py-0.5 text-[11px] font-semibold text-rose-700 ring-1 ring-rose-200"
                    >
                      #{d}
                    </span>
                  ))
                ) : (
                  <span className="text-[11px] text-gray-400">정보 없음</span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 가격 & 좋아요 */}
        <div className="mt-3 flex items-center justify-between">
          <span
            className="text-[17px] font-extrabold tracking-tight text-gray-900"
            style={{
              background: 'linear-gradient(90deg, #111 0%, #444 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            {product.price.toLocaleString()}원
          </span>

          <button
            onClick={onToggleLike}
            className="inline-flex items-center gap-1 rounded-full border px-3 py-1.5 text-xs font-semibold text-gray-700 hover:bg-gray-50"
            aria-label="좋아요 토글"
          >
            <Heart size={14} className={liked ? 'fill-pink-500 stroke-pink-500' : 'stroke-gray-700'} />
            {likeCount.toLocaleString()}
          </button>
        </div>
      </section>

      {/* 구매/올리브영 링크 */}
      <section className="mt-3">
        <Link
          href={product.oliveyoungUrl}
          target="_blank"
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gray-900 py-3 text-sm font-bold text-white hover:opacity-95"
        >
          올리브영 상세페이지 열기
          <ExternalLink size={16} />
        </Link>
      </section>

      {/* 제품설명 */}
      <section className="mt-4 rounded-2xl border bg-white p-4">
        <h2 className="text-sm font-bold text-gray-900">제품설명</h2>
        <p className="text-sm leading-relaxed text-gray-700 whitespace-pre-line">
          {prettyDescription}
        </p>
      </section>

      {/* 전성분 */}
      <section className="mt-3 rounded-2xl border bg-white p-4">
        <h2 className="text-sm font-bold text-gray-900">전성분</h2>
        <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-gray-700">
          {product.ingredients}
        </p>
      </section>

      {/* 탭바 간격 */}
      <div aria-hidden style={tabSpacerStyle} />
    </main>
  );
}
