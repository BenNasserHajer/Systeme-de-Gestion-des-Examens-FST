import type { Planification } from "@/lib/types/planification";

import { DataTable } from "@/components/ui/DataTable";
import { getPrimarySalle } from "@/lib/utils/planificationHelpers";

type EmploiDuTempsProps = {
  items: Planification[];
};

type PlanificationRow = {
  matiere: string;
  salle: string;
  date: string;
  statut: string;
};

export function EmploiDuTemps({ items }: EmploiDuTempsProps) {
  const rows: PlanificationRow[] = items.map((item) => ({
    matiere: item.matiere,
    salle: getPrimarySalle(item),
    date: formatDate(item.date_examen),
    statut: item.statut,
  }));

  return (
    <DataTable
      columns={[
        { key: "matiere", label: "Matiere" },
        { key: "salle", label: "Salle" },
        { key: "date", label: "Date" },
        { key: "statut", label: "Statut" },
      ]}
      rows={rows}
    />
  );
}

function formatDate(value: string): string {
  const date = new Date(`${value}T12:00:00`);
  return new Intl.DateTimeFormat("fr-FR", { dateStyle: "medium" }).format(date);
}
