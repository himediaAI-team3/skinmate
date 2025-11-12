// ./src/features/account/api.ts
import { http } from '@/lib/http';
import type { MemberResponse, MemberUpdateDTO } from '@/entities/account';

// GET /api/members/me
export async function getMe(): Promise<MemberResponse> {
  const res = await http('/api/members/me', { method: 'GET', withAuth: true });
  // 백엔드 공통 래퍼(ApiResponse) 구조: { code, success, message, data, ... }
  return (res?.data ?? null) as MemberResponse;
}

// PUT /api/members/me
export async function updateMe(payload: MemberUpdateDTO): Promise<MemberResponse> {
  const res = await http('/api/members/me', {
    method: 'PUT',
    withAuth: true,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return (res?.data ?? null) as MemberResponse;
}

// 성별 기반 기본 아바타 경로
export function getDefaultAvatar(gender?: string | null): string {
  if (!gender) return '/images/1.webp'; // 기본(미지정/여성)
  const g = gender.trim().toLowerCase();
  if (g === '남성' || g === 'male' || g === 'm') return '/images/2.webp';
  return '/images/1.webp';
}
