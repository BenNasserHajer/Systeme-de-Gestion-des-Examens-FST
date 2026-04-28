"use client";

import { useSearchParams } from "next/navigation";

import { ChargeTable } from "@/components/surveillance/ChargeTable";
import { Layout } from "@/components/ui/Layout";
import { useTeacherCharge } from "@/hooks/useTeacherCharge";

export default function ChargePage() {
  const searchParams = useSearchParams();
  const sessionParam = searchParams.get("sessionId") ?? searchParams.get("session_id");
  const sessionId = sessionParam ? Number(sessionParam) : null;
  const validSessionId = Number.isFinite(sessionId ?? NaN) ? sessionId : null;

  const { items, loading, error } = useTeacherCharge(validSessionId);

  return (
    <Layout title="Tableau des charges" subtitle="Suivi du volume de surveillance">
      {loading && <p className="text-sm text-slate-600">Chargement...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {!validSessionId && (
        <p className="text-sm text-amber-600">
          Ajoutez un paramètre sessionId dans l’URL pour charger les charges.
        </p>
      )}
      <ChargeTable items={items} />
    </Layout>
  );
}
