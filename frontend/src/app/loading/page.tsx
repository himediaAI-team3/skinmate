// /src/app/loading/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { analysisApi } from '@/features/loading';
import type { SkinAnalysisOutputT } from '@/entities/loading';
import { getAccessToken } from '@/features/auth';

// dataURL → File 변환
function dataURLtoFile(dataURL: string, fileName: string) {
  const [meta, base64] = dataURL.split(',');
  const mime = (meta.match(/data:(.*);base64/)?.[1]) || 'image/jpeg';
  const bytes = atob(base64);
  const arr = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
  return new File([arr], fileName || 'upload.jpg', { type: mime });
}

type PendingUpload = { member_id: number; image_data_url: string; file_name?: string };
type SkinInfo = { skin_type?: string; min_price?: number; max_price?: number };

export default function LoadingPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        // 0) 토큰 없으면 로그인으로
        const at = getAccessToken();
        if (!at) {
          router.replace('/login?error=no_token');
          return;
        }

        // 1) 업로드 대기 데이터
        const raw0 = sessionStorage.getItem('skinMatePendingUpload');
        if (!raw0) throw new Error('업로드 대기 데이터가 없습니다.');
        const pending: PendingUpload = JSON.parse(raw0);

        // 2) 피부 옵션 (없으면 빈 객체)
        const skinInfoRaw = sessionStorage.getItem('skinMateSkinInfo');
        const skinInfo: SkinInfo = skinInfoRaw ? JSON.parse(skinInfoRaw) : {};

        // 3) dataURL → File
        const file = dataURLtoFile(pending.image_data_url, pending.file_name || 'upload.jpg');

        // 4) 서버에 업로드 + 즉시 조회 (✅ 인자 순서 고정)
        const res: SkinAnalysisOutputT = await analysisApi.submit(file, {
          skinType: skinInfo.skin_type || undefined,
          minPrice: typeof skinInfo.min_price === 'number' ? skinInfo.min_price : undefined,
          maxPrice: typeof skinInfo.max_price === 'number' ? skinInfo.max_price : undefined,
        });

        if (!res.success) throw new Error(res.message || '분석 실패');

        // 5) 결과 보존 및 이동
        try { sessionStorage.setItem('skinMateAnalysis', JSON.stringify(res)); } catch {}
        sessionStorage.removeItem('skinMatePendingUpload');
        sessionStorage.removeItem('skinMateSkinInfo');

        router.push(`/result/${res.data.analysis_id}`);
      } catch (e: any) {
        setError(e?.message ?? '분석 요청 중 오류가 발생했습니다.');
      } finally {
        // 실패 시에도 pending 정리
        sessionStorage.removeItem('skinMatePendingUpload');
      }
    };

    run();
  }, [router]);

  return (
    <div className="max-w-md mx-auto min-h-screen flex flex-col items-center justify-center text-center p-6">
      {!error ? (
        <>
          <svg xmlns="http://www.w3.org/2000/svg" width="60" height="60"
               viewBox="0 0 24 24" fill="none" stroke="currentColor"
               strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
               className="text-orange-500 animate-spin">
            <line x1="12" y1="2" x2="12" y2="6"></line>
            <line x1="12" y1="18" x2="12" y2="22"></line>
            <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
            <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
            <line x1="2" y1="12" x2="6" y2="12"></line>
            <line x1="18" y1="12" x2="22" y2="12"></line>
            <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
            <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
          </svg>
          <h1 className="text-2xl font-bold text-gray-800 mt-6">AI가 피부를 분석중입니다...</h1>
          <p className="text-gray-500 mt-2">잠시만 기다려주세요.</p>
        </>
      ) : (
        <>
          <h1 className="text-2xl font-bold text-gray-800 mt-2">분석을 진행할 수 없습니다</h1>
          <p className="text-gray-500 mt-2">{error}</p>
          <button
            onClick={() => router.replace('/upload')}
            className="mt-6 px-6 py-3 rounded-full bg-orange-500 text-white font-semibold hover:bg-orange-600"
          >
            다시 업로드
          </button>
        </>
      )}
    </div>
  );
}
