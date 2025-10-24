// 리스트에 쓰이는 요약 항목
export type DiagnosisSummary = {
    analysis_id: number;          // 상세 페이지용 키 (/result/[analysis_id])
    disease_name: string;         // 진단명
    diagnosed_at: string;         // ISO 날짜 (UI에는 YYYY-MM-DD로 표시)
    thumbnail_url?: string | null;
  };
  
  // 공통 리스트 응답 래퍼
  export type ApiListResponse<T> = {
    success: boolean;
    message?: string;
    data: {
      items: T[];
      next_cursor?: string | null;
    };
  };
  