"use client";

import { useEffect, useMemo, useState } from "react";

import type { Planification } from "@/lib/types/planification";
import type { CatalogueSalle } from "@/lib/api/referentiel";
import { getSallesDisponibles } from "@/lib/api/referentiel";

import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { formatTimeAmPm, getPrimarySalle } from "@/lib/utils/planificationHelpers";

type EditExamModalProps = {
  open: boolean;
  planif: Planification | null;
  salles: CatalogueSalle[];
  onClose: () => void;
  onSave: (planifId: number, salleId: string) => Promise<void>;
};

export function EditExamModal({ open, planif, salles, onClose, onSave }: EditExamModalProps) {
  const [sallesListe, setSallesListe] = useState<CatalogueSalle[]>(salles);
  const [loadingSalles, setLoadingSalles] = useState(false);
  const currentSalleId = planif ? getPrimarySalle(planif) : "";

  useEffect(() => {
    if (!open || !planif) {
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

  return (
    <Modal
      open={open}
      title={`Modifier · ${planif.matiere}`}
      description={`${planif.date_examen} · ${formatTimeAmPm(planif.heure_debut)} - ${formatTimeAmPm(planif.heure_fin)}`}
      onClose={onClose}
      actions={
        <>
          <Button variant="secondary" onClick={onClose}>
            Annuler
          </Button>
          <SaveButton
            planif={planif}
            defaultSalleId={currentSalleId}
            disabled={!loadingSalles && !hasSelectable}
            onSave={onSave}
            onClose={onClose}
          />
        </>
      }
    >
      <form id="edit-exam-form" className="space-y-4">
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
      </form>
    </Modal>
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
