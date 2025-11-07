// /src/lib/http.ts
type HttpOptions = {
  method?: string;
  headers?: HeadersInit;
  json?: unknown;       // JSON 바디로 보낼 때
  body?: BodyInit;      // FormData나 Blob 등으로 보낼 때
  withAuth?: boolean;   // 기본 true
  throwOnNonOK?: boolean; // 기본 true
};

export async function http<T = any>(path: string, opts: HttpOptions = {}): Promise<T> {
  const {
    method = 'GET',
    headers,
    json,
    body,
    withAuth = true,
    throwOnNonOK = true,
  } = opts;

  const base = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/+$/, '');

  // 절대 URL이면 그대로, 아니면 base와 결합
  const url = /^https?:\/\//i.test(path) ? path : `${base}${path}`;

  const h = new Headers(headers);

  // JSON VS FormData 바디 설정
  let finalBody: BodyInit | undefined = body as BodyInit | undefined;
  if (json !== undefined) {
    // json이 오면 JSON으로 보냄
    h.set('Content-Type', 'application/json');
    finalBody = JSON.stringify(json);
  } else if (finalBody instanceof FormData) {
    // FormData는 Content-Type 자동 설정(절대 수동 지정 X)
  }

  // 토큰 자동 첨부
  if (withAuth) {
    const at = typeof window !== 'undefined' ? localStorage.getItem('accessToken') : null;
    if (at) h.set('Authorization', `Bearer ${at}`);
  }

  const res = await fetch(url, {
    method,
    headers: h,
    body: finalBody,
    // 쿠키 세션 기반이면:
    // credentials: 'include',
  });

  const contentType = res.headers.get('Content-Type') || '';
  const isJson = contentType.toLowerCase().includes('application/json');
  const payload = isJson ? await res.json().catch(() => ({})) : await res.text().catch(() => '');

  if (!res.ok && throwOnNonOK) {
    const msg = isJson ? (payload?.message || JSON.stringify(payload)) : String(payload);
    throw new Error(msg || `HTTP ${res.status}`);
  }

  return payload as T;
}
