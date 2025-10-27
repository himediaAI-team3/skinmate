// app/features/likes/api.ts
import type { ApiListResponse, LikedItem, LikedProductDTO } from '@/entities/likes';

const API = process.env.NEXT_PUBLIC_API_PROXY_TARGET

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
  memberId: number,
  cursor?: string | null
): Promise<ApiListResponse<LikedItem>> {
  const body: { member_id: number; cursor?: string } = { member_id: memberId };
  if (cursor) body.cursor = cursor;

  const res = await fetch(`${API}/api/likes`, {
    method: 'POST',
    // credentials: 'include', // CORS 문제로 임시 주석처리
    headers: { 
      'Content-Type': 'application/json',
      'Accept': 'application/json' 
    },
    body: JSON.stringify(body),
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

// 좋아요 토글 (추가/취소를 자동으로 처리)
export async function toggleProductLike(
  memberId: number, 
  cosmeticId: number
): Promise<{ isLiked: boolean; likeCount: number }> {
  const res = await fetch(`${API}/api/cosmetics/${cosmeticId}/likes`, {
    method: 'POST',
    // credentials: 'include', // CORS 문제로 임시 주석처리
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
    likeCount: result.data.like_count
  };
}