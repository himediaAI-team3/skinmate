import type { ApiListResponse, DiagnosisSummary } from '@/app/entities/history';

const API = process.env.API_PROXY_TARGET;

// 진단 이력 조회 (커서 기반)
export async function fetchDiagnosisHistory(cursor?: string | null): Promise<ApiListResponse<DiagnosisSummary>> {
  const url = new URL(`${API}/api/hisroty`);
  if (cursor) url.searchParams.set('cursor', cursor);

  const res = await fetch(url.toString(), {
    method: 'GET',
    credentials: 'include',     // JWT HttpOnly 쿠키 전송
    headers: { Accept: 'application/json' },
    cache: 'no-store',
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `HTTP ${res.status}`);
  }

  const json = (await res.json()) as ApiListResponse<DiagnosisSummary>;
  if (!json?.success) throw new Error(json?.message || '진단 이력 조회 실패');
  return json;
}
