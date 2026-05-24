"use client";

import type { Planification } from "@/lib/types/planification";

type ConflictMessage = string | { message: string };

type UnscheduledExamsListProps = {
  conflictMessages: ConflictMessage[];
  scheduledExams: Planification[];
  onAddManually: (matiere: string) => void;
};

function getMessageText(msg: ConflictMessage): string {
  return typeof msg === "string" ? msg : msg.message;
}

export function UnscheduledExamsList({
  conflictMessages,
  scheduledExams,
  onAddManually,
}: UnscheduledExamsListProps) {
  // Extract matiere names from conflict messages
  const unscheduledMatieres = conflictMessages
    .map((msg) => {
      const text = getMessageText(msg);
      // Extract matiere name from message like "[C1/C7/C8] Section-2 / Machine Learning - ..."
      const match = text.match(/Section-\d+ \/ (.+?) -/);
      return match ? match[1] : null;
    })
    .filter((m): m is string => m !== null)
    .filter((m) => !scheduledExams.some((exam) => exam.matiere === m));

  if (unscheduledMatieres.length === 0) {
    return null;
  }

  return (
    <div className="rounded-xl border border-orange-200 bg-orange-50 p-4">
      <div className="flex items-start gap-3">
        <div className="rounded-full bg-orange-100 p-2">
          <WarningIcon />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-orange-900">
            Examens non planifiés ({unscheduledMatieres.length})
          </h3>
          <p className="mt-1 text-xs text-orange-700">
            Ces examens n&apos;ont pas pu être planifiés automatiquement. Cliquez sur un créneau
            vide dans le calendrier pour les ajouter manuellement.
          </p>
          <div className="mt-3 space-y-2">
            {unscheduledMatieres.map((matiere, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between rounded-md border border-orange-200 bg-white px-3 py-2"
              >
                <span className="text-sm font-medium text-slate-900">{matiere}</span>
                <button
                  type="button"
                  onClick={() => onAddManually(matiere)}
                  className="rounded-md bg-orange-600 px-3 py-1 text-xs font-medium text-white hover:bg-orange-700"
                >
                  Ajouter manuellement
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function WarningIcon() {
  return (
    <svg viewBox="0 0 20 20" className="h-5 w-5 text-orange-600" fill="currentColor">
      <path
        fillRule="evenodd"
        d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z"
        clipRule="evenodd"
      />
    </svg>
  );
}
