
// hooks/useDashboard.ts
"use client";

import { useEffect, useState, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export interface DashboardStats {
  sessions_total: number;
  sessions_en_cours: number;
  planifications_total: number;
  conflits_total: number;
  salles_total: number;
  sections_total: number;
  enseignants_total: number;
  taux_succes: number;
}

export interface RecentPlanif {
  id: number;
  intitule: string;
  section_nom: string;
  date: string;
  statut: string;
}

export interface SessionInfo {
  id: number;
  nom: string;
  statut: string;
  date_debut: string;
  date_fin: string;
}

interface UseDashboardReturn {
  stats: DashboardStats | null;
  recents: RecentPlanif[];
  sessions: SessionInfo[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useDashboard(): UseDashboardReturn {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recents, setRecents] = useState<RecentPlanif[]>([]);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [planifRes, sallesRes, sessionsRes] = await Promise.all([
        fetch(`${API_BASE}/api/planifications/`),
        fetch(`${API_BASE}/api/salles/`),
        fetch(`${API_BASE}/api/sessions/`),
      ]);

      const planifs = planifRes.ok ? await planifRes.json() : [];
      const salles = sallesRes.ok ? await sallesRes.json() : [];
      const sessionsList = sessionsRes.ok ? await sessionsRes.json() : [];

      const conflits = planifs.filter((p: RecentPlanif) => p.statut === "Conflit").length;
      const sections = new Set(planifs.map((p: { section_nom: string }) => p.section_nom)).size;
      const taux = planifs.length > 0
        ? Math.round(((planifs.length - conflits) / planifs.length) * 100)
        : 0;

      setStats({
        sessions_total: sessionsList.length,
        sessions_en_cours: sessionsList.filter(
          (s: SessionInfo) => s.statut === "BROUILLON" || s.statut === "VALIDEE"
        ).length,
        planifications_total: planifs.length,
        conflits_total: conflits,
        salles_total: salles.length,
        sections_total: sections,
        enseignants_total: 0,
        taux_succes: taux,
      });

      setRecents(
        [...planifs]
          .sort((a: RecentPlanif, b: RecentPlanif) => b.id - a.id)
          .slice(0, 6)
      );
      setSessions(sessionsList.slice(0, 4));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return { stats, recents, sessions, loading, error, refresh: fetchAll };
}