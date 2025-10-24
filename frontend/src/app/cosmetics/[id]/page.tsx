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
  description: string; // 제품 상세설명
  main_effect: string; // 주요 효능
  care_symptom: string; // 케어 증상
  key_ingredient: string; // 핵심 성분
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
    description: '아토피와 건선으로 인한 손상된 피부 장벽을 복원하고 극건조한 피부에 집중 보습을 제공하는 데 도움을 줍니다. 세라마이드 유사 성분과 피토스테롤이 피부 장벽을 강화하고 수분 손실을 방지하며, 히알루론산이 깊은 수분 공급을 통해 건조와 인설을 완화합니다. 비사보롤 성분이 민감해진 피부를 진정시키고 가려움을 달래주어 예민한 피부에도 안전하게 사용할 수 있습니다.',
    main_effect: '보습, 피부장벽강화, 진정, 수분공급',
    care_symptom: '건조, 인설, 가려움, 피부장벽손상, 당김',
    key_ingredient: '미리스토일/팔미토일옥소스테아라마이드/아라카마이드엠이에이, 피토스테롤, 소듐하이알루로네이트, 비사보롤',
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
    description: '가벼운 텍스처로 끈적임 없이 발리며 강력한 자외선 차단 효과를 제공합니다. 오일프리 포뮬러로 지성 피부에도 부담 없이 사용할 수 있으며, 백탁 현상 없이 자연스러운 마무리감을 연출합니다.',
    main_effect: '자외선 차단, 피부 보호, 수분 공급',
    care_symptom: '자외선 손상, 건조함, 피부 노화',
    key_ingredient: '에칠헥실메톡시신나메이트, 티타늄디옥사이드, 글리세린',
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
    description: '고농도 히알루론산이 함유된 대용량 토너로 깊은 수분 공급과 피부 진정 효과를 제공합니다. 끈적임 없는 수분감으로 모든 피부 타입에 적합하며, 매일 사용해도 부담 없는 순한 성분으로 구성되었습니다.',
    main_effect: '수분 공급, 피부 진정, 각질 정리',
    care_symptom: '건조함, 거칠음, 수분 부족',
    key_ingredient: '소듐하이알루로네이트, 베타인, 판테놀, 알란토인',
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
  const [activeTab, setActiveTab] = useState<'info' | 'effect' | 'ingredient'>('info');

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

  // 효능/증상/성분을 배열로 변환하는 함수
  const toChipList = (value: string) => 
    value.split(',').map(s => s.trim()).filter(Boolean);

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
              <span className="mt-1 text-[11px] font-bold text-gray-600 w-16 shrink-0">관련질환</span>
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

      {/* 탭 네비게이션 */}
      <section className="mt-4">
        <div className="flex rounded-2xl border bg-white p-1">
          <button
            onClick={() => setActiveTab('info')}
            className={`flex-1 rounded-xl py-2 px-3 text-sm font-semibold transition-all ${
              activeTab === 'info'
                ? 'bg-gray-900 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            기본정보
          </button>
          <button
            onClick={() => setActiveTab('effect')}
            className={`flex-1 rounded-xl py-2 px-3 text-sm font-semibold transition-all ${
              activeTab === 'effect'
                ? 'bg-gray-900 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            효능정보
          </button>
          <button
            onClick={() => setActiveTab('ingredient')}
            className={`flex-1 rounded-xl py-2 px-3 text-sm font-semibold transition-all ${
              activeTab === 'ingredient'
                ? 'bg-gray-900 text-white shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            성분정보
          </button>
        </div>
      </section>

      {/* 탭 컨텐츠 */}
      <section className="mt-3 rounded-2xl border bg-white p-4">
        {activeTab === 'info' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">제품 설명</h3>
              <p className="text-sm leading-relaxed text-gray-700">
                {product.description}
              </p>
            </div>
          </div>
        )}

        {activeTab === 'effect' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">주요 효능</h3>
              <div className="flex flex-wrap gap-2">
                {toChipList(product.main_effect).map((effect, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700 ring-1 ring-green-200"
                  >
                    {effect}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">케어 증상</h3>
              <div className="flex flex-wrap gap-2">
                {toChipList(product.care_symptom).map((symptom, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center rounded-full bg-orange-50 px-3 py-1 text-xs font-medium text-orange-700 ring-1 ring-orange-200"
                  >
                    {symptom}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ingredient' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">핵심 성분</h3>
              <div className="space-y-2">
                {toChipList(product.key_ingredient).map((ingredient, idx) => (
                  <div
                    key={idx}
                    className="flex items-start gap-2 rounded-lg bg-blue-50 p-3"
                  >
                    <span className="mt-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-600">
                      {idx + 1}
                    </span>
                    <span className="text-sm font-medium text-blue-900">
                      {ingredient}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">전체 성분</h3>
              <p className="text-xs leading-relaxed text-gray-600 bg-gray-50 rounded-lg p-3">
                {product.ingredients}
              </p>
            </div>
          </div>
        )}
      </section>

      {/* 탭바 간격 */}
      <div aria-hidden style={tabSpacerStyle} />
    </main>
  );
}
