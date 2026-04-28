import { DataTable } from "@/components/ui/DataTable";
import type { GetAllSurveillantsItem, TeacherCharge } from "@/lib/types/surveillance";

type ChargeTableProps = {
  charges?: TeacherCharge;
  items?: GetAllSurveillantsItem[];
};

type ChargeRow = {
  enseignant: string;
  departement?: string;
  volume_horaire?: number;
  volume_consomme?: number;
  volume_restant?: number;
  nb_surveillances?: number;
  charge?: number;
};

export function ChargeTable({ charges, items }: ChargeTableProps) {
  const rows: ChargeRow[] = items
    ? items.map((item) => ({
        enseignant: `${item.prenom} ${item.nom}`.trim(),
        departement: typeof item.departement === "object"
          ? (item.departement as { nom?: string | null }).nom ?? ""
          : "",
        volume_horaire: item.volume_horaire,
        volume_consomme: item.volume_consomme,
        volume_restant: item.volume_restant,
        nb_surveillances: item.nb_surveillances,
      }))
    : Object.entries(charges ?? {}).map(([enseignant, charge]) => ({
        enseignant,
        charge,
      }));

  if (rows.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
        Aucune donnée de charge disponible.
      </div>
    );
  }

  return (
    <DataTable
      columns={
        items
          ? [
              { key: "enseignant", label: "Enseignant" },
              { key: "departement", label: "Département" },
              { key: "volume_horaire", label: "Volume horaire" },
              { key: "volume_consomme", label: "Consommé" },
              { key: "volume_restant", label: "Restant" },
              { key: "nb_surveillances", label: "Surveillances" },
            ]
          : [
              { key: "enseignant", label: "Enseignant" },
              { key: "charge", label: "Charge" },
            ]
      }
      rows={rows}
    />
  );
}
