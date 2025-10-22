import type { Metadata } from "next";
import "./globals.css";
import { cookies } from "next/headers";
import AppHeader from "@/components/AppHeader";
import TabBar from "@/components/TabBar"; // 이미 만든 탭바
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "SkinMate - AI 피부 진단",
  description: "AI로 피부를 분석하고 나에게 맞는 화장품을 추천받으세요.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const hasJwt = !!cookies().get("sm_token")?.value; // 백엔드가 세팅한 JWT 쿠키명

  return (
    <html lang="ko">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Nunito:wght@700;800&family=Pretendard:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body>
        {/* ✅ 기존 컨테이너 스타일 그대로 */}
        <div className="max-w-md mx-auto bg-white min-h-screen relative">
          {/* 공통 상단 헤더 */}
          <AppHeader />
          {/* 탭이 있을 때만 본문 하단 여백 확보 */}
          <main className={hasJwt ? "pb-16" : ""}>
            {children}
          </main>
          {/* JWT가 있으면 하단 탭 표시 */}
          {hasJwt && <TabBar />}
        </div>
      </body>
    </html>
  );
}
