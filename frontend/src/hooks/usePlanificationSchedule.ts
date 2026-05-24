"use client";

import { useCallback, useEffect, useState } from "react";

import type { Catalogue } from "@/lib/api/referentiel";
import { getCatalogue } from "@/lib/api/referentiel";
import { genererAuto, getEmploiDuTemps, validerSession } from "@/lib/api/planification";
import type {
  GenerationAutoResponse,
  GenerationParams,
  Planification,
} from "@/lib/types/planification";

export function usePlanificationSchedule() {
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [items, setItems] = useState<Planification[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [sectionId, setSectionId] = useState<number | null>(null);
  const [semestre, setSemestre] = useState<GenerationParams["semestre"]>("S1");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generationResult, setGenerationResult] = useState<GenerationAutoResponse | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);

  useEffect(() => {
    void getCatalogue()
      .then((data) => {
        setCatalogue(data);
        setSessionId(data.sessions[0]?.session_id ?? null);
        setSectionId(data.sections[0]?.section_id ?? null);
        setSemestre((data.semestres[0] as GenerationParams["semestre"]) ?? "S1");
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Erreur catalogue");
      });
  }, []);

  const refreshSchedule = useCallback(
    async (sid?: number | null, secId?: number | null) => {
      const effectiveSession = sid ?? sessionId;
      if (!effectiveSession) {
        setItems([]);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const data = await getEmploiDuTemps(effectiveSession, {
          section_id: secId ?? sectionId ?? undefined,
        });
        setItems(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur emploi du temps");
      } finally {
        setLoading(false);
      }
    },
    [sessionId, sectionId],
  );

  useEffect(() => {
    if (sessionId && sectionId) {
      void refreshSchedule(sessionId, sectionId);
    }
  }, [sessionId, sectionId, refreshSchedule]);

  const generate = useCallback(async (params: GenerationParams) => {
    setLoading(true);
    setError(null);
    setGenerationResult(null);
    setWarnings([]);
    try {
      const result = await genererAuto(params);
      setGenerationResult(result);
      setSessionId(params.session_id);
      setSectionId(params.section_id);
      setSemestre(params.semestre);
      setItems(result.planifications);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Echec generation");
    } finally {
      setLoading(false);
    }
  }, []);

  const validateAll = useCallback(async () => {
    if (!sessionId) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await validerSession({
        session_id: sessionId,
        section_id: sectionId ?? undefined,
      });
      if (!result.success) {
        setError(result.erreurs.join(" · ") || "Validation echouee");
        return;
      }
      setItems(result.planifications);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Echec validation");
    } finally {
      setLoading(false);
    }
  }, [sessionId, sectionId]);

  return {
    catalogue,
    items,
    loading,
    error,
    generationResult,
    warnings,
    sessionId,
    sectionId,
    semestre,
    setSemestre,
    generate,
    validateAll,
    refreshSchedule,
    setWarnings,
  };
}
