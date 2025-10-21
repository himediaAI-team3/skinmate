import { z } from 'zod';

export const ProductSchema = z.object({
  name: z.string(),
  brand: z.string(),
  price: z.number().int().nonnegative(),
  image_url: z.string().min(1),
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

export const SkinAnalysisOutput = z.object({
  code: z.number(),
  success: z.boolean(),
  message: z.string(),
  data: SkinAnalysisData,
});

export type SkinAnalysisOutputT = z.infer<typeof SkinAnalysisOutput>;
