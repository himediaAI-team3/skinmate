// /src/app/features/likes/api.ts
import type {
  CursorListResponse as ApiListResponse, // 커서형 응답 래퍼 { success, data:{ items, next_cursor } }
  UiLikedItem as LikedItem,
  LikedProductDTO,
} from '@/entities/likes';

const API = process.env.NEXT_PUBLIC_API_PROXY_TARGET;

/* =========================
   커서형: POST /api/likes
   ========================= */

// DTO -> UI 타입 매핑
function mapLikedDTOtoItem(dto: LikedProductDTO): LikedItem {
  return {
    id: dto.product_id,
    brand: dto.brand,
    name: dto.name,
    price: dto.price,
    image: dto.image_url,
    href: dto.href || `/cosmetics/${dto.product_id}`,
  };
}

// 좋아요 목록 조회 (커서 기반)
export async function fetchLikedProducts(
  memberId: number,
  cursor?: string | null
): Promise<ApiListResponse<LikedItem>> {
  const body: { member_id: number; cursor?: string } = { member_id: memberId };
  if (cursor) body.cursor = cursor;

  const res = await fetch(`${API}/api/likes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify(body),
    cache: 'no-store',
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `HTTP ${res.status}`);
  }

  // message 필드가 없는 CursorListResponse 타입
  const json = (await res.json()) as ApiListResponse<LikedProductDTO>;
  if (!json || json.success !== true) {
    const fallbackMsg = (json as any)?.message ?? '좋아요 목록 조회 실패';
    throw new Error(fallbackMsg);
  }

  return {
    success: true,
    data: {
      items: json.data.items.map(mapLikedDTOtoItem),
      next_cursor: json.data.next_cursor ?? null,
    },
  };
}

/* =========================
   토글: POST /api/cosmetics/{id}/likes
   ========================= */

export async function toggleProductLike(
  memberId: number,
  cosmeticId: number
): Promise<{ isLiked: boolean; likeCount: number }> {
  const res = await fetch(`${API}/api/cosmetics/${cosmeticId}/likes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ member_id: memberId }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `좋아요 토글 실패 (HTTP ${res.status})`);
  }

  const result = await res.json();
  if (!result?.success) {
    throw new Error(result?.message || '좋아요 토글 실패');
  }

  return {
    isLiked: result.data.is_liked,
    likeCount: result.data.like_count,
  };
}

/* =========================
   페이지형: GET /api/cosmetics/likes/{member_id}
   ========================= */

interface RawLikedCosmeticItemV2 {
  cosmetic_id: number;
  name: string;
  brand: string;
  price: number;
  file_id: number;
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

// 파일(이미지) URL 생성
function buildImageUrlV2(file_id?: number): string {
  if (file_id === undefined || file_id === null) {
    return 'https://placehold.co/640x640/E5E7EB/9CA3AF?text=No+Image';
  }
  const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return `${base}/api/files/${file_id}`;
}

// V2 원시 아이템 -> UI 항목
function mapRawLikedToItemV2(dto: RawLikedCosmeticItemV2): LikedItem {
  return {
    id: dto.cosmetic_id,
    brand: dto.brand,
    name: dto.name,
    price: dto.price,
    image: buildImageUrlV2(dto.file_id),
    href: `/cosmetics/${dto.cosmetic_id}`,
  };
}

/**
 * 배열만 필요할 때 (이전 likes 페이지 사용)
 * GET /api/cosmetics/likes/{member_id}?page=&size=
 */
export async function fetchMemberLikedCosmeticsV2(
  opts?: { memberId?: number; page?: number; size?: number }
): Promise<LikedItem[]> {
  const memberId = opts?.memberId ?? 1;
  const page = opts?.page ?? 1;
  const size = opts?.size ?? 20;

  const usp = new URLSearchParams({ page: String(page), size: String(size) });
  const base = (typeof API === 'string' && API) ? API : '';
  const url = `${base}/api/cosmetics/likes/${memberId}?${usp.toString()}`;

  const res = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`좋아요 목록 조회 실패(${res.status}): ${text}`);
  }

  const json = (await res.json()) as ApiEnvelopeV2<RawLikedCosmeticsPageV2>;
  if (!json?.success) throw new Error(json?.message || '좋아요 목록 조회 실패');

  return (json.data?.items ?? []).map(mapRawLikedToItemV2);
}

/**
 * 페이지 정보까지 필요할 때(총 개수/페이지네이션 계산)
 * GET /api/cosmetics/likes/{member_id}?page=&size=
 */
export async function fetchMemberLikedCosmeticsPage(opts?: {
  memberId?: number; page?: number; size?: number;
}): Promise<{ items: LikedItem[]; total: number; page: number; size: number }> {
  const memberId = opts?.memberId ?? 1;
  const page = opts?.page ?? 1;
  const size = opts?.size ?? 10;

  const usp = new URLSearchParams({ page: String(page), size: String(size) });
  const base = (typeof API === 'string' && API) ? API : '';
  const url = `${base}/api/cosmetics/likes/${memberId}?${usp.toString()}`;

  const res = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`좋아요 목록 조회 실패(${res.status}): ${text}`);
  }

  const json = (await res.json()) as ApiEnvelopeV2<RawLikedCosmeticsPageV2>;
  if (!json?.success) throw new Error(json?.message || '좋아요 목록 조회 실패');

  const data = json.data;
  return {
    items: (data.items ?? []).map(mapRawLikedToItemV2),
    total: data.total ?? 0,
    page: data.page ?? page,
    size: data.size ?? size,
  };
}

// (선택) 페이지 코드에서 기존 이름을 그대로 쓰고 싶다면 이 별칭 사용
export { fetchMemberLikedCosmeticsV2 as fetchLikedCosmetics };
