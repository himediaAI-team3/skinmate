'use client';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { analysisApi } from '@/features/loading';
import type { SkinAnalysisOutputT } from '@/entities/loading';

type UserData = {
  skinType?: string;
  gender?: string;
  ageGroup?: string;
  priceMin?: string;  // 저장을 문자열로 해두셨으니 그대로 사용
  priceMax?: string;
  uploadedImage?: string | null;
};

export default function ResultPage() {
  const params = useSearchParams();
  const analysisId = Number(params.get('analysis'));

  const [userData, setUserData] = useState<UserData | null>(null);
  const [data, setData] = useState<SkinAnalysisOutputT['data'] | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 사용자 선택/이미지 복구
  useEffect(() => {
    try {
      const stored = localStorage.getItem('skinMateUserData');
      if (stored) setUserData(JSON.parse(stored));
    } catch {}
  }, []);

  // 결과 데이터 로드: 세션 우선 → GET 복구
  useEffect(() => {
    const boot = async () => {
      try {
        // 1) 세션에 저장된 즉시 결과(loading 단계에서 넣음) 사용
        const raw = sessionStorage.getItem('skinMateAnalysis');
        if (raw) {
          const parsed: SkinAnalysisOutputT = JSON.parse(raw);
          if (parsed?.data?.analysis_id === analysisId) {
            setData(parsed.data);
            sessionStorage.removeItem('skinMateAnalysis'); // 일회성이라면 정리
            return;
          }
        }
        // 2) 복구: GET /api/skin-analysis/:id
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

  return (
    <div className="max-w-md mx-auto min-h-screen p-6 bg-white">
      <header className="pt-4 pb-8">
        <h1 className="text-3xl font-bold text-gray-800">AI 분석 결과</h1>
      </header>

      {/* 등록된 이미지 */}
      <section>
        <h2 className="text-xl font-bold text-gray-800">등록된 이미지</h2>
        <div className="mt-4 w-full h-48 bg-gray-100 rounded-2xl flex items-center justify-center overflow-hidden">
          {userData?.uploadedImage ? (
            <img src={userData.uploadedImage} alt="Uploaded skin" className="w-full h-full object-cover" />
          ) : (
            <p className="text-gray-500">이미지를 불러올 수 없습니다.</p>
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
                <img src={p.image_url} alt={p.name} className="w-20 h-20 rounded-lg object-cover flex-shrink-0" />
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

      {/* 나의 선택 정보 
      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-800">나의 선택 정보</h2>
        <div className="mt-4 bg-gray-50 p-6 rounded-2xl text-gray-700 space-y-2">
          <div className="flex justify-between">
            <span className="font-semibold">피부 타입:</span>
            <span>{userData?.skinType || '선택 안 함'}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-semibold">성별:</span>
            <span>{userData?.gender || '선택 안 함'}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-semibold">연령대:</span>
            <span>{userData?.ageGroup || '선택 안 함'}</span>
          </div>
          <div className="flex justify-between">
            <span className="font-semibold">가격대:</span>
            <span>
              {userData
                ? `${userData.priceMin ? Number(userData.priceMin).toLocaleString() : '0'}원 ~ ${
                    userData.priceMax ? Number(userData.priceMax).toLocaleString() : '제한 없음'
                  }`
                : '선택 안 함'}
            </span>
          </div>
        </div>
      </section>
      */}
      <p className="text-xs text-gray-400 mt-6">
        분석 ID: {data.analysis_id} · 파일 ID: {data.file_id} · {data.created_at}
      </p>

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
