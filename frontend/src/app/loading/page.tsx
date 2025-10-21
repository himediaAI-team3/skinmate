'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
// 변경: 올바른 경로로
import { analysisApi } from '@/features/loading';
import type { SkinAnalysisOutputT } from '@/entities/loading';

// dataURL → File 변환 유틸
function dataURLtoFile(dataURL: string, fileName: string) {
  const [meta, base64] = dataURL.split(',');
  const mime = (meta.match(/data:(.*);base64/)?.[1]) || 'image/jpeg';
  const bytes = atob(base64);
  const arr = new Uint8Array(bytes.length);
  for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
  return new File([arr], fileName || 'upload.jpg', { type: mime });
}

type PendingUpload = { member_id: number; image_data_url: string; file_name?: string };

export default function LoadingPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      try {
        //[del]테스트용
        setTimeout(() => { router.push('/result?analysis=0'); }, 3000);
        return;
        /*
        const raw0 = sessionStorage.getItem('skinMatePendingUpload');
        if (raw0 == null) throw new Error('업로드 대기 데이터가 없습니다.');
        const raw: string = raw0;
        const pending: PendingUpload = JSON.parse(raw) as PendingUpload;

        const file = dataURLtoFile(pending.image_data_url, pending.file_name || 'upload.jpg');

        // 동기 실행: 결과 나올 때까지 서버 대기
        const res: SkinAnalysisOutputT = await analysisApi.submit(pending.member_id, file);
        if (!res.success) throw new Error(res.message || '분석 실패');

        // 결과 저장(+ 복원 대비)
        try { sessionStorage.setItem('skinMateAnalysis', JSON.stringify(res)); } catch {}
        router.push(`/result?analysis=${res.data.analysis_id}`);
        */
      } catch (e: any) {
        setError(e?.message ?? '분석 요청 중 오류가 발생했습니다.');
      } finally {
        // 한 번 사용한 pending은 정리(선택)
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
