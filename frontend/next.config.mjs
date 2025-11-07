/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // ORIGIN(도메인만) 사용: 예) https://api.skinmate.site
    const apiOrigin  = process.env.NEXT_PUBLIC_API_ORIGIN  || "http://127.0.0.1:8000";
    const authOrigin = process.env.NEXT_PUBLIC_AUTH_ORIGIN || "http://127.0.0.1:8080";

    return [
      // 프론트 /api/*  -> apiOrigin + /api/*
      { source: "/api/:path*",  destination: `${apiOrigin}/api/:path*` },
      // 프론트 /auth/* -> authOrigin + /auth/*
      { source: "/auth/:path*", destination: `${authOrigin}/auth/:path*` },
    ];
  },
  images: {
    remotePatterns: [{ protocol: "https", hostname: "placehold.co" }],
  },
};

export default nextConfig;
