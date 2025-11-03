// /entities/auth/model/schemas.ts
export type SocialProvider = 'Google' | 'Naver' | 'Kakao';

export interface OAuthProviderMeta {
  authorizePath: string; // 백엔드 시작점이 필요할 때만 사용(#면 무시)
  label: string;
  enabled: boolean;
}

export const OAUTH_PROVIDERS: Record<SocialProvider, OAuthProviderMeta> = {
  Google: {
    authorizePath: '/auth/oauth2/authorization/google',
    label: 'Google로 시작하기',
    enabled: false,
  },
  Naver: {
    authorizePath: '/auth/oauth2/authorization/naver',
    label: '네이버로 시작하기',
    enabled: false,
  },
  Kakao: {
    authorizePath: '/auth/oauth2/authorization/kakao',
    label: '카카오로 시작하기',
    enabled: true,
  },
};
