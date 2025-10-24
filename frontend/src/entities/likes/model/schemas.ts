// 서버가 내려주는 원시 필드(예시)
export type LikedProductDTO = {
    product_id: number;
    brand: string;
    name: string;
    price: number;
    image_url: string;
    // 서버가 링크를 안 주면 클라이언트에서 /cosmetics/:id 로 매핑
    href?: string | null;
  };
  
  // 앱에서 쓰는 정규화 타입 (UI에서 사용)
  export type LikedItem = {
    id: number;
    brand: string;
    name: string;
    price: number;
    image: string;
    href: string;
  };
  
  // 공통 리스트 응답
  export type ApiListResponse<T> = {
    success: boolean;
    message?: string;
    data: {
      items: T[];
      next_cursor?: string | null;
    };
  };
  