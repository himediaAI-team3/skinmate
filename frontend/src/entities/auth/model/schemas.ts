// /entities/auth/model/schemas.ts
export type SocialProvider = 'Google' | 'Naver' | 'Kakao';

export interface OAuthProviderMeta {
  authorizePath: string; // 백엔드 시작점이 필요할 때만 사용(#면 무시)
  label: string;
  enabled: boolean;
}

export const OAUTH_PROVIDERS: Record<SocialProvider, OAuthProviderMeta> = {
  Google: {
    authorizePath: 'http://192.168.0.235:8080/oauth2/authorization/google',
    label: 'Google로 시작하기',
    enabled: false,
  },
  Naver: {
    authorizePath: 'http://192.168.0.235:8080/oauth2/authorization/naver',
    label: '네이버로 시작하기',
    enabled: false,
  },
  Kakao: {
    authorizePath: 'https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=a7c27574c30bb99e563d2b584d58de73&redirect_uri=http://192.168.0.249:3000/login/oauth2/code/kakao&scope=profile_nickname&state=skinmate',
    label: '카카오로 시작하기',
    enabled: true,
  },
};
