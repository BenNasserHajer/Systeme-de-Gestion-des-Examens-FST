export type TypeEpreuve = "EXAMEN_FINAL" | "DS";
export type ModeAffectation = "AUTO" | "MANUEL";
export type StatutPlanification = "BROUILLON" | "VALIDEE" | "PUBLIEE";
export type StatutSession = "BROUILLON" | "VALIDEE" | "PUBLIEE";

export type PlanifSalle = {
  id: number;
  salle_id: string;
  salle_capacite: number;
  salle_batiment: string | null;
  salle_departement_id: number | null;
  groupe_id: number;
  groupe_effectif: number;
  creneau_date: string;
  heure_debut: string;
};

export type Planification = {
  id: number;
  session_id: number;
  section_id: number;
  section_matiere_id: number;
  section_departement_id: number | null;
  matiere: string;
  type_epreuve: TypeEpreuve;
  mode_affectation: ModeAffectation;
  statut: StatutPlanification;
  date_examen: string;
  heure_debut: string;
  heure_fin: string;
  session_date_debut: string;
  session_date_fin: string;
  session_statut: StatutSession;
  duree: number;
  coefficient: number;
  section_nb_etudiants: number;
  nb_groupes: number;
  nb_surveillants_requis: number;
  created_at: string;
  updated_at: string;
  salles: PlanifSalle[];
};

export type PlanifSalleAssign = {
  salle_id: string;
  salle_capacite: number;
  salle_batiment?: string | null;
  salle_departement_id?: number | null;
  groupe_id: number;
  groupe_effectif: number;
};

export type PlanificationCreatePayload = {
  session_id: number;
  section_id: number;
  section_matiere_id: number;
  section_departement_id?: number | null;
  matiere: string;
  type_epreuve: TypeEpreuve;
  mode_affectation?: ModeAffectation;
  statut?: StatutPlanification;
  date_examen: string;
  heure_debut: string;
  heure_fin: string;
  session_date_debut: string;
  session_date_fin: string;
  session_statut?: StatutSession;
  duree?: number;
  coefficient?: number;
  section_nb_etudiants: number;
  nb_groupes?: number;
  nb_surveillants_requis?: number;
  salles?: PlanifSalleAssign[];
};

export type PlanificationUpdatePayload = {
  date_examen?: string;
  heure_debut?: string;
  heure_fin?: string;
  statut?: StatutPlanification;
  mode_affectation?: ModeAffectation;
  duree?: number;
  nb_groupes?: number;
  nb_surveillants_requis?: number;
  salles?: PlanifSalleAssign[];
};
