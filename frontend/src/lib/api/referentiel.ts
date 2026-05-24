const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export type CatalogueSection = {
  label: string;
  section_id: number;
  effectif: number;
  niveau: string;
};

export type CatalogueMatiere = {
  section_matiere_id: number;
  matiere: string;
  /** DB annee_sem e.g. "2025/2026-S1" or "S1" */
  semestre?: string;
  coefficient: number;
  duree: number;
  nb_surveillants_requis: number;
  a_examen_final: boolean;
  a_ds: boolean;
};

export type CatalogueSession = {
  label: string;
  session_id: number;
  date_debut: string;
  date_fin: string;
  statut: string;
};

export type CatalogueSalle = {
  salle_id: string;
  capacite: number;
  batiment?: string;
  disponible?: boolean;
  motif_indisponible?: string | null;
};

export type TypeEpreuveOption = {
  value: "EXAMEN_FINAL" | "DS";
  label: string;
};

export type Catalogue = {
  source: string;
  message?: string;
  sessions: CatalogueSession[];
  sections: CatalogueSection[];
  semestres: string[];
  types_epreuve: TypeEpreuveOption[];
  matieres_by_section: Record<string, CatalogueMatiere[]>;
  salles: CatalogueSalle[];
  creneaux: { date_examen: string; heure_debut: string; heure_fin: string }[];
};

export async function getCatalogue(): Promise<Catalogue> {
  const response = await fetch(`${API_BASE}/referentiel/catalogue`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Impossible de charger le catalogue depuis la base");
  }
  return response.json();
}

export async function getSallesDisponibles(params: {
  date_examen: string;
  heure_debut: string;
  capacite_min?: number;
  exclude_planif_id?: number;
  toutes_les_salles?: boolean;
}): Promise<CatalogueSalle[]> {
  const query = new URLSearchParams({
    date_examen: params.date_examen,
    heure_debut: params.heure_debut,
    capacite_min: String(params.capacite_min ?? 1),
    toutes_les_salles: String(params.toutes_les_salles ?? true),
  });
  if (params.exclude_planif_id !== undefined) {
    query.set("exclude_planif_id", String(params.exclude_planif_id));
  }
  const response = await fetch(`${API_BASE}/referentiel/salles-disponibles?${query}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Impossible de charger les salles disponibles");
  }
  return response.json();
}
