"use client";

import { useMemo } from "react";
import {
  CALENDAR_END_HOUR,
  CALENDAR_START_HOUR,
  formatDayHeader,
  formatTimeAmPm,
  HOUR_HEIGHT_PX,
  parseTimeToMinutes,
} from "@/lib/utils/planificationHelpers";

type ConvocationAssignment = {
  matiere: string;
  date: string;
  heure_debut?: string;
  heure_fin?: string;
  salle?: string;
  groupe?: string;
  charge?: number;
};

type TeacherCalendarGridProps = {
  assignments: ConvocationAssignment[];
};

export function TeacherCalendarGrid({ assignments }: TeacherCalendarGridProps) {
  // Extraire les jours uniques triés
  const weekDays = useMemo(() => {
    const days = new Set<string>();
    assignments.forEach((a) => {
      if (a.date && a.date !== "—") days.add(a.date);
    });
    return Array.from(days).sort();
  }, [assignments]);

  const hours = useMemo(
    () => Array.from({ length: CALENDAR_END_HOUR - CALENDAR_START_HOUR }, (_, i) => CALENDAR_START_HOUR + i),
    [],
  );
  const totalHeight = hours.length * HOUR_HEIGHT_PX;

  if (assignments.length === 0) {
    return (
      <div className="rounded-md border border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-500">
        Aucune surveillance assignée.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="min-w-[800px]">
        <CalendarHeader weekDays={weekDays} />
        <div className="grid" style={{ gridTemplateColumns: `80px repeat(${weekDays.length}, 1fr)` }}>
          <TimeColumn hours={hours} />
          {weekDays.map((day) => (
            <DayColumn
              key={day}
              date={day}
              hours={hours}
              totalHeight={totalHeight}
              items={assignments.filter((a) => a.date === day)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function CalendarHeader({ weekDays }: { weekDays: string[] }) {
  return (
    <div
      className="grid border-b border-slate-200 bg-slate-50"
      style={{ gridTemplateColumns: `80px repeat(${weekDays.length}, 1fr)` }}
    >
      <div className="px-3 py-3 text-xs font-semibold text-slate-600">Heure</div>
      {weekDays.map((day) => (
        <div key={day} className="px-2 py-3 text-center text-xs font-semibold text-slate-700">
          {formatDayHeader(day)}
        </div>
      ))}
    </div>
  );
}

function TimeColumn({ hours }: { hours: number[] }) {
  return (
    <div>
      {hours.map((hour) => (
        <div
          key={hour}
          className="border-b border-r border-slate-100 px-2 text-right text-[11px] text-slate-500"
          style={{ height: HOUR_HEIGHT_PX, lineHeight: `${HOUR_HEIGHT_PX}px` }}
        >
          {formatTimeAmPm(`${String(hour).padStart(2, "0")}:00:00`)}
        </div>
      ))}
    </div>
  );
}

function DayColumn({
  hours,
  totalHeight,
  items,
}: {
  date: string;
  hours: number[];
  totalHeight: number;
  items: ConvocationAssignment[];
}) {
  return (
    <div className="relative border-r border-slate-100" style={{ height: totalHeight }}>
      {hours.map((hour) => (
        <div
          key={hour}
          className="border-b border-slate-100 bg-white"
          style={{ height: HOUR_HEIGHT_PX }}
        />
      ))}

      {items.map((assignment, idx) => {
        if (!assignment.heure_debut || !assignment.heure_fin) return null;

        const startMinutes = parseTimeToMinutes(assignment.heure_debut);
        const endMinutes = parseTimeToMinutes(assignment.heure_fin);
        const durationMinutes = endMinutes - startMinutes;

        const topPx = ((startMinutes - CALENDAR_START_HOUR * 60) / 60) * HOUR_HEIGHT_PX;
        const heightPx = (durationMinutes / 60) * HOUR_HEIGHT_PX;

        return (
          <div
            key={idx}
            className="absolute left-1 right-1 overflow-hidden rounded-md border border-blue-200 bg-blue-50 p-2 shadow-sm transition-shadow hover:shadow-md"
            style={{
              top: topPx,
              height: heightPx,
              zIndex: 10,
            }}
          >
            <div className="flex h-full flex-col">
              <span className="truncate text-xs font-bold text-blue-900">
                {assignment.matiere}
              </span>
              <span className="mt-0.5 text-[10px] font-medium text-blue-700">
                {assignment.heure_debut} - {assignment.heure_fin}
              </span>
              <div className="mt-auto flex flex-wrap gap-1">
                {assignment.salle && assignment.salle !== "—" && (
                  <span className="rounded bg-blue-100 px-1 py-0.5 text-[9px] font-semibold text-blue-800">
                    Salle {assignment.salle}
                  </span>
                )}
                {assignment.groupe && assignment.groupe !== "—" && (
                  <span className="rounded bg-blue-100 px-1 py-0.5 text-[9px] font-semibold text-blue-800">
                    {assignment.groupe}
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
