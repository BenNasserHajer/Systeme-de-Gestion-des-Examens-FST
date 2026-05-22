"use client";

import { useState } from "react";
import { usePlanifications } from "@/hooks/usePlanifications";
import { useSalles } from "@/hooks/useSalles";
import { EmploiDuTemps } from "@/components/planification/EmploiDuTemps";
import { GroupeTable } from "@/components/planification/GroupeTable";
import PlanifGeneration from "@/components/planification/PlaniGeneration_artifact";

// ─── ID de session par défaut (à adapter selon votre logique) ─────────────────
const DEFAULT_SESSION_ID = 1;

export default function PlanificationPage() {
  const [activeTab, setActiveTab] = useState<"planif" | "salles">("planif");
  const [deptFilter, setDeptFilter] = useState("");
  const [statutFilter, setStatutFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");

  // ── Données depuis FastAPI ──────────────────────────────────────────────────
  const {
    planifications,
    stats,
    loading: loadingPlanif,
    error: errorPlanif,
    refresh: refreshPlanif,
    deletePlanif,
  } = usePlanifications(DEFAULT_SESSION_ID);

  const {
    salles,
    loading: loadingSalles,
    error: errorSalles,
    createSalle,
    deleteSalle,
  } = useSalles();

  // ── Filtrage côté client ───────────────────────────────────────────────────
  const filtered = planifications.filter((p) => {
    if (deptFilter && p.departement_nom !== deptFilter) return false;
    if (statutFilter && p.statut !== statutFilter) return false;
    if (dateFilter && p.date !== dateFilter) return false;
    return true;
  });

  const depts = [...new Set(planifications.map((p) => p.departement_nom).filter(Boolean))];
  const dates = [...new Set(planifications.map((p) => p.date))].sort();

  // ── Badge statut ───────────────────────────────────────────────────────────
  const badgeClass = (s: string) =>
    s === "Planifié"
      ? "bg-green-100 text-green-800"
      : s === "Conflit"
      ? "bg-red-100 text-red-800"
      : "bg-amber-100 text-amber-800";

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-900">Planification</h2>
        <button
          onClick={refreshPlanif}
          className="text-sm text-slate-500 hover:text-slate-800 border border-slate-200 rounded-lg px-3 py-1.5"
        >
          ↺ Actualiser
        </button>
      </div>

      {/* Onglets */}
      <div className="flex gap-1 border-b border-slate-200">
        {(["planif", "salles"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? "border-slate-900 text-slate-900"
                : "border-transparent text-slate-500 hover:text-slate-700"
            }`}
          >
            {tab === "planif" ? "Planification des examens" : "Gestion des salles"}
          </button>
        ))}
      </div>

      {/* ── Onglet Planification ── */}
      {activeTab === "planif" && (
        <div className="space-y-4">
          {/* Génération automatique */}
          <PlanifGeneration />

          {/* Erreur / chargement */}
          {loadingPlanif && (
            <p className="text-sm text-slate-500">Chargement des planifications…</p>
          )}
          {errorPlanif && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {errorPlanif}
            </div>
          )}

          {/* Stats */}
          {!loadingPlanif && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { val: stats.total, lbl: "Planifiés" },
                { val: stats.conflits, lbl: "Conflits" },
                { val: stats.sections, lbl: "Sections" },
                { val: stats.score_moyen ?? "—", lbl: "Score moyen" },
              ].map(({ val, lbl }) => (
                <div key={lbl} className="bg-slate-50 rounded-lg p-3">
                  <p className="text-2xl font-medium text-slate-900">{val}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{lbl}</p>
                </div>
              ))}
            </div>
          )}

          {/* Filtres */}
          <div className="flex flex-wrap gap-2">
            <select
              value={deptFilter}
              onChange={(e) => setDeptFilter(e.target.value)}
              className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 bg-white text-slate-700"
            >
              <option value="">Tous les départements</option>
              {depts.map((d) => (
                <option key={d!} value={d!}>{d}</option>
              ))}
            </select>
            <select
              value={statutFilter}
              onChange={(e) => setStatutFilter(e.target.value)}
              className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 bg-white text-slate-700"
            >
              <option value="">Tous les statuts</option>
              {["Planifié", "Conflit", "En attente"].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 bg-white text-slate-700"
            >
              <option value="">Toutes les dates</option>
              {dates.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          {/* Tableau */}
          {!loadingPlanif && filtered.length > 0 && (
            <div className="rounded-xl border border-slate-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50 border-b border-slate-200">
                    <tr>
                      {["Matière", "Section", "Date", "Horaire", "Salle(s)", "Effectif", "Groupes", "Statut", ""].map(
                        (h) => (
                          <th
                            key={h}
                            className="px-3 py-2.5 text-left text-xs font-medium text-slate-500 uppercase tracking-wide"
                          >
                            {h}
                          </th>
                        )
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {filtered.map((p) => {
                      const sallesCodes = p.attributions.map((a) => a.salle_code).join(", ");
                      const totalEff = p.attributions.reduce((s, a) => s + a.groupe_effectif, 0);
                      return (
                        <tr
                          key={p.id}
                          className={p.statut === "Conflit" ? "bg-red-50" : "hover:bg-slate-50"}
                        >
                          <td className="px-3 py-2.5 font-medium text-slate-900 max-w-[160px] truncate" title={p.intitule}>
                            {p.intitule}
                          </td>
                          <td className="px-3 py-2.5 text-slate-500 truncate">{p.section_nom}</td>
                          <td className="px-3 py-2.5 tabular-nums">{p.date}</td>
                          <td className="px-3 py-2.5 tabular-nums whitespace-nowrap">
                            {p.heure_debut} – {p.heure_fin}
                          </td>
                          <td className="px-3 py-2.5 truncate" title={sallesCodes}>{sallesCodes || "—"}</td>
                          <td className="px-3 py-2.5">{totalEff || "—"}</td>
                          <td className="px-3 py-2.5">{p.nb_groupes}</td>
                          <td className="px-3 py-2.5">
                            <span className={`inline-block text-xs px-2 py-0.5 rounded font-medium ${badgeClass(p.statut)}`}>
                              {p.statut}
                            </span>
                          </td>
                          <td className="px-3 py-2.5">
                            <button
                              onClick={() => deletePlanif(p.id)}
                              className="text-xs text-slate-400 hover:text-red-600"
                            >
                              Supprimer
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {!loadingPlanif && filtered.length === 0 && !errorPlanif && (
            <p className="text-sm text-slate-400 text-center py-8">
              Aucune planification trouvée pour ces filtres.
            </p>
          )}

          {/* Emploi du temps & groupes */}
          <EmploiDuTemps items={planifications} />
          <GroupeTable />
        </div>
      )}

      {/* ── Onglet Salles ── */}
      {activeTab === "salles" && (
        <div className="space-y-4">
          {loadingSalles && <p className="text-sm text-slate-500">Chargement des salles…</p>}
          {errorSalles && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {errorSalles}
            </div>
          )}

          {/* Stat capacité totale */}
          {!loadingSalles && (
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="text-2xl font-medium text-slate-900">{salles.length}</p>
                <p className="text-xs text-slate-500 mt-0.5">Salles</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="text-2xl font-medium text-slate-900">
                  {salles.reduce((s, r) => s + r.capacite, 0)}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">Capacité totale</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="text-2xl font-medium text-slate-900">
                  {new Set(salles.map((s) => s.batiment)).size}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">Bâtiments</p>
              </div>
            </div>
          )}

          {/* Tableau des salles */}
          {!loadingSalles && salles.length > 0 && (
            <div className="rounded-xl border border-slate-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    {["Code", "Bâtiment", "Capacité", "Département", ""].map((h) => (
                      <th
                        key={h}
                        className="px-4 py-2.5 text-left text-xs font-medium text-slate-500 uppercase tracking-wide"
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {salles.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-50">
                      <td className="px-4 py-2.5 font-medium text-slate-900">{s.code}</td>
                      <td className="px-4 py-2.5 text-slate-500">{s.batiment}</td>
                      <td className="px-4 py-2.5">{s.capacite}</td>
                      <td className="px-4 py-2.5 text-slate-500">{s.departement_nom ?? "Général"}</td>
                      <td className="px-4 py-2.5">
                        <button
                          onClick={() => deleteSalle(s.id)}
                          className="text-xs text-slate-400 hover:text-red-600"
                        >
                          Supprimer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Formulaire ajout salle */}
          <AddSalleForm onAdd={createSalle} />
        </div>
      )}
    </section>
  );
}

// ─── Formulaire ajout salle ────────────────────────────────────────────────────
function AddSalleForm({ onAdd }: { onAdd: (data: { code: string; batiment: string; capacite: number; departement_id: null }) => Promise<void> }) {
  const [code, setCode] = useState("");
  const [batiment, setBatiment] = useState("");
  const [capacite, setCapacite] = useState(40);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!code || !batiment) return;
    setSubmitting(true);
    await onAdd({ code, batiment, capacite, departement_id: null });
    setCode(""); setBatiment(""); setCapacite(40);
    setSubmitting(false);
  };

  return (
    <div className="border border-slate-200 rounded-xl p-4 space-y-3">
      <p className="text-sm font-medium text-slate-700">Ajouter une salle</p>
      <div className="grid grid-cols-3 gap-3">
        <input
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Code (ex. D301)"
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-900 placeholder-slate-400"
        />
        <input
          value={batiment}
          onChange={(e) => setBatiment(e.target.value)}
          placeholder="Bâtiment (ex. Bât-D)"
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-900 placeholder-slate-400"
        />
        <input
          type="number"
          value={capacite}
          onChange={(e) => setCapacite(Number(e.target.value))}
          placeholder="Capacité"
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-900"
        />
      </div>
      <button
        onClick={handleSubmit}
        disabled={submitting || !code || !batiment}
        className="text-sm bg-slate-900 text-white px-4 py-2 rounded-lg disabled:opacity-50 hover:bg-slate-700"
      >
        {submitting ? "Ajout…" : "Ajouter"}
      </button>
    </div>
  );
}