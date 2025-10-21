/** @type {import('next').NextConfig} */
const nextConfig = {
  // ✅ /api/* → (환경변수 또는 기본값)/api/* 로 전달
  async rewrites() {
    // .env* 에서 API_PROXY_TARGET 읽기, 없으면 기본값 사용
    const target = process.env.API_PROXY_TARGET || "http://localhost";
    return [
      // 프론트의 /api/xxx  →  http://...:8000/api/xxx
      { source: "/api/:path*", destination: `${target}/api/:path*` },
    ];
  },

  // ✅ 기존 이미지 원격 도메인 허용 유지
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