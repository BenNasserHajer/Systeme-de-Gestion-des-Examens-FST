"use client";

type DisponibiliteFormProps = {
  onSubmit: (payload: { date: string; type: string }) => void;
};

export function DisponibiliteForm({ onSubmit }: DisponibiliteFormProps) {
  return (
    <form
      className="space-y-3 rounded-lg border border-slate-200 bg-white p-4"
      onSubmit={(event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        onSubmit({
          date: String(formData.get("date") ?? ""),
          type: String(formData.get("type") ?? "DISPONIBLE"),
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
      <select
        name="type"
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
        defaultValue="DISPONIBLE"
      >
        <option value="DISPONIBLE">Disponible</option>
        <option value="INDISPONIBLE">Indisponible</option>
      </select>
      <button
        type="submit"
        className="rounded-md bg-slate-900 px-3 py-2 text-sm font-medium text-white"
      >
        Enregistrer
      </button>
    </form>
  );
}
