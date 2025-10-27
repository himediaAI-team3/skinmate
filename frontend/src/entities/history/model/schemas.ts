// 분석 이력 도메인 타입
export type DiseaseName =
  | '건선'
  | '아토피'
  | '여드름'
  | '지루'
  | '주사'
  | '정상'
  | string;

export interface AnalysisHistory {
  id: number;
  member_id: number;
  disease_name: DiseaseName;
  summary: string;
  analyzed_at: string; // ISO 또는 'YYYY-MM-DD' (백엔드 응답 형식 사용)
}

export interface Paged<T> {
  items: T[];
  page: number;       // 1-based
  size: number;
  total: number;
  totalPages: number;
}

export type Period = 'all' | 'day' | 'week' | 'month';

export type GetHistoryParams = {
  member_id?: number;
  page?: number;
  size?: number;
  disease_name?: string;
  period?: 'all' | 'day' | 'week' | 'month';
};
