export const MODE_AFFECTATION_LABELS: Record<string, string> = {
  AUTOMATIQUE: "Automatique",
  MANUELLE: "Manuelle",
};

export const STATUT_SURVEILLANCE_LABELS: Record<string, string> = {
  AFFECTE: "Affecté",
  CONFIRME: "Confirmé",
};

export const DISPONIBILITE_TYPE_LABELS: Record<string, string> = {
  DISPONIBLE: "Disponible",
  INDISPONIBLE: "Indisponible",
  COURS_PREVU: "Cours prévu",
  MISSION: "Mission",
  CONGE: "Congé",
};

export const DISPONIBILITE_TYPE_BADGE: Record<string, string> = {
  DISPONIBLE: "bg-emerald-100 text-emerald-700",
  INDISPONIBLE: "bg-red-100 text-red-700",
  COURS_PREVU: "bg-amber-100 text-amber-700",
  MISSION: "bg-blue-100 text-blue-700",
  CONGE: "bg-slate-100 text-slate-700",
};

export const STATUT_SURVEILLANCE_BADGE: Record<string, string> = {
  AFFECTE: "bg-indigo-100 text-indigo-700",
  CONFIRME: "bg-emerald-100 text-emerald-700",
};

export const CHARGE_LEVELS = {
  low: { min: 0, max: 2, badge: "bg-emerald-100 text-emerald-700" },
  medium: { min: 2, max: 5, badge: "bg-amber-100 text-amber-700" },
  high: { min: 5, max: Number.POSITIVE_INFINITY, badge: "bg-red-100 text-red-700" },
};
