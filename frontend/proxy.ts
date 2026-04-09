import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const protectedPaths = ['/wardrobe', '/outfits', '/generate', '/create-outfit'];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Redirect root to login
  if (pathname === '/') {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Protect routes — check for token in cookies
  const isProtected = protectedPaths.some((p) => pathname.startsWith(p));
  if (isProtected) {
    const token = request.cookies.get('sw_token');
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|_next/data|favicon.ico).*)',
  ],
};
