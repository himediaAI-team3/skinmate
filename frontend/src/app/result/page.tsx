'use client';
import { useEffect, useState } from 'react';

// 'any' 타입을 피하기 위해 데이터 구조에 대한 타입을 정의합니다.
interface UserData {
  skinType: string;
  priceMin: string;
  priceMax: string;
  uploadedImage: string | null;
}

interface Product {
  product_image_url: string;
  product_name: string;
  brand_name: string;
  price: string;
  reason: string;
}

interface ResultData {
  skin_analysis: {
    disease_name: string;
    description: string;
  };
  recommended_products: Product[];
}

export default function ResultPage() {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [resultData, setResultData] = useState<ResultData | null>(null);

  useEffect(() => {
    // localStorage에서 사용자 데이터와 이미지 불러오기
    const storedUserData = localStorage.getItem('skinMateUserData');
    if (storedUserData) {
      const parsedData = JSON.parse(storedUserData);
      setUserData(parsedData);
    }
    
    // 예시 결과 데이터 (실제로는 API 호출로 받아옵니다)
    const mockResultData: ResultData = {
      skin_analysis: {
        disease_name: "여드름 (Acne)",
        description: "피지 분비 증가, 모낭의 각질화, 세균 증식으로 인해 발생하는 염증성 피부 질환입니다. 꾸준한 클렌징과 유수분 밸런스 조절이 중요합니다."
      },
      recommended_products: [
        { product_image_url: "https://placehold.co/100x100/FBD38D/000000?text=Cosmetic1", product_name: "티트리 클리어링 토너", brand_name: "SkinSolution", price: "28,000원", reason: "티트리 성분이 트러블을 진정시키고 과도한 피지를 조절하여 지성 및 여드름성 피부에 적합합니다." },
        { product_image_url: "https://placehold.co/100x100/F6AD55/000000?text=Cosmetic2", product_name: "BHA 2% 리퀴드 익스폴리언트", brand_name: "DermaCare", price: "35,000원", reason: "BHA(살리실산) 성분이 모공 속 각질과 노폐물을 효과적으로 제거하여 블랙헤드 개선에 도움을 줍니다." },
        { product_image_url: "https://placehold.co/100x100/ED8936/000000?text=Cosmetic3", product_name: "시카풀 앰플", brand_name: "Nature Republic", price: "22,000원", reason: "병풀 추출물이 민감해진 피부를 진정시키고 손상된 피부 장벽을 강화하는 데 도움을 줍니다." }
      ]
    };
    setResultData(mockResultData);

  }, []);

  return (
    <div className="max-w-md mx-auto min-h-screen p-6 bg-white">
      <header className="pt-4 pb-8">
        <h1 className="text-3xl font-bold text-gray-800">AI 분석 결과</h1>
      </header>
      
      {/* 등록된 이미지 표시 */}
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
        <div id="analysis-result" className="bg-orange-50 p-6 rounded-2xl mt-4">
            <h3 className="text-lg font-bold text-orange-600">{resultData?.skin_analysis.disease_name}</h3>
            <p className="text-gray-700 mt-2">{resultData?.skin_analysis.description}</p>
        </div>
      </section>

      {/* 추천 제품 */}
      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-800">추천 제품 Top 3</h2>
        <div id="product-list" className="mt-4 space-y-4">
          {resultData?.recommended_products.map((product, index) => (
            <div key={index} className="bg-gray-50 p-4 rounded-2xl">
                <div className="flex items-start space-x-4">
                    <img src={product.product_image_url} alt={product.product_name} className="w-20 h-20 rounded-lg object-cover flex-shrink-0" />
                    <div className="flex-1">
                        <p className="text-sm text-gray-500">{product.brand_name}</p>
                        <p className="font-semibold text-gray-800 mt-1">{product.product_name}</p>
                        <p className="font-bold text-orange-600 mt-2">{product.price}</p>
                    </div>
                </div>
                <div className="mt-3 bg-white p-3 rounded-lg">
                    <p className="text-xs font-bold text-gray-600">추천 이유</p>
                    <p className="text-sm text-gray-700 mt-1">{product.reason}</p>
                </div>
            </div>
          ))}
        </div>
      </section>

      {/* 나의 선택 정보 */}
      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-800">나의 선택 정보</h2>
        <div className="mt-4 bg-gray-50 p-6 rounded-2xl text-gray-700 space-y-2">
            <div className="flex justify-between">
                <span className="font-semibold">피부 타입:</span>
                <span>{userData?.skinType || '선택안함'}</span>
            </div>
            <div className="flex justify-between">
                <span className="font-semibold">가격대:</span>
                <span>{userData ? `${userData.priceMin || '0'}원 ~ ${userData.priceMax || '0'}원` : '선택안함'}</span>
            </div>
        </div>
      </section>

      <div className="pt-10 pb-6">
        <a href="/" className="block w-full bg-orange-500 text-white text-center font-bold py-4 px-8 rounded-full shadow-lg hover:bg-orange-600 transition-colors">
          처음으로 돌아가기
        </a>
      </div>
    </div>
  );
}

