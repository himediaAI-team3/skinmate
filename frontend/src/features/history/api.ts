// /src/features/history/index.ts
'use client';

import { getAccessToken } from '@/features/auth';
import {
  ApiResponseHistoryPage,
  type AnalysisHistory,
  type GetHistoryParams,
  type Paged,
} from '@/entities/history';

/* ============ 공통 유틸 ============ */
function base(): string {
  const B = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/+$/, '');
  if (!B) throw new Error('env 누락: NEXT_PUBLIC_API_URL (예: http://127.0.0.1:8000)');
  return B;
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

function normalizeToPaged<T>(raw: any): Paged<T> {
  // { code, success, message, data: { items, total, page, size } } 전제
  const parsed = ApiResponseHistoryPage.safeParse(raw);
  if (parsed.success) {
    const d = parsed.data.data;
    const size = d.size ?? d.items?.length ?? 0;
    return {
      items: d.items as unknown as T[],
      page: d.page ?? 1,
      size,
      total: d.total ?? 0,
      totalPages: Math.max(1, Math.ceil((d.total ?? 0) / Math.max(1, size || 1))),
    };
  }

  // 혹시 다른 형태면 최대한 방어
  if (raw?.data?.items && typeof raw.data.total === 'number') {
    const d = raw.data;
    const size = d.size ?? d.items?.length ?? 0;
    return {
      items: d.items,
      page: d.page ?? 1,
      size,
      total: d.total,
      totalPages: Math.max(1, Math.ceil((d.total ?? 0) / Math.max(1, size || 1))),
    };
  }
  return { items: [], page: 1, size: 0, total: 0, totalPages: 1 };
}

/* ============ 이력 조회: GET /api/skin-analysis/history (JWT) ============ */
export async function getAnalysisHistory(params: GetHistoryParams): Promise<Paged<AnalysisHistory>> {
  const {
    page = 1,
    size = 10,
    disease_name = '',
    period = 'all',
  } = params || {};

  const q = new URLSearchParams();
  q.set('page', String(page));
  q.set('size', String(size));
  if (disease_name) q.set('disease_name', disease_name);
  if (period) q.set('period', period);

  const url = `${base()}/api/skin-analysis/history?${q.toString()}`;

  const res = await fetch(url, {
    method: 'GET',
    headers: {
      ...authHeaders(),
      Accept: 'application/json',
    },
  });

  const payload = await readPayload(res);

  if (res.status === 401) {
    throw new Error('인증이 필요합니다. 다시 로그인해 주세요.');
  }
  if (!res.ok) {
    const msg = (payload && (payload.message || payload.detail)) || `HTTP ${res.status}`;
    throw new Error(`분석 이력 조회 실패: ${msg}`);
  }

  // 표준 페이지 구조로 정규화 → UI 타입으로 매핑
  const pageData = normalizeToPaged<any>(payload);
  const items: AnalysisHistory[] = (pageData.items || []).map((x: any) => ({
    id: x.analysis_id,
    disease_name: x.disease_name,
    analyzed_at: x.created_at,
    summary: x.disease_name || '분석 결과',
  }));

  return {
    ...pageData,
    items,
  };
}

/* ============ 삭제: DELETE /api/skin-analysis/{analysis_id} (JWT) ============ */
export async function deleteAnalysis(analysis_id: number): Promise<void> {
  if (!Number.isFinite(analysis_id) || analysis_id <= 0) {
    throw new Error('analysis_id가 올바르지 않습니다.');
  }

  const url = `${base()}/api/skin-analysis/${analysis_id}`;
  const res = await fetch(url, {
    method: 'DELETE',
    headers: {
      ...authHeaders(),
      Accept: 'application/json',
    },
  });

  const payload = await readPayload(res);

  if (res.status === 401) {
    throw new Error('인증이 필요합니다. 다시 로그인해 주세요.');
  }
  if (!res.ok) {
    const msg = (payload && (payload.message || payload.detail)) || `HTTP ${res.status}`;
    throw new Error(`삭제 실패: ${msg}`);
  }
}
