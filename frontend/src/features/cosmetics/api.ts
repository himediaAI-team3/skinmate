import { http } from '@/lib/http';
import type { 
  ApiResponse, 
  CosmeticItem, 
  CosmeticDetail, 
  CosmeticListResponse,
  CosmeticSearchParams 
} from '@/entities/cosmetics';

const API_BASE = '/api/cosmetics';

// 이미지 URL 생성 함수
function createImageUrl(filePath?: string): string {
  if (!filePath) return 'https://placehold.co/640x640/E5E7EB/9CA3AF?text=No+Image';

  // 이미 완전한 URL이면 그대로 사용
  if (/^https?:\/\//i.test(filePath)) return filePath;

  // 백엔드 베이스와 안전하게 결합
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const path = filePath.startsWith('/') ? filePath : `/${filePath}`;
  return `${baseUrl}${path}`;
}

// 화장품 목록 조회
export async function fetchCosmetics(params: CosmeticSearchParams = {}): Promise<ApiResponse<CosmeticListResponse>> {
  const searchParams = new URLSearchParams();
  
  // 파라미터가 있는 경우에만 추가
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  
  const queryString = searchParams.toString();
  const url = queryString ? `${API_BASE}?${queryString}` : API_BASE;
  
  const response = await http<ApiResponse<CosmeticListResponse>>(url, {
    method: 'GET',
  });

  // 응답 데이터에 image_url 추가
  if (response.success && response.data?.items) {
    response.data.items = response.data.items.map(item => ({
      ...item,
      image_url: createImageUrl(item.file_path)
    }));
  }

  return response;
}

// 화장품 상세 조회
export async function fetchCosmeticDetail(
  cosmetic_id: number, 
  member_id?: number
): Promise<ApiResponse<CosmeticDetail>> {
  const params = member_id ? `?member_id=${member_id}` : '';
  const url = `${API_BASE}/${cosmetic_id}${params}`;
  
  const response = await http<ApiResponse<CosmeticDetail>>(url, {
    method: 'GET',
  });

  // 응답 데이터에 image_url 추가
  if (response.success && response.data) {
    response.data.image_url = createImageUrl(response.data.file_path);
  }

  return response;
}

// 기존 좋아요 API 사용 (features/likes/api.ts 참조)
// 좋아요 토글 함수는 기존 likeProduct/unlikeProduct 조합으로 대체
