import { DataTable } from "@/components/ui/DataTable";

type GroupRow = {
  groupe: string;
  effectif: number;
};

const rows: GroupRow[] = [
  { groupe: "INF/IOT G1", effectif: 15 },
  { groupe: "INF/IOT G2", effectif: 14 },
];

export function GroupeTable() {
  return (
    <DataTable
      columns={[
        { key: "groupe", label: "Groupe" },
        { key: "effectif", label: "Effectif" },
      ]}
      rows={rows}
    />
  );
}
