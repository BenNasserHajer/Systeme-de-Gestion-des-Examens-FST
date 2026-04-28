"use client";

import type { ReactNode } from "react";

type AuthGuardProps = {
  allowed: boolean;
  fallback?: ReactNode;
  children: ReactNode;
};

export function AuthGuard({ allowed, fallback, children }: AuthGuardProps) {
  if (!allowed) {
    return (
      fallback ?? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
          Accès non autorisé.
        </div>
      )
    );
  }

  return <>{children}</>;
}
