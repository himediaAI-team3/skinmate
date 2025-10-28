/** (페이지네이션형) GET 계열 공통 래퍼 */
export interface ApiEnvelope<T> {
  code: number;
  success: boolean;
  message: string;
  data: T;
  timestamp?: string;
}

/** (커서형) POST /api/likes 응답 래퍼 */
export interface CursorListResponse<T> {
  success: boolean;
  data: {
    items: T[];
    next_cursor?: string | null;
  };
}

/** items 원시 레코드 */
export interface RawLikedCosmeticItem {
  cosmetic_id: number;
  name: string;
  brand: string;
  price: number;
  file_id: number;
  is_liked: boolean;
}

/** data 페이로드 */
export interface RawLikedCosmeticsPage {
  items: RawLikedCosmeticItem[];
  total: number;
  page: number;
  size: number;
}


/** 커서 기반 “좋아요 상품” DTO (백엔드가 내려주는 항목) */
export interface LikedProductDTO {
  product_id: number;
  brand: string;
  name: string;
  price: number;
  image_url?: string;
  href?: string;
}


export interface UiLikedItem {
  id: number;      // cosmetic_id or product_id 매핑
  href: string;    // 예: /cosmetics/:id
  image?: string;  // 썸네일 URL
  brand: string;
  name: string;
  price: number;
}

/** 페이지/서비스 코드에서 쓰기 쉽게 별칭 제공 */
export type LikedItem = UiLikedItem;


export function buildImageUrl(file_id?: number): string {
  if (file_id === undefined || file_id === null) {
    return 'https://placehold.co/640x640/E5E7EB/9CA3AF?text=No+Image';
  }
  const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return `${base}/api/files/${file_id}`;
}

/** (GET형) Raw → UI (단건) */
export function mapRawLikedToUi(item: RawLikedCosmeticItem): UiLikedItem {
  return {
    id: item.cosmetic_id,
    href: `/cosmetics/${item.cosmetic_id}`,
    image: buildImageUrl(item.file_id),
    brand: item.brand,
    name: item.name,
    price: Number(item.price ?? 0),
  };
}

/** (GET형) Raw 페이지 → UI 배열 */
export function mapRawPageToUiItems(page: RawLikedCosmeticsPage): UiLikedItem[] {
  return (page.items ?? []).map(mapRawLikedToUi);
}

/** (커서형) DTO → UI (단건) */
export function mapCursorDtoToUi(dto: LikedProductDTO): UiLikedItem {
  return {
    id: dto.product_id,
    href: dto.href ?? `/cosmetics/${dto.product_id}`,
    image: dto.image_url,
    brand: dto.brand,
    name: dto.name,
    price: Number(dto.price ?? 0),
  };
}

/** (커서형) DTO 배열 → UI 배열 */
export function mapCursorListToUi(dtos: LikedProductDTO[] = []): UiLikedItem[] {
  return dtos.map(mapCursorDtoToUi);
}
