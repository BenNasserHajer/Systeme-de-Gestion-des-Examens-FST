"use client";

import { useEffect, useMemo, useState } from "react";

import type { Catalogue } from "@/lib/api/referentiel";
import type { GenerationParams } from "@/lib/types/planification";
import { filterMatieresForSemestre } from "@/lib/utils/semestre";
import { Button } from "@/components/ui/Button";

type PlanificationFormProps = {
  catalogue: Catalogue | null;
  loading: boolean;
  semestre: GenerationParams["semestre"];
  sessionId: number | null;
  sectionId: number | null;
  onSemestreChange: (semestre: GenerationParams["semestre"]) => void;
  onSessionChange: (sessionId: number) => void;
  onSectionChange: (sectionId: number) => void;
  onGenerate: (params: GenerationParams) => Promise<void>;
};

export function PlanificationForm({
  catalogue,
  loading,
  semestre,
  sessionId,
  sectionId,
  onSemestreChange,
  onSessionChange,
  onSectionChange,
  onGenerate,
}: PlanificationFormProps) {
  const [typeEpreuve, setTypeEpreuve] = useState<GenerationParams["type_epreuve"]>("EXAMEN_FINAL");

  useEffect(() => {
    if (!catalogue) {
      return;
    }
    // Initialize with first values if not set
    if (!sectionId && catalogue.sections[0]) {
      onSectionChange(catalogue.sections[0].section_id);
    }
    if (!sessionId && catalogue.sessions[0]) {
      onSessionChange(catalogue.sessions[0].session_id);
    }
    setTypeEpreuve(catalogue.types_epreuve[0]?.value ?? "EXAMEN_FINAL");
  }, [catalogue, sectionId, sessionId, onSectionChange, onSessionChange]);



  const selectedSection = useMemo(
    () => catalogue?.sections.find((s) => s.section_id === sectionId) ?? null,
    [catalogue, sectionId],
  );

  const matiereCount = selectedSection
    ? filterMatieresForSemestre(
        catalogue?.matieres_by_section[selectedSection.label] ?? [],
        semestre,
      ).length
    : 0;

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!sectionId || !sessionId) {
      return;
    }
    await onGenerate({
      section_id: sectionId,
      session_id: sessionId,
      type_epreuve: typeEpreuve,
      semestre,
    });
  };

  if (!catalogue) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
        Chargement du catalogue depuis la base...
      </div>
    );
  }

  return (
    <form
      onSubmit={(e) => void handleSubmit(e)}
      className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <h3 className="text-base font-semibold text-slate-900">Parametres de generation</h3>
      <p className="mt-1 text-sm text-slate-500">
        Selectionnez la section, la session, le type d&apos;epreuve et le semestre.
      </p>
      <p className="mt-1 text-xs text-slate-400">
        Source: {catalogue.source === "database" ? "Base de donnees" : "Catalogue statique"}
        {catalogue.message ? ` · ${catalogue.message}` : ""}
      </p>

      <div className="mt-4 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Field label="Section">
          <select
            value={sectionId ?? ""}
            onChange={(e) => onSectionChange(Number(e.target.value))}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            {catalogue.sections.map((section) => (
              <option key={section.section_id} value={section.section_id}>
                {section.label}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Session">
          <select
            value={sessionId ?? ""}
            onChange={(e) => onSessionChange(Number(e.target.value))}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            {catalogue.sessions.map((session) => (
              <option key={session.session_id} value={session.session_id}>
                {session.label} ({session.date_debut} au {session.date_fin})
              </option>
            ))}
          </select>
        </Field>

        <Field label="Type d'epreuve">
          <select
            value={typeEpreuve}
            onChange={(e) => setTypeEpreuve(e.target.value as GenerationParams["type_epreuve"])}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            {catalogue.types_epreuve.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Semestre">
          <select
            value={semestre}
            onChange={(e) => onSemestreChange(e.target.value as GenerationParams["semestre"])}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            {catalogue.semestres.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </Field>
      </div>

      <div className="mt-5 flex items-center gap-3">
        <Button type="submit" isLoading={loading}>
          Generer automatiquement
        </Button>
        {selectedSection ? (
          <span className="text-xs text-slate-500">
            {selectedSection.effectif} etudiants · {matiereCount} matieres
          </span>
        ) : null}
      </div>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block text-sm font-medium text-slate-700">
      {label}
      <div className="mt-1">{children}</div>
    </label>
  );
}

function motionDiv({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <div className={className}>{children}</div>;
}
