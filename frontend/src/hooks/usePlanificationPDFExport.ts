"use client";

import { pdf } from "@react-pdf/renderer";
import { createElement, useCallback, useState } from "react";

import { PlanificationPDF } from "@/components/planification/PlanificationPDF";

type PlanificationExam = {
  matiere: string;
  date: string;
  heure_debut: string;
  heure_fin: string;
  salles: string[];
  groupes: string[];
  duree: number;
};

type ExportPayload = {
  session?: {
    type_session?: string | null;
    annee_universitaire?: string | null;
  };
  section?: {
    label?: string;
    effectif?: number;
  };
  semestre?: string;
  exams: PlanificationExam[];
};

type UsePlanificationPDFExportState = {
  exportPDF: (payload: ExportPayload) => Promise<void>;
  loading: boolean;
  error: string | null;
};

export function usePlanificationPDFExport(): UsePlanificationPDFExportState {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportPDF = useCallback(async (payload: ExportPayload) => {
    setLoading(true);
    setError(null);
    try {
      const doc = createElement(PlanificationPDF, payload) as unknown as Parameters<typeof pdf>[0];
      const blob = await pdf(doc).toBlob();
      
      const sessionLabel = payload.session?.type_session ?? "session";
      const sectionLabel = payload.section?.label ?? "section";
      const semestreLabel = payload.semestre ?? "semestre";
      const name = `planification-${sessionLabel}-${sectionLabel}-${semestreLabel}.pdf`
        .toLowerCase()
        .replace(/\s+/g, "-");
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = name;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, []);

  return { exportPDF, loading, error };
}
