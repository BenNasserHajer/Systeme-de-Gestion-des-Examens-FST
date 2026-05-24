import type { Planification, PlanifSalleAssign } from "@/lib/types/planification";

export function getPrimarySalle(planif: Planification): string {
  if (planif.salles.length === 0) {
    return "Non assignee";
  }
  return planif.salles.map((s) => s.salle_id).join(", ");
}

export function getStudentCount(planif: Planification): number {
  if (planif.salles.length > 0) {
    return planif.salles.reduce((sum, s) => sum + s.groupe_effectif, 0);
  }
  return planif.section_nb_etudiants;
}

export function parseTimeToMinutes(time: string): number {
  const [hours, minutes] = time.split(":").map(Number);
  return hours * 60 + (minutes || 0);
}

export function minutesToTimeString(totalMinutes: number): string {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:00`;
}

export function addMinutesToTime(time: string, minutes: number): string {
  return minutesToTimeString(parseTimeToMinutes(time) + minutes);
}

export function formatTimeAmPm(time: string): string {
  const [hoursRaw, minutesRaw] = time.split(":");
  let hours = Number(hoursRaw);
  const minutes = Number(minutesRaw || 0);
  const suffix = hours >= 12 ? "PM" : "AM";
  hours = hours % 12;
  if (hours === 0) {
    hours = 12;
  }
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")} ${suffix}`;
}

export function formatDayHeader(dateStr: string): string {
  const date = new Date(`${dateStr}T12:00:00`);
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "short",
    day: "numeric",
  }).format(date);
}

export function getWeekDaysFromPlanifs(
  items: Planification[],
  sessionStart?: string,
  sessionEnd?: string
): string[] {
  // If we have session dates, use them to determine the calendar range
  if (sessionStart && sessionEnd) {
    const start = new Date(`${sessionStart}T12:00:00`);
    const end = new Date(`${sessionEnd}T12:00:00`);
    const days: string[] = [];
    
    const current = new Date(start);
    while (current <= end && days.length < 10) { // Max 10 days to avoid huge calendars
      days.push(current.toISOString().slice(0, 10));
      current.setDate(current.getDate() + 1);
    }
    
    return days;
  }

  // Fallback to existing logic if no session dates
  if (items.length === 0) {
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

  const dates = [...new Set(items.map((p) => p.date_examen))].sort();
  if (dates.length >= 5) {
    return dates.slice(0, 10); // Show up to 10 days
  }

  const first = new Date(`${dates[0]}T12:00:00`);
  const monday = new Date(first);
  const day = monday.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  monday.setDate(monday.getDate() + diff);

  return Array.from({ length: 5 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return d.toISOString().slice(0, 10);
  });
}

export const CALENDAR_START_HOUR = 8;
export const CALENDAR_END_HOUR = 18;
export const HOUR_HEIGHT_PX = 64;

export function buildSallesUpdate(
  planif: Planification,
  newSalleId: string,
  availableSalles: { salle_id: string; capacite: number; batiment?: string }[],
): PlanifSalleAssign[] {
  const template = availableSalles.find((s) => s.salle_id === newSalleId);
  const capacity = template?.capacite ?? planif.section_nb_etudiants;
  const batiment = template?.batiment ?? null;

  if (planif.salles.length === 0) {
    return [
      {
        salle_id: newSalleId,
        salle_capacite: capacity,
        salle_batiment: batiment,
        groupe_id: 1,
        groupe_effectif: planif.section_nb_etudiants,
      },
    ];
  }

  return planif.salles.map((s) => ({
    salle_id: newSalleId,
    salle_capacite: capacity,
    salle_batiment: batiment,
    salle_departement_id: s.salle_departement_id,
    groupe_id: s.groupe_id,
    groupe_effectif: s.groupe_effectif,
  }));
}
