"use client";

import { useCallback, useEffect, useState } from "react";

import { getEnseignantSurveillances } from "@/lib/api/surveillance";

type UseConvocationState = {
  data: Record<string, unknown> | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

type ConvocationFilters = {
  annee_universitaire?: string;
  semestre?: number;
  type_epreuve?: string;
};

export function useConvocation(
  enseignantId: number | null,
  filters: ConvocationFilters = {},
): UseConvocationState {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!enseignantId) {
      setData(null);
      setLoading(false);
      setError("Enseignant ID manquant");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await getEnseignantSurveillances(enseignantId, filters);
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [enseignantId, filters]);

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
