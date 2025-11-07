// /src/entities/auth/model/schemas.ts
export type SocialProvider = 'kakao' | 'google' | 'naver';

export interface OAuthProviderMeta {
  label: string;          // 버튼 라벨
  enabled: boolean;       // 버튼 활성/비활성
  registrationId: string; // 백엔드 /oauth2/authorization/{registrationId}
}

export const OAUTH_PROVIDERS: Record<SocialProvider, OAuthProviderMeta> = {
  kakao:  { label: '카카오로 시작하기', enabled: true,  registrationId: 'kakao' },
  google: { label: 'Google로 시작하기', enabled: false, registrationId: 'google' },
  naver:  { label: '네이버로 시작하기',  enabled: false, registrationId: 'naver' },
};
