"use client";

import { useMemo } from "react";
import { useParams, useSearchParams } from "next/navigation";

import { ConvocationCard } from "@/components/surveillance/ConvocationCard";
import { Layout } from "@/components/ui/Layout";
import { useConvocation } from "@/hooks/useConvocation";
import { usePDFExport } from "@/hooks/usePDFExport";

export default function ConvocationAdminPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const enseignantId = Number(params.enseignant_id);
  const validEnseignantId = Number.isFinite(enseignantId) ? enseignantId : null;

  const filters = useMemo(
    () => ({
      annee_universitaire: searchParams.get("annee_universitaire") ?? undefined,
      semestre: searchParams.get("semestre")
        ? Number(searchParams.get("semestre"))
        : undefined,
      type_epreuve: searchParams.get("type_epreuve") ?? undefined,
    }),
    [searchParams],
  );

  const { data, loading, error } = useConvocation(validEnseignantId, filters);
  const { exportPDF, loading: exporting, error: exportError } = usePDFExport();

  const enseignant = (data?.enseignant ?? {}) as {
    nom?: string;
    prenom?: string;
    grade?: string | null;
    departement?: { nom?: string | null } | string | null;
    email?: string | null;
  };

  const session = (data?.session ?? {}) as {
    type_session?: string | null;
    annee_universitaire?: string | null;
  };

  const assignments = Array.isArray(data?.surveillances)
    ? data.surveillances.map((item: Record<string, any>) => ({
        matiere: item?.matiere?.intitule ?? item?.matiere?.code ?? "—",
        date: item?.creneau?.date ?? "—",
        heure_debut: item?.creneau?.heure_debut ?? undefined,
        heure_fin: item?.creneau?.heure_fin ?? undefined,
        salle: item?.salle?.code ?? item?.salle?.designation ?? "—",
        groupe: item?.groupe?.numero ? `G${item.groupe.numero}` : "—",
        charge: item?.surveillance?.charge ?? item?.charge ?? undefined,
      }))
    : [];

  const canExport = validEnseignantId && enseignant.nom && enseignant.prenom;

  return (
    <Layout title="Convocation enseignant" subtitle="Vue détaillée des surveillances">
      {loading && <p className="text-sm text-slate-600">Chargement...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {exportError && <p className="text-sm text-red-600">{exportError}</p>}

      {!validEnseignantId && (
        <p className="text-sm text-amber-600">Enseignant ID manquant dans l’URL.</p>
      )}

      <ConvocationCard
        enseignant={{
          nom: enseignant.nom ?? "—",
          prenom: enseignant.prenom ?? "—",
          grade: enseignant.grade ?? null,
          departement:
            typeof enseignant.departement === "string"
              ? enseignant.departement
              : enseignant.departement?.nom ?? null,
          email: enseignant.email ?? null,
        }}
        session={session}
        assignments={assignments}
        onExport={
          canExport
            ? () =>
                exportPDF({
                  enseignant: {
                    nom: enseignant.nom ?? "—",
                    prenom: enseignant.prenom ?? "—",
                    grade: enseignant.grade ?? null,
                    departement:
                      typeof enseignant.departement === "string"
                        ? enseignant.departement
                        : enseignant.departement?.nom ?? null,
                    email: enseignant.email ?? null,
                  },
                  session,
                  assignments,
                })
            : undefined
        }
      />

      {exporting && <p className="text-xs text-slate-500">Génération du PDF...</p>}
    </Layout>
  );
}
