"use client";

import { useMemo } from "react";
import { useParams, useSearchParams } from "next/navigation";

import { DisponibiliteForm } from "@/components/surveillance/DisponibiliteForm";
import { Layout } from "@/components/ui/Layout";
import { useDisponibilite } from "@/hooks/useDisponibilite";
import { createDisponibilite } from "@/lib/api/surveillance";

export default function DisponibiliteAdminPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const enseignantId = Number(params.enseignant_id);
  const validEnseignantId = Number.isFinite(enseignantId) ? enseignantId : null;

  const { dateDebut, dateFin } = useMemo(() => {
    return {
      dateDebut: searchParams.get("date_debut"),
      dateFin: searchParams.get("date_fin"),
    };
  }, [searchParams]);

  const { data, loading, error, refresh } = useDisponibilite(
    validEnseignantId,
    dateDebut,
    dateFin,
  );

  return (
    <Layout title="Disponibilités" subtitle="Historique des indisponibilités">
      {!validEnseignantId && (
        <p className="text-sm text-amber-600">Enseignant ID manquant dans l’URL.</p>
      )}
      {!dateDebut || !dateFin ? (
        <p className="text-sm text-amber-600">
          Ajoutez date_debut et date_fin dans l’URL.
        </p>
      ) : null}
      {loading && <p className="text-sm text-slate-600">Chargement...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      <DisponibiliteForm
        enseignantId={validEnseignantId ?? 0}
        onSubmit={async (payload) => {
          if (!validEnseignantId) {
            return;
          }
          await createDisponibilite(payload);
          await refresh();
        }}
      />

      <div className="space-y-2 rounded-lg border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-semibold text-slate-900">Indisponibilités</h3>
        {data?.disponibilites?.length ? (
          data.disponibilites.map((item, index) => (
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
