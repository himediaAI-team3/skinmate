// /src/features/loading/api.ts
'use client';

import { getAccessToken } from '@/features/auth';
import {
  SkinAnalysisOutput,
  SkinAnalysisData,
  SkinAnalysisDataT,
  SkinAnalysisOutputT,
} from '@/entities/loading';

/* =========================
 * 내부 유틸 (리라이트/프록시 미사용)
 * ========================= */

function resolveBaseStrict(): string {
  const base = (process.env.NEXT_PUBLIC_API_URL ?? '').trim().replace(/\/+$/, '');
  if (!base) throw new Error('env 누락: NEXT_PUBLIC_API_URL (예: http://127.0.0.1:8000)');
  return base;
}

function joinUrl(base: string, path: string) {
  if (/^https?:\/\//i.test(path)) return path;
  if (!path.startsWith('/')) path = `/${path}`;
  return `${base}${path}`;
}

function authHeaders(): HeadersInit {
  const at = getAccessToken();
  return at ? { Authorization: `Bearer ${at}` } : {};
}

async function readPayload(res: Response) {
  const ct = res.headers.get('Content-Type') || '';
  if (ct.toLowerCase().includes('application/json')) {
    try { return await res.json(); } catch { return null; }
  }
  try { return await res.text(); } catch { return null; }
}

function pickMessage(payload: any, fallback: string) {
  if (!payload) return fallback;
  if (typeof payload === 'string') return payload;
  if (typeof payload?.message === 'string') return payload.message;
  if (typeof payload?.detail === 'string') return payload.detail;
  const txt = (() => { try { return JSON.stringify(payload); } catch { return ''; } })();
  // MySQL 1146 등 DB 뷰 힌트 문구 감지
  if (txt.includes('1146') || txt.includes("doesn't exist") || txt.includes('analysis_result_view')) {
    return '서버 DB 뷰(analysis_result_view)가 없어 조회에 실패했습니다. DB에 뷰를 생성해주세요.';
  }
  return txt || fallback;
}

/* =========================
 * 정적 URL 유틸 (제품 이미지용)
 * ========================= */

export function resolveStaticUrl(path?: string | null): string | null {
  if (!path) return null;
  if (/^https?:\/\//i.test(path)) return path; // 이미 절대 URL
  const base = resolveBaseStrict();
  const clean = path.startsWith('/') ? path : `/${path}`;
  return `${base}${clean}`;
}

export function getProductImageSrc(file_path?: string | null): string {
  return resolveStaticUrl(file_path) ?? '/placeholder.png';
}

/* =========================
 * 1) 분석 생성 (POST /api/skin-analysis)
 * ========================= */

export async function createAnalysis(
  file: File,
  options?: { skinType?: string; minPrice?: number; maxPrice?: number }
): Promise<{ analysisId: number; fileId?: number }> {
  if (!(file instanceof File)) throw new Error('이미지 파일이 없습니다.');
  if (file.size > 20 * 1024 * 1024) {
    throw new Error('파일이 너무 큽니다. 20MB 이하 이미지를 업로드해주세요.');
  }

  const form = new FormData();
  form.append('image', file);
  if (options?.skinType) form.append('skin_type', options.skinType);
  if (typeof options?.minPrice === 'number') form.append('min_price', String(options.minPrice));
  if (typeof options?.maxPrice === 'number') form.append('max_price', String(options.maxPrice));

  const base = resolveBaseStrict();
  const url = joinUrl(base, '/api/skin-analysis');

  let res: Response;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: {
        // FormData: Content-Type 자동 설정
        ...authHeaders(),
      },
      body: form,
      // credentials: 'include', // 쿠키 세션 쓰면 활성화
    });
  } catch (e: any) {
    if (e?.message?.includes('Failed to fetch') || e?.message?.includes('ERR_CONNECTION_REFUSED')) {
      console.error('[analysis.create] 서버 연결 실패:', url);
      throw new Error('백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
    }
    throw e;
  }

  const payload = await readPayload(res);

  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('분석 생성 권한이 없습니다(401). 로그인/토큰을 확인해주세요.');
    }
    const msg = pickMessage(payload, `POST /api/skin-analysis 실패 (${res.status})`);
    console.error('[analysis.create] HTTP ERROR', res.status, payload);
    throw new Error(msg);
  }

  const data: any = payload && typeof payload === 'object' && 'data' in payload ? payload.data : payload;
  const rawId = data?.analysis_id ?? data?.id;
  const analysisId = Number(rawId);
  if (!Number.isFinite(analysisId) || analysisId <= 0) {
    console.warn('[analysis.create] 예상치 못한 응답 형태:', payload);
    throw new Error('POST 응답에 analysis_id가 없습니다.');
  }
  const fileId = data?.file_id ?? undefined;
  return { analysisId, fileId };
}

/* =========================
 * 2) 결과 조회 (GET /api/skin-analysis/{id})
 * ========================= */

export async function getAnalysis(analysisId: number): Promise<SkinAnalysisOutputT> {
  if (!Number.isFinite(analysisId) || analysisId <= 0) {
    throw new Error('analysisId가 올바르지 않습니다.');
  }

  const base = resolveBaseStrict();
  const url = joinUrl(base, `/api/skin-analysis/${analysisId}`);

  const res = await fetch(url, {
    method: 'GET',
    headers: {
      ...authHeaders(),
      Accept: 'application/json',
    },
  });

  const payload = await readPayload(res);

  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('분석 결과 조회 권한이 없습니다(401). 로그인/토큰을 확인해주세요.');
    }
    const msg = pickMessage(payload, `GET /api/skin-analysis/${analysisId} 실패 (${res.status})`);
    console.error('[analysis.get] HTTP ERROR', res.status, payload);
    throw new Error(msg);
  }

  try {
    return SkinAnalysisOutput.parse(payload);
  } catch {
    try {
      const data = payload?.data || payload;
      const parsedData = SkinAnalysisData.parse(data);
      return SkinAnalysisOutput.parse({
        code: res.status,
        success: true,
        message: payload?.message || 'ok',
        data: parsedData,
      });
    } catch (parseError) {
      console.error('[analysis.get] 파싱 실패:', parseError, payload);
      throw new Error('응답 데이터 형식이 올바르지 않습니다.');
    }
  }
}

/* =========================
 * 3) 이미지 바이너리 (GET /api/files/{file_id})
 * ========================= */

export async function getFileBlob(fileId: number): Promise<Blob> {
  if (!Number.isFinite(fileId) || fileId <= 0) throw new Error('fileId가 올바르지 않습니다.');

  const base = resolveBaseStrict();
  const url = joinUrl(base, `/api/files/${fileId}`);

  const res = await fetch(url, {
    method: 'GET',
    headers: {
      ...authHeaders(),
      Accept: 'image/*',
    },
  });

  if (!res.ok) {
    const payload = await readPayload(res);
    if (res.status === 401) {
      throw new Error('이미지에 접근할 권한이 없습니다(401). 로그인/토큰을 확인해주세요.');
    }
    const msg = pickMessage(payload, `GET /api/files/${fileId} 실패 (${res.status})`);
    console.error('[files.getBlob] HTTP ERROR', res.status, payload);
    throw new Error(msg);
  }

  return await res.blob();
}

export async function getFileObjectUrl(fileId: number): Promise<string> {
  const blob = await getFileBlob(fileId);
  return URL.createObjectURL(blob);
}

/* =========================
 * 4) 업로드 → 즉시 조회 (data만 반환)
 * ========================= */

export async function submitAndFetchResult(
  file: File,
  options?: { skinType?: string; minPrice?: number; maxPrice?: number }
): Promise<SkinAnalysisDataT> {
  const { analysisId } = await createAnalysis(file, options);
  const response = await getAnalysis(analysisId);
  return response.data;
}

/* =========================
 * 5) 업로드 → 조회 (envelope 반환)
 * ========================= */

export async function submit(
  file: File,
  options?: { skinType?: string; minPrice?: number; maxPrice?: number }
): Promise<SkinAnalysisOutputT> {
  const { analysisId } = await createAnalysis(file, options);

  const base = resolveBaseStrict();
  const url = joinUrl(base, `/api/skin-analysis/${analysisId}`);

  const res = await fetch(url, {
    method: 'GET',
    headers: {
      ...authHeaders(),
      Accept: 'application/json',
    },
  });

  const payload = await readPayload(res);

  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('분석 결과 조회 권한이 없습니다(401). 로그인/토큰을 확인해주세요.');
    }
    const msg = pickMessage(payload, `GET /api/skin-analysis/${analysisId} 실패 (${res.status})`);
    console.error('[analysis.submit] HTTP ERROR', res.status, payload);
    throw new Error(msg);
  }

  try {
    return SkinAnalysisOutput.parse(payload);
  } catch {
    try {
      const data = payload?.data || payload;
      const parsedData = SkinAnalysisData.parse(data);
      return SkinAnalysisOutput.parse({
        code: res.status,
        success: true,
        message: payload?.message || 'ok',
        data: parsedData,
      });
    } catch (parseError) {
      console.error('[analysis.submit] 파싱 실패:', parseError, payload);
      throw new Error('응답 데이터 형식이 올바르지 않습니다.');
    }
  }
}

export const analysisApi = {
  create: createAnalysis,
  get: getAnalysis,
  submitAndFetchResult,
  submit,
  getFileBlob,
  getFileObjectUrl,
};
