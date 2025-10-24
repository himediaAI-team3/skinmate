import type { Metadata } from "next";
import "./globals.css";
import HeaderGate from "@/components/HeaderGate";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "SkinMate - AI 피부 진단",
  description: "AI로 피부를 분석하고 나에게 맞는 화장품을 추천받으세요.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Nunito:wght@700;800&family=Pretendard:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body>
        <div className="max-w-md mx-auto bg-white min-h-screen relative">
          <HeaderGate />
          <main className="pb-16">{children}</main>
        </div>
      </body>
    </html>
  );
}