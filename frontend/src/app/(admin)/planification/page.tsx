"use client";

import { ExamCalendarGrid } from "@/components/planification/ExamCalendarGrid";
import { PlanificationForm } from "@/components/planification/PlanificationForm";
import { Button } from "@/components/ui/Button";
import { usePlanificationSchedule } from "@/hooks/usePlanificationSchedule";

export default function PlanificationPage() {
  const {
    catalogue,
    items,
    loading,
    error,
    generationResult,
    generate,
    validateAll,
    refreshSchedule,
    sessionId,
    sectionId,
  } = usePlanificationSchedule();

  const draftCount = items.filter((item) => item.statut === "BROUILLON").length;

  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Planification des examens</h2>
          <p className="text-sm text-slate-600">
            Generez l&apos;emploi du temps, ajustez par glisser-deposer, puis validez.
          </p>
        </div>
        <Button
          variant="secondary"
          isLoading={loading}
          disabled={!sessionId || draftCount === 0}
          onClick={() => void validateAll()}
        >
          Valider ({draftCount})
        </Button>
      </header>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <PlanificationForm catalogue={catalogue} loading={loading} onGenerate={generate} />

      {generationResult ? (
        <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
          {generationResult.nb_crees} examen(s) genere(s)
          {generationResult.nb_conflits > 0
            ? ` · ${generationResult.nb_conflits} conflit(s) detecte(s)`
            : ""}
          {generationResult.conflits.length > 0 ? (
            <ul className="mt-2 list-disc pl-5 text-xs">
              {generationResult.conflits.map((msg) => (
                <li key={msg}>{msg}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      {items.length > 0 ? (
        <ExamCalendarGrid
          items={items}
          salles={catalogue?.salles ?? []}
          onUpdated={() => refreshSchedule(sessionId, sectionId)}
        />
      ) : (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">
          Aucun emploi du temps. Remplissez le formulaire et cliquez sur &quot;Generer automatiquement&quot;.
        </div>
      )}
    </section>
  );
}
