export type ModeAffectation = "AUTOMATIQUE" | "MANUELLE";

export type StatutSurveillance = "AFFECTE" | "CONFIRME";

export type ReasonExclusion =
  | "INDISPONIBLE"
  | "DEJA_AFFECTE"
  | "VOLUME_EPUISE"
  | "CONFLIT_MATIERE"
  | "HORS_DEPARTEMENT";

export type DisponibiliteType =
  | "DISPONIBLE"
  | "INDISPONIBLE"
  | "COURS_PREVU"
  | "MISSION"
  | "CONGE";

export type Departement = {
  id?: number | null;
  nom?: string | null;
  code?: string | null;
};

export type Niveau = {
  id?: number | null;
  libelle?: string | null;
  type_formation?: string | null;
};

export type Section = {
  id?: number | null;
  nom?: string | null;
  niveau?: Niveau | null;
};

export type Groupe = {
  id?: number | null;
  numero?: number | null;
  effectif?: number | null;
  nb_etudiants?: number | null;
  annee?: string | null;
};

export type Salle = {
  id?: number | null;
  code?: string | null;
  designation?: string | null;
  capacite?: number | null;
  batiment?: string | null;
};

export type Matiere = {
  id?: number | null;
  code?: string | null;
  intitule?: string | null;
  coefficient?: number | null;
  credit?: number | null;
  duree_examen?: number | null;
  duree_ds?: number | null;
};

export type Creneau = {
  id?: number | null;
  date?: string | null;
  heure_debut?: string | null;
  heure_fin?: string | null;
  libelle?: string | null;
};

export type Session = {
  id?: number | null;
  type_session?: string | null;
  annee_universitaire?: string | null;
  date_debut?: string | null;
  date_fin?: string | null;
  statut?: string | null;
};

export type Surveillance = {
  id: number;
  planification_id: number;
  enseignant_id: number;
  groupe_id?: number | null;
  salle_id?: number | null;
  charge: number;
  presence: boolean;
  mode_affectation: ModeAffectation | string;
  statut_surveillance: StatutSurveillance | string;
  est_externe: boolean;
  motif_externe?: string | null;
};

export type SurveillanceCreatePayload = {
  planification_id: number;
  enseignant_id: number;
  groupe_id?: number | null;
  salle_id?: number | null;
  charge?: number;
  mode_affectation?: ModeAffectation;
  statut_surveillance?: StatutSurveillance;
  est_externe?: boolean;
  motif_externe?: string | null;
};

export type SurveillanceUpdatePayload = {
  presence?: boolean | null;
  statut_surveillance?: StatutSurveillance | null;
  charge?: number | null;
  motif_externe?: string | null;
};

export type ManualAssignmentRequest = {
  session_id: number;
  planification_id: number;
  groupe_id: number;
  salle_id: number;
  enseignant_ids: number[];
  motifs_externes?: Record<number, string>;
};

export type ManualAssignmentItem = {
  planification_id: number;
  groupe_id: number;
  salle_id: number;
  enseignant_ids: number[];
};

export type ManualAssignmentBatchRequest = {
  session_id: number;
  affectations: ManualAssignmentItem[];
  motifs_externes?: Record<number, string>;
};

export type RaisonExclusion = {
  enseignant_id: number;
  nom: string;
  prenom: string;
  raison: ReasonExclusion | string;
  details?: string | null;
};

export type EnseignantAffecte = {
  surveillance_id: number;
  enseignant_id: number;
  nom: string;
  prenom: string;
  grade?: string | null;
  email?: string | null;
  telephone?: string | null;
  departement?: Departement | null;
  groupe?: Groupe | null;
  salle?: Salle | null;
  charge: number;
  mode_affectation: ModeAffectation | string;
  statut_surveillance: StatutSurveillance | string;
  presence: boolean;
  est_externe: boolean;
  motif_externe?: string | null;
};

export type GroupeResult = {
  groupe?: Groupe | null;
  salle?: Salle | null;
  statut: string;
  surveillants_affectes: EnseignantAffecte[];
  surveillants_requis: number;
  manquants: number;
};

export type AffecterSessionResult = {
  planification_id: number;
  type_epreuve?: string | null;
  semestre?: number | null;
  duree?: number | null;
  statut_planif?: string | null;
  nb_surveillants_requis?: number | null;
  matiere?: Matiere | null;
  section?: Section | null;
  departement_examen?: Departement | null;
  creneau?: Creneau | null;
  session?: Session | null;
  statut: string;
  surveillants_requis: number;
  surveillants_affectes: number;
  manquants: number;
  groupes?: GroupeResult[];
  raisons_exclusion?: RaisonExclusion[];
};

export type AffecterSessionResponse = {
  session_id: number;
  session?: Session | null;
  total_planifications: number;
  affectees_automatiquement: number;
  en_conflit: number;
  message: string;
  resultats: AffecterSessionResult[];
  non_affectees: AffecterSessionResult[];
};

export type AvertissementIndisponibilite = {
  date: string;
  heure_debut: string;
  heure_fin: string;
  type_dispo: string;
  motif?: string | null;
};

export type EnseignantDisponible = {
  enseignant_id: number;
  nom: string;
  prenom: string;
  grade?: string | null;
  email?: string | null;
  telephone?: string | null;
  volume_horaire: number;
  volume_consomme: number;
  volume_restant: number;
  nb_surveillances: number;
  a_avertissement: boolean;
  avertissements: AvertissementIndisponibilite[];
};

export type DepartementDisponibles = {
  departement_id?: number | null;
  departement_nom?: string | null;
  departement_code?: string | null;
  enseignants: EnseignantDisponible[];
  total: number;
};

export type EnseignantsDisponiblesResponse = {
  planification_id: number;
  date_planification: string;
  total_disponibles: number;
  total_avec_avertissement: number;
  departements: DepartementDisponibles[];
};

export type GetAllSurveillantsItem = {
  enseignant_id: number;
  nom: string;
  prenom: string;
  grade?: string | null;
  departement: Departement | Record<string, unknown>;
  volume_horaire: number;
  volume_consomme: number;
  volume_restant: number;
  nb_surveillances: number;
};

export type GetAllSurveillantsResponse = {
  data: GetAllSurveillantsItem[];
  pagination: Record<string, unknown>;
};

export type DisponibiliteItem = {
  date: string;
  heure_debut: string;
  heure_fin: string;
  type: string;
  motif?: string | null;
};

export type GetDisponibilitesResponse = {
  enseignant_id: number;
  date_debut: string;
  date_fin: string;
  disponibilites: DisponibiliteItem[];
};

export type DisponibiliteEnseignant = {
  id: number;
  enseignant_id: number;
  date: string;
  heure_debut: string;
  heure_fin: string;
  type_dispo: string;
  motif?: string | null;
  confirme: boolean;
};

export type DisponibiliteEnseignantCreatePayload = {
  enseignant_id: number;
  date: string;
  heure_debut: string;
  heure_fin: string;
  type_dispo: string;
  motif?: string | null;
  confirme?: boolean;
};

export type StatistiquesResponse = {
  annee_universitaire: string;
  total_surveillances: number;
  total_heures: number;
  unique_enseignants: number;
  count_externes: number;
  taux_externe: number;
  taux_remplissage: number;
};

export type TeacherCharge = Record<string, number>;
