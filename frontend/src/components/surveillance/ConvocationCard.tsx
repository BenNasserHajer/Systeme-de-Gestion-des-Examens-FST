type ConvocationAssignment = {
  matiere: string;
  date: string;
  heure_debut?: string;
  heure_fin?: string;
  salle?: string;
  groupe?: string;
  charge?: number;
};

type ConvocationCardProps = {
  enseignant: {
    nom: string;
    prenom: string;
    grade?: string | null;
    departement?: string | null;
    email?: string | null;
  };
  session?: {
    type_session?: string | null;
    annee_universitaire?: string | null;
  };
  assignments: ConvocationAssignment[];
  onExport?: () => void;
};

export function ConvocationCard({
  enseignant,
  session,
  assignments,
  onExport,
}: ConvocationCardProps) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Convocation</h3>
          <p className="text-sm text-slate-600">
            {enseignant.prenom} {enseignant.nom}
          </p>
          {enseignant.grade ? (
            <p className="text-xs text-slate-500">{enseignant.grade}</p>
          ) : null}
          {enseignant.departement ? (
            <p className="text-xs text-slate-500">{enseignant.departement}</p>
          ) : null}
        </div>
        {onExport ? (
          <button
            type="button"
            className="rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100"
            onClick={onExport}
          >
            Exporter PDF
          </button>
        ) : null}
      </div>

      {session ? (
        <div className="mt-3 text-xs text-slate-500">
          {session.type_session ?? "Session"} · {session.annee_universitaire ?? "—"}
        </div>
      ) : null}

      <div className="mt-4 space-y-3">
        {assignments.length === 0 ? (
          <p className="text-sm text-slate-500">Aucune surveillance assignée.</p>
        ) : (
          assignments.map((assignment, index) => (
            <div key={index} className="rounded-md border border-slate-100 bg-slate-50 px-3 py-2">
              <p className="text-sm font-medium text-slate-800">
                {assignment.matiere}
              </p>
              <p className="text-xs text-slate-600">
                {assignment.date}
                {assignment.heure_debut ? ` · ${assignment.heure_debut}` : ""}
                {assignment.heure_fin ? ` - ${assignment.heure_fin}` : ""}
              </p>
              <p className="text-xs text-slate-600">
                Salle: {assignment.salle ?? "—"} · Groupe: {assignment.groupe ?? "—"}
              </p>
              {assignment.charge !== undefined ? (
                <p className="text-xs text-slate-600">Charge: {assignment.charge}</p>
              ) : null}
            </div>
          ))
        )}
      </div>
    </article>
  );
}
