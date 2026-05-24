import type { AffecterSessionResponse } from "@/lib/types/surveillance";

type AffectationBoardProps = {
  data: AffecterSessionResponse | null;
};

export function AffectationBoard({ data }: AffectationBoardProps) {
  if (!data) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
        Aucune affectation disponible.
      </div>
    );
  }

  return (
    <section className="space-y-4">
      <div className="grid gap-3 md:grid-cols-4">
        <StatCard label="Planifications" value={data.total_planifications} />
        <StatCard label="Affectées" value={data.affectees_automatiquement} />
        <StatCard label="En conflit" value={data.en_conflit} />
        <StatCard label="Non affectées" value={data.non_affectees.length} />
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <p className="text-sm text-slate-700">{data.message}</p>
      </div>

      <div className="space-y-3">
        {data.resultats.map((result) => (
          <div key={result.planification_id} className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">
                  Planification #{result.planification_id}
                </h3>
                <p className="text-xs text-slate-500">
                  {result.matiere?.intitule ?? "Matière"} · {result.section?.nom ?? "Section"}
                </p>
              </div>
              <span className="text-xs font-medium text-slate-500">
                {result.surveillants_affectes}/{result.surveillants_requis}
              </span>
            </div>

            {result.manquants > 0 ? (
              <p className="mt-2 text-xs text-amber-600">
                Manquants: {result.manquants}
              </p>
            ) : (
              <p className="mt-2 text-xs text-emerald-600">Affectation complète</p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

type StatCardProps = {
  label: string;
  value: number;
};

function StatCard({ label, value }: StatCardProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
