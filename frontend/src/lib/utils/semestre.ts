import type { CatalogueMatiere } from "@/lib/api/referentiel";

/** Normalize UI semestre (S1, S2) for comparison with DB values like "2025/2026-S1". */
export function normalizeSemestreCode(semestre: string): string {
  const value = semestre.trim().toUpperCase();
  if (value.startsWith("S")) {
    return value;
  }
  return `S${value}`;
}

export function matiereMatchesSemestre(
  matiereSemestre: string | undefined,
  selectedSemestre: string,
): boolean {
  if (!matiereSemestre?.trim()) {
    return true;
  }
  const code = normalizeSemestreCode(selectedSemestre);
  const raw = matiereSemestre.trim().toUpperCase();
  return raw === code || raw.endsWith(`-${code}`);
}

export function filterMatieresForSemestre(
  matieres: CatalogueMatiere[],
  selectedSemestre: string,
): CatalogueMatiere[] {
  return matieres.filter((m) => matiereMatchesSemestre(m.semestre, selectedSemestre));
}
