"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  affecterManuellement,
  getEnseignantsDisponibles,
  remplacerSurveillant,
  type EnseignantDisponible,
  type EnseignantsDisponiblesResponse,
  type GroupeResult,
  type PlanificationResult,
} from "@/lib/api/surveillance";

type SurveillantPickerModalProps = {
  planif: PlanificationResult;
  sessionId: number;
  onClose: () => void;
  onSaved: () => Promise<void>;
};

type GroupEntry = {
  key: string;
  group: GroupeResult;
};

export function SurveillantPickerModal({
  planif,
  sessionId,
  onClose,
  onSaved,
}: SurveillantPickerModalProps) {
  const groups = useMemo(() => getAllGroups(planif), [planif]);

  const [selectedGroupKey, setSelectedGroupKey] = useState(groups[0]?.key ?? "");
  const [availableEnseignants, setAvailableEnseignants] =
    useState<EnseignantsDisponiblesResponse | null>(null);
  const [selectedEnseignants, setSelectedEnseignants] = useState<Set<number>>(new Set());
  const [replacingSurveillanceId, setReplacingSurveillanceId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingList, setLoadingList] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDepartement, setFilterDepartement] = useState<number | null>(null);
  const [showOnlyWarnings, setShowOnlyWarnings] = useState(false);

  const selectedGroup = groups.find((g) => g.key === selectedGroupKey)?.group ?? null;
  const slotsToFill = selectedGroup?.manquants ?? 0;
  const isReplaceMode = replacingSurveillanceId !== null;

  const loadEnseignants = useCallback(async () => {
    setLoadingList(true);
    setError(null);
    try {
      const data = await getEnseignantsDisponibles(planif.planification_id);
      setAvailableEnseignants(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Impossible de charger les enseignants");
    } finally {
      setLoadingList(false);
    }
  }, [planif.planification_id]);

  useEffect(() => {
    void loadEnseignants();
  }, [loadEnseignants]);

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
          .some((value) => String(value).toLowerCase().includes(term)),
      );
    }

    if (showOnlyWarnings) {
      enseignants = enseignants.filter((ens) => (ens.avertissements?.length ?? 0) > 0);
    }

    return enseignants.sort((a, b) => b.volume_restant - a.volume_restant);
  }, [availableEnseignants, filterDepartement, searchTerm, showOnlyWarnings]);

  const handleToggleEnseignant = (enseignantId: number) => {
    if (isReplaceMode) {
      setSelectedEnseignants(new Set([enseignantId]));
      return;
    }
    const next = new Set(selectedEnseignants);
    if (next.has(enseignantId)) {
      next.delete(enseignantId);
    } else if (next.size < slotsToFill) {
      next.add(enseignantId);
    }
    setSelectedEnseignants(next);
  };

  const handleStartReplace = (surveillanceId: number) => {
    setReplacingSurveillanceId(surveillanceId);
    setSelectedEnseignants(new Set());
  };

  const handleCancelReplace = () => {
    setReplacingSurveillanceId(null);
    setSelectedEnseignants(new Set());
  };

  const handleAssign = async () => {
    if (!selectedGroup?.groupe?.id || !selectedGroup.salle?.id) {
      setError("Groupe ou salle introuvable.");
      return;
    }

    if (selectedEnseignants.size === 0) {
      setError("Sélectionnez au moins un enseignant.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      if (isReplaceMode && replacingSurveillanceId) {
        const newId = Array.from(selectedEnseignants)[0];
        await remplacerSurveillant(replacingSurveillanceId, newId);
      } else {
        await affecterManuellement({
          session_id: sessionId,
          planification_id: planif.planification_id,
          groupe_id: selectedGroup.groupe.id,
          salle_id: selectedGroup.salle.id,
          enseignant_ids: Array.from(selectedEnseignants),
        });
      }
      await onSaved();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de l'affectation");
    } finally {
      setLoading(false);
    }
  };

  const canSubmit =
    selectedEnseignants.size > 0 &&
    !loading &&
    selectedGroup &&
    (isReplaceMode ? selectedEnseignants.size === 1 : true);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4 backdrop-blur-sm">
      <section className="flex max-h-[92vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-slate-200">
        <header className="border-b border-slate-200 bg-gradient-to-r from-slate-50 to-white px-6 py-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-indigo-600">
                Affectation manuelle
              </p>
              <h2 className="mt-1 text-xl font-semibold text-slate-950">
                {planif.matiere?.intitule || "Examen"}
              </h2>
              <p className="mt-1 text-sm text-slate-600">
                {planif.section?.nom} · {formatSlotDate(planif.creneau?.date)} ·{" "}
                {planif.creneau?.heure_debut?.slice(0, 5)} – {planif.creneau?.heure_fin?.slice(0, 5)}
              </p>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
            >
              Fermer
            </button>
          </div>
        </header>

        {error ? (
          <div className="mx-6 mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <div className="grid min-h-0 flex-1 overflow-hidden lg:grid-cols-[300px_1fr]">
          <aside className="overflow-y-auto border-b border-slate-200 bg-slate-50 p-5 lg:border-b-0 lg:border-r">
            <h3 className="text-sm font-semibold text-slate-950">Groupes & salles</h3>
            <p className="mt-1 text-xs text-slate-600">
              Choisissez un groupe pour affecter ou remplacer un surveillant.
            </p>

            <div className="mt-4 space-y-2">
              {groups.map(({ key, group }) => (
                <label
                  key={key}
                  className={`block cursor-pointer rounded-lg border p-3 transition ${
                    selectedGroupKey === key
                      ? "border-indigo-500 bg-white ring-2 ring-indigo-500/20"
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
                      handleCancelReplace();
                    }}
                    className="sr-only"
                  />
                  <p className="text-sm font-medium text-slate-950">
                    Groupe {group.groupe?.numero ?? "—"} · Salle {group.salle?.code ?? "—"}
                  </p>
                  <p className="mt-1 text-xs text-slate-600">
                    {group.surveillants_affectes.length} / {group.surveillants_requis} affecté(s)
                    {group.manquants > 0 ? ` · ${group.manquants} manquant(s)` : ""}
                  </p>

                  {selectedGroupKey === key && group.surveillants_affectes.length > 0 ? (
                    <ul className="mt-2 space-y-1 border-t border-slate-100 pt-2">
                      {group.surveillants_affectes.map((s) => (
                        <li
                          key={s.surveillance_id}
                          className="flex items-center justify-between gap-2 text-xs"
                        >
                          <span className="text-slate-700">
                            {s.prenom} {s.nom}
                          </span>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.preventDefault();
                              handleStartReplace(s.surveillance_id);
                            }}
                            className="shrink-0 rounded px-2 py-0.5 font-medium text-indigo-600 hover:bg-indigo-50"
                          >
                            Remplacer
                          </button>
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </label>
              ))}
            </div>

            {isReplaceMode ? (
              <div className="mt-4 rounded-md border border-indigo-200 bg-indigo-50 p-3 text-xs text-indigo-900">
                Mode remplacement : sélectionnez un enseignant dans la liste.
                <button
                  type="button"
                  onClick={handleCancelReplace}
                  className="mt-2 block font-medium text-indigo-700 underline"
                >
                  Annuler le remplacement
                </button>
              </div>
            ) : slotsToFill > 0 ? (
              <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                À sélectionner : {selectedEnseignants.size} / {slotsToFill}
              </div>
            ) : (
              <div className="mt-4 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
                Groupe complet. Utilisez « Remplacer » sur un surveillant existant.
              </div>
            )}
          </aside>

          <div className="flex min-h-0 flex-col overflow-hidden p-5">
            <div className="grid shrink-0 gap-3 md:grid-cols-[1fr_200px_auto]">
              <input
                type="search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Rechercher nom, grade, département..."
                className="h-10 rounded-lg border border-slate-300 px-3 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
              />
              <select
                value={filterDepartement ?? ""}
                onChange={(e) =>
                  setFilterDepartement(e.target.value ? Number(e.target.value) : null)
                }
                className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm"
              >
                <option value="">Tous départements</option>
                {availableEnseignants?.departements.map((dept) => (
                  <option key={dept.departement_id} value={dept.departement_id}>
                    {dept.departement_nom} ({dept.total})
                  </option>
                ))}
              </select>
              <label className="flex h-10 items-center gap-2 rounded-lg border border-slate-300 px-3 text-sm">
                <input
                  type="checkbox"
                  checked={showOnlyWarnings}
                  onChange={(e) => setShowOnlyWarnings(e.target.checked)}
                />
                Avec alerte
              </label>
            </div>

            {loadingList ? (
              <p className="py-16 text-center text-sm text-slate-500">Chargement des enseignants...</p>
            ) : (
              <div className="mt-4 flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg border border-slate-200">
                <div className="shrink-0 border-b border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-700">
                  {filteredEnseignants.length} enseignant(s) disponible(s)
                  {isReplaceMode ? " · remplacement" : ""}
                </div>
                <div className="min-h-0 flex-1 divide-y divide-slate-100 overflow-y-auto">
                  {filteredEnseignants.map((ens) => {
                    const checked = selectedEnseignants.has(ens.enseignant_id);
                    const maxReached =
                      !isReplaceMode &&
                      !checked &&
                      selectedEnseignants.size >= slotsToFill &&
                      slotsToFill > 0;

                    return (
                      <label
                        key={ens.enseignant_id}
                        className={`flex cursor-pointer gap-3 px-4 py-3 md:items-center ${
                          maxReached ? "bg-slate-50 opacity-50" : "hover:bg-slate-50"
                        }`}
                      >
                        <input
                          type={isReplaceMode ? "radio" : "checkbox"}
                          name="enseignant"
                          checked={checked}
                          disabled={maxReached}
                          onChange={() => handleToggleEnseignant(ens.enseignant_id)}
                          className="h-4 w-4 shrink-0"
                        />
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-slate-950">
                            {ens.nom} {ens.prenom}
                          </p>
                          <p className="text-xs text-slate-500">
                            {ens.grade || "—"} · {ens.departement?.nom || "—"}
                          </p>
                          {ens.avertissements?.length ? (
                            <p className="mt-1 text-xs text-amber-700">{ens.avertissements.join(", ")}</p>
                          ) : null}
                        </div>
                        <div className="shrink-0 text-right">
                          <p className="text-sm font-semibold text-slate-900">
                            {ens.volume_restant.toFixed(1)} h
                          </p>
                          <p className="text-[10px] text-slate-500">restant</p>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        <footer className="flex shrink-0 flex-col gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-slate-600">
            {isReplaceMode
              ? "Sélectionnez le nouvel enseignant puis confirmez."
              : slotsToFill > 0
                ? "Cochez les enseignants à affecter pour le groupe sélectionné."
                : "Remplacez un surveillant existant ou changez de groupe."}
          </p>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-100"
            >
              Annuler
            </button>
            <button
              type="button"
              onClick={() => void handleAssign()}
              disabled={!canSubmit}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Enregistrement..." : isReplaceMode ? "Confirmer le remplacement" : "Affecter"}
            </button>
          </div>
        </footer>
      </section>
    </div>
  );
}

function getAllGroups(planif: PlanificationResult): GroupEntry[] {
  return (planif.groupes ?? []).map((group, index) => ({
    key: `${group.groupe?.id ?? "g"}-${group.salle?.id ?? "s"}-${index}`,
    group,
  }));
}

function formatSlotDate(value?: string | null) {
  if (!value) return "—";
  const date = new Date(value.includes("T") ? value : `${value}T12:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("fr-FR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
  }).format(date);
}
