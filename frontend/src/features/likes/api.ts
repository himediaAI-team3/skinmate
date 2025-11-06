// /src/app/features/likes/api.ts
'use client';

import type {
  CursorListResponse as ApiListResponse, // { success, data:{ items, next_cursor } }
  UiLikedItem as LikedItem,
  LikedProductDTO,
} from '@/entities/likes';
import { getAccessToken } from '@/features/auth';

/* ========================================
   공통 유틸
   ======================================== */

function resolveBaseStrict(): string {
  const base = (process.env.NEXT_PUBLIC_API_URL ?? '').trim().replace(/\/+$/, '');
  if (!base) throw new Error('env 누락: NEXT_PUBLIC_API_URL (예: http://127.0.0.1:8000)');
  return base;
}
const API = resolveBaseStrict();

function authHeaders(): HeadersInit {
  const at = getAccessToken();
  return at ? { Authorization: `Bearer ${at}` } : {};
}

async function readPayload(res: Response) {
  const ct = res.headers.get('Content-Type') || '';
  if (ct.toLowerCase().includes('application/json')) {
    try { return await res.json(); } catch { return null; }
  }
  try { return await res.text(); } catch { return null; }
}

function pickMessage(payload: any, fallback: string) {
  if (!payload) return fallback;
  if (typeof payload === 'string') return payload;
  if (typeof payload?.message === 'string') return payload.message;
  if (typeof payload?.detail === 'string') return payload.detail;
  try { return JSON.stringify(payload); } catch { return fallback; }
}

/* ========================================
   이미지 URL 보강
   - 서버가 '/media/..' 같은 상대경로를 줄 수 있음
   ======================================== */
function buildImageUrl(file_path?: string | null): string {
  if (!file_path) {
    return 'https://placehold.co/640x640/E5E7EB/9CA3AF?text=No+Image';
  }
  if (/^https?:\/\//i.test(file_path)) return file_path;
  return `${API}${file_path.startsWith('/') ? '' : '/'}${file_path}`;
}

/* ========================================
   DTO -> UI 변환
   ======================================== */
function mapLikedDTOtoItem(dto: LikedProductDTO): LikedItem {
  return {
    id: dto.product_id,
    brand: dto.brand,
    name: dto.name,
    price: dto.price,
    image: dto.image_url ? buildImageUrl(dto.image_url) : buildImageUrl(null),
    href: dto.href || `/cosmetics/${dto.product_id}`,
  };
}

/* ============== 커서형: POST /api/likes ============== */
/** 좋아요 목록 조회 (커서 기반) */
export async function fetchLikedProducts(
  memberId: number,
  cursor?: string | null
): Promise<ApiListResponse<LikedItem>> {
  const body: { member_id: number; cursor?: string } = { member_id: memberId };
  if (cursor) body.cursor = cursor;

  const res = await fetch(`${API}/api/likes`, {
    method: 'POST',
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...authHeaders(),
    },
    body: JSON.stringify(body),
  });

  const payload = await readPayload(res);
  if (!res.ok) {
    throw new Error(pickMessage(payload, `좋아요 목록 조회 실패 (HTTP ${res.status})`));
  }

  const json = payload as ApiListResponse<LikedProductDTO>;
  if (!json || json.success !== true) {
    const fallbackMsg = (json as any)?.message ?? '좋아요 목록 조회 실패';
    throw new Error(fallbackMsg);
  }

  return {
    success: true,
    data: {
      items: (json.data.items ?? []).map(mapLikedDTOtoItem),
      next_cursor: json.data.next_cursor ?? null,
    },
  };
}

/* ============== 토글: POST /api/cosmetics/{id}/likes ============== */
/** 좋아요 토글 (JWT 기반이더라도 member_id를 함께 보내면 백엔드에서 호환 처리 가능) */
export async function toggleProductLike(
  memberId: number,
  cosmeticId: number
): Promise<{ isLiked: boolean; likeCount: number }> {
  const res = await fetch(`${API}/api/cosmetics/${cosmeticId}/likes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders(),
    },
    body: JSON.stringify({ member_id: memberId }),
  });

  const payload = await readPayload(res);
  if (!res.ok) {
    throw new Error(pickMessage(payload, `좋아요 토글 실패 (HTTP ${res.status})`));
  }

  if (!payload?.success) {
    throw new Error(payload?.message || '좋아요 토글 실패');
  }

  return {
    isLiked: payload.data?.is_liked,
    likeCount: payload.data?.like_count,
  };
}

/* ============== 페이지형: GET /api/cosmetics/likes ============== */
interface RawLikedCosmeticItemV2 {
  cosmetic_id: number;
  name: string;
  brand: string;
  price: number;
  file_path?: string | null;
  is_liked: boolean;
}
interface RawLikedCosmeticsPageV2 {
  items: RawLikedCosmeticItemV2[];
  total: number;
  page: number;
  size: number;
}
interface ApiEnvelopeV2<T> {
  code: number;
  success: boolean;
  message: string;
  data: T;
  timestamp?: string;
}

// V2 원시 아이템 -> UI 항목
function mapRawLikedToItemV2(dto: RawLikedCosmeticItemV2): LikedItem {
  return {
    id: dto.cosmetic_id,
    brand: dto.brand,
    name: dto.name,
    price: dto.price,
    image: buildImageUrl(dto.file_path ?? undefined),
    href: `/cosmetics/${dto.cosmetic_id}`,
  };
}

/** 배열만 필요할 때 (이전 likes 페이지 사용) */
export async function fetchMemberLikedCosmeticsV2(opts?: {
  /** 페이지 번호(1-based) */ page?: number;
  /** 페이지 크기 */ size?: number;
  /** 호환용: 기존 코드가 memberId를 전달해도 무시 (JWT 기반) */ memberId?: number;
}): Promise<LikedItem[]> {
  const page = opts?.page ?? 1;
  const size = opts?.size ?? 20;

  const usp = new URLSearchParams({ page: String(page), size: String(size) });
  const url = `${API}/api/cosmetics/likes?${usp.toString()}`;

  const res = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    headers: {
      'Accept': 'application/json',
      ...authHeaders(),
    },
  });

  const payload = await readPayload(res);
  if (!res.ok) {
    throw new Error(pickMessage(payload, `좋아요 목록 조회 실패(${res.status})`));
  }

  const json = payload as ApiEnvelopeV2<RawLikedCosmeticsPageV2>;
  if (!json?.success) throw new Error(json?.message || '좋아요 목록 조회 실패');

  return (json.data?.items ?? []).map(mapRawLikedToItemV2);
}

/** 페이지/총합까지 필요할 때 */
export async function fetchMemberLikedCosmeticsPage(opts?: {
  /** 페이지 번호(1-based) */ page?: number;
  /** 페이지 크기 */ size?: number;
  /** 호환용: 기존 코드가 memberId를 전달해도 무시 (JWT 기반) */ memberId?: number;
}): Promise<{ items: LikedItem[]; total: number; page: number; size: number }> {
  const page = opts?.page ?? 1;
  const size = opts?.size ?? 10;

  const usp = new URLSearchParams({ page: String(page), size: String(size) });
  const url = `${API}/api/cosmetics/likes?${usp.toString()}`;

  const res = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    headers: {
      'Accept': 'application/json',
      ...authHeaders(),
    },
  });

  const payload = await readPayload(res);
  if (!res.ok) {
    throw new Error(pickMessage(payload, `좋아요 목록 조회 실패(${res.status})`));
  }

  const json = payload as ApiEnvelopeV2<RawLikedCosmeticsPageV2>;
  if (!json?.success) throw new Error(json?.message || '좋아요 목록 조회 실패');

  const data = json.data;
  return {
    items: (data.items ?? []).map(mapRawLikedToItemV2),
    total: data.total ?? 0,
    page: data.page ?? page,
    size: data.size ?? size,
  };
}

// (선택) 기존 이름 유지용 별칭
export { fetchMemberLikedCosmeticsV2 as fetchLikedCosmetics };
