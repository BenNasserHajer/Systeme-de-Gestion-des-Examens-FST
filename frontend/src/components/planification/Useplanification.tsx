"use client";

import { useEffect, useState, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Attribution {
  salle_id: number;
  salle_code: string;
  groupe_id: number;
  groupe_effectif: number;
}

export interface Planification {
  id: number;
  session_id: number;
  section_matiere_id: number;
  intitule: string;
  section_nom: string;
  departement_nom: string;
  date: string;
  heure_debut: string;
  heure_fin: string;
  type_epreuve: string;
  nb_groupes: number;
  score: number;
  statut: string; // "Planifié" | "Conflit" | "En attente"
  attributions: Attribution[];
}

export interface PlanifStats {
  total: number;
  conflits: number;
  sections: number;
  score_moyen: number | null;
}

interface UsePlanificationsReturn {
  planifications: Planification[];
  stats: PlanifStats;
  loading: boolean;
  error: string | null;
  refresh: () => void;
  generate: (sessionId: number) => Promise<void>;
  deletePlanif: (id: number) => Promise<void>;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function usePlanifications(sessionId?: number): UsePlanificationsReturn {
  const [planifications, setPlanifications] = useState<Planification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const url = sessionId
        ? `${API_BASE}/api/planifications/?session_id=${sessionId}`
        : `${API_BASE}/api/planifications/`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Erreur ${res.status}: ${res.statusText}`);
      const data: Planification[] = await res.json();
      setPlanifications(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Génération automatique
  const generate = useCallback(
    async (sid: number) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/api/planifications/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sid }),
        });
        if (!res.ok) {
          const detail = await res.json().catch(() => ({}));
          throw new Error(detail?.detail ?? `Erreur ${res.status}`);
        }
        await fetchData();
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Erreur inconnue");
        setLoading(false);
      }
    },
    [fetchData]
  );

  // Suppression
  const deletePlanif = useCallback(
    async (id: number) => {
      try {
        const res = await fetch(`${API_BASE}/api/planifications/${id}`, {
          method: "DELETE",
        });
        if (!res.ok) throw new Error(`Erreur ${res.status}`);
        setPlanifications((prev) => prev.filter((p) => p.id !== id));
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : "Erreur inconnue");
      }
    },
    []
  );

  // Stats calculées côté client
  const stats: PlanifStats = {
    total: planifications.length,
    conflits: planifications.filter((p) => p.statut === "Conflit").length,
    sections: new Set(planifications.map((p) => p.section_nom)).size,
    score_moyen:
      planifications.length > 0
        ? Math.round(
            planifications.reduce((s, p) => s + (p.score ?? 0), 0) /
              planifications.length
          )
        : null,
  };

  return {
    planifications,
    stats,
    loading,
    error,
    refresh: fetchData,
    generate,
    deletePlanif,
  };
}