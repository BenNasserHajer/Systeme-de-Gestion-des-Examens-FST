"use client";

import { ChargeTable } from "@/components/surveillance/ChargeTable";
import { useSurveillance } from "@/hooks/useSurveillance";

export default function SurveillancePage() {
  const { items, charges, loading, error } = useSurveillance();

  return (
    <section className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-900">Surveillance</h2>
      {loading && <p className="text-sm text-slate-600">Chargement...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      <p className="text-sm text-slate-600">
        Affectations enregistrees: {items.length}
      </p>

      <ChargeTable charges={charges} />
    </section>
  );
}
