export type Surveillance = {
  id: number;
  planification_id: number;
  enseignant: string;
  charge: number;
  statut: string;
  created_at: string;
};

export type SurveillanceCreatePayload = {
  planification_id: number;
  enseignant: string;
  charge: number;
};

export type TeacherCharge = Record<string, number>;
