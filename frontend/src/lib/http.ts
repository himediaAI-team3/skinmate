// /lib/http.ts
import { getAccessToken } from '@/features/auth'; // 이미 구현한 토큰 getter 사용

export type Options = {
  method?: string;
  headers?: Record<string, string>;
  json?: unknown;                 // body를 JSON으로 보낼 때
  body?: BodyInit | null;         // 바이너리/폼데이터 등 직접 보낼 때
  credentials?: RequestCredentials; // 쿠키 인증이면 'include'
  withAuth?: boolean;             // 기본 true: Authorization 자동 첨부
  throwOnNonOK?: boolean;         // 기본 true: !res.ok 이면 throw
  signal?: AbortSignal;           // 필요 시 AbortController 신호
};

export async function http<T>(path: string, opts: Options = {}) {
  const {
    json,
    body,
    headers,
    method = 'GET',
    credentials,
    withAuth = true,
    throwOnNonOK = true,
    signal,
  } = opts;

  // 헤더 구성
  const h = new Headers(headers ?? {});
  if (json !== undefined && !h.has('content-type')) {
    h.set('content-type', 'application/json');
  }

  // Authorization 자동 첨부
  if (withAuth) {
    const at = getAccessToken();
    if (at) h.set('Authorization', `Bearer ${at}`);
  }

  // 절대/상대 경로 그대로 사용(프록시는 Next/Vercel/Nginx에서 처리)
  const url = path;

  const res = await fetch(url, {
    method,
    headers: h,
    body: json !== undefined ? JSON.stringify(json) : body,
    credentials,
    signal,
  });

  // 컨텐츠 타입 판단
  const isJson = (res.headers.get('content-type') || '').includes('application/json');

  // 오류 처리
  if (throwOnNonOK && !res.ok) {
    let detail: any = undefined;
    try {
      detail = isJson ? await res.json() : await res.text();
    } catch {
      /* ignore */
    }
    const msg =
      (isJson ? detail?.message : undefined) ||
      res.statusText ||
      'Request failed';

    const err = new Error(`API ${res.status}: ${msg}`);
    (err as any).status = res.status;
    (err as any).detail = detail;
    throw err;
  }

  // No Content
  if (res.status === 204 || res.status === 205) {
    return undefined as T;
  }

  // 성공 응답 파싱
  if (isJson) {
    return (await res.json()) as T;
  }
  // JSON이 아닌 응답을 기대한다면 호출부에서 제네릭 T를 string 등으로 지정
  const text = await res.text();
  return text as unknown as T;
}
