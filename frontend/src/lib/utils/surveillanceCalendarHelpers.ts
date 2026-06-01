import type { PlanificationResult } from "@/lib/api/surveillance";

export function normalizeExamDate(date?: string | null): string | null {
  if (!date) return null;
  const trimmed = date.trim();
  if (/^\d{4}-\d{2}-\d{2}/.test(trimmed)) {
    return trimmed.slice(0, 10);
  }
  const parsed = new Date(trimmed);
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toISOString().slice(0, 10);
}

export function getWeekDaysFromAffectationResults(
  items: PlanificationResult[],
  sessionStart?: string,
  sessionEnd?: string,
): string[] {
  if (sessionStart && sessionEnd) {
    const start = new Date(`${sessionStart}T12:00:00`);
    const end = new Date(`${sessionEnd}T12:00:00`);
    if (!Number.isNaN(start.getTime()) && !Number.isNaN(end.getTime()) && start <= end) {
      const days: string[] = [];
      const totalDays = Math.floor((end.getTime() - start.getTime()) / 86400000) + 1;
      const maxDays = Math.min(totalDays, 31);
      const current = new Date(start);
      while (current <= end && days.length < maxDays) {
        days.push(current.toISOString().slice(0, 10));
        current.setDate(current.getDate() + 1);
      }
      return days;
    }
  }

  const dates = [
    ...new Set(
      items
        .map((item) => normalizeExamDate(item.creneau?.date))
        .filter((d): d is string => Boolean(d)),
    ),
  ].sort();

  if (dates.length === 0) {
    const today = new Date();
    const monday = new Date(today);
    const day = monday.getDay();
    const diff = day === 0 ? -6 : 1 - day;
    monday.setDate(monday.getDate() + diff);
    return Array.from({ length: 5 }, (_, i) => {
      const d = new Date(monday);
      d.setDate(monday.getDate() + i);
      return d.toISOString().slice(0, 10);
    });
  }

  if (dates.length >= 5) {
    return dates.slice(0, 14);
  }

  const first = new Date(`${dates[0]}T12:00:00`);
  const monday = new Date(first);
  const day = monday.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  monday.setDate(monday.getDate() + diff);

  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return d.toISOString().slice(0, 10);
  });
}

export function getAffectationStatusStyles(statut: string): {
  card: string;
  badge: string;
  label: string;
} {
  if (statut === "AFFECTEE") {
    return {
      card: "border-emerald-300/80 bg-gradient-to-br from-emerald-50 to-white shadow-[0_4px_14px_rgba(16,185,129,0.12)]",
      badge: "bg-emerald-100 text-emerald-800",
      label: "Complet",
    };
  }
  if (statut === "CONFLIT_PARTIEL") {
    return {
      card: "border-amber-300/80 bg-gradient-to-br from-amber-50 to-white shadow-[0_4px_14px_rgba(245,158,11,0.14)]",
      badge: "bg-amber-100 text-amber-800",
      label: "Partiel",
    };
  }
  return {
    card: "border-red-300/80 bg-gradient-to-br from-red-50 to-white shadow-[0_4px_14px_rgba(239,68,68,0.12)]",
    badge: "bg-red-100 text-red-800",
    label: "Conflit",
  };
}
