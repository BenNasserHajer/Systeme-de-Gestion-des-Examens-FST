"use client";

import { useMemo, useState } from "react";

import { ExamCalendarGrid } from "@/components/planification/ExamCalendarGrid";
import { PlanificationForm } from "@/components/planification/PlanificationForm";
import { UnscheduledExamsList } from "@/components/planification/UnscheduledExamsList";
import { AddExamModal } from "@/components/planification/AddExamModal";
import { Button } from "@/components/ui/Button";
import { usePlanificationSchedule } from "@/hooks/usePlanificationSchedule";
import { usePlanificationPDFExport } from "@/hooks/usePlanificationPDFExport";
import { createPlanification } from "@/lib/api/planification";
import { ApiError } from "@/lib/api/errors";
import type { ConflitDetail } from "@/lib/types/planification";
import { filterMatieresForSemestre, matiereMatchesSemestre } from "@/lib/utils/semestre";

function conflictMessage(item: ConflitDetail | string): string {
  return typeof item === "string" ? item : item.message;
}

export default function PlanificationPage() {
  const {
    catalogue,
    items,
    loading,
    error,
    generationResult,
    warnings,
    generate,
    validateAll,
    refreshSchedule,
    sessionId,
    sectionId,
    semestre,
    setSemestre,
    setWarnings,
  } = usePlanificationSchedule();

  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<{ date: string; hour: number } | null>(null);
  
  const { exportPDF, loading: exporting, error: exportError } = usePlanificationPDFExport();
  
  const draftCount = items.filter((item) => item.statut === "BROUILLON").length;

  const conflictIds = useMemo(() => new Set<number>(), [generationResult]);

  const sectionLabel = useMemo(
    () => catalogue?.sections.find((s) => s.section_id === sectionId)?.label,
    [catalogue, sectionId],
  );

  const matieresForSemestre = useMemo(() => {
    if (!catalogue || !sectionLabel) return [];
    return filterMatieresForSemestre(
      catalogue.matieres_by_section[sectionLabel] ?? [],
      semestre,
    );
  }, [catalogue, sectionLabel, semestre]);

  const unscheduledMatieres = useMemo(() => {
    if (!generationResult) return [];
    const allowedNames = new Set(matieresForSemestre.map((m) => m.matiere));
    return generationResult.conflits
      .map((c) => {
        const msg = conflictMessage(c);
        const match = msg.match(/Section-\d+ \/ (.+?) -/);
        return match ? match[1] : null;
      })
      .filter((m): m is string => m !== null)
      .filter((m) => allowedNames.has(m))
      .filter((m) => !items.some((exam) => exam.matiere === m));
  }, [generationResult, items, matieresForSemestre]);

  const handleClickSlot = (date: string, hour: number) => {
    if (unscheduledMatieres.length === 0) {
      alert("Aucun examen non planifié. Tous les examens sont déjà dans le calendrier.");
      return;
    }
    setSelectedSlot({ date, hour });
    setAddModalOpen(true);
  };

  const handleCreateExam = async (data: {
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
  }) => {
    if (!sessionId || !sectionId || !catalogue) {
      throw new ApiError("Session ou section non selectionnee.");
    }

    const section = catalogue.sections.find((s) => s.section_id === sectionId);
    if (!section) {
      throw new ApiError("Section introuvable dans le catalogue.");
    }

    const session = catalogue.sessions.find((s) => s.session_id === sessionId);
    if (!session) {
      throw new ApiError("Session introuvable dans le catalogue.");
    }

    const matiereInfo = matieresForSemestre.find((m) => m.matiere === data.matiere);
    if (!matiereInfo) {
      throw new ApiError(
        `La matiere "${data.matiere}" n'est pas disponible pour ${section.label} en ${semestre}.`,
      );
    }
    if (!matiereMatchesSemestre(matiereInfo.semestre, semestre)) {
      throw new ApiError(`La matiere "${data.matiere}" n'appartient pas au semestre ${semestre}.`);
    }

    const examDate = new Date(`${data.date}T12:00:00`);
    const sessionStart = new Date(`${session.date_debut}T00:00:00`);
    const sessionEnd = new Date(`${session.date_fin}T23:59:59`);

    if (examDate < sessionStart || examDate > sessionEnd) {
      throw new ApiError(
        `La date ${data.date} doit etre entre ${session.date_debut} et ${session.date_fin}.`,
      );
    }

    await createPlanification({
      session_id: sessionId,
      section_id: sectionId,
      section_matiere_id: matiereInfo.section_matiere_id,
      matiere: data.matiere,
      semestre,
      type_epreuve: "EXAMEN_FINAL",
      date_examen: data.date,
      heure_debut: data.heureDebut,
      heure_fin: data.heureFin,
      duree: data.duree,
      session_date_debut: session.date_debut,
      session_date_fin: session.date_fin,
      section_nb_etudiants: section.effectif,
      nb_groupes: data.salles.length,
      mode_affectation: "MANUEL",
      statut: "BROUILLON",
      coefficient: matiereInfo.coefficient,
      nb_surveillants_requis: matiereInfo.nb_surveillants_requis,
      salles: data.salles,
    });

    setAddModalOpen(false);
    await refreshSchedule(sessionId, sectionId);

    const groupInfo =
      data.salles.length > 1
        ? ` (${data.salles.length} groupes dans ${data.salles.length} salles)`
        : "";
    setSuccessMessage(`Examen "${data.matiere}" ajoute avec succes${groupInfo}.`);
  };

  const handleValidate = async () => {
    setSuccessMessage(null);
    await validateAll();
    setSuccessMessage("Emploi du temps valide et enregistre (statut VALIDEE).");
  };

  const handleExportPDF = async () => {
    if (!catalogue || !sessionId || !sectionId) {
      alert("Veuillez sélectionner une session et une section.");
      return;
    }

    const session = catalogue.sessions.find((s) => s.session_id === sessionId);
    const section = catalogue.sections.find((s) => s.section_id === sectionId);

    // Transform items to PDF format
    const exams = items.map((item) => ({
      matiere: item.matiere,
      date: item.date_examen,
      heure_debut: item.heure_debut,
      heure_fin: item.heure_fin,
      salles: item.salles.map((s) => s.salle_id || "—"),
      groupes: item.salles.map((s) => `G${s.groupe_id}`),
      duree: item.duree,
    }));

    await exportPDF({
      session: session
        ? {
            type_session: session.label,
            annee_universitaire: null,
          }
        : undefined,
      section: section
        ? {
            label: section.label,
            effectif: section.effectif,
          }
        : undefined,
      semestre,
      exams,
    });
  };

  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Planification des examens</h2>
          <p className="text-sm text-slate-600">
            Generez l&apos;emploi du temps, ajustez par glisser-deposer, puis validez.
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            isLoading={exporting}
            disabled={!sessionId || items.length === 0}
            onClick={() => void handleExportPDF()}
          >
            Exporter en PDF
          </Button>
          <Button
            variant="secondary"
            isLoading={loading}
            disabled={!sessionId || draftCount === 0}
            onClick={() => void handleValidate()}
          >
            Valider ({draftCount})
          </Button>
        </div>
      </header>

      {error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      ) : null}

      {exportError ? (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          Erreur d&apos;export PDF: {exportError}
        </div>
      ) : null}

      {successMessage ? (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {successMessage}
        </div>
      ) : null}

      {warnings.length > 0 ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <ul className="list-disc pl-5 text-xs">
            {warnings.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <PlanificationForm
        catalogue={catalogue}
        loading={loading}
        semestre={semestre}
        onSemestreChange={setSemestre}
        onGenerate={generate}
      />

      {generationResult && generationResult.nb_conflits > 0 ? (
        <UnscheduledExamsList
          conflictMessages={generationResult.conflits}
          scheduledExams={items}
          onAddManually={(matiere) => {
            alert(`Pour ajouter "${matiere}", cliquez sur un créneau vide dans le calendrier ci-dessous.`);
          }}
        />
      ) : null}

      {generationResult ? (
        <div className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
          {generationResult.nb_crees} examen(s) genere(s)
          {generationResult.nb_conflits > 0
            ? ` · ${generationResult.nb_conflits} conflit(s) detecte(s)`
            : ""}
          {generationResult.conflits.length > 0 ? (
            <ul className="mt-2 list-disc pl-5 text-xs">
              {generationResult.conflits.map((c, index) => (
                <li key={`${conflictMessage(c)}-${index}`}>{conflictMessage(c)}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      {items.length > 0 ? (
        <>
          <ExamCalendarGrid
            items={items}
            salles={catalogue?.salles ?? []}
            conflictIds={conflictIds}
            sessionStart={catalogue?.sessions.find((s) => s.session_id === sessionId)?.date_debut}
            sessionEnd={catalogue?.sessions.find((s) => s.session_id === sessionId)?.date_fin}
            onUpdated={() => refreshSchedule(sessionId, sectionId)}
            onWarnings={(w) => setWarnings(w)}
            onAddExam={handleClickSlot}
          />
          
          <AddExamModal
            open={addModalOpen}
            date={selectedSlot?.date ?? ""}
            hour={selectedSlot?.hour ?? 8}
            availableMatieres={unscheduledMatieres}
            salles={catalogue?.salles ?? []}
            studentCount={catalogue?.sections.find((s) => s.section_id === sectionId)?.effectif ?? 0}
            onClose={() => setAddModalOpen(false)}
            onCreate={handleCreateExam}
          />
        </>
      ) : (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">
          Aucun emploi du temps. Remplissez le formulaire et cliquez sur &quot;Generer automatiquement&quot;.
        </div>
      )}
    </section>
  );
}
