"use client";

import type { Planification } from "@/lib/types/planification";
import { getPrimarySalle, getStudentCount } from "@/lib/utils/planificationHelpers";

type ExamEventCardProps = {
  planif: Planification;
  topPx: number;
  heightPx: number;
  hasConflict?: boolean;
  onDragStart: (planifId: number) => void;
  onClick: (planif: Planification) => void;
};

const STATUS_STYLES: Record<
  Planification["statut"],
  { card: string; bar: string; title: string; meta: string }
> = {
  BROUILLON: {
    card: "border-blue-200 bg-blue-50 hover:bg-blue-100",
    bar: "bg-blue-700",
    title: "text-blue-900",
    meta: "text-blue-800",
  },
  VALIDEE: {
    card: "border-emerald-200 bg-emerald-50 hover:bg-emerald-100",
    bar: "bg-emerald-700",
    title: "text-emerald-900",
    meta: "text-emerald-800",
  },
  PUBLIEE: {
    card: "border-slate-200 bg-slate-100 hover:bg-slate-200",
    bar: "bg-slate-600",
    title: "text-slate-900",
    meta: "text-slate-700",
  },
};

export function ExamEventCard({
  planif,
  topPx,
  heightPx,
  hasConflict = false,
  onDragStart,
  onClick,
}: ExamEventCardProps) {
  const styles = hasConflict
    ? {
        card: "border-red-300 bg-red-50 hover:bg-red-100",
        bar: "bg-red-600",
        title: "text-red-900",
        meta: "text-red-800",
      }
    : STATUS_STYLES[planif.statut];

  const draggable = planif.statut === "BROUILLON";

  return (
    <button
      type="button"
      draggable={draggable}
      onDragStart={() => draggable && onDragStart(planif.id)}
      onClick={() => onClick(planif)}
      className={`absolute left-1 right-1 overflow-hidden rounded-md border text-left shadow-sm transition ${draggable ? "cursor-grab active:cursor-grabbing" : "cursor-pointer"} ${styles.card}`}
      style={{ top: topPx, height: Math.max(heightPx - 4, 48) }}
      title={
        draggable
          ? "Glisser pour deplacer · Cliquer pour modifier la salle"
          : "Cliquer pour voir les details"
      }
    >
      <span className={`absolute bottom-0 left-0 top-0 w-1 rounded-l-md ${styles.bar}`} aria-hidden />
      <div className="relative z-10 px-2 py-1.5">
        <p className={`truncate text-xs font-bold ${styles.title}`}>{planif.matiere}</p>
        <p className={`mt-0.5 flex items-center gap-1 truncate text-[10px] ${styles.meta}`}>
          <DoorIcon />
          {getPrimarySalle(planif)}
        </p>
        <p className={`mt-0.5 flex items-center gap-1 text-[10px] ${styles.meta}`}>
          <PeopleIcon />
          {getStudentCount(planif)} Students
        </p>
      </div>
    </button>
  );
}

function DoorIcon() {
  return (
    <svg viewBox="0 0 16 16" className="h-3 w-3 shrink-0" fill="currentColor" aria-hidden>
      <path d="M3 2h7v12H3V2zm8 0h1v12h-1V2zM6 8h1v1H6V8z" />
    </svg>
  );
}

function PeopleIcon() {
  return (
    <svg viewBox="0 0 16 16" className="h-3 w-3 shrink-0" fill="currentColor" aria-hidden>
      <path d="M6 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm4.5 1a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM1 13c0-2.2 2.2-4 5-4s5 1.8 5 4v1H1v-1z" />
    </svg>
  );
}
