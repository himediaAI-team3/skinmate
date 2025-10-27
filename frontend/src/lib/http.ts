type Options = {
  method?: string;
  headers?: Record<string, string>;
  json?: unknown;            // body를 JSON으로 보낼 때
  credentials?: RequestCredentials; // 쿠키 인증이면 'include'
};

export async function http<T>(path: string, opts: Options = {}) {
  const { json, headers, ...rest } = opts;

  const init: RequestInit = {
    ...rest,
    headers: {
      ...(json ? { 'Content-Type': 'application/json' } : {}),
      ...headers,
    },
    body: json ? JSON.stringify(json) : undefined,
  };

  // 절대 URL이면 그대로 사용, 상대 경로면 Next.js 프록시 사용
  const url = path.startsWith('http') ? path : path;

  const res = await fetch(url, init);
  let data: any = null;
  try { data = await res.json(); } catch { /* empty */ }

  if (!res.ok) {
    const msg = data?.message || res.statusText;
    throw new Error(`API ${res.status}: ${msg}`);
  }
  return data as T;
}

