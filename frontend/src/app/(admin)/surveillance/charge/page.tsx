"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { ChargeSummaryCards, ChargeTable } from "@/components/surveillance/ChargeTable";
import { Layout } from "@/components/ui/Layout";
import { getCatalogue } from "@/lib/api/referentiel";
import type { CatalogueSession } from "@/lib/api/referentiel";
import { useTeacherCharge } from "@/hooks/useTeacherCharge";

export default function ChargePage() {
  return (
    <Suspense
      fallback={
        <Layout title="Tableau des charges" subtitle="Charge de surveillance et volume annuel par enseignant">
          <p className="text-sm text-slate-600">Chargement...</p>
        </Layout>
      }
    >
      <ChargePageContent />
    </Suspense>
  );
}

function ChargePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionParam = searchParams.get("sessionId") ?? searchParams.get("session_id");
  const initialSessionId = sessionParam ? Number(sessionParam) : null;

  const [sessions, setSessions] = useState<CatalogueSession[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(
    Number.isFinite(initialSessionId ?? NaN) ? initialSessionId : null,
  );

  const validSessionId = Number.isFinite(sessionId ?? NaN) ? sessionId : null;
  const { items, pagination, meta, loading, error } = useTeacherCharge(validSessionId);

  useEffect(() => {
    void getCatalogue()
      .then((catalogue) => {
        setSessions(catalogue.sessions);
        if (!validSessionId && catalogue.sessions[0]) {
          const firstId = catalogue.sessions[0].session_id;
          setSessionId(firstId);
          router.replace(`/surveillance/charge?sessionId=${firstId}`);
        }
      })
      .catch(() => {
        /* ignore */
      });
  }, [router, validSessionId]);

  const selectedSession = useMemo(
    () => sessions.find((s) => s.session_id === validSessionId),
    [sessions, validSessionId],
  );

  const handleSessionChange = (id: number) => {
    setSessionId(id);
    router.replace(`/surveillance/charge?sessionId=${id}`);
  };

  return (
    <Layout
      title="Tableau des charges"
      subtitle="Charge de surveillance et volume annuel par enseignant"
    >
      <div className="space-y-4">
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <label className="block text-sm font-medium text-slate-700">
            Session d&apos;examen
            <select
              value={validSessionId ?? ""}
              onChange={(e) => handleSessionChange(Number(e.target.value))}
              className="mt-1 w-full max-w-md rounded-md border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">Choisir une session...</option>
              {sessions.map((session) => (
                <option key={session.session_id} value={session.session_id}>
                  {session.label} ({session.date_debut} → {session.date_fin})
                </option>
              ))}
            </select>
          </label>
          {meta ? (
            <p className="mt-2 text-sm text-slate-600">
              Calcul sur l&apos;année universitaire{" "}
              <strong>{meta.anneeUniversitaire}</strong>
              {meta.sessionLabel ? ` · ${meta.sessionLabel}` : ""}
              {selectedSession ? (
                <span className="text-slate-500">
                  {" "}
                  (session du {selectedSession.date_debut} au {selectedSession.date_fin})
                </span>
              ) : null}
            </p>
          ) : (
            <p className="mt-2 text-xs text-slate-500">
              Le volume annuel provient de la charge horaire enseignant pour cette année. La
              charge de surveillance est la somme des heures affectées sur toutes les sessions de
              la même année universitaire.
            </p>
          )}
        </div>

        {loading ? <p className="text-sm text-slate-600">Chargement...</p> : null}
        {error ? <p className="text-sm text-red-600">{error}</p> : null}

        {!validSessionId ? (
          <p className="text-sm text-amber-600">Sélectionnez une session pour afficher les charges.</p>
        ) : null}

        {meta && items.length > 0 ? (
          <ChargeSummaryCards items={items} anneeUniversitaire={meta.anneeUniversitaire} />
        ) : null}

        <ChargeTable items={items} />

        {pagination?.total ? (
          <p className="text-xs text-slate-500">
            {pagination.total} enseignant(s) · page {pagination.page ?? 1} / {pagination.pages ?? 1}
          </p>
        ) : null}
      </div>
    </Layout>
  );
}
