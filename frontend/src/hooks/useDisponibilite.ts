"use client";

import { useCallback, useEffect, useState } from "react";

import { getEnseignantDisponibilites } from "@/lib/api/surveillance";
import type { GetDisponibilitesResponse } from "@/lib/types/surveillance";

type UseDisponibiliteState = {
  data: GetDisponibilitesResponse | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

export function useDisponibilite(
  enseignantId: number | null,
  dateDebut: string | null,
  dateFin: string | null,
): UseDisponibiliteState {
  const [data, setData] = useState<GetDisponibilitesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!enseignantId || !dateDebut || !dateFin) {
      setData(null);
      setLoading(false);
      setError("Paramètres manquants");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await getEnseignantDisponibilites(enseignantId, dateDebut, dateFin);
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [dateDebut, dateFin, enseignantId]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [refresh]);

  return { data, loading, error, refresh };
}
