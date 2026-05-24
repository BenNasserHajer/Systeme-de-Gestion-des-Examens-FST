"use client";

import { useCallback, useEffect, useState } from "react";

import { getAllSurveillants, getSessionSurveillances } from "@/lib/api/surveillance";
import type { TeacherCharge } from "@/lib/types/surveillance";

export function useSurveillance(sessionId: number | null) {
  const [items, setItems] = useState<Array<Record<string, unknown>>>([]);
  const [charges, setCharges] = useState<TeacherCharge>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!sessionId) {
      setItems([]);
      setCharges({});
      setLoading(false);
      setError("Session ID manquant");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [surveillancesData, chargesData] = await Promise.all([
        getSessionSurveillances(sessionId),
        getAllSurveillants(sessionId),
      ]);
      setItems(surveillancesData.data ?? []);
      const chargeMap: TeacherCharge = {};
      for (const item of chargesData.data) {
        const key = `${item.prenom} ${item.nom}`.trim();
        chargeMap[key] = item.volume_restant ?? 0;
      }
      setCharges(chargeMap);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [refresh]);

  return { items, charges, loading, error, refresh };
}
