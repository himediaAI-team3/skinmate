export type DiagnosisSummary = {
  analysis_id: number;          // 상세 조회용 키 (/result/[id])
  disease_name: string;         // 진단명(예: 여드름, 아토피 등)
  diagnosed_at: string;         // ISO (예: 2025-10-22T10:23:45Z)
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
