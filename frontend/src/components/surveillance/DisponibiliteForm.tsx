"use client";

import { Button } from "@/components/ui/Button";
import { DISPONIBILITE_TYPE_LABELS } from "@/lib/constants";
import type { DisponibiliteEnseignantCreatePayload } from "@/lib/types/surveillance";

type DisponibiliteFormProps = {
  enseignantId: number;
  onSubmit: (payload: DisponibiliteEnseignantCreatePayload) => void;
};

export function DisponibiliteForm({ enseignantId, onSubmit }: DisponibiliteFormProps) {
  return (
    <form
      className="space-y-3 rounded-lg border border-slate-200 bg-white p-4"
      onSubmit={(event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        onSubmit({
          enseignant_id: enseignantId,
          date: String(formData.get("date") ?? ""),
          heure_debut: String(formData.get("heure_debut") ?? ""),
          heure_fin: String(formData.get("heure_fin") ?? ""),
          type_dispo: String(formData.get("type_dispo") ?? "DISPONIBLE"),
          motif: String(formData.get("motif") ?? ""),
          confirme: Boolean(formData.get("confirme")),
        });
      }}
    >
      <h3 className="text-base font-semibold text-slate-900">Disponibilite</h3>
      <input
        type="date"
        name="date"
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        required
      />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <input
          type="time"
          name="heure_debut"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          required
        />
        <input
          type="time"
          name="heure_fin"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          required
        />
      </div>
      <select
        name="type_dispo"
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        defaultValue="DISPONIBLE"
      >
        {Object.entries(DISPONIBILITE_TYPE_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
      <input
        type="text"
        name="motif"
        placeholder="Motif (optionnel)"
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
      />
      <label className="flex items-center gap-2 text-xs text-slate-600">
        <input type="checkbox" name="confirme" defaultChecked className="h-4 w-4" />
        Confirmer cette indisponibilité
      </label>
      <Button type="submit">Enregistrer</Button>
    </form>
  );
}
