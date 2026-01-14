import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { getKindeServerSession } from "@kinde-oss/kinde-auth-nextjs/server";

export async function middleware(request: NextRequest) {
  const { isAuthenticated } = getKindeServerSession();
  const authenticated = await isAuthenticated();

  if (!authenticated) {
    // Redirect to login with return URL
    const loginUrl = new URL('/api/auth/login', request.url);
    loginUrl.searchParams.set('post_login_redirect_url', request.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/document-selection/:path*",
    "/informed-consent/:path*", 
    "/site-checklist/:path*"
  ]
};
