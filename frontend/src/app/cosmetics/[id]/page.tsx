// src/app/cosmetics/[id]/page.tsx
'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Heart, Tag, ExternalLink, ChevronLeft } from 'lucide-react';
import type { CosmeticDetail } from '@/entities/cosmetics';
import { fetchCosmeticDetail } from '@/features/cosmetics';
import { toggleProductLike } from '@/features/likes/api';

export default function CosmeticDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();

  // 백엔드 데이터 상태
  const [product, setProduct] = useState<CosmeticDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [liked, setLiked] = useState<boolean>(false);
  const [likeCount, setLikeCount] = useState<number>(0);
  const [activeTab, setActiveTab] = useState<'info' | 'effect' | 'ingredient'>('info');

  // API 데이터 로딩
  useEffect(() => {
    async function loadProduct() {
      try {
        setLoading(true);
        setError(null);
        
        const cosmetic_id = Number(params.id);
        if (isNaN(cosmetic_id)) {
          throw new Error('잘못된 제품 ID입니다.');
        }
        
        // TODO: member_id를 실제 로그인 사용자 ID로 교체
        const response = await fetchCosmeticDetail(cosmetic_id);
        
        if (response.success && response.data) {
          setProduct(response.data);
          setLiked(response.data.is_liked || false);
          setLikeCount(response.data.like_count || 0);
        } else {
          throw new Error(response.message || '제품 정보를 찾을 수 없습니다.');
        }
      } catch (err) {
        console.error('제품 상세 로딩 실패:', err);
        setError(err instanceof Error ? err.message : '데이터 로딩에 실패했습니다.');
      } finally {
        setLoading(false);
      }
    }
    
    loadProduct();
  }, [params.id]);

  // 로딩 상태
  if (loading) {
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

        <div className="mt-6 rounded-2xl border p-6 text-center text-sm text-gray-500">
          로딩 중...
        </div>
      </main>
    );
  }

  // 에러 상태
  if (error || !product) {
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

        <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-6 text-center text-sm text-red-600">
          {error || '제품 정보를 찾을 수 없습니다.'}
        </div>
      </main>
    );
  }

  const onToggleLike = async () => {
    if (!product) return;
    
    try {
      // TODO: 실제 로그인 사용자의 member_id를 가져오는 로직 필요
      const memberId = 1; // 임시 하드코딩
      
      const result = await toggleProductLike(memberId, product.cosmetic_id);
      
      // 백엔드 응답으로 상태 업데이트
      setLiked(result.isLiked);
      setLikeCount(result.likeCount);
      
      console.log(`✅ 좋아요 ${result.isLiked ? '추가' : '취소'} 완료! 총 ${result.likeCount}개`);
    } catch (error) {
      console.error('좋아요 토글 실패:', error);
      // TODO: 사용자에게 에러 메시지 표시
    }
  };

  // 효능/증상/성분을 배열로 변환하는 함수
  const toChipList = (value?: string) => 
    (value || '').split(',').map(s => s.trim()).filter(Boolean);

  // "건성, 민감성" 같은 문자열도 배열로 변환
  const toList = (v?: string[] | string) =>
    Array.isArray(v)
      ? v
      : (v ?? '')
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean);

  const skinChips = toList(product.skin_type);
  const diseaseChips = toList(product.skin_disease);

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
          <img 
            src={product.image_url || 'https://placehold.co/800x800/E5E7EB/9CA3AF?text=No+Image'} 
            alt={product.name || '제품 이미지'} 
            className="h-full w-full object-cover" 
          />
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
            {Math.floor(product.price || 0).toLocaleString()}원
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
        {product.buy_url && (
          <Link
            href={product.buy_url}
            target="_blank"
            className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gray-900 py-3 text-sm font-bold text-white hover:opacity-95"
          >
            구매 사이트 열기
            <ExternalLink size={16} />
          </Link>
        )}
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
                {product.description || '설명이 없습니다.'}
              </p>
            </div>
            
            {product.short_description && (
              <div>
                <h3 className="text-sm font-bold text-gray-900 mb-2">한줄 설명</h3>
                <p className="text-sm leading-relaxed text-gray-700">
                  {product.short_description}
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'effect' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">주요 효능</h3>
              <div className="flex flex-wrap gap-2">
                {toChipList(product.main_effect).length > 0 ? (
                  toChipList(product.main_effect).map((effect, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700 ring-1 ring-green-200"
                    >
                      {effect}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-gray-400">정보 없음</span>
                )}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">케어 증상</h3>
              <div className="flex flex-wrap gap-2">
                {toChipList(product.care_symptom).length > 0 ? (
                  toChipList(product.care_symptom).map((symptom, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center rounded-full bg-orange-50 px-3 py-1 text-xs font-medium text-orange-700 ring-1 ring-orange-200"
                    >
                      {symptom}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-gray-400">정보 없음</span>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ingredient' && (
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">핵심 성분</h3>
              <div className="space-y-2">
                {toChipList(product.key_ingredient).length > 0 ? (
                  toChipList(product.key_ingredient).map((ingredient, idx) => (
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
                  ))
                ) : (
                  <div className="text-xs text-gray-400 p-3">정보 없음</div>
                )}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-gray-900 mb-2">전체 성분</h3>
              <p className="text-xs leading-relaxed text-gray-600 bg-gray-50 rounded-lg p-3">
                {product.ingredients || '성분 정보가 없습니다.'}
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