export default function Home() {
  return (
    <section className="space-y-4">
      <h2 className="text-2xl font-semibold text-slate-900">Accueil</h2>
      <p className="text-sm text-slate-700">
        Cette base suit une convention stricte: logique metier dans hooks/services uniquement.
      </p>
      <ul className="list-disc pl-5 text-sm text-slate-700">
        <li>/planification - gestion planification examens</li>
        <li>/surveillance - gestion affectation surveillance</li>
        <li>/salles et /matieres - referentiel</li>
        <li>/enseignants et /convocation - flux enseignant</li>
      </ul>
    </section>
  );
}
