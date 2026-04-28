"use client";

import { pdf } from "@react-pdf/renderer";
import { createElement, useCallback, useState } from "react";

import { ConvocationPDF } from "@/components/surveillance/ConvocationPDF";

type ConvocationAssignment = {
  matiere: string;
  date: string;
  heure_debut?: string;
  heure_fin?: string;
  salle?: string;
  groupe?: string;
  charge?: number;
};

type ExportPayload = {
  enseignant: {
    nom: string;
    prenom: string;
    grade?: string | null;
    departement?: string | null;
    email?: string | null;
  };
  session?: {
    type_session?: string | null;
    annee_universitaire?: string | null;
  };
  assignments: ConvocationAssignment[];
};

type UsePDFExportState = {
  exportPDF: (payload: ExportPayload) => Promise<void>;
  loading: boolean;
  error: string | null;
};

export function usePDFExport(): UsePDFExportState {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const exportPDF = useCallback(async (payload: ExportPayload) => {
    setLoading(true);
    setError(null);
    try {
      const doc = createElement(ConvocationPDF, payload) as unknown as Parameters<typeof pdf>[0];
      const blob = await pdf(doc).toBlob();
      const name = `convocation-${payload.enseignant.nom}-${payload.enseignant.prenom}.pdf`;
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
