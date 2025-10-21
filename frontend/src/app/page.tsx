'use client';

import { Camera, BrainCircuit, Award } from 'lucide-react';

export default function Home() {
  return (
    <div>
      {/* Header */}
      <header className="p-7 pb-1 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <h1 className="text-3xl font-bold font-gmarket text-gray-800 tracking-tighter">SkinMate</h1>
        </div>
        <button className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </button>
      </header>

      {/* Main Content */}
      <main className="p-6 pt-2 pb-24">
        {/* Hero Section Card */}
        <section className="bg-gradient-to-br from-orange-50 via-white to-pink-50 p-8 rounded-3xl text-center card-glow relative">
          <div className="w-28 h-28 bg-white rounded-full flex items-center justify-center mx-auto shadow-md">
            <div className="w-24 h-24 bg-gradient-to-br from-orange-400 to-pink-500 rounded-full flex items-center justify-center">
              {/* Image 컴포넌트를 img 태그로 변경 */}
              <img src="/main_icon.png" alt="SkinMate Logo" width={64} height={64} className="object-contain filter brightness-0 invert" />
            </div>
          </div>
          <h2 className="text-2xl font-extrabold text-gray-800 mt-6">
            단 한 장의 사진으로<br />
            <span className="text-gradient">나만의 스킨 솔루션</span> 찾기
          </h2>
          <p className="text-gray-500 mt-3">
            AI가 내 피부 질환을 정확히 분석하고<br />꼭 맞는 화장품을 추천해 드려요.
          </p>
          {/* Link 컴포넌트를 a 태그로 변경 */}
          <a href="/login">
            <button className="mt-8 w-full bg-gradient-to-r from-orange-500 to-pink-500 text-white font-bold py-4 px-8 rounded-full shadow-lg hover:scale-105 transform transition-transform duration-300">
              AI 피부 진단 시작하기
            </button>
          </a>
        </section>

        {/* Features Section */}
        <section className="mt-12">
          <h3 className="text-xl font-bold text-gray-800 text-center mb-6">SkinMate만의 특별한 기능</h3>
          <div className="space-y-4">
            <FeatureCard icon={<Camera className="text-orange-500" />} title="간편한 사진 촬영" description="얼굴 사진 한 장이면 준비 끝!" />
            <FeatureCard icon={<BrainCircuit className="text-pink-500" />} title="AI 정밀 분석" description="수만 개의 데이터로 학습한 AI가 피부를 진단해요." />
            <FeatureCard icon={<Award className="text-orange-500" />} title="1:1 맞춤 추천" description="내 피부에 딱 맞는 화장품을 추천해 드려요." />
          </div>
        </section>
      </main>
    </div>
  );
}

const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) => (
  <div className="flex items-center space-x-4 bg-gray-100 p-4 rounded-xl">
    <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center flex-shrink-0">
      {icon}
    </div>
    <div>
      <p className="font-semibold text-gray-800">{title}</p>
      <p className="text-sm text-gray-500">{description}</p>
    </div>
  </div>
);