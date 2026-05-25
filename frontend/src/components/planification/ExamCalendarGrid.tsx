"use client";

import { useMemo, useState } from "react";

import type { Planification } from "@/lib/types/planification";
import type { CatalogueSalle } from "@/lib/api/referentiel";

import { ExamEventCard } from "@/components/planification/ExamEventCard";
import { EditExamModal } from "@/components/planification/EditExamModal";
import {
  addMinutesToTime,
  CALENDAR_END_HOUR,
  CALENDAR_START_HOUR,
  formatDayHeaderParts,
  formatDayRange,
  formatTimeAmPm,
  getWeekDaysFromPlanifs,
  HOUR_HEIGHT_PX,
  parseTimeToMinutes,
} from "@/lib/utils/planificationHelpers";
import { changerSallePlanification, deplacerPlanification } from "@/lib/api/planification";
import { isApiError } from "@/lib/api/errors";

type ExamCalendarGridProps = {
  items: Planification[];
  salles: CatalogueSalle[];
  conflictIds?: Set<number>;
  sessionStart?: string;
  sessionEnd?: string;
  onUpdated: () => Promise<void>;
  onWarnings?: (warnings: string[]) => void;
  onAddExam?: (date: string, hour: number) => void;
};

export function ExamCalendarGrid({
  items,
  salles,
  conflictIds,
  sessionStart,
  sessionEnd,
  onUpdated,
  onWarnings,
  onAddExam,
}: ExamCalendarGridProps) {
  const [draggingId, setDraggingId] = useState<number | null>(null);
  const [editing, setEditing] = useState<Planification | null>(null);
  const [saving, setSaving] = useState(false);
  const [dropError, setDropError] = useState<string | null>(null);

  const weekDays = useMemo(
    () => getWeekDaysFromPlanifs(items, sessionStart, sessionEnd),
    [items, sessionStart, sessionEnd]
  );
  const rangeLabel = useMemo(() => {
    if (weekDays.length === 0) {
      return "";
    }
    return formatDayRange(weekDays[0], weekDays[weekDays.length - 1]);
  }, [weekDays]);
  const hours = useMemo(
    () => Array.from({ length: CALENDAR_END_HOUR - CALENDAR_START_HOUR }, (_, i) => CALENDAR_START_HOUR + i),
    [],
  );
  const totalHeight = hours.length * HOUR_HEIGHT_PX;

  const handleDrop = async (date: string, hour: number) => {
    if (draggingId === null) {
      return;
    }
    const planif = items.find((p) => p.id === draggingId);
    if (!planif || planif.statut !== "BROUILLON") {
      setDraggingId(null);
      return;
    }

    const heureDebut = `${String(hour).padStart(2, "0")}:00:00`;
    const heureFin = addMinutesToTime(heureDebut, planif.duree);

    setSaving(true);
    setDropError(null);
    try {
      const { warnings } = await deplacerPlanification(planif.id, {
        nouvelle_date: date,
        nouvelle_heure_debut: heureDebut,
        nouvelle_heure_fin: heureFin,
      });
      onWarnings?.(warnings);
      await onUpdated();
    } catch (err) {
      const message = isApiError(err)
        ? err.message
        : err instanceof Error
          ? err.message
          : "Impossible de deplacer l'examen";
      setDropError(message);
      onWarnings?.([message]);
    } finally {
      setSaving(false);
      setDraggingId(null);
    }
  };

  const handleSaveSalle = async (planifId: number, salleId: string) => {
    setSaving(true);
    try {
      const { warnings } = await changerSallePlanification(planifId, {
        nouvelle_salle_id: salleId,
      });
      onWarnings?.(warnings);
      await onUpdated();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-3">
      <CalendarToolbar saving={saving} count={items.length} rangeLabel={rangeLabel} dayCount={weekDays.length} />
      {dropError ? (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {dropError}
        </div>
      ) : null}

      <div className="overflow-x-auto rounded-2xl border border-slate-200/70 bg-[linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] shadow-[0_12px_40px_rgba(15,23,42,0.08)]">
        <div className="min-w-[900px] bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.12),_transparent_50%)]">
          <CalendarHeader weekDays={weekDays} />
          <CalendarBody
            weekDays={weekDays}
            hours={hours}
            totalHeight={totalHeight}
            items={items}
            draggingId={draggingId}
            conflictIds={conflictIds}
            onDragStart={setDraggingId}
            onDrop={handleDrop}
            onEdit={setEditing}
            onClickEmpty={(date, hour) => onAddExam?.(date, hour)}
          />
        </div>
      </div>

      <EditExamModal
        open={editing !== null}
        planif={editing}
        salles={salles}
        onClose={() => setEditing(null)}
        onSave={handleSaveSalle}
        onUpdated={onUpdated}
      />
    </div>
  );
}

function CalendarToolbar({
  saving,
  count,
  rangeLabel,
  dayCount,
}: {
  saving: boolean;
  count: number;
  rangeLabel: string;
  dayCount: number;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200/70 bg-white/70 px-4 py-3 shadow-sm backdrop-blur">
      <div>
        <h3 className="text-base font-semibold text-slate-900">Emploi du temps d&apos;examen</h3>
        <p className="text-sm text-slate-500">
          {count} examen{count !== 1 ? "s" : ""} · Glissez-deposez pour ajuster
        </p>
      </div>
      <div className="flex items-center gap-2">
        {rangeLabel ? (
          <span className="rounded-full bg-slate-900/5 px-3 py-1 text-[11px] font-semibold text-slate-700">
            {rangeLabel}
          </span>
        ) : null}
        {dayCount > 0 ? (
          <span className="rounded-full bg-slate-900/5 px-3 py-1 text-[11px] font-semibold text-slate-600">
            {dayCount} jours
          </span>
        ) : null}
        {saving ? <span className="text-xs font-semibold text-blue-600">Enregistrement...</span> : null}
      </div>
    </div>
  );
}

function CalendarHeader({ weekDays }: { weekDays: string[] }) {
  return (
    <GridDiv
      className="sticky top-0 z-10 grid border-b border-slate-200/70 bg-gradient-to-b from-white via-slate-50 to-slate-50/60 shadow-[inset_0_-1px_0_rgba(148,163,184,0.3)] backdrop-blur"
      style={{ gridTemplateColumns: `80px repeat(${weekDays.length}, 1fr)` }}
    >
      <div className="sticky left-0 z-20 border-r border-slate-200/70 bg-white/90 px-3 py-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500 backdrop-blur">
        Time
      </div>
      {weekDays.map((day) => {
        const { weekday, monthDay } = formatDayHeaderParts(day);
        const weekend = isWeekendDate(day);
        return (
          <div
            key={day}
            className={`border-l border-slate-200/60 px-2 py-3 text-center ${
              weekend ? "text-amber-700" : "text-slate-700"
            }`}
          >
            <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">
              {weekday}
            </div>
            <div className="text-sm font-semibold">{monthDay}</div>
          </div>
        );
      })}
    </GridDiv>
  );
}

function CalendarBody({
  weekDays,
  hours,
  totalHeight,
  items,
  draggingId,
  conflictIds,
  onDragStart,
  onDrop,
  onEdit,
  onClickEmpty,
}: {
  weekDays: string[];
  hours: number[];
  totalHeight: number;
  items: Planification[];
  draggingId: number | null;
  conflictIds?: Set<number>;
  onDragStart: (id: number) => void;
  onDrop: (date: string, hour: number) => Promise<void>;
  onEdit: (planif: Planification) => void;
  onClickEmpty?: (date: string, hour: number) => void;
}) {
  return (
    <div className="grid" style={{ gridTemplateColumns: `80px repeat(${weekDays.length}, 1fr)` }}>
      <TimeColumn hours={hours} />
      {weekDays.map((day) => (
        <DayColumn
          key={day}
          date={day}
          hours={hours}
          totalHeight={totalHeight}
          items={items.filter((p) => p.date_examen === day)}
          draggingId={draggingId}
          conflictIds={conflictIds}
          onDragStart={onDragStart}
          onDrop={onDrop}
          onEdit={onEdit}
          onClickEmpty={onClickEmpty}
        />
      ))}
    </div>
  );
}

function TimeColumn({ hours }: { hours: number[] }) {
  return (
    <div className="sticky left-0 z-10 bg-gradient-to-b from-white via-slate-50 to-white">
      {hours.map((hour) => (
        <GridDiv
          key={hour}
          className="border-b border-r border-slate-200/70 px-2 text-right text-[11px] font-medium text-slate-500"
          style={{ height: HOUR_HEIGHT_PX, lineHeight: `${HOUR_HEIGHT_PX}px` }}
        >
          {formatTimeAmPm(`${String(hour).padStart(2, "0")}:00:00`)}
        </GridDiv>
      ))}
    </div>
  );
}

function DayColumn({
  date,
  hours,
  totalHeight,
  items,
  draggingId,
  conflictIds,
  onDragStart,
  onDrop,
  onEdit,
  onClickEmpty,
}: {
  date: string;
  hours: number[];
  totalHeight: number;
  items: Planification[];
  draggingId: number | null;
  conflictIds?: Set<number>;
  onDragStart: (id: number) => void;
  onDrop: (date: string, hour: number) => Promise<void>;
  onEdit: (planif: Planification) => void;
  onClickEmpty?: (date: string, hour: number) => void;
}) {
  return (
    <div
      className={`relative border-r border-slate-200/70 ${
        isWeekendDate(date) ? "bg-amber-50/40" : "bg-white/70"
      }`}
      style={{ height: totalHeight }}
    >
      {hours.map((hour) => (
        <div
          key={hour}
          className={`border-b border-slate-100 transition-colors ${
            draggingId !== null 
              ? "bg-sky-100/40 cursor-copy" 
              : "hover:bg-slate-50/80 cursor-pointer"
          }`}
          style={{ height: HOUR_HEIGHT_PX }}
          onDragOver={(e) => e.preventDefault()}
          onDrop={() => void onDrop(date, hour)}
          onClick={() => onClickEmpty?.(date, hour)}
          title="Cliquer pour ajouter un examen"
        />
      ))}

      {items.map((planif) => {
        const startMinutes = parseTimeToMinutes(planif.heure_debut);
        const topPx = ((startMinutes - CALENDAR_START_HOUR * 60) / 60) * HOUR_HEIGHT_PX;
        const heightPx = (planif.duree / 60) * HOUR_HEIGHT_PX;

        return (
          <ExamEventCard
            key={planif.id}
            planif={planif}
            topPx={topPx}
            heightPx={heightPx}
            hasConflict={conflictIds?.has(planif.id) ?? false}
            onDragStart={onDragStart}
            onClick={onEdit}
          />
        );
      })}
    </div>
  );
}

function GridDiv({
  className,
  children,
  style,
}: {
  className?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <div className={className} style={style}>
      {children}
    </div>
  );
}

function isWeekendDate(dateStr: string): boolean {
  const date = new Date(`${dateStr}T12:00:00`);
  const day = date.getDay();
  return day === 0 || day === 6;
}
