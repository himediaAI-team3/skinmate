// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  if (pathname === '/') {
    const seen = req.cookies.get('seenLanding')?.value;
    if (seen !== '1') {
      const url = req.nextUrl.clone();
      url.pathname = '/welcome';
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/'],
};