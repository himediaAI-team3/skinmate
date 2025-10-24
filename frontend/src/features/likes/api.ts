// app/features/likes/api.ts
import type { ApiListResponse, LikedItem, LikedProductDTO } from '@/app/entities/likes';

const API = process.env.API_PROXY_TARGET!; // 예: https://api.example.com

// DTO -> App 타입 매핑
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
  cursor?: string | null
): Promise<ApiListResponse<LikedItem>> {
  const url = new URL(`${API}/api/me/likes`);
  if (cursor) url.searchParams.set('cursor', cursor);

  const res = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'include',
    headers: { Accept: 'application/json' },
    cache: 'no-store',
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `HTTP ${res.status}`);
  }

  const json = (await res.json()) as ApiListResponse<LikedProductDTO>;
  if (!json?.success) throw new Error(json?.message || '좋아요 목록 조회 실패');

  return {
    success: true,
    data: {
      items: json.data.items.map(mapLikedDTOtoItem),
      next_cursor: json.data.next_cursor ?? null,
    },
  };
}

// 좋아요 추가
export async function likeProduct(productId: number): Promise<void> {
  const res = await fetch(`${API}/api/me/likes`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `좋아요 실패 (HTTP ${res.status})`);
  }
}

// 좋아요 취소
export async function unlikeProduct(productId: number): Promise<void> {
  const res = await fetch(`${API}/api/me/likes/${productId}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `좋아요 취소 실패 (HTTP ${res.status})`);
  }
}
