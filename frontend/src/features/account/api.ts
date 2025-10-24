import type { ApiResponse, MeProfile, MeProfileDTO } from '@/app/entities/account';

const API = process.env.API_PROXY_TARGET!; // 예: https://api.example.com

// DTO -> UI 타입 매핑
function mapMe(dto: MeProfileDTO): MeProfile {
  return {
    id: dto.id,
    name: dto.name,
    email: dto.email,
    avatar: dto.avatar_url || '/avatar-placeholder.png', // 없으면 플레이스홀더
    info: Array.isArray(dto.info) ? dto.info : [],
  };
}

// 내 정보 조회
export async function fetchMyProfile(): Promise<ApiResponse<MeProfile>> {
  const res = await fetch(`${API}/api/me/profile`, {
    method: 'GET',
    credentials: 'include', // JWT 쿠키
    headers: { Accept: 'application/json' },
    cache: 'no-store',
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `HTTP ${res.status}`);
  }

  const json = (await res.json()) as ApiResponse<MeProfileDTO>;
  if (!json?.success) throw new Error(json?.message || '내 정보 조회 실패');

  return { success: true, data: mapMe(json.data) };
}
