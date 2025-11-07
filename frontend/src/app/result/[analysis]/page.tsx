// /src/app/result/[analysis]/page.tsx
'use client';

import { useEffect, useMemo, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ExternalLink } from 'lucide-react';
import { analysisApi, getProductImageSrc } from '@/features/loading';
import type { SkinAnalysisOutputT, SkinAnalysisDataT } from '@/entities/loading';

export default function ResultPage() {
  const router = useRouter();
  const params = useParams();
  const analysisId = useMemo(() => {
    const v = (params as any)?.analysis;
    const n = Array.isArray(v) ? Number(v[0]) : Number(v);
    return Number.isFinite(n) ? n : NaN;
  }, [params]);

  const [data, setData] = useState<SkinAnalysisDataT | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imgErr, setImgErr] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 1) 결과 데이터 로드
  useEffect(() => {
    const boot = async () => {
      try {
        if (!Number.isFinite(analysisId)) throw new Error('유효하지 않은 분석 ID입니다.');

        // 세션 캐시 우선 사용
        const raw = sessionStorage.getItem('skinMateAnalysis');
        if (raw) {
          try {
            const parsed: SkinAnalysisOutputT = JSON.parse(raw);
            if (parsed?.data?.analysis_id === analysisId) {
              setData(parsed.data);
              sessionStorage.removeItem('skinMateAnalysis');
              return;
            }
          } catch {
            // 파싱 실패 시 무시하고 서버 조회로 진행
          }
        }

        // 서버 조회
        const res = await analysisApi.get(analysisId);
        if (!res.success) throw new Error(res.message || '결과 조회 실패');
        setData(res.data);
      } catch (e: any) {
        setError(e?.message ?? '결과를 불러오는 중 오류가 발생했습니다.');
      }
    };
    boot();
  }, [analysisId]);

  // 2) 원본 업로드 이미지 Blob → objectURL 생성 (Authorization 헤더 필요)
  useEffect(() => {
    let alive = true;
    let objectUrl: string | null = null;

    async function loadImage(fileId: number) {
      try {
        const url = await analysisApi.getFileObjectUrl(fileId);
        if (!alive) return;
        objectUrl = url;
        setImageUrl(url);
      } catch (e: any) {
        setImgErr(e?.message ?? '이미지를 불러오지 못했습니다.');
        setImageUrl(null);
      }
    }

    if (data?.file_id) {
      loadImage(data.file_id);
    } else {
      setImageUrl(null);
      setImgErr(null);
    }

    return () => {
      alive = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [data?.file_id]);

  // 버튼 컴포넌트
  function GlassActionButton({
    href,
    children,
    label,
    disabled,
    variant = 'glass', // 'primary' | 'outline' | 'glass'
  }: {
    href?: string;
    children: React.ReactNode;
    label?: string;
    disabled?: boolean;
    variant?: 'primary' | 'outline' | 'glass';
  }) {
    let isValid = true;
    try {
      if (!href) throw new Error('no href');
      new URL(href);
    } catch {
      isValid = false;
    }
    const isDisabled = disabled || !isValid;

    const base =
      'group relative inline-flex w-full items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-bold transition will-change-transform focus:outline-none focus:ring-2 focus:ring-orange-200 hover:scale-[1.01] active:scale-[0.99]';

    const variantClass =
      variant === 'primary'
        ? [
            'text-white shadow-sm hover:shadow',
            'bg-gradient-to-r from-orange-500 to-pink-500',
            'after:absolute after:inset-0 after:rounded-2xl after:pointer-events-none',
            'after:[background:linear-gradient(180deg,rgba(255,255,255,.35),rgba(255,255,255,0))]',
          ].join(' ')
        : variant === 'outline'
        ? [
            'bg-white/30 backdrop-blur text-gray-900',
            'shadow-sm hover:shadow',
            'before:absolute before:inset-0 before:rounded-2xl before:p-[1px] before:[background:linear-gradient(135deg,#f59e0b,#ec4899)]',
            'after:absolute after:inset-[1px] after:rounded-2xl after:bg-white/80',
            'relative overflow-hidden',
          ].join(' ')
        : [
            'text-gray-900 shadow-sm hover:shadow',
            'bg-white/80 backdrop-blur border border-gray-300',
            'relative overflow-hidden',
            'before:absolute before:inset-0 before:rounded-2xl before:pointer-events-none',
            'before:[background:linear-gradient(135deg,rgba(255,255,255,.9),rgba(255,255,255,.5))]',
          ].join(' ');

    return (
      <a
        href={isValid ? href : undefined}
        target="_blank"
        rel="noopener noreferrer nofollow"
        aria-label={label || '구매하러 가기'}
        title={label || '구매하러 가기'}
        onClick={(e) => isDisabled && e.preventDefault()}
        className={[base, variantClass, isDisabled ? 'opacity-50 pointer-events-none' : ''].join(' ')}
      >
        <span className={variant === 'primary' ? 'relative' : 'relative bg-clip-text'}>
          {children}
        </span>
        <ExternalLink
          size={16}
          className={
            variant === 'primary'
              ? 'relative opacity-95'
              : 'relative text-gray-800 transition-transform group-hover:translate-x-[1px]'
          }
          aria-hidden
        />
      </a>
    );
  }

  // 에러/로딩 뷰
  if (error) {
    return (
      <div className="max-w-md mx-auto min-h-screen p-6 bg-white">
        <header className="pt-4 pb-8">
          <h1 className="text-3xl font-bold text-gray-800">AI 분석 결과</h1>
        </header>
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-2xl p-4">
          <p className="font-semibold">결과 조회 실패</p>
          <p className="mt-1">{error}</p>
        </div>
        <div className="pt-10 pb-6">
          <a
            href="/upload"
            className="block w-full bg-orange-500 text-white text-center font-bold py-4 px-8 rounded-full shadow-lg hover:bg-orange-600 transition-colors"
          >
            다시 업로드하기
          </a>
        </div>
      </div>
    );
  }
  if (!data) {
    return (
      <div className="max-w-md mx-auto min-h-screen p-6 bg-white">
        <header className="pt-4 pb-8">
          <h1 className="text-3xl font-bold text-gray-800">AI 분석 결과</h1>
        </header>
        <p className="text-gray-500">결과를 불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto min-h-screen p-6 bg-white">
      <header className="pt-4 pb-8">
        <h1 className="text-3xl font-bold text-gray-800">AI 분석 결과</h1>
      </header>

      {/* 원본 업로드 이미지 (JWT 필요 → Blob → objectURL) */}
      <section>
        <h2 className="text-xl font-bold text-gray-800">등록된 이미지</h2>
        <div className="mt-4 w-full aspect-square max-h-[520px] bg-gray-100 rounded-2xl overflow-hidden shadow-sm flex items-center justify-center">
          {imageUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={imageUrl} alt="Uploaded skin" className="w-full h-full object-cover" />
          ) : imgErr ? (
            <p className="text-gray-500">{imgErr}</p>
          ) : (
            <p className="text-gray-500">이미지 로딩 중…</p>
          )}
        </div>
      </section>

      {/* 분석 결과 */}
      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-800">피부 진단</h2>
        <div className="bg-orange-50 p-6 rounded-2xl mt-4">
          <h3 className="text-lg font-bold text-orange-600">{data.disease_name}</h3>
          <p className="text-gray-700 mt-2 whitespace-pre-wrap">{data.diagnosis_summary}</p>
        </div>
      </section>

      {/* 추천 제품 */}
      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-800">추천 제품</h2>
        <div className="mt-4 space-y-4">
          {data.products.map((p, idx) => {
            const pid = (p as any)?.cosmetic_id as number | undefined;
            const detailHref =
              typeof pid === 'number' && !Number.isNaN(pid) ? `/cosmetics/${pid}` : undefined;
            const productImg = getProductImageSrc((p as any)?.file_path ?? null);

            const CardImage = (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={productImg}
                alt={p.name}
                className="w-20 h-20 rounded-lg object-cover flex-shrink-0"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src = '/placeholder.png';
                }}
              />
            );

            return (
              <div key={idx} className="bg-gray-50 p-4 rounded-2xl">
                <div className="flex items-start gap-4">
                  {detailHref ? (
                    <a href={detailHref} aria-label={`${p.name} 상세 보기`}>
                      {CardImage}
                    </a>
                  ) : (
                    CardImage
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-500">{p.brand}</p>
                    {detailHref ? (
                      <a href={detailHref} className="font-semibold text-gray-800 mt-1 hover:underline line-clamp-2">
                        {p.name}
                      </a>
                    ) : (
                      <p className="font-semibold text-gray-800 mt-1 line-clamp-2">{p.name}</p>
                    )}
                    <p className="font-bold text-orange-600 mt-2">
                      {Number(p.price).toLocaleString()}원
                    </p>
                  </div>
                </div>

                <div className="mt-3 bg-white p-3 rounded-lg">
                  <p className="text-xs font-bold text-gray-600">추천 이유</p>
                  <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">{p.reason}</p>
                  <GlassActionButton href={(p as any)?.buy_url} label="구매하러 가기" variant="glass">
                    구매하러 가기
                  </GlassActionButton>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <div className="pt-10 pb-6">
        <a
          href="/"
          className="block w-full bg-orange-500 text-white text-center font-bold py-4 px-8 rounded-full shadow-lg hover:bg-orange-600 transition-colors"
        >
          처음으로 돌아가기
        </a>
      </div>
    </div>
  );
}
