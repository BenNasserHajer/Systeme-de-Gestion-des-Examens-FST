"use client";

import { Suspense, useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useSearchParams } from "next/navigation";

import {
  affecterManuellement,
  affecterSessionAutomatique,
  getEnseignantsDisponibles,
  type EnseignantDisponible,
  type EnseignantsDisponiblesResponse,
  type GroupeResult,
  type PlanificationResult,
} from "@/lib/api/surveillance";
import { getCatalogue, type Catalogue } from "@/lib/api/referentiel";

type Summary = {
  total: number;
  affectees: number;
  conflits: number;
  message: string;
};

type StatusFilter = "TOUS" | "AFFECTEE" | "CONFLIT_PARTIEL" | "CONFLIT";

const statusLabels: Record<string, string> = {
  AFFECTEE: "Complet",
  CONFLIT_PARTIEL: "Partiel",
  CONFLIT: "Conflit",
};

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
    sessionParam && Number.isFinite(Number(sessionParam)) ? Number(sessionParam) : null
  );
  const [selectedSectionNom, setSelectedSectionNom] = useState("");
  const [loadingCatalogue, setLoadingCatalogue] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<PlanificationResult[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("TOUS");
  const [activeView, setActiveView] = useState<"tableau" | "conflits">("tableau");
  const [isPreview, setIsPreview] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [selectedPlanif, setSelectedPlanif] = useState<PlanificationResult | null>(null);
  const [availableEnseignants, setAvailableEnseignants] =
    useState<EnseignantsDisponiblesResponse | null>(null);
  const [selectedEnseignants, setSelectedEnseignants] = useState<Set<number>>(new Set());
  const [selectedGroupKey, setSelectedGroupKey] = useState("");
  const [loadingModal, setLoadingModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDepartement, setFilterDepartement] = useState<number | null>(null);
  const [showOnlyWarnings, setShowOnlyWarnings] = useState(false);

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

  const handleAffecterAutomatique = async () => {
    if (!selectedSessionId) {
      setError("Veuillez selectionner une session.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await affecterSessionAutomatique(selectedSessionId, {
        section_nom: selectedSectionNom || undefined,
        save: false,
      });

      setResults(response.resultats);
      setSummary({
        total: response.total_planifications,
        affectees: response.affectees_automatiquement,
        conflits: response.en_conflit,
        message: response.message,
      });
      setActiveView(response.en_conflit > 0 ? "conflits" : "tableau");
      setStatusFilter(response.en_conflit > 0 ? "CONFLIT" : "TOUS");
      setIsPreview(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'affectation automatique");
    } finally {
      setLoading(false);
    }
  };

  const handleValiderAffectations = async () => {
    if (!selectedSessionId) return;
    setIsSaving(true);
    setError(null);
    try {
      const response = await affecterSessionAutomatique(selectedSessionId, {
        section_nom: selectedSectionNom || undefined,
        save: true,
      });
      setResults(response.resultats);
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

  const handleOpenModal = async (planif: PlanificationResult) => {
    const groupKey = getMissingGroups(planif)[0]?.key ?? "";

    setSelectedPlanif(planif);
    setSelectedGroupKey(groupKey);
    setSelectedEnseignants(new Set());
    setSearchTerm("");
    setFilterDepartement(null);
    setShowOnlyWarnings(false);
    setLoadingModal(true);

    try {
      const data = await getEnseignantsDisponibles(planif.planification_id);
      setAvailableEnseignants(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors du chargement des enseignants");
    } finally {
      setLoadingModal(false);
    }
  };

  const handleCloseModal = () => {
    setSelectedPlanif(null);
    setAvailableEnseignants(null);
    setSelectedEnseignants(new Set());
    setSelectedGroupKey("");
  };

  const selectedGroup = useMemo(() => {
    if (!selectedPlanif) return null;
    return getMissingGroups(selectedPlanif).find((item) => item.key === selectedGroupKey)?.group ?? null;
  }, [selectedGroupKey, selectedPlanif]);

  const selectedGroupMissing = selectedGroup?.manquants ?? selectedPlanif?.manquants ?? 0;

  const handleToggleEnseignant = (enseignantId: number) => {
    const next = new Set(selectedEnseignants);
    if (next.has(enseignantId)) {
      next.delete(enseignantId);
    } else if (next.size < selectedGroupMissing) {
      next.add(enseignantId);
    }
    setSelectedEnseignants(next);
  };

  const handleAffecterManuellement = async () => {
    if (!selectedPlanif || !selectedSessionId || !selectedGroup) return;

    if (!selectedGroup.groupe || !selectedGroup.salle) {
      setError("Impossible de trouver le groupe ou la salle pour cette affectation.");
      return;
    }

    if (selectedEnseignants.size === 0) {
      setError("Veuillez selectionner au moins un enseignant.");
      return;
    }

    setLoadingModal(true);
    setError(null);
    try {
      await affecterManuellement({
        session_id: selectedSessionId,
        planification_id: selectedPlanif.planification_id,
        groupe_id: selectedGroup.groupe.id,
        salle_id: selectedGroup.salle.id,
        enseignant_ids: Array.from(selectedEnseignants),
      });

      handleCloseModal();
      if (isPreview) {
        await handleAffecterAutomatique();
      } else {
        // Run with save: true to just refresh and get the latest state from DB without changing isPreview to true
        await handleValiderAffectations();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'affectation manuelle");
    } finally {
      setLoadingModal(false);
    }
  };

  const stats = useMemo(() => {
    const complets = results.filter((item) => item.statut === "AFFECTEE").length;
    const partiels = results.filter((item) => item.statut === "CONFLIT_PARTIEL").length;
    const conflits = results.filter((item) => item.statut === "CONFLIT").length;
    const manquants = results.reduce((total, item) => total + item.manquants, 0);
    return { complets, partiels, conflits, manquants };
  }, [results]);

  const filteredResults = useMemo(() => {
    const base = activeView === "conflits" ? results.filter((item) => item.statut !== "AFFECTEE") : results;
    if (statusFilter === "TOUS") return base;
    return base.filter((item) => item.statut === statusFilter);
  }, [activeView, results, statusFilter]);

  const filteredEnseignants = useMemo(() => {
    if (!availableEnseignants) return [];

    let enseignants: EnseignantDisponible[] = [];
    availableEnseignants.departements.forEach((dept) => {
      if (filterDepartement === null || dept.departement_id === filterDepartement) {
        enseignants = enseignants.concat(dept.enseignants);
      }
    });

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      enseignants = enseignants.filter((ens) =>
        [ens.nom, ens.prenom, ens.departement?.nom, ens.grade]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(term))
      );
    }

    if (showOnlyWarnings) {
      enseignants = enseignants.filter((ens) => (ens.avertissements?.length ?? 0) > 0);
    }

    return enseignants.sort((a, b) => b.volume_restant - a.volume_restant);
  }, [availableEnseignants, filterDepartement, searchTerm, showOnlyWarnings]);

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
            Chargez l&apos;emploi des examens par section, lancez l&apos;affectation automatique,
            puis traitez uniquement les conflits restants.
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
            <StepBadge active label="1" text="Selection" />
            <StepBadge active={results.length > 0} label="2" text="Generation" />
            <StepBadge active={stats.conflits + stats.partiels > 0} label="3" text="Resolution" />
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
              <option value="">Selectionner une session</option>
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
            onClick={handleAffecterAutomatique}
            disabled={loading || loadingCatalogue || !selectedSessionId}
            className="h-10 rounded-md bg-slate-950 px-5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Generation..." : "Affecter automatiquement"}
          </button>
        </div>
      </section>

      {results.length > 0 ? (
        <>
          {isPreview && (
            <div className="rounded-md border border-amber-200 bg-amber-50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-amber-800">Mode prévisualisation</h3>
                  <p className="mt-1 text-sm text-amber-700">
                    Voici les affectations suggérées. Aucune donnée n&apos;a été sauvegardée.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleAnnulerAffectations}
                    disabled={isSaving}
                    className="rounded-md px-3 py-2 text-sm font-medium text-amber-800 hover:bg-amber-100 disabled:opacity-50"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={handleValiderAffectations}
                    disabled={isSaving}
                    className="rounded-md bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700 disabled:opacity-50"
                  >
                    {isSaving ? "Sauvegarde..." : "✓ Valider les affectations"}
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

          <section className="rounded-lg border border-slate-200 bg-white">
            <div className="flex flex-col gap-4 border-b border-slate-200 px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-base font-semibold text-slate-950">Planning d&apos;affectation</h2>
                <p className="mt-1 text-sm text-slate-600">
                  {stats.manquants > 0
                    ? `${stats.manquants} surveillant(s) restent a affecter manuellement.`
                    : "Toutes les surveillances sont completees."}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <SegmentButton active={activeView === "tableau"} onClick={() => setActiveView("tableau")}>
                  Tableau
                </SegmentButton>
                <SegmentButton active={activeView === "conflits"} onClick={() => setActiveView("conflits")}>
                  Conflits
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

            <div className="overflow-x-auto">
              <table className="w-full min-w-[920px] text-left text-sm">
                <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-5 py-3 font-semibold">Statut</th>
                    <th className="px-5 py-3 font-semibold">Examen</th>
                    <th className="px-5 py-3 font-semibold">Section</th>
                    <th className="px-5 py-3 font-semibold">Date et heure</th>
                    <th className="px-5 py-3 font-semibold">Salles / groupes</th>
                    <th className="px-5 py-3 font-semibold">Surveillants</th>
                    <th className="px-5 py-3 text-right font-semibold">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {filteredResults.map((result) => (
                    <tr key={result.planification_id} className="align-top hover:bg-slate-50">
                      <td className="px-5 py-4">
                        <StatusPill status={result.statut} />
                      </td>
                      <td className="px-5 py-4">
                        <p className="font-medium text-slate-950">
                          {result.matiere?.intitule || "Matiere non definie"}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          {result.type_epreuve} · Semestre {result.semestre || "-"}
                        </p>
                      </td>
                      <td className="px-5 py-4 text-slate-700">{result.section?.nom || "-"}</td>
                      <td className="px-5 py-4 text-slate-700">
                        <p>{formatDate(result.creneau?.date)}</p>
                        <p className="mt-1 text-xs text-slate-500">
                          {result.creneau?.heure_debut || "--:--"} - {result.creneau?.heure_fin || "--:--"}
                        </p>
                      </td>
                      <td className="px-5 py-4">
                        <GroupSummary groups={result.groupes} />
                      </td>
                      <td className="px-5 py-4">
                        <p className="font-medium text-slate-950">
                          {result.surveillants_affectes} / {result.surveillants_requis}
                        </p>
                        {result.groupes?.some(g => g.surveillants_affectes?.length > 0) && (
                          <div className="mt-1 mb-1 text-xs text-slate-600">
                            {result.groupes.flatMap(g => g.surveillants_affectes || []).map((s, i) => (
                              <span key={s.surveillance_id || i} className="block">
                                • {s.prenom} {s.nom}
                              </span>
                            ))}
                          </div>
                        )}
                        {result.manquants > 0 ? (
                          <p className="mt-1 text-xs text-red-600">{result.manquants} manquant(s)</p>
                        ) : (
                          <p className="mt-1 text-xs text-emerald-700">Complet</p>
                        )}
                      </td>
                      <td className="px-5 py-4 text-right">
                        {result.statut !== "AFFECTEE" ? (
                          <button
                            type="button"
                            onClick={() => handleOpenModal(result)}
                            className="rounded-md bg-slate-950 px-3 py-2 text-xs font-medium text-white hover:bg-slate-800"
                          >
                            Resoudre
                          </button>
                        ) : (
                          <span className="text-xs text-slate-400">Aucune action</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      ) : (
        <section className="rounded-lg border border-dashed border-slate-300 bg-white px-5 py-8 text-center">
          <h2 className="text-base font-semibold text-slate-950">Aucun resultat pour le moment</h2>
          <p className="mt-2 text-sm text-slate-600">
            Selectionnez une session et une section, puis lancez l&apos;affectation automatique.
          </p>
        </section>
      )}

      {selectedPlanif ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <section className="max-h-[90vh] w-full max-w-5xl overflow-hidden rounded-lg bg-white shadow-xl">
            <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Resolution manuelle
                </p>
                <h2 className="mt-1 text-xl font-semibold text-slate-950">
                  {selectedPlanif.matiere?.intitule || "Examen"}
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  {selectedPlanif.section?.nom || "Section"} · {formatDate(selectedPlanif.creneau?.date)} ·{" "}
                  {selectedPlanif.creneau?.heure_debut} - {selectedPlanif.creneau?.heure_fin}
                </p>
              </div>
              <button
                type="button"
                onClick={handleCloseModal}
                className="rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
              >
                Fermer
              </button>
            </div>

            <div className="grid max-h-[calc(90vh-145px)] overflow-y-auto lg:grid-cols-[320px_1fr]">
              <aside className="border-b border-slate-200 bg-slate-50 p-5 lg:border-b-0 lg:border-r">
                <h3 className="text-sm font-semibold text-slate-950">Cible d&apos;affectation</h3>
                <p className="mt-1 text-sm text-slate-600">
                  Choisissez le groupe ou la salle qui manque de surveillants.
                </p>

                <div className="mt-4 space-y-3">
                  {getMissingGroups(selectedPlanif).map(({ key, group }) => (
                    <label
                      key={key}
                      className={`block cursor-pointer rounded-md border p-3 ${
                        selectedGroupKey === key
                          ? "border-slate-900 bg-white"
                          : "border-slate-200 bg-white hover:border-slate-300"
                      }`}
                    >
                      <input
                        type="radio"
                        name="group"
                        checked={selectedGroupKey === key}
                        onChange={() => {
                          setSelectedGroupKey(key);
                          setSelectedEnseignants(new Set());
                        }}
                        className="sr-only"
                      />
                      <p className="text-sm font-medium text-slate-950">
                        Groupe {group.groupe?.numero ?? "-"} · Salle {group.salle?.code ?? "-"}
                      </p>
                      <p className="mt-1 text-xs text-slate-600">
                        {group.surveillants_affectes.length} / {group.surveillants_requis} affecte(s),
                        {" "}{group.manquants} manquant(s)
                      </p>
                    </label>
                  ))}
                </div>

                <div className="mt-5 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                  Selection: {selectedEnseignants.size} / {selectedGroupMissing} enseignant(s)
                </div>
              </aside>

              <div className="p-5">
                <div className="grid gap-3 md:grid-cols-[1fr_220px_auto]">
                  <input
                    type="search"
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    placeholder="Rechercher par nom, grade, departement..."
                    className="h-10 rounded-md border border-slate-300 px-3 text-sm outline-none focus:border-slate-500"
                  />
                  <select
                    value={filterDepartement ?? ""}
                    onChange={(event) =>
                      setFilterDepartement(event.target.value ? Number(event.target.value) : null)
                    }
                    className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
                  >
                    <option value="">Tous departements</option>
                    {availableEnseignants?.departements.map((dept) => (
                      <option key={dept.departement_id} value={dept.departement_id}>
                        {dept.departement_nom} ({dept.total})
                      </option>
                    ))}
                  </select>
                  <label className="flex h-10 items-center gap-2 rounded-md border border-slate-300 px-3 text-sm text-slate-700">
                    <input
                      type="checkbox"
                      checked={showOnlyWarnings}
                      onChange={(event) => setShowOnlyWarnings(event.target.checked)}
                    />
                    Avec alerte
                  </label>
                </div>

                {loadingModal ? (
                  <div className="py-12 text-center text-sm text-slate-600">
                    Chargement des enseignants disponibles...
                  </div>
                ) : (
                  <div className="mt-4 overflow-hidden rounded-md border border-slate-200">
                    <div className="border-b border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                      {filteredEnseignants.length} enseignant(s) disponible(s)
                    </div>
                    <div className="max-h-[430px] divide-y divide-slate-200 overflow-y-auto">
                      {filteredEnseignants.map((ens) => {
                        const checked = selectedEnseignants.has(ens.enseignant_id);
                        const locked = !checked && selectedEnseignants.size >= selectedGroupMissing;

                        return (
                          <label
                            key={ens.enseignant_id}
                            className={`grid cursor-pointer gap-3 px-4 py-3 md:grid-cols-[auto_1fr_120px] md:items-center ${
                              locked ? "bg-slate-50 opacity-60" : "bg-white hover:bg-slate-50"
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={checked}
                              disabled={locked}
                              onChange={() => handleToggleEnseignant(ens.enseignant_id)}
                              className="mt-1 h-4 w-4 rounded border-slate-300"
                            />
                            <div>
                              <p className="text-sm font-medium text-slate-950">
                                {ens.nom} {ens.prenom}
                              </p>
                              <p className="mt-1 text-xs text-slate-500">
                                {ens.grade || "Grade non defini"} · {ens.departement?.nom || "Departement"}
                              </p>
                              {ens.avertissements?.length ? (
                                <p className="mt-2 rounded-md bg-amber-50 px-2 py-1 text-xs text-amber-800">
                                  {ens.avertissements.join(", ")}
                                </p>
                              ) : null}
                            </div>
                            <div className="text-left md:text-right">
                              <p className="text-sm font-semibold text-slate-950">
                                {ens.volume_restant.toFixed(1)}h
                              </p>
                              <p className="text-xs text-slate-500">volume restant</p>
                            </div>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <footer className="flex flex-col gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-slate-600">
                Le bouton devient actif apres selection d&apos;au moins un enseignant.
              </p>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
                >
                  Annuler
                </button>
                <button
                  type="button"
                  onClick={handleAffecterManuellement}
                  disabled={selectedEnseignants.size === 0 || loadingModal || !selectedGroup}
                  className="rounded-md bg-slate-950 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loadingModal ? "Affectation..." : "Affecter"}
                </button>
              </div>
            </footer>
          </section>
        </div>
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

function StatusPill({ status }: { status: string }) {
  const classes =
    status === "AFFECTEE"
      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
      : status === "CONFLIT_PARTIEL"
        ? "border-amber-200 bg-amber-50 text-amber-700"
        : "border-red-200 bg-red-50 text-red-700";

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-medium ${classes}`}>
      {statusLabels[status] ?? status}
    </span>
  );
}

function GroupSummary({ groups }: { groups: GroupeResult[] }) {
  if (!groups?.length) {
    return <span className="text-slate-400">Aucun groupe</span>;
  }

  return (
    <div className="space-y-1">
      {groups.slice(0, 2).map((group, index) => (
        <p key={`${group.groupe?.id ?? index}-${group.salle?.id ?? index}`} className="text-xs text-slate-600">
          Groupe {group.groupe?.numero ?? "-"} · Salle {group.salle?.code ?? "-"}
        </p>
      ))}
      {groups.length > 2 ? <p className="text-xs text-slate-400">+{groups.length - 2} autre(s)</p> : null}
    </div>
  );
}

function getMissingGroups(planif: PlanificationResult) {
  return (planif.groupes ?? [])
    .filter((group) => group.manquants > 0)
    .map((group, index) => ({
      key: `${group.groupe?.id ?? "g"}-${group.salle?.id ?? "s"}-${index}`,
      group,
    }));
}

function formatDate(value?: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}
