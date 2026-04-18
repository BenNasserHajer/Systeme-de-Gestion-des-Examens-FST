import type { Planification } from "@/lib/types/planification";

import { DataTable } from "@/components/ui/DataTable";
import { formatDate } from "@/lib/utils";

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
    salle: item.salle,
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
