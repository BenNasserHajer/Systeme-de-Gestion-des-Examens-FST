import { DataTable } from "@/components/ui/DataTable";
import type { GetAllSurveillantsItem, TeacherCharge } from "@/lib/types/surveillance";

type ChargeTableProps = {
  charges?: TeacherCharge;
  items?: GetAllSurveillantsItem[];
};

type ChargeRow = {
  enseignant: string;
  departement?: string;
  grade?: string;
  volume_annuel?: string;
  charge_surveillance?: string;
  volume_restant?: string;
  taux_utilisation?: string;
  nb_surveillances?: number;
  charge?: number;
};

function formatHeures(value: number | undefined): string {
  if (value === undefined) {
    return "—";
  }
  return `${value.toFixed(1)} h`;
}

function formatTaux(value: number | undefined): string {
  if (value === undefined) {
    return "—";
  }
  return `${value.toFixed(1)} %`;
}

export function ChargeTable({ charges, items }: ChargeTableProps) {
  const rows: ChargeRow[] = items
    ? items.map((item) => {
        const volumeAnnuel = item.volume_annuel ?? item.volume_horaire;
        const chargeSurv = item.charge_surveillance ?? item.volume_consomme;
        return {
          enseignant: `${item.prenom} ${item.nom}`.trim(),
          departement:
            typeof item.departement === "object"
              ? ((item.departement as { nom?: string | null }).nom ?? "")
              : "",
          grade: item.grade ?? "",
          volume_annuel: formatHeures(volumeAnnuel),
          charge_surveillance: formatHeures(chargeSurv),
          volume_restant: formatHeures(item.volume_restant),
          taux_utilisation: formatTaux(item.taux_utilisation),
          nb_surveillances: item.nb_surveillances,
        };
      })
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
              { key: "grade", label: "Grade" },
              { key: "volume_annuel", label: "Volume annuel" },
              { key: "charge_surveillance", label: "Charge surveillance" },
              { key: "volume_restant", label: "Restant" },
              { key: "taux_utilisation", label: "Taux" },
              { key: "nb_surveillances", label: "Nb surveillances" },
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

export function ChargeSummaryCards({
  items,
  anneeUniversitaire,
}: {
  items: GetAllSurveillantsItem[];
  anneeUniversitaire: string;
}) {
  const totalAnnuel = items.reduce(
    (sum, i) => sum + (i.volume_annuel ?? i.volume_horaire),
    0,
  );
  const totalCharge = items.reduce(
    (sum, i) => sum + (i.charge_surveillance ?? i.volume_consomme),
    0,
  );
  const totalRestant = items.reduce((sum, i) => sum + i.volume_restant, 0);
  const tauxGlobal =
    totalAnnuel > 0 ? Math.round((totalCharge / totalAnnuel) * 1000) / 10 : 0;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <SummaryCard
        label="Année universitaire"
        value={anneeUniversitaire}
        hint="Périmètre de calcul"
      />
      <SummaryCard
        label="Volume annuel total"
        value={formatHeures(totalAnnuel)}
        hint="Quota surveillance alloué"
      />
      <SummaryCard
        label="Charge surveillance totale"
        value={formatHeures(totalCharge)}
        hint="Heures déjà affectées"
      />
      <SummaryCard
        label="Taux global"
        value={`${tauxGlobal} %`}
        hint={`${formatHeures(totalRestant)} restantes`}
      />
    </div>
  );
}

function SummaryCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-slate-900">{value}</p>
      <p className="mt-1 text-xs text-slate-500">{hint}</p>
    </div>
  );
}
