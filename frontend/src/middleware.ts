/**
 * src/middleware.ts
 * Protection des routes :
 *   /enseignant/*     → réservé aux ENSEIGNANT
 *   /admin/*          → réservé aux ADMIN
 *   /planification/*  → interdit aux ENSEIGNANT
 *   /surveillance/*   → interdit aux ENSEIGNANT
 *   /salles/*         → interdit aux ENSEIGNANT
 */
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

function parseJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64 = token.split(".")[1];
    const json = Buffer.from(base64, "base64").toString("utf-8");
    return JSON.parse(json);
  } catch {
    return null;
  }
}

// Routes réservées aux ADMIN uniquement
const ADMIN_ONLY_ROUTES = [
  "/admin",
  "/planification",
  "/surveillance",
  "/salles",
];

// Routes réservées aux ENSEIGNANT uniquement
const ENSEIGNANT_ONLY_ROUTES = [
  "/enseignant",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isAdminRoute      = ADMIN_ONLY_ROUTES.some(r => pathname.startsWith(r));
  const isEnseignantRoute = ENSEIGNANT_ONLY_ROUTES.some(r => pathname.startsWith(r));

  // Si la route n'est pas protégée → laisser passer
  if (!isAdminRoute && !isEnseignantRoute) {
    return NextResponse.next();
  }

  // Chercher le token dans le cookie
  const token = request.cookies.get("access_token")?.value;

  // Pas de token → redirect login
  if (!token) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Token illisible → redirect login
  const payload = parseJwtPayload(token);
  if (!payload) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Token expiré → redirect login + supprime le cookie
  const exp = payload.exp as number | undefined;
  if (exp && Date.now() / 1000 > exp) {
    const res = NextResponse.redirect(new URL("/", request.url));
    res.cookies.delete("access_token");
    return res;
  }

  const type = payload.type as string;

  // ENSEIGNANT essaie d'accéder à une route admin → redirect login
  if (isAdminRoute && type !== "ADMIN") {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // ADMIN essaie d'accéder à une route enseignant → redirect login
  if (isEnseignantRoute && type !== "ENSEIGNANT") {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Tout est OK → laisser passer
  return NextResponse.next();
}

// Routes surveillées par le middleware
export const config = {
  matcher: [
    "/admin/:path*",
    "/enseignant/:path*",
    "/planification/:path*",
    "/surveillance/:path*",
    "/salles/:path*",
  ],
};