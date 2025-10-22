// src/lib/auth.ts
import type { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import NaverProvider from "next-auth/providers/naver";
import KakaoProvider from "next-auth/providers/kakao";

export const authOptions: NextAuthOptions = {
  session: { strategy: "jwt" },
  secret: process.env.NEXTAUTH_SECRET, // 필수

  providers: [
    // Google
    GoogleProvider({
      clientId: process.env.GOOGLE_ID!,
      clientSecret: process.env.GOOGLE_SECRET!,
    }),

    // Naver
    NaverProvider({
      clientId: process.env.NAVER_CLIENT_ID!,
      clientSecret: process.env.NAVER_CLIENT_SECRET!,
    }),

    // Kakao
    KakaoProvider({
      clientId: process.env.KAKAO_CLIENT_ID!,
      clientSecret: process.env.KAKAO_CLIENT_SECRET!,
    }),
  ],

  callbacks: {
    async jwt({ token, account, user }) {
      // 최초 로그인 시 provider 정보/사용자 id 보관
      if (account) token.provider = account.provider;
      if (user?.id) token.userId = user.id;
      return token;
    },
    async session({ session, token }) {
      // 클라이언트에서도 provider, userId 접근 가능
      (session as any).provider = token.provider;
      (session as any).userId = token.userId;
      return session;
    },
  },

  // 필요 시 커스텀 로그인 페이지 사용
  // pages: { signIn: "/login" },
};