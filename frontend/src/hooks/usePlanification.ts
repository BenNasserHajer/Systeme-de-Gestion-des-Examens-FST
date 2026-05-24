"use client";

import { useCallback, useEffect, useState } from "react";

import {
  createPlanification,
  getPlanifications,
} from "@/lib/api/planification";
import type {
  Planification,
  PlanificationCreatePayload,
} from "@/lib/types/planification";

export function usePlanification() {
  const [items, setItems] = useState<Planification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPlanifications();
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  const createDraft = useCallback(async (payload: PlanificationCreatePayload) => {
    await createPlanification(payload);
    await refresh();
  }, [refresh]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [refresh]);

  return { items, loading, error, refresh, createDraft };
}
