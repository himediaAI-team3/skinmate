// src/lib/auth.ts
// 주의: 현재 프로젝트는 NextAuth를 사용하지 않습니다.
// 인증은 별도의 Auth 서버(`/auth/*` 프록시)와 토큰 저장 유틸로 처리합니다.
// 남겨둔 이 파일은 레거시 참조 방지를 위한 더미(export 형태)입니다.

import type { NextAuthOptions } from "next-auth";

export const authOptions: NextAuthOptions = {
  // 비활성 (사용하지 않음)
  session: { strategy: "jwt" },
  // NextAuth 미사용: providers 비움
  providers: [],
  callbacks: {},
};