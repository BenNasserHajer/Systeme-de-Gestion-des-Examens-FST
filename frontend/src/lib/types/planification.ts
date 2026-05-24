export type TypeEpreuve = "EXAMEN_FINAL" | "DS";
export type ModeAffectation = "AUTO" | "MANUEL";
export type StatutPlanification = "BROUILLON" | "VALIDEE" | "PUBLIEE";
export type StatutSession = "BROUILLON" | "VALIDEE" | "PUBLIEE";

export type PlanifSalle = {
  id?: number | null;
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
  semestre: string;
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
  a_examen_final: boolean;
  a_ds: boolean;
  created_at: string;
  updated_at: string;
  salles: PlanifSalle[];
  has_conflict?: boolean;
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
  semestre?: string;
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

export type ConflitDetail = {
  matiere?: string;
  contrainte?: string;
  message: string;
  suggestion?: string;
};

export type GenerationAutoResponse = {
  success: boolean;
  nb_crees: number;
  nb_conflits: number;
  planifications: Planification[];
  conflits: (ConflitDetail | string)[];
};

export type ValiderSessionResponse = {
  success: boolean;
  nb_planifications: number;
  statut: StatutPlanification;
  planifications: Planification[];
  erreurs: string[];
};

export type GenerationParams = {
  section_id: number;
  session_id: number;
  type_epreuve: TypeEpreuve;
  semestre: "S1" | "S2";
};
