"use client";

import { useCallback, useEffect, useState } from "react";

import { getAllSurveillants } from "@/lib/api/surveillance";
import type { GetAllSurveillantsItem, GetAllSurveillantsResponse } from "@/lib/types/surveillance";

type Pagination = {
  page: number;
  limit: number;
  total: number;
  pages: number;
};

type ChargeMeta = {
  sessionId: number;
  anneeUniversitaire: string;
  sessionLabel: string | null;
};

type UseTeacherChargeState = {
  items: GetAllSurveillantsItem[];
  pagination: Pagination | null;
  meta: ChargeMeta | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

export function useTeacherCharge(
  sessionId: number | null,
  options: { page?: number; limit?: number; sort?: string; order?: "asc" | "desc" } = {},
): UseTeacherChargeState {
  const [items, setItems] = useState<GetAllSurveillantsItem[]>([]);
  const [pagination, setPagination] = useState<Pagination | null>(null);
  const [meta, setMeta] = useState<ChargeMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!sessionId) {
      setItems([]);
      setPagination(null);
      setMeta(null);
      setLoading(false);
      setError("Session ID manquant");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data: GetAllSurveillantsResponse = await getAllSurveillants({
        session_id: sessionId,
        page: options.page ?? 1,
        limit: options.limit ?? 500,
        sort: options.sort ?? "charge_surveillance",
        order: options.order ?? "desc",
      });
      setItems(data.data);
      setPagination(data.pagination as Pagination);
      setMeta({
        sessionId: data.session_id,
        anneeUniversitaire: data.annee_universitaire,
        sessionLabel: data.session_label ?? null,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [options.limit, options.order, options.page, options.sort, sessionId]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void refresh();
    }, 0);

    return () => {
      window.clearTimeout(timer);
    };
  }, [refresh]);

  return { items, pagination, meta, loading, error, refresh };
}
