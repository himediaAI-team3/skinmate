// /src/entities/history/index.ts
import { z } from 'zod';

/** ===== 서버 원본 스키마 (이력 조회 응답) ===== */
export const RawHistoryItem = z.object({
  analysis_id: z.number().int(),
  disease_name: z.string(),
  created_at: z.string(), // ISO date string
});

export const RawHistoryPageData = z.object({
  items: z.array(RawHistoryItem),
  total: z.number().int(),
  page: z.number().int(),
  size: z.number().int(),
});

export const ApiResponseHistoryPage = z.object({
  code: z.number().int(),
  success: z.boolean(),
  message: z.string(),
  data: RawHistoryPageData,
}).passthrough();

export type RawHistoryItemT = z.infer<typeof RawHistoryItem>;
export type RawHistoryPageDataT = z.infer<typeof RawHistoryPageData>;

/** ===== 프론트(UI)에서 쓰는 표준 타입 ===== */
export type AnalysisHistory = {
  id: number;                 // = analysis_id
  disease_name: string;
  analyzed_at: string;        // = created_at
  summary?: string;           // UI용 요약(없으면 질환명으로 대체)
};

export type Paged<T> = {
  items: T[];
  page: number;
  size: number;
  total: number;
  totalPages: number;
};

/** 히스토리 조회 파라미터 (member_id는 더 이상 쓰지 않지만 호환 위해 남김) */
export type GetHistoryParams = {
  member_id?: number;
  page?: number;
  size?: number;
  disease_name?: string;               // ''이면 전체
  period?: 'all' | 'day' | 'week' | 'month';
};
