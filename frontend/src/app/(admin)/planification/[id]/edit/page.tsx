type EditPlanificationPageProps = {
  params: Promise<{ id: string }>;
};

export default async function EditPlanificationPage({
  params,
}: EditPlanificationPageProps) {
  const { id } = await params;

  return (
    <section className="space-y-2">
      <h2 className="text-xl font-semibold text-slate-900">Edition Planification</h2>
      <p className="text-sm text-slate-600">Planification ID: {id}</p>
      <p className="text-sm text-slate-600">
        La logique d edition est geree via hooks/services dans l etape suivante.
      </p>
    </section>
  );
}
