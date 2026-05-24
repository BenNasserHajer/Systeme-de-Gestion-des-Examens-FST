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
  formatDayHeader,
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
      <CalendarToolbar saving={saving} count={items.length} />
      {dropError ? (
        <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
          {dropError}
        </div>
      ) : null}

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="min-w-[900px]">
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
      />
    </div>
  );
}

function CalendarToolbar({ saving, count }: { saving: boolean; count: number }) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h3 className="text-base font-semibold text-slate-900">Emploi du temps d&apos;examen</h3>
        <p className="text-sm text-slate-500">
          {count} examen{count !== 1 ? "s" : ""} · Glissez-deposez pour ajuster
        </p>
      </div>
      {saving ? <span className="text-xs text-blue-600">Enregistrement...</span> : null}
    </div>
  );
}

function CalendarHeader({ weekDays }: { weekDays: string[] }) {
  return (
    <GridDiv
      className="grid border-b border-slate-200 bg-slate-50"
      style={{ gridTemplateColumns: `80px repeat(${weekDays.length}, 1fr)` }}
    >
      <div className="px-3 py-3 text-xs font-semibold text-slate-600">Time</div>
      {weekDays.map((day) => (
        <div key={day} className="px-2 py-3 text-center text-xs font-semibold text-slate-700">
          {formatDayHeader(day)}
        </div>
      ))}
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
    <div>
      {hours.map((hour) => (
        <GridDiv
          key={hour}
          className="border-b border-r border-slate-100 px-2 text-right text-[11px] text-slate-500"
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
    <div className="relative border-r border-slate-100" style={{ height: totalHeight }}>
      {hours.map((hour) => (
        <div
          key={hour}
          className={`border-b border-slate-100 transition-colors ${
            draggingId !== null 
              ? "bg-blue-50/40 cursor-copy" 
              : "hover:bg-slate-50 cursor-pointer"
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
