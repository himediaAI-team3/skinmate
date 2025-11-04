/** @type {import('next').NextConfig} */
const nextConfig = {
  // /api/*, /auth/* → 환경변수 기반으로 백엔드/인증 서버에 프록시
  async rewrites() {
    // 우선순위: NEXT_PUBLIC_* → 레거시(API_PROXY_TARGET) → 기본값
    const apiTarget = process.env.NEXT_PUBLIC_API_URL || process.env.API_PROXY_TARGET || "http://localhost:8000";
    const authTarget = process.env.NEXT_PUBLIC_AUTH_URL || process.env.AUTH_PROXY_TARGET || "http://localhost:8080";

    return [
      // 프론트의 /api/xxx  →  http://...:8000/api/xxx (FastAPI)
      { source: "/api/:path*", destination: `${apiTarget}/api/:path*` },
      // 프론트의 /auth/xxx →  http://...:8080/auth/xxx (Spring Auth)
      { source: "/auth/:path*", destination: `${authTarget}/auth/:path*` },
    ];
  },

  // 기존 이미지 원격 도메인 허용 유지
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "placehold.co",
      },
    ],
  },
};

export default nextConfig;