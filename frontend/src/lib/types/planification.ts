export type Planification = {
  id: number;
  matiere: string;
  salle: string;
  date_examen: string;
  statut: string;
  created_at: string;
};

export type PlanificationCreatePayload = {
  matiere: string;
  salle: string;
  date_examen: string;
};
