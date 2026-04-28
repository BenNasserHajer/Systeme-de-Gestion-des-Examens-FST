"use client";

import { useMemo } from "react";
import { useSearchParams } from "next/navigation";

import { ConvocationCard } from "@/components/surveillance/ConvocationCard";
import { DisponibiliteForm } from "@/components/surveillance/DisponibiliteForm";
import { Layout } from "@/components/ui/Layout";
import { useConvocation } from "@/hooks/useConvocation";
import { useDisponibilite } from "@/hooks/useDisponibilite";
import { usePDFExport } from "@/hooks/usePDFExport";
import { createDisponibilite } from "@/lib/api/surveillance";

export default function ConvocationPage() {
  const searchParams = useSearchParams();
  const enseignantParam = searchParams.get("enseignantId") ?? searchParams.get("enseignant_id");
  const enseignantId = enseignantParam ? Number(enseignantParam) : null;
  const validEnseignantId = Number.isFinite(enseignantId ?? NaN) ? enseignantId : null;

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

  const { dateDebut, dateFin } = useMemo(() => {
    return {
      dateDebut: searchParams.get("date_debut"),
      dateFin: searchParams.get("date_fin"),
    };
  }, [searchParams]);

  const { data: disponibilites, refresh: refreshDisponibilites } = useDisponibilite(
    validEnseignantId,
    dateDebut,
    dateFin,
  );

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
    <Layout title="Convocation enseignant" subtitle="Vue personnelle des surveillances">
      {loading && <p className="text-sm text-slate-600">Chargement...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {exportError && <p className="text-sm text-red-600">{exportError}</p>}
      {!validEnseignantId && (
        <p className="text-sm text-amber-600">
          Ajoutez un paramètre enseignantId dans l’URL.
        </p>
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

      <DisponibiliteForm
        enseignantId={validEnseignantId ?? 0}
        onSubmit={async (payload) => {
          if (!validEnseignantId) {
            return;
          }
          await createDisponibilite(payload);
          await refreshDisponibilites();
        }}
      />

      <div className="space-y-2 rounded-lg border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-900">Indisponibilités</h3>
        {disponibilites?.disponibilites?.length ? (
          disponibilites.disponibilites.map((item, index) => (
            <div key={index} className="rounded-md border border-slate-100 px-3 py-2 text-xs text-slate-600">
              <p>
                {item.date} · {item.heure_debut} - {item.heure_fin}
              </p>
              <p>
                {item.type} {item.motif ? `· ${item.motif}` : ""}
              </p>
            </div>
          ))
        ) : (
          <p className="text-xs text-slate-500">Aucune indisponibilité trouvée.</p>
        )}
      </div>
    </Layout>
  );
}
