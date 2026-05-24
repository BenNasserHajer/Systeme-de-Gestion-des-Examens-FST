"use client";

import { Suspense, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

import { getCatalogue, type Catalogue } from "@/lib/api/referentiel";
import { getAllSurveillants } from "@/lib/api/surveillance";
import type { GetAllSurveillantsResponse } from "@/lib/types/surveillance";
import { useConvocation } from "@/hooks/useConvocation";
import { usePDFExport } from "@/hooks/usePDFExport";

import { Layout } from "@/components/ui/Layout";
import { Button } from "@/components/ui/Button";
import { ConvocationCard } from "@/components/surveillance/ConvocationCard";

export default function SurveillancePage() {
  return (
    <Suspense
      fallback={
        <Layout title="Surveillance" subtitle="Pilotage des affectations et convocations">
          <p className="text-sm text-slate-600">Chargement de la page...</p>
        </Layout>
      }
    >
      <SurveillancePageContent />
    </Suspense>
  );
}

function SurveillancePageContent() {
  const searchParams = useSearchParams();
  const sessionParam = searchParams.get("sessionId") ?? searchParams.get("session_id");
  
  // States for catalogue & sessions
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [loadingCatalogue, setLoadingCatalogue] = useState(true);
  const [catalogueError, setCatalogueError] = useState<string | null>(null);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(
    sessionParam && Number.isFinite(Number(sessionParam)) ? Number(sessionParam) : null
  );

  // States for surveillants (enseignants)
  const [allSurveillantsData, setAllSurveillantsData] = useState<GetAllSurveillantsResponse | null>(null);
  const [loadingSurveillants, setLoadingSurveillants] = useState(false);
  const [selectedEnseignantId, setSelectedEnseignantId] = useState<number | null>(null);

  // Fetch catalogue
  useEffect(() => {
    async function load() {
      try {
        const data = await getCatalogue();
        setCatalogue(data);
        if (!selectedSessionId && data.sessions.length > 0) {
          setSelectedSessionId(data.sessions[0].session_id);
        }
      } catch (err) {
        setCatalogueError(err instanceof Error ? err.message : "Erreur catalogue");
      } finally {
        setLoadingCatalogue(false);
      }
    }
    void load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch all surveillants when session changes
  useEffect(() => {
    async function loadSurveillants() {
      if (!selectedSessionId) {
        setAllSurveillantsData(null);
        setSelectedEnseignantId(null);
        return;
      }
      setLoadingSurveillants(true);
      try {
        // limit: 500 to respect backend max
        const res = await getAllSurveillants(selectedSessionId, { limit: 500 });
        setAllSurveillantsData(res);
      } catch (err) {
        console.error("Failed to load surveillants", err);
      } finally {
        setLoadingSurveillants(false);
      }
    }
    void loadSurveillants();
  }, [selectedSessionId]);

  // Convocation logic
  const { data: convocationData, loading: convocationLoading, error: convocationError } = useConvocation(
    selectedEnseignantId, 
    { annee_universitaire: allSurveillantsData?.annee_universitaire }
  );
  const { exportPDF, loading: exporting, error: exportError } = usePDFExport();

  // Selected teacher stats
  const selectedTeacherStats = useMemo(() => {
    if (!selectedEnseignantId || !allSurveillantsData?.data) return null;
    return allSurveillantsData.data.find((e: any) => e.enseignant_id === selectedEnseignantId);
  }, [selectedEnseignantId, allSurveillantsData]);

  // Prepare convocation mapping
  const convEnseignant = (convocationData?.enseignant ?? {}) as any;
  const convSession = (convocationData?.session ?? {
    annee_universitaire: allSurveillantsData?.annee_universitaire,
    type_session: catalogue?.sessions.find(s => s.session_id === selectedSessionId)?.label || "Session"
  }) as any;
  const convAssignments = Array.isArray(convocationData?.surveillances)
    ? convocationData.surveillances.map((item: any) => ({
        matiere: item?.matiere?.intitule ?? item?.matiere?.code ?? "—",
        date: item?.creneau?.date ?? "—",
        heure_debut: item?.creneau?.heure_debut ?? undefined,
        heure_fin: item?.creneau?.heure_fin ?? undefined,
        salle: item?.salle?.code ?? item?.salle?.designation ?? "—",
        groupe: item?.groupe?.numero ? `G${item.groupe.numero}` : "—",
        charge: item?.surveillance?.charge ?? item?.charge ?? undefined,
      }))
    : [];

  const canExport = selectedEnseignantId && convEnseignant.nom && convEnseignant.prenom;

  return (
    <Layout
      title="Surveillance"
      subtitle="Pilotage des affectations et convocations"
      actions={
        <Link href={selectedSessionId ? `/surveillance/charge?sessionId=${selectedSessionId}` : "/surveillance/charge"}>
          <Button variant="secondary">Voir les charges globales</Button>
        </Link>
      }
    >
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-2 mb-8">
        <Link
          className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-medium text-slate-700 hover:bg-slate-50 flex flex-col"
          href={selectedSessionId ? `/surveillance/affectation?sessionId=${selectedSessionId}` : "/surveillance/affectation"}
        >
          <span className="text-base font-semibold text-slate-900">Affectation Automatique</span>
          <span className="mt-1 text-slate-500">Lancer l'algorithme d'affectation ou résoudre les conflits</span>
        </Link>
        <Link
          className="rounded-lg border border-slate-200 bg-white p-4 text-sm font-medium text-slate-700 hover:bg-slate-50 flex flex-col"
          href={selectedSessionId ? `/surveillance/charge?sessionId=${selectedSessionId}` : "/surveillance/charge"}
        >
          <span className="text-base font-semibold text-slate-900">Tableau des charges</span>
          <span className="mt-1 text-slate-500">Vue globale des volumes horaires par enseignant</span>
        </Link>
      </div>

      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-4">
          <h2 className="text-base font-semibold text-slate-950">Consultation des emplois de surveillance</h2>
        </div>
        <div className="grid gap-4 p-5 lg:grid-cols-2 items-end">
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-700">Session</span>
            <select
              value={selectedSessionId ?? ""}
              onChange={(e) => setSelectedSessionId(Number(e.target.value))}
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none focus:border-slate-500"
              disabled={loadingCatalogue}
            >
              <option value="">Sélectionner une session</option>
              {catalogue?.sessions.map((s) => (
                <option key={s.session_id} value={s.session_id}>
                  {s.label}
                </option>
              ))}
            </select>
          </label>

          <label className="block relative">
            <span className="mb-1 block text-sm font-medium text-slate-700">Enseignant</span>
            <select
              value={selectedEnseignantId ?? ""}
              onChange={(e) => setSelectedEnseignantId(e.target.value ? Number(e.target.value) : null)}
              disabled={loadingSurveillants || !selectedSessionId}
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none focus:border-slate-500"
            >
              <option value="">Sélectionner un enseignant</option>
              {allSurveillantsData?.data?.map((ens: any) => (
                <option key={ens.enseignant_id} value={ens.enseignant_id}>
                  {ens.prenom} {ens.nom} {ens.departement?.nom ? `(${ens.departement.nom})` : ""}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      {selectedTeacherStats && (
        <section className="grid gap-3 md:grid-cols-4 mt-6">
          <Metric label="Volume Horaire" value={`${selectedTeacherStats.volume_horaire}h`} tone="slate" />
          <Metric label="Charge Surveillance" value={`${selectedTeacherStats.charge_surveillance}h`} tone="amber" />
          <Metric label="Volume Restant" value={`${selectedTeacherStats.volume_restant}h`} tone={selectedTeacherStats.volume_restant < 0 ? "red" : "green"} />
          <Metric label="Total Affectations" value={selectedTeacherStats.nb_surveillances} tone="slate" />
        </section>
      )}

      {selectedEnseignantId && (
        <section className="mt-6">
          {convocationLoading && <p className="text-sm text-slate-600 mb-4">Chargement de la convocation...</p>}
          {convocationError && <p className="text-sm text-red-600 mb-4">{convocationError}</p>}
          {exportError && <p className="text-sm text-red-600 mb-4">{exportError}</p>}
          
          <ConvocationCard
            enseignant={{
              nom: convEnseignant.nom ?? "—",
              prenom: convEnseignant.prenom ?? "—",
              grade: convEnseignant.grade ?? null,
              departement: typeof convEnseignant.departement === "string"
                ? convEnseignant.departement
                : convEnseignant.departement?.nom ?? null,
              email: convEnseignant.email ?? null,
            }}
            session={convSession}
            assignments={convAssignments}
            onExport={
              canExport
                ? () =>
                    exportPDF({
                      enseignant: {
                        nom: convEnseignant.nom ?? "—",
                        prenom: convEnseignant.prenom ?? "—",
                        grade: convEnseignant.grade ?? null,
                        departement: typeof convEnseignant.departement === "string"
                          ? convEnseignant.departement
                          : convEnseignant.departement?.nom ?? null,
                        email: convEnseignant.email ?? null,
                      },
                      session: convSession,
                      assignments: convAssignments,
                    })
                : undefined
            }
          />
          {exporting && <p className="text-xs text-slate-500 mt-2">Génération du PDF...</p>}
        </section>
      )}
    </Layout>
  );
}

function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: string | number;
  tone: "slate" | "green" | "amber" | "red";
}) {
  const toneClasses = {
    slate: "border-slate-200 text-slate-950",
    green: "border-emerald-200 text-emerald-700",
    amber: "border-amber-200 text-amber-700",
    red: "border-red-200 text-red-700",
  };

  return (
    <div className={`rounded-lg border bg-white p-4 ${toneClasses[tone]}`}>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold">{value}</p>
    </div>
  );
}
