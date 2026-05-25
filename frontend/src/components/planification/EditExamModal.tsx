"use client";

import { useEffect, useMemo, useState } from "react";

import type { Planification } from "@/lib/types/planification";
import type { CatalogueSalle } from "@/lib/api/referentiel";
import { getSallesDisponibles } from "@/lib/api/referentiel";
import { deplacerPlanification } from "@/lib/api/planification";

import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { formatTimeAmPm, getPrimarySalle, addMinutesToTime } from "@/lib/utils/planificationHelpers";

type EditExamModalProps = {
  open: boolean;
  planif: Planification | null;
  salles: CatalogueSalle[];
  onClose: () => void;
  onSave: (planifId: number, salleId: string) => Promise<void>;
  onUpdated?: () => Promise<void>;
};

type EditMode = "salle" | "datetime";

export function EditExamModal({ open, planif, salles, onClose, onSave, onUpdated }: EditExamModalProps) {
  const [mode, setMode] = useState<EditMode>("salle");
  const [sallesListe, setSallesListe] = useState<CatalogueSalle[]>(salles);
  const [loadingSalles, setLoadingSalles] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const currentSalleId = planif ? getPrimarySalle(planif) : "";

  useEffect(() => {
    if (!open || !planif) {
      setMode("salle");
      setError(null);
      return;
    }
    let cancelled = false;
    setLoadingSalles(true);
    void getSallesDisponibles({
      date_examen: planif.date_examen,
      heure_debut: planif.heure_debut,
      capacite_min: 1,
      exclude_planif_id: planif.id,
      toutes_les_salles: true,
    })
      .then((rows) => {
        if (cancelled) {
          return;
        }
        const merged = [...rows];
        if (currentSalleId && !merged.some((s) => s.salle_id === currentSalleId)) {
          const fromCatalogue = salles.find((s) => s.salle_id === currentSalleId);
          merged.unshift(
            fromCatalogue ?? {
              salle_id: currentSalleId,
              capacite: planif.section_nb_etudiants,
              batiment: planif.salles[0]?.salle_batiment ?? undefined,
              disponible: true,
            },
          );
        }
        setSallesListe(merged);
      })
      .catch(() => {
        if (!cancelled) {
          setSallesListe(salles.map((s) => ({ ...s, disponible: true })));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoadingSalles(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [open, planif, salles, currentSalleId]);

  const selectOptions = useMemo(() => sallesListe, [sallesListe]);
  const hasSelectable = selectOptions.some((s) => s.disponible !== false);

  if (!planif) {
    return null;
  }

  const handleSaveSalle = async () => {
    const select = document.querySelector<HTMLSelectElement>('select[name="salle"]');
    const salleId = select?.value || currentSalleId;
    if (!salleId) {
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await onSave(planif.id, salleId);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors de la sauvegarde");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveDateTime = async () => {
    const dateInput = document.querySelector<HTMLInputElement>('input[name="date"]');
    const heureInput = document.querySelector<HTMLInputElement>('input[name="heure"]');
    const dureeInput = document.querySelector<HTMLInputElement>('input[name="duree"]');
    
    const newDate = dateInput?.value || planif.date_examen;
    const newHeure = heureInput?.value || planif.heure_debut.slice(0, 5);
    const newDuree = parseInt(dureeInput?.value || String(planif.duree), 10);
    
    const heureDebut = `${newHeure}:00`;
    const heureFin = addMinutesToTime(heureDebut, newDuree);
    
    setSaving(true);
    setError(null);
    try {
      await deplacerPlanification(planif.id, {
        nouvelle_date: newDate,
        nouvelle_heure_debut: heureDebut,
        nouvelle_heure_fin: heureFin,
      });
      if (onUpdated) {
        await onUpdated();
      }
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur lors du déplacement");
    } finally {
      setSaving(false);
    }
  };

  const isEditable = planif.statut === "BROUILLON";

  return (
    <Modal
      open={open}
      title={`Modifier · ${planif.matiere}`}
      description={`${planif.date_examen} · ${formatTimeAmPm(planif.heure_debut)} - ${formatTimeAmPm(planif.heure_fin)} · ${planif.statut}`}
      onClose={onClose}
      actions={
        <>
          <Button variant="secondary" onClick={onClose}>
            Annuler
          </Button>
          <Button
            isLoading={saving}
            disabled={!isEditable || (mode === "salle" && (!loadingSalles && !hasSelectable))}
            onClick={mode === "salle" ? handleSaveSalle : handleSaveDateTime}
          >
            Enregistrer
          </Button>
        </>
      }
    >
      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </div>
      )}

      {!isEditable && (
        <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Cette planification est {planif.statut.toLowerCase()} et ne peut plus être modifiée.
        </div>
      )}

      {/* Mode selector */}
      <div className="mb-4 flex gap-2 rounded-lg border border-slate-200 bg-slate-50 p-1">
        <button
          type="button"
          onClick={() => setMode("salle")}
          disabled={!isEditable}
          className={`flex-1 rounded px-3 py-2 text-sm font-medium transition ${
            mode === "salle"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900"
          } disabled:opacity-50`}
        >
          Changer la salle
        </button>
        <button
          type="button"
          onClick={() => setMode("datetime")}
          disabled={!isEditable}
          className={`flex-1 rounded px-3 py-2 text-sm font-medium transition ${
            mode === "datetime"
              ? "bg-white text-slate-900 shadow-sm"
              : "text-slate-600 hover:text-slate-900"
          } disabled:opacity-50`}
        >
          Changer date/heure
        </button>
      </div>

      {mode === "salle" ? (
        <SalleEditor
          planif={planif}
          currentSalleId={currentSalleId}
          selectOptions={selectOptions}
          loadingSalles={loadingSalles}
          hasSelectable={hasSelectable}
        />
      ) : (
        <DateTimeEditor planif={planif} />
      )}
    </Modal>
  );
}

function SalleEditor({
  planif,
  currentSalleId,
  selectOptions,
  loadingSalles,
  hasSelectable,
}: {
  planif: Planification;
  currentSalleId: string;
  selectOptions: CatalogueSalle[];
  loadingSalles: boolean;
  hasSelectable: boolean;
}) {
  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-slate-700">
        Choisir une salle
        {loadingSalles ? (
          <p className="mt-1 text-xs text-slate-500">Chargement...</p>
        ) : null}
        <select
          name="salle"
          key={`${planif.id}-${selectOptions.length}`}
          defaultValue={currentSalleId}
          disabled={loadingSalles || !hasSelectable}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-100"
        >
          {!hasSelectable ? (
            <option value="">Aucune salle selectable</option>
          ) : (
            selectOptions.map((salle) => (
              <option
                key={salle.salle_id}
                value={salle.salle_id}
                disabled={salle.disponible === false}
              >
                {salle.salle_id} ({salle.capacite} places)
                {salle.batiment ? ` · ${salle.batiment}` : ""}
                {salle.disponible === false
                  ? ` — ${salle.motif_indisponible ?? "indisponible"}`
                  : " — disponible"}
              </option>
            ))
          )}
        </select>
      </label>
      <p className="text-xs text-slate-500">
        Toutes les salles du referentiel sont listees. Seules les salles libres a cet horaire
        peuvent etre selectionnees.
      </p>
    </div>
  );
}

function DateTimeEditor({ planif }: { planif: Planification }) {
  const defaultHeure = planif.heure_debut.slice(0, 5); // "HH:MM"
  
  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-slate-700">
        Date de l&apos;examen
        <input
          type="date"
          name="date"
          defaultValue={planif.date_examen}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
      </label>

      <label className="block text-sm font-medium text-slate-700">
        Heure de début
        <input
          type="time"
          name="heure"
          defaultValue={defaultHeure}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
      </label>

      <label className="block text-sm font-medium text-slate-700">
        Durée (minutes)
        <input
          type="number"
          name="duree"
          defaultValue={planif.duree}
          min="30"
          max="300"
          step="15"
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
      </label>

      <div className="rounded-md border border-blue-200 bg-blue-50 px-3 py-2 text-xs text-blue-800">
        <p className="font-medium">Informations actuelles :</p>
        <ul className="mt-1 space-y-0.5">
          <li>• Date : {planif.date_examen}</li>
          <li>• Horaire : {formatTimeAmPm(planif.heure_debut)} - {formatTimeAmPm(planif.heure_fin)}</li>
          <li>• Durée : {planif.duree} minutes</li>
          <li>• Salle : {getPrimarySalle(planif)}</li>
        </ul>
      </div>

      <p className="text-xs text-slate-500">
        La modification de la date ou de l&apos;heure vérifiera automatiquement les contraintes
        (disponibilité de la salle, conflits avec d&apos;autres examens, etc.).
      </p>
    </div>
  );
}

function SaveButton({
  planif,
  defaultSalleId,
  disabled,
  onSave,
  onClose,
}: {
  planif: Planification;
  defaultSalleId: string;
  disabled?: boolean;
  onSave: (planifId: number, salleId: string) => Promise<void>;
  onClose: () => void;
}) {
  return (
    <Button
      disabled={disabled}
      onClick={async () => {
        const select = document.querySelector<HTMLSelectElement>('select[name="salle"]');
        const salleId = select?.value || defaultSalleId;
        if (!salleId) {
          return;
        }
        await onSave(planif.id, salleId);
        onClose();
      }}
    >
      Enregistrer
    </Button>
  );
}
