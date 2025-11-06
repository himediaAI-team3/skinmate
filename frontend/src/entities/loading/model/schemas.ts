// /src/entities/loading/schemas.ts
import { z } from 'zod';

export const ProductSchema = z.object({
  name: z.string(),
  brand: z.string(),
  // DECIMAL 문자열도 허용 → number로 강제 변환
  price: z.coerce.number().nonnegative(),
  // 백엔드가 null 줄 수 있음
  file_path: z.string().nullable().optional(),
  buy_url: z.string().nullable().optional(),
  reason: z.string(),
});

export const SkinAnalysisData = z.object({
  analysis_id: z.number().int().nonnegative(),
  file_id: z.number().int().nonnegative(),
  disease_name: z.string(),
  diagnosis_summary: z.string(),
  products: z.array(ProductSchema),
  created_at: z.string(),
});

export const SkinAnalysisOutput = z
  .object({
    code: z.number(),
    success: z.boolean(),
    message: z.string(),
    data: SkinAnalysisData,
  })
  // timestamp 등 여분 필드 허용
  .passthrough();

export type SkinAnalysisDataT = z.infer<typeof SkinAnalysisData>;
export type SkinAnalysisOutputT = z.infer<typeof SkinAnalysisOutput>;
