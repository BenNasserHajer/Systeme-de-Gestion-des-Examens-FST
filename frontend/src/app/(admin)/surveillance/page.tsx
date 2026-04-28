"use client";

import Link from "next/link";

import { ChargeTable } from "@/components/surveillance/ChargeTable";
import { Button } from "@/components/ui/Button";
import { Layout } from "@/components/ui/Layout";
import { useSurveillance } from "@/hooks/useSurveillance";
import { useSearchParams } from "next/navigation";

export default function SurveillancePage() {
  const searchParams = useSearchParams();
  const sessionParam = searchParams.get("sessionId") ?? searchParams.get("session_id");
  const sessionId = sessionParam ? Number(sessionParam) : null;
  const validSessionId = Number.isFinite(sessionId ?? NaN) ? sessionId : null;
  const { items, charges, loading, error } = useSurveillance(validSessionId);

  return (
    <Layout
      title="Surveillance"
      subtitle="Pilotage des affectations et convocations"
      actions={
        <Link href={validSessionId ? `/surveillance/charge?sessionId=${validSessionId}` : "/surveillance/charge"}>
          <Button variant="secondary">Voir les charges</Button>
        </Link>
      }
    >
      {loading && <p className="text-sm text-slate-600">Chargement...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {!validSessionId && (
        <p className="text-sm text-amber-600">
          Ajoutez un paramètre sessionId dans l’URL pour charger les données.
        </p>
      )}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Link
          className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-medium text-slate-700 hover:bg-slate-50"
          href={validSessionId ? `/surveillance/affectation?sessionId=${validSessionId}` : "/surveillance/affectation"}
        >
          Lancer une affectation
        </Link>
        <Link
          className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-medium text-slate-700 hover:bg-slate-50"
          href={validSessionId ? `/surveillance/charge?sessionId=${validSessionId}` : "/surveillance/charge"}
        >
          Tableau des charges
        </Link>
        <Link
          className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-medium text-slate-700 hover:bg-slate-50"
          href="/surveillance/1/convocation"
        >
          Convocation enseignant
        </Link>
      </div>

      <p className="text-sm text-slate-600">Affectations enregistrées: {items.length}</p>

      <ChargeTable charges={charges} />
    </Layout>
  );
}
