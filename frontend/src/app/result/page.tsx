// 변경 포인트만 요약:
// 1) userData 관련 코드 제거(사용 안 함)
// 2) 등록된 이미지 섹션을 file_id 기준으로 표시

'use client';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { analysisApi } from '@/features/loading';
import type { SkinAnalysisOutputT } from '@/entities/loading';

export default function ResultPage() {
  const params = useSearchParams();
  const analysisId = Number(params.get('analysis'));

  const [data, setData] = useState<SkinAnalysisOutputT['data'] | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 이미지 베이스 URL (필요에 맞게 경로 조정: 예 /files/:id 또는 /files/:id/content 등)
  const IMG_BASE = 'http://192.168.0.235:8000/api';

  // 결과 데이터 로드
  useEffect(() => {
    const boot = async () => {
      try {
        const raw = sessionStorage.getItem('skinMateAnalysis');
        if (raw) {
          const parsed: SkinAnalysisOutputT = JSON.parse(raw);
          if (parsed?.data?.analysis_id === analysisId) {
            setData(parsed.data);
            sessionStorage.removeItem('skinMateAnalysis');
            return;
          }
        }
        if (!analysisId || Number.isNaN(analysisId)) throw new Error('유효하지 않은 분석 ID입니다.');
        const res = await analysisApi.get(analysisId);
        if (!res.success) throw new Error(res.message || '결과 조회 실패');
        setData(res.data);
      } catch (e: any) {
        setError(e?.message ?? '결과를 불러오는 중 오류가 발생했습니다.');
      }
    };
    boot();
  }, [analysisId]);

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
          <a href="/upload" className="block w-full bg-orange-500 text-white text-center font-bold py-4 px-8 rounded-full shadow-lg hover:bg-orange-600 transition-colors">
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

  // file_id가 있으면 이미지 URL 생성
  const imageUrl = data.file_id ? `${IMG_BASE}/files/${data.file_id}` : null;

  return (
    <div className="max-w-md mx-auto min-h-screen p-6 bg-white">
      <header className="pt-4 pb-8">
        <h1 className="text-3xl font-bold text-gray-800">AI 분석 결과</h1>
      </header>

      {/* 등록된 이미지: file_id 기준으로 표시 */}
      <section>
        <h2 className="text-xl font-bold text-gray-800">등록된 이미지</h2>
        <div
          className="mt-4 w-full aspect-square max-h-[520px] bg-gray-100 rounded-2xl overflow-hidden shadow-sm
                     flex items-center justify-center"
        >
          {imageUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={imageUrl}
              alt="Uploaded skin"
              className="w-full h-full object-cover"
            />
          ) : (
            <p className="text-gray-500">등록된 이미지를 찾을 수 없습니다.</p>
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
          {data.products.map((p, idx) => (
            <div key={idx} className="bg-gray-50 p-4 rounded-2xl">
              <div className="flex items-start gap-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={`${IMG_BASE}${p.image_url}`} alt={p.name} className="w-20 h-20 rounded-lg object-cover flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm text-gray-500">{p.brand}</p>
                  <p className="font-semibold text-gray-800 mt-1">{p.name}</p>
                  <p className="font-bold text-orange-600 mt-2">{Number(p.price).toLocaleString()}원</p>
                </div>
              </div>
              <div className="mt-3 bg-white p-3 rounded-lg">
                <p className="text-xs font-bold text-gray-600">추천 이유</p>
                <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">{p.reason}</p>
              </div>
            </div>
          ))}
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
