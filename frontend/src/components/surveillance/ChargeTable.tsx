import { DataTable } from "@/components/ui/DataTable";
import type { TeacherCharge } from "@/lib/types/surveillance";

type ChargeTableProps = {
  charges: TeacherCharge;
};

type ChargeRow = {
  enseignant: string;
  charge: number;
};

export function ChargeTable({ charges }: ChargeTableProps) {
  const rows: ChargeRow[] = Object.entries(charges).map(([enseignant, charge]) => ({
    enseignant,
    charge,
  }));

  return (
    <DataTable
      columns={[
        { key: "enseignant", label: "Enseignant" },
        { key: "charge", label: "Charge" },
      ]}
      rows={rows}
    />
  );
}
