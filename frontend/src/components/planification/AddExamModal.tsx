"use client";

import { useEffect, useMemo, useState } from "react";
import type { CatalogueSalle } from "@/lib/api/referentiel";
import { getSallesDisponibles } from "@/lib/api/referentiel";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { isApiError } from "@/lib/api/errors";

type AddExamModalProps = {
  open: boolean;
  date: string;
  hour: number;
  availableMatieres: string[];
  salles: CatalogueSalle[];
  studentCount: number;
  onClose: () => void;
  onCreate: (data: {
    matiere: string;
    date: string;
    heureDebut: string;
    heureFin: string;
    duree: number;
    salles: Array<{
      salle_id: string;
      salle_capacite: number;
      salle_batiment: string | null;
      groupe_id: number;
      groupe_effectif: number;
    }>;
  }) => Promise<void>;
};

export function AddExamModal({
  open,
  date,
  hour,
  availableMatieres,
  salles,
  studentCount,
  onClose,
  onCreate,
}: AddExamModalProps) {
  const [matiere, setMatiere] = useState("");
  const [duree, setDuree] = useState(120);
  const [selectedSalles, setSelectedSalles] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [constraintErrors, setConstraintErrors] = useState<string[]>([]);
  const [sallesListe, setSallesListe] = useState<CatalogueSalle[]>(salles);
  const [loadingSalles, setLoadingSalles] = useState(false);

  const heureDebut = `${String(hour).padStart(2, "0")}:00:00`;
  const heureFinMinutes = hour * 60 + duree;
  const heureFin = `${String(Math.floor(heureFinMinutes / 60)).padStart(2, "0")}:${String(heureFinMinutes % 60).padStart(2, "0")}:00`;

  useEffect(() => {
    if (!open || !date) {
      return;
    }
    let cancelled = false;
    setLoadingSalles(true);
    void getSallesDisponibles({
      date_examen: date,
      heure_debut: heureDebut,
      capacite_min: 1,
      toutes_les_salles: true,
    })
      .then((rows) => {
        if (!cancelled) {
          setSallesListe(rows);
          setSelectedSalles((prev) =>
            prev.filter((id) => rows.some((s) => s.salle_id === id && s.disponible !== false)),
          );
        }
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
  }, [open, date, hour, heureDebut, studentCount, salles]);

  // Calculate room allocation
  const roomAllocation = useMemo(() => {
    if (selectedSalles.length === 0) return null;

    const rooms = selectedSalles
      .map((id) => sallesListe.find((s) => s.salle_id === id))
      .filter((s): s is CatalogueSalle => s !== undefined);

    const totalCapacity = rooms.reduce((sum, r) => sum + r.capacite, 0);
    const needsMultipleRooms = totalCapacity < studentCount;

    if (needsMultipleRooms && rooms.length === 1) {
      return {
        valid: false,
        message: `⚠️ Capacité insuffisante: ${rooms[0].capacite} places pour ${studentCount} étudiants`,
        groups: [],
      };
    }

    // Distribute students across rooms
    const groups: Array<{
      salle_id: string;
      salle_capacite: number;
      salle_batiment: string | null;
      groupe_id: number;
      groupe_effectif: number;
    }> = [];

    let remainingStudents = studentCount;
    rooms.forEach((room, index) => {
      const studentsInRoom = Math.min(room.capacite, remainingStudents);
      if (studentsInRoom > 0) {
        groups.push({
          salle_id: room.salle_id,
          salle_capacite: room.capacite,
          salle_batiment: room.batiment || null,
          groupe_id: index + 1,
          groupe_effectif: studentsInRoom,
        });
        remainingStudents -= studentsInRoom;
      }
    });

    return {
      valid: remainingStudents === 0,
      message:
        remainingStudents > 0
          ? `⚠️ ${remainingStudents} étudiants sans salle`
          : `✅ ${groups.length} groupe(s): ${groups.map((g) => `${g.groupe_effectif} étudiants`).join(", ")}`,
      groups,
    };
  }, [selectedSalles, sallesListe, studentCount]);

  const sallesLibres = useMemo(
    () => sallesListe.filter((s) => s.disponible !== false),
    [sallesListe],
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!matiere || !roomAllocation?.valid) return;

    setSaving(true);
    setError(null);
    setConstraintErrors([]);
    try {
      await onCreate({
        matiere,
        date,
        heureDebut,
        heureFin,
        duree,
        salles: roomAllocation.groups,
      });
      onClose();
    } catch (err) {
      if (isApiError(err)) {
        setError(err.message);
        setConstraintErrors(err.constraints);
      } else {
        setError(err instanceof Error ? err.message : "Echec de la creation");
      }
    } finally {
      setSaving(false);
    }
  };

  const toggleSalle = (salle: CatalogueSalle) => {
    if (salle.disponible === false) {
      return;
    }
    setSelectedSalles((prev) =>
      prev.includes(salle.salle_id)
        ? prev.filter((id) => id !== salle.salle_id)
        : [...prev, salle.salle_id],
    );
  };

  if (!open) return null;

  return (
    <Modal
      open={open}
      title="Ajouter un examen manuellement"
      description={`${date} à ${hour}:00 · ${studentCount} étudiants`}
      onClose={onClose}
      actions={
        <>
          <Button variant="secondary" onClick={onClose}>
            Annuler
          </Button>
          <Button
            onClick={handleSubmit}
            isLoading={saving}
            disabled={!matiere || !roomAllocation?.valid}
          >
            Créer l&apos;examen
          </Button>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error ? (
          <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
            <p className="font-medium">{error}</p>
            {constraintErrors.length > 1 ? (
              <ul className="mt-2 list-disc pl-5 text-xs">
                {constraintErrors.map((msg) => (
                  <li key={msg}>{msg}</li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : null}

        <label className="block text-sm font-medium text-slate-700">
          Matière
          <select
            value={matiere}
            onChange={(e) => setMatiere(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            required
          >
            <option value="">Sélectionner une matière...</option>
            {availableMatieres.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>

        <label className="block text-sm font-medium text-slate-700">
          Durée (minutes)
          <select
            value={duree}
            onChange={(e) => setDuree(Number(e.target.value))}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            <option value={60}>1 heure</option>
            <option value={90}>1h30</option>
            <option value={120}>2 heures</option>
            <option value={150}>2h30</option>
            <option value={180}>3 heures</option>
          </select>
        </label>

        <div className="block text-sm font-medium text-slate-700">
          Salles ({sallesLibres.length} libre{sallesLibres.length !== 1 ? "s" : ""} sur{" "}
          {sallesListe.length})
          {loadingSalles ? (
            <p className="mt-2 text-xs text-slate-500">Chargement...</p>
          ) : null}
          <div className="mt-2 max-h-48 space-y-2 overflow-y-auto rounded-md border border-slate-300 p-3">
            {sallesListe.length === 0 && !loadingSalles ? (
              <p className="text-xs text-amber-700">Aucune salle dans le referentiel.</p>
            ) : null}
            {sallesLibres.length === 0 && sallesListe.length > 0 && !loadingSalles ? (
              <p className="mb-2 text-xs text-amber-700">
                Aucune salle libre a {heureDebut.slice(0, 5)} — toutes sont occupees.
              </p>
            ) : null}
            {sallesListe.map((salle) => {
              const libre = salle.disponible !== false;
              return (
                <label
                  key={salle.salle_id}
                  className={`flex items-center gap-2 rounded px-2 py-1 ${
                    libre ? "cursor-pointer hover:bg-slate-50" : "cursor-not-allowed opacity-60"
                  }`}
                >
                  <input
                    type="checkbox"
                    disabled={!libre}
                    checked={libre && selectedSalles.includes(salle.salle_id)}
                    onChange={() => toggleSalle(salle)}
                    className="h-4 w-4 rounded border-slate-300 disabled:cursor-not-allowed"
                  />
                  <span className="flex-1 text-sm">
                    {salle.salle_id} - {salle.capacite} places
                    {salle.batiment ? ` (${salle.batiment})` : ""}
                    {libre ? (
                      <span className="ml-1 text-emerald-600">· disponible</span>
                    ) : (
                      <span className="ml-1 text-slate-500">
                        · {salle.motif_indisponible ?? "indisponible"}
                      </span>
                    )}
                  </span>
                </label>
              );
            })}
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Vous pouvez combiner plusieurs salles libres si la capacite totale couvre{" "}
            {studentCount} etudiants.
          </p>
        </div>

        {roomAllocation && (
          <div
            className={`rounded-md px-3 py-2 text-xs ${
              roomAllocation.valid
                ? "bg-emerald-50 text-emerald-700"
                : "bg-orange-50 text-orange-700"
            }`}
          >
            {roomAllocation.message}
          </div>
        )}

        <div className="rounded-md bg-blue-50 px-3 py-2 text-xs text-blue-700">
          Horaire: {heureDebut.slice(0, 5)} - {heureFin.slice(0, 5)}
        </div>
      </form>
    </Modal>
  );
}
