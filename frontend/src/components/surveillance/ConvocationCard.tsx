type ConvocationCardProps = {
  enseignant: string;
  matiere: string;
  salle: string;
  date: string;
};

export function ConvocationCard({
  enseignant,
  matiere,
  salle,
  date,
}: ConvocationCardProps) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="text-base font-semibold text-slate-900">Convocation</h3>
      <p className="text-sm text-slate-600">Enseignant: {enseignant}</p>
      <p className="text-sm text-slate-600">Matiere: {matiere}</p>
      <p className="text-sm text-slate-600">Salle: {salle}</p>
      <p className="text-sm text-slate-600">Date: {date}</p>
    </article>
  );
}
