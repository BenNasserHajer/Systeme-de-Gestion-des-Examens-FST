"use client";

import { useMemo } from "react";

import type { PlanificationResult } from "@/lib/api/surveillance";
import {
  CALENDAR_END_HOUR,
  CALENDAR_START_HOUR,
  formatDayHeaderParts,
  formatDayRange,
  formatTimeAmPm,
  HOUR_HEIGHT_PX,
  parseTimeToMinutes,
} from "@/lib/utils/planificationHelpers";
import {
  getAffectationStatusStyles,
  getWeekDaysFromAffectationResults,
  normalizeExamDate,
} from "@/lib/utils/surveillanceCalendarHelpers";

type SurveillanceCalendarGridProps = {
  items: PlanificationResult[];
  sessionStart?: string;
  sessionEnd?: string;
  onSelectPlanif: (planif: PlanificationResult) => void;
};

export function SurveillanceCalendarGrid({
  items,
  sessionStart,
  sessionEnd,
  onSelectPlanif,
}: SurveillanceCalendarGridProps) {
  const weekDays = useMemo(
    () => getWeekDaysFromAffectationResults(items, sessionStart, sessionEnd),
    [items, sessionStart, sessionEnd],
  );

  const rangeLabel = useMemo(() => {
    if (weekDays.length === 0) return "";
    return formatDayRange(weekDays[0], weekDays[weekDays.length - 1]);
  }, [weekDays]);

  const hours = useMemo(
    () => Array.from({ length: CALENDAR_END_HOUR - CALENDAR_START_HOUR }, (_, i) => CALENDAR_START_HOUR + i),
    [],
  );
  const totalHeight = hours.length * HOUR_HEIGHT_PX;

  const stats = useMemo(() => {
    const complets = items.filter((i) => i.statut === "AFFECTEE").length;
    const partiels = items.filter((i) => i.statut === "CONFLIT_PARTIEL").length;
    const conflits = items.filter((i) => i.statut === "CONFLIT").length;
    return { complets, partiels, conflits };
  }, [items]);

  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center text-sm text-slate-600">
        Aucun examen à afficher dans le calendrier.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200/70 bg-white/80 px-4 py-3 shadow-sm backdrop-blur">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Calendrier des surveillances</h3>
          <p className="text-sm text-slate-500">
            {items.length} examen{items.length !== 1 ? "s" : ""} · Cliquez sur un créneau pour modifier les
            surveillants
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {rangeLabel ? (
            <span className="rounded-full bg-slate-900/5 px-3 py-1 text-[11px] font-semibold text-slate-700">
              {rangeLabel}
            </span>
          ) : null}
          <LegendDot color="emerald" label={`Complets (${stats.complets})`} />
          <LegendDot color="amber" label={`Partiels (${stats.partiels})`} />
          <LegendDot color="red" label={`Conflits (${stats.conflits})`} />
        </div>
      </div>

      <div className="overflow-x-auto rounded-2xl border border-slate-200/70 bg-[linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)] shadow-[0_12px_40px_rgba(15,23,42,0.08)]">
        <div className="min-w-[900px] bg-[radial-gradient(circle_at_top_left,_rgba(99,102,241,0.1),_transparent_50%)]">
          <div
            className="sticky top-0 z-10 grid border-b border-slate-200/70 bg-gradient-to-b from-white via-slate-50 to-slate-50/60"
            style={{ gridTemplateColumns: `80px repeat(${weekDays.length}, 1fr)` }}
          >
            <div className="px-3 py-3 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">
              Heure
            </div>
            {weekDays.map((day) => {
              const { weekday, monthDay } = formatDayHeaderParts(day);
              const weekend = isWeekend(day);
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
          </div>

          <div className="grid" style={{ gridTemplateColumns: `80px repeat(${weekDays.length}, 1fr)` }}>
            <div className="sticky left-0 z-10 bg-white/90">
              {hours.map((hour) => (
                <div
                  key={hour}
                  className="border-b border-r border-slate-200/70 px-2 text-right text-[11px] font-medium text-slate-500"
                  style={{ height: HOUR_HEIGHT_PX, lineHeight: `${HOUR_HEIGHT_PX}px` }}
                >
                  {formatTimeAmPm(`${String(hour).padStart(2, "0")}:00:00`)}
                </div>
              ))}
            </div>

            {weekDays.map((day) => (
              <DayColumn
                key={day}
                day={day}
                hours={hours}
                totalHeight={totalHeight}
                items={items.filter((p) => normalizeExamDate(p.creneau?.date) === day)}
                onSelectPlanif={onSelectPlanif}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function DayColumn({
  day,
  hours,
  totalHeight,
  items,
  onSelectPlanif,
}: {
  day: string;
  hours: number[];
  totalHeight: number;
  items: PlanificationResult[];
  onSelectPlanif: (planif: PlanificationResult) => void;
}) {
  return (
    <div
      className={`relative border-r border-slate-200/70 ${isWeekend(day) ? "bg-amber-50/30" : "bg-white/60"}`}
      style={{ height: totalHeight }}
    >
      {hours.map((hour) => (
        <div
          key={hour}
          className="border-b border-slate-100"
          style={{ height: HOUR_HEIGHT_PX }}
        />
      ))}

      {items.map((planif) => {
        const heureDebut = planif.creneau?.heure_debut;
        const heureFin = planif.creneau?.heure_fin;
        if (!heureDebut) return null;

        const startMinutes = parseTimeToMinutes(heureDebut);
        const endMinutes = heureFin ? parseTimeToMinutes(heureFin) : startMinutes + (planif.duree || 120);
        const durationMinutes = Math.max(endMinutes - startMinutes, 30);

        const topPx = ((startMinutes - CALENDAR_START_HOUR * 60) / 60) * HOUR_HEIGHT_PX;
        const heightPx = Math.max((durationMinutes / 60) * HOUR_HEIGHT_PX, 52);

        return (
          <SurveillanceEventCard
            key={planif.planification_id}
            planif={planif}
            topPx={topPx}
            heightPx={heightPx}
            onClick={() => onSelectPlanif(planif)}
          />
        );
      })}
    </div>
  );
}

function SurveillanceEventCard({
  planif,
  topPx,
  heightPx,
  onClick,
}: {
  planif: PlanificationResult;
  topPx: number;
  heightPx: number;
  onClick: () => void;
}) {
  const styles = getAffectationStatusStyles(planif.statut);
  const teachers = (planif.groupes ?? []).flatMap((g) => g.surveillants_affectes ?? []);
  const salles = [...new Set((planif.groupes ?? []).map((g) => g.salle?.code).filter(Boolean))];

  return (
    <button
      type="button"
      onClick={onClick}
      className={`absolute left-1 right-1 overflow-hidden rounded-lg border p-2 text-left transition hover:scale-[1.02] hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${styles.card}`}
      style={{ top: topPx, height: heightPx, zIndex: 10 }}
      title="Modifier les surveillants"
    >
      <div className="flex h-full flex-col gap-0.5">
        <div className="flex items-start justify-between gap-1">
          <span className="line-clamp-2 text-[11px] font-bold leading-tight text-slate-900">
            {planif.matiere?.intitule || "Examen"}
          </span>
          <span className={`shrink-0 rounded px-1 py-0.5 text-[9px] font-semibold ${styles.badge}`}>
            {styles.label}
          </span>
        </div>
        <span className="truncate text-[10px] text-slate-600">{planif.section?.nom || "Section"}</span>
        <span className="text-[10px] font-medium text-slate-700">
          {planif.surveillants_affectes}/{planif.surveillants_requis} surveillant(s)
        </span>
        {teachers.length > 0 ? (
          <div className="mt-auto space-y-0.5 overflow-hidden">
            {teachers.slice(0, 2).map((t) => (
              <p key={t.surveillance_id} className="truncate text-[9px] text-slate-600">
                {t.prenom} {t.nom}
              </p>
            ))}
            {teachers.length > 2 ? (
              <p className="text-[9px] text-slate-400">+{teachers.length - 2} autre(s)</p>
            ) : null}
          </div>
        ) : planif.manquants > 0 ? (
          <p className="mt-auto text-[9px] font-semibold text-red-600">
            {planif.manquants} manquant(s) — cliquer pour affecter
          </p>
        ) : null}
        {salles.length > 0 ? (
          <div className="flex flex-wrap gap-0.5 pt-0.5">
            {salles.slice(0, 2).map((code) => (
              <span
                key={code}
                className="rounded bg-white/80 px-1 py-0.5 text-[8px] font-medium text-slate-600 ring-1 ring-slate-200/80"
              >
                {code}
              </span>
            ))}
          </div>
        ) : null}
      </div>
    </button>
  );
}

function LegendDot({ color, label }: { color: "emerald" | "amber" | "red"; label: string }) {
  const bg =
    color === "emerald" ? "bg-emerald-500" : color === "amber" ? "bg-amber-500" : "bg-red-500";
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-900/5 px-2.5 py-1 text-[11px] font-medium text-slate-600">
      <span className={`h-2 w-2 rounded-full ${bg}`} />
      {label}
    </span>
  );
}

function isWeekend(dateStr: string): boolean {
  const date = new Date(`${dateStr}T12:00:00`);
  const day = date.getDay();
  return day === 0 || day === 6;
}
