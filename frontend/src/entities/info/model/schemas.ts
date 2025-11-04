import { z } from 'zod';

export const SkinTypeEnum = z.enum(['지성', '건성', '복합성', '민감성']);
export const GenderEnum   = z.enum(['남성', '여성']);
export const AgeGroupEnum = z.enum(['10', '20', '30', '40', '50']);

export const UpdateSkinInfoInput = z.object({
  min_price: z.number().int().positive(),
  max_price: z.number().int().positive(),
  skin_type: SkinTypeEnum,
}).superRefine((v, ctx) => {
  if (v.min_price > v.max_price) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ['min_price'], message: '최소 금액이 최대 금액보다 클 수 없습니다.' });
  }
});

export const UpdateSkinInfoOutput = z.object({
  code: z.number(),
  success: z.boolean(),
  message: z.string(),
  data: z.object({
    member_id: z.number(),
    skin_type: z.string(),
    min_price: z.number(),
    max_price: z.number(),
  }),
  timestamp: z.string(),
});

export type UpdateSkinInfoInputT  = z.infer<typeof UpdateSkinInfoInput>;
export type UpdateSkinInfoOutputT = z.infer<typeof UpdateSkinInfoOutput>;