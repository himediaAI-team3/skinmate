// 백엔드 Cosmetic 모델에 맞춘 타입 정의

export interface CosmeticItem {
  cosmetic_id: number;
  name: string;
  brand: string;
  category: string;
  price: number;
  ingredients?: string;
  short_description?: string;  // 한줄설명
  description?: string;        // 상세설명
  buy_url?: string;
  skin_type?: string;          // 피부타입
  skin_disease?: string;       // 관련질환
  main_effect?: string;        // 주요효능
  care_symptom?: string;       // 케어증상
  key_ingredient?: string;     // 핵심성분
  
  // API 응답에 포함된 필드들
  file_path?: string;          // 백엔드에서 오는 이미지 경로
  like_count?: number;         // 좋아요 수
  is_liked?: boolean;          // 좋아요 여부
  rating?: number;             // 평점 (추후 추가될 수 있음)
  
  // UI에서 사용할 계산된 필드
  image_url?: string;          // file_path를 기반으로 생성된 전체 URL
}

export interface CosmeticDetail extends CosmeticItem {
  // 상세 페이지에서만 필요한 추가 필드들이 있다면 여기에
}

// API 응답 타입
export interface CosmeticListResponse {
  items: CosmeticItem[];
  total: number;
  page: number;
  size: number;
}

export interface CosmeticDetailResponse {
  data: CosmeticDetail;
}

// 검색 파라미터 타입
export interface CosmeticSearchParams {
  brand?: string;
  name?: string;
  skin_type?: string;
  category?: string;
  member_id?: number;
  page?: number;
  size?: number;
}

// 카테고리 타입 (백엔드와 일치하도록)
export type CosmeticCategory = 
  | '로션/크림/올인원'
  | '에센스/세럼'
  | '스킨/토너'
  | '아이크림'
  | '미스트/오일'
  | '패드'
  | '클렌징'
  | '선크림'
  | '앰플'
  | '젤';

// API 공통 응답 타입
export interface ApiResponse<T = any> {
  code: number;
  success: boolean;
  message: string;
  data: T;
}
