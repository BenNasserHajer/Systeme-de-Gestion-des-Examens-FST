"use client";

import { useCallback, useEffect, useState } from "react";

import {
  createSurveillance,
  getSurveillances,
  getTeacherCharges,
} from "@/lib/api/surveillance";
import type {
  Surveillance,
  SurveillanceCreatePayload,
  TeacherCharge,
} from "@/lib/types/surveillance";

export function useSurveillance() {
  const [items, setItems] = useState<Surveillance[]>([]);
  const [charges, setCharges] = useState<TeacherCharge>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [surveillancesData, chargesData] = await Promise.all([
        getSurveillances(),
        getTeacherCharges(),
      ]);
      setItems(surveillancesData);
      setCharges(chargesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  const createAssignment = useCallback(
    async (payload: SurveillanceCreatePayload) => {
      await createSurveillance(payload);
      await refresh();
    },
    [refresh],
  );

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [refresh]);

  return { items, charges, loading, error, refresh, createAssignment };
}
