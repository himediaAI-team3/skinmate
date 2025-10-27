import type {
  AnalysisHistory,
  Paged,
  GetHistoryParams,
} from '@/entities/history';

const API = process.env.API_PROXY_TARGET || 'http://192.168.0.182:8000';

/** 공용 페이지 응답 정규화 */
function normalizePage<T>(raw: any): Paged<T> {
  // 케이스 0: { code, success, message, data: { items, total, page, size }, ... }
  if (raw?.data?.items && typeof raw.data.total === 'number') {
    const d = raw.data;
    const size = d.size ?? d.items?.length ?? 0;
    return {
      items: d.items,
      page: d.page ?? 1,
      size,
      total: d.total,
      totalPages: Math.max(1, Math.ceil((d.total ?? 0) / Math.max(1, size))),
    };
  }
  // 기존 케이스들
  if (raw?.items && typeof raw.total === 'number') {
    return {
      items: raw.items,
      page: raw.page ?? 1,
      size: raw.size ?? raw.items?.length ?? 0,
      total: raw.total,
      totalPages:
        raw.totalPages ??
        Math.max(1, Math.ceil((raw.total ?? 0) / Math.max(1, raw.size ?? 1))),
    };
  }
  if (raw?.content && typeof raw.totalElements === 'number') {
    return {
      items: raw.content,
      page: (raw.number ?? 0) + 1,
      size: raw.size ?? raw.content?.length ?? 0,
      total: raw.totalElements,
      totalPages:
        raw.totalPages ??
        Math.max(
          1,
          Math.ceil((raw.totalElements ?? 0) / Math.max(1, raw.size ?? 1)),
        ),
    };
  }
  if (Array.isArray(raw)) {
    return { items: raw, page: 1, size: raw.length, total: raw.length, totalPages: 1 };
  }
  return { items: [], page: 1, size: 0, total: 0, totalPages: 1 };
}

/** 분석 이력 조회: GET /api/skin-analysis/history/{member_id} */
export async function getAnalysisHistory(
  params: GetHistoryParams,
  init?: RequestInit,
): Promise<Paged<AnalysisHistory>> {
  const {
    member_id,
    page = 1,
    size = 10,
    disease_name = '',
    period = 'all',
  } = params;

  const member =
    member_id ??
    Number(process.env.NEXT_PUBLIC_TEST_MEMBER_ID ?? 1);

  const usp = new URLSearchParams();
  usp.set('page', String(page));
  usp.set('size', String(size));
  if (disease_name) usp.set('disease_name', disease_name);
  if (period) usp.set('period', period);

  const url = `${API}/api/skin-analysis/history/${member}?${usp.toString()}`;
  const res = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`히스토리 조회 실패(${res.status}): ${text}`);
  }
  const data = await res.json();

  const normalized = normalizePage<AnalysisHistory>(data);
  // 필드 매핑: analysis_id → id, created_at → analyzed_at, summary fallback
  normalized.items = normalized.items.map((x: any) => ({
    id: x.analysis_id ?? x.id, // ← 핵심
    member_id: x.member_id ?? member,
    disease_name: x.disease_name ?? x.diagnosis ?? '정상',
    summary: x.summary ?? x.title ?? x.note ?? x.disease_name ?? '', // ← 요약 없으면 질환명 사용
    analyzed_at: x.analyzed_at ?? x.created_at ?? x.date,
  }));
  return normalized;
}

/** 분석 이력 삭제: DELETE /api/skin-analysis/{analysis_id} */
export async function deleteAnalysis(
  analysis_id: number,
  init?: RequestInit,
): Promise<void> {
  const url = `${API}/api/skin-analysis/${analysis_id}`;
  const res = await fetch(url, {
    method: 'DELETE',
    cache: 'no-store',
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`삭제 실패(${res.status}): ${text}`);
  }
}
