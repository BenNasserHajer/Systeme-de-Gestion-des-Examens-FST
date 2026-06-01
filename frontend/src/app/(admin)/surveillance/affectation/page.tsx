"use client";

import { Suspense, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useSearchParams } from "next/navigation";

import {
  affecterSessionAutomatique,
  type PlanificationResult,
} from "@/lib/api/surveillance";
import { getCatalogue, type Catalogue } from "@/lib/api/referentiel";
import { SurveillanceCalendarGrid } from "@/components/surveillance/SurveillanceCalendarGrid";
import { SurveillantPickerModal } from "@/components/surveillance/SurveillantPickerModal";

type Summary = {
  total: number;
  affectees: number;
  conflits: number;
  message: string;
};

type StatusFilter = "TOUS" | "AFFECTEE" | "CONFLIT_PARTIEL" | "CONFLIT";

export default function AffectationSurveillancePage() {
  return (
    <Suspense
      fallback={
        <main className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">
          Chargement de la page d&apos;affectation...
        </main>
      }
    >
      <AffectationSurveillanceContent />
    </Suspense>
  );
}

function AffectationSurveillanceContent() {
  const searchParams = useSearchParams();
  const sessionParam = searchParams.get("sessionId") ?? searchParams.get("session_id");

  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(
    sessionParam && Number.isFinite(Number(sessionParam)) ? Number(sessionParam) : null,
  );
  const [selectedSectionNom, setSelectedSectionNom] = useState("");
  const [loadingCatalogue, setLoadingCatalogue] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<PlanificationResult[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("TOUS");
  const [activeView, setActiveView] = useState<"calendrier" | "conflits">("calendrier");
  const [isPreview, setIsPreview] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [selectedPlanif, setSelectedPlanif] = useState<PlanificationResult | null>(null);

  const selectedSession = useMemo(
    () => catalogue?.sessions.find((s) => s.session_id === selectedSessionId) ?? null,
    [catalogue, selectedSessionId],
  );

  const loadCatalogue = useCallback(async () => {
    setLoadingCatalogue(true);
    setError(null);
    try {
      const data = await getCatalogue();
      setCatalogue(data);
      setSelectedSessionId((current) => current ?? data.sessions[0]?.session_id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible de charger le catalogue");
    } finally {
      setLoadingCatalogue(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadCatalogue();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadCatalogue]);

  const applyResponse = useCallback((response: Awaited<ReturnType<typeof affecterSessionAutomatique>>, saved: boolean) => {
    setResults(response.resultats);
    setSummary({
      total: response.total_planifications,
      affectees: response.affectees_automatiquement,
      conflits: response.en_conflit,
      message: response.message,
    });
    if (!saved) {
      setActiveView(response.en_conflit > 0 ? "conflits" : "calendrier");
      setStatusFilter(response.en_conflit > 0 ? "CONFLIT" : "TOUS");
    }
  }, []);

  const handleAffecterAutomatique = async () => {
    if (!selectedSessionId) {
      setError("Veuillez sélectionner une session.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await affecterSessionAutomatique(selectedSessionId, {
        section_nom: selectedSectionNom || undefined,
        save: false,
      });
      applyResponse(response, false);
      setIsPreview(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'affectation automatique");
    } finally {
      setLoading(false);
    }
  };

  const refreshResults = useCallback(async () => {
    if (!selectedSessionId) return;
    const response = await affecterSessionAutomatique(selectedSessionId, {
      section_nom: selectedSectionNom || undefined,
      save: false,
    });
    applyResponse(response, false);
    if (!isPreview) {
      setSummary((prev) => ({
        ...(prev ?? {
          total: response.total_planifications,
          affectees: response.affectees_automatiquement,
          conflits: response.en_conflit,
        }),
        message: "Modification enregistrée.",
      }));
    }
  }, [applyResponse, isPreview, selectedSectionNom, selectedSessionId]);

  const handleValiderAffectations = async () => {
    if (!selectedSessionId) return;
    setIsSaving(true);
    setError(null);
    try {
      const response = await affecterSessionAutomatique(selectedSessionId, {
        section_nom: selectedSectionNom || undefined,
        save: true,
      });
      applyResponse(response, true);
      setSummary({
        total: response.total_planifications,
        affectees: response.affectees_automatiquement,
        conflits: response.en_conflit,
        message: "Affectations sauvegardées avec succès.",
      });
      setIsPreview(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de la sauvegarde");
    } finally {
      setIsSaving(false);
    }
  };

  const handleAnnulerAffectations = () => {
    setResults([]);
    setSummary(null);
    setIsPreview(false);
  };

  const stats = useMemo(() => {
    const complets = results.filter((item) => item.statut === "AFFECTEE").length;
    const partiels = results.filter((item) => item.statut === "CONFLIT_PARTIEL").length;
    const conflits = results.filter((item) => item.statut === "CONFLIT").length;
    const manquants = results.reduce((total, item) => total + item.manquants, 0);
    return { complets, partiels, conflits, manquants };
  }, [results]);

  const filteredResults = useMemo(() => {
    const base =
      activeView === "conflits" ? results.filter((item) => item.statut !== "AFFECTEE") : results;
    if (statusFilter === "TOUS") return base;
    return base.filter((item) => item.statut === statusFilter);
  }, [activeView, results, statusFilter]);

  return (
    <main className="space-y-6">
      <header className="flex flex-col gap-3 border-b border-slate-200 pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Surveillance des examens
          </p>
          <h1 className="mt-1 text-2xl font-semibold text-slate-950">
            Affectation des surveillants
          </h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            Emploi du temps par section, affectation automatique, puis résolution des conflits sur le
            calendrier en cliquant sur chaque examen.
          </p>
        </div>

        {summary ? (
          <div className="rounded-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
            {summary.message}
          </div>
        ) : null}
      </header>

      {error ? (
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-5 py-4">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <StepBadge active label="1" text="Sélection" />
            <StepBadge active={results.length > 0} label="2" text="Génération" />
            <StepBadge active={stats.conflits + stats.partiels > 0} label="3" text="Résolution" />
          </div>
        </div>

        <div className="grid gap-4 p-5 lg:grid-cols-[1fr_1fr_auto] lg:items-end">
          <Field label="Session">
            <select
              value={selectedSessionId ?? ""}
              onChange={(event) => setSelectedSessionId(Number(event.target.value))}
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none focus:border-slate-500"
              disabled={loadingCatalogue}
            >
              <option value="">Sélectionner une session</option>
              {catalogue?.sessions.map((session) => (
                <option key={session.session_id} value={session.session_id}>
                  {session.label}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Section">
            <select
              value={selectedSectionNom}
              onChange={(event) => setSelectedSectionNom(event.target.value)}
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none focus:border-slate-500"
              disabled={loadingCatalogue}
            >
              <option value="">Toutes les sections</option>
              {catalogue?.sections.map((section) => (
                <option key={section.section_id} value={section.label}>
                  {section.label}
                </option>
              ))}
            </select>
          </Field>

          <button
            type="button"
            onClick={() => void handleAffecterAutomatique()}
            disabled={loading || loadingCatalogue || !selectedSessionId}
            className="h-10 rounded-md bg-slate-950 px-5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Génération..." : "Affecter automatiquement"}
          </button>
        </div>
      </section>

      {results.length > 0 ? (
        <>
          {isPreview && (
            <div className="rounded-md border border-amber-200 bg-amber-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-sm font-medium text-amber-800">Mode prévisualisation</h3>
                  <p className="mt-1 text-sm text-amber-700">
                    Affectations suggérées — non sauvegardées. Cliquez sur un examen pour corriger.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={handleAnnulerAffectations}
                    disabled={isSaving}
                    className="rounded-md px-3 py-2 text-sm font-medium text-amber-800 hover:bg-amber-100 disabled:opacity-50"
                  >
                    Annuler
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleValiderAffectations()}
                    disabled={isSaving}
                    className="rounded-md bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700 disabled:opacity-50"
                  >
                    {isSaving ? "Sauvegarde..." : "Valider les affectations"}
                  </button>
                </div>
              </div>
            </div>
          )}

          <section className="grid gap-3 md:grid-cols-4">
            <Metric label="Examens" value={summary?.total ?? results.length} tone="slate" />
            <Metric label="Complets" value={stats.complets} tone="green" />
            <Metric label="Partiels" value={stats.partiels} tone="amber" />
            <Metric label="Conflits" value={stats.conflits} tone="red" />
          </section>

          <section className="rounded-lg border border-slate-200 bg-white p-5">
            <div className="mb-4 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-base font-semibold text-slate-950">Calendrier</h2>
                <p className="mt-1 text-sm text-slate-600">
                  {stats.manquants > 0
                    ? `${stats.manquants} surveillant(s) à affecter — cliquez sur un créneau.`
                    : "Toutes les surveillances sont complètes. Cliquez pour remplacer un surveillant."}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <SegmentButton
                  active={activeView === "calendrier"}
                  onClick={() => setActiveView("calendrier")}
                >
                  Tous
                </SegmentButton>
                <SegmentButton
                  active={activeView === "conflits"}
                  onClick={() => setActiveView("conflits")}
                >
                  Conflits uniquement
                </SegmentButton>
                <select
                  value={statusFilter}
                  onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
                  className="h-9 rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-800"
                >
                  <option value="TOUS">Tous les statuts</option>
                  <option value="AFFECTEE">Complets</option>
                  <option value="CONFLIT_PARTIEL">Partiels</option>
                  <option value="CONFLIT">Conflits</option>
                </select>
              </div>
            </div>

            <SurveillanceCalendarGrid
              items={filteredResults}
              sessionStart={selectedSession?.date_debut}
              sessionEnd={selectedSession?.date_fin}
              onSelectPlanif={setSelectedPlanif}
            />
          </section>
        </>
      ) : (
        <section className="rounded-lg border border-dashed border-slate-300 bg-white px-5 py-8 text-center">
          <h2 className="text-base font-semibold text-slate-950">Aucun résultat</h2>
          <p className="mt-2 text-sm text-slate-600">
            Sélectionnez une session et une section, puis lancez l&apos;affectation automatique.
          </p>
        </section>
      )}

      {selectedPlanif && selectedSessionId ? (
        <SurveillantPickerModal
          planif={selectedPlanif}
          sessionId={selectedSessionId}
          onClose={() => setSelectedPlanif(null)}
          onSaved={refreshResults}
        />
      ) : null}
    </main>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function StepBadge({ active, label, text }: { active: boolean; label: string; text: string }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 ${
        active ? "border-slate-900 bg-slate-950 text-white" : "border-slate-200 bg-white text-slate-500"
      }`}
    >
      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-white/15 text-xs">
        {label}
      </span>
      {text}
    </span>
  );
}

function SegmentButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`h-9 rounded-md px-3 text-sm font-medium ${
        active ? "bg-slate-950 text-white" : "bg-slate-100 text-slate-700 hover:bg-slate-200"
      }`}
    >
      {children}
    </button>
  );
}

function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: number;
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
