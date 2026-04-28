"use client";

import { EmploiDuTemps } from "@/components/planification/EmploiDuTemps";
import { GroupeTable } from "@/components/planification/GroupeTable";
import { PlanifCard } from "@/components/planification/PlanifCard";
import { usePlanification } from "@/hooks/usePlanification";

export default function PlanificationPage() {
  const { items, loading, error } = usePlanification();

  return (
    <section className="space-y-6">
      <h2 className="text-xl font-semibold text-slate-900">Planification</h2>
      {loading && <p className="text-sm text-slate-600">Chargement...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {items.slice(0, 3).map((item) => (
          <PlanifCard key={item.id} item={item} />
        ))}
      </div>

      <EmploiDuTemps items={items} />
      <GroupeTable />
    </section>
  );
}
