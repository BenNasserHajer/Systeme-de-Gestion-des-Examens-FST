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
  { card: string; bar: string; title: string; meta: string; editBtn: string }
> = {
  BROUILLON: {
    card: "border-blue-200/80 bg-gradient-to-br from-blue-50 via-white to-blue-50/60 hover:from-blue-100 hover:via-white hover:to-blue-50",
    bar: "bg-blue-600",
    title: "text-blue-950",
    meta: "text-blue-900/80",
    editBtn: "bg-blue-600 hover:bg-blue-700 text-white",
  },
  VALIDEE: {
    card: "border-emerald-200/80 bg-gradient-to-br from-emerald-50 via-white to-emerald-50/60 hover:from-emerald-100 hover:via-white hover:to-emerald-50",
    bar: "bg-emerald-600",
    title: "text-emerald-950",
    meta: "text-emerald-900/80",
    editBtn: "bg-emerald-600 hover:bg-emerald-700 text-white",
  },
  PUBLIEE: {
    card: "border-slate-200/80 bg-gradient-to-br from-slate-100 via-white to-slate-100/70 hover:from-slate-200 hover:via-white hover:to-slate-100",
    bar: "bg-slate-600",
    title: "text-slate-900",
    meta: "text-slate-700",
    editBtn: "bg-slate-600 hover:bg-slate-700 text-white",
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
        card: "border-red-300/80 bg-gradient-to-br from-red-50 via-white to-red-50/70 hover:from-red-100 hover:via-white hover:to-red-50",
        bar: "bg-red-600",
        title: "text-red-950",
        meta: "text-red-900/80",
        editBtn: "bg-red-600 hover:bg-red-700 text-white",
      }
    : STATUS_STYLES[planif.statut];

  const draggable = planif.statut === "BROUILLON";
  const isCompact = heightPx < 80;

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClick(planif);
  };

  return (
    <div
      draggable={draggable}
      onDragStart={() => draggable && onDragStart(planif.id)}
      className={`group absolute left-1 right-1 overflow-hidden rounded-lg border text-left shadow-sm ring-1 ring-white/70 transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-md ${draggable ? "cursor-grab active:cursor-grabbing" : ""} ${styles.card}`}
      style={{ top: topPx, height: Math.max(heightPx - 4, 48) }}
      title={
        draggable
          ? "Glisser pour deplacer"
          : "Examen validé ou publié"
      }
    >
      <span className={`absolute bottom-0 left-0 top-0 w-1 rounded-l-md ${styles.bar}`} aria-hidden />
      
      <div className="relative z-10 flex h-full items-start justify-between gap-1 px-2 py-1.5">
        <div className="min-w-0 flex-1">
          <p className={`truncate text-xs font-bold ${styles.title}`}>{planif.matiere}</p>
          <p className={`mt-0.5 flex items-center gap-1 truncate text-[10px] ${styles.meta}`}>
            <DoorIcon />
            {getPrimarySalle(planif)}
          </p>
          {!isCompact && (
            <p className={`mt-0.5 flex items-center gap-1 text-[10px] ${styles.meta}`}>
              <PeopleIcon />
              {getStudentCount(planif)} étudiants
            </p>
          )}
        </div>

        {/* Bouton de modification */}
        <button
          type="button"
          onClick={handleEditClick}
          className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium shadow-sm transition opacity-0 group-hover:opacity-100 ${styles.editBtn}`}
          title="Modifier la planification"
        >
          <EditIcon />
        </button>
      </div>
    </div>
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

function EditIcon() {
  return (
    <svg viewBox="0 0 16 16" className="h-3 w-3" fill="currentColor" aria-hidden>
      <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 2.793L10.5 3 4 9.5l-.955 2.386a.5.5 0 0 0 .569.569L6 11.5l6.5-6.5z" />
    </svg>
  );
}
