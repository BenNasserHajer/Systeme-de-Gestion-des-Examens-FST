import type { Planification } from "@/lib/types/planification";

import { getPrimarySalle } from "@/lib/utils/planificationHelpers";

type PlanifCardProps = {
  item: Planification;
};

export function PlanifCard({ item }: PlanifCardProps) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="text-base font-semibold text-slate-900">{item.matiere}</h3>
      <p className="text-sm text-slate-600">Salle: {getPrimarySalle(item)}</p>
      <p className="text-sm text-slate-600">Date: {formatDate(item.date_examen)}</p>
      <p className="mt-2 inline-flex rounded-full bg-blue-100 px-2 py-1 text-xs font-semibold text-blue-700">
        {item.statut}
      </p>
    </article>
  );
}

function formatDate(value: string): string {
  const date = new Date(`${value}T12:00:00`);
  return new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium" }).format(date);
}
