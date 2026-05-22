"use client";

import { useEffect, useState, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface PlanifSalle {
  salle_id: number;
  salle_capacite: number;
  salle_batiment?: string;
  groupe_id: number;
  groupe_effectif: number;
}

interface PlanificationOut {
  id: number;
  matiere?: string;
  section_id?: number;
  date_examen?: string;
  heure_debut?: string;
  heure_fin?: string;
  statut: string;
  type_epreuve?: string;
  duree?: number;
  coefficient?: number;
  salles?: PlanifSalle[];
}

interface SessionOut {
  id: number;
  type_session: string;
  annee_universitaire: string;
  date_debut: string;
  date_fin: string;
  statut: string;
}

interface GenerationResult {
  nb_crees: number;
  nb_conflits: number;
  conflits: string[];
}

interface GenerationParams {
  section_id: number;
  section_nom: string;
  annee: string;
}

// ─── Design tokens ─────────────────────────────────────────────────────────────

const T = {
  navy:    "#1B2B4B",
  navyMid: "#2C4470",
  blue:    "#3B6CB7",
  blueSoft:"#EBF1FA",
  gold:    "#B8913A",
  goldSoft:"#FBF5E7",
  green:   "#2D6A4F",
  greenSoft:"#EAF5EE",
  amber:   "#92400E",
  amberSoft:"#FEF5E4",
  red:     "#7F1D1D",
  redSoft: "#FEF2F2",
  slate:   "#4B5563",
  gray:    "#6B7280",
  grayLight:"#F3F4F6",
  border:  "#D1D5DB",
  borderStrong: "#9CA3AF",
  white:   "#FFFFFF",
  text:    "#111827",
  textMid: "#374151",
  radius:  "4px",
  radiusMd:"6px",
};

// ─── Utils ─────────────────────────────────────────────────────────────────────

function fmtHeure(h?: string) { return h ? h.slice(0, 5) : "—"; }

function fmtDate(d: string) {
  try {
    return new Date(d + "T00:00:00").toLocaleDateString("fr-FR", {
      weekday: "long", day: "numeric", month: "long",
    });
  } catch { return d; }
}

const SUBJECT_COLORS = [
  { border: "#1B2B4B", accent: "#2C4470", bg: "#EBF1FA", tag: "#3B6CB7" },
  { border: "#2D6A4F", accent: "#2D6A4F", bg: "#EAF5EE", tag: "#2D6A4F" },
  { border: "#7C3AED", accent: "#6D28D9", bg: "#F5F3FF", tag: "#7C3AED" },
  { border: "#B8913A", accent: "#92400E", bg: "#FBF5E7", tag: "#B8913A" },
  { border: "#0369A1", accent: "#0284C7", bg: "#E0F2FE", tag: "#0369A1" },
  { border: "#BE185D", accent: "#9D174D", bg: "#FDF2F8", tag: "#BE185D" },
  { border: "#065F46", accent: "#047857", bg: "#ECFDF5", tag: "#065F46" },
  { border: "#92400E", accent: "#B45309", bg: "#FFFBEB", tag: "#92400E" },
];

function colorFor(m: string) {
  let h = 0;
  for (let i = 0; i < m.length; i++) h = (h * 31 + m.charCodeAt(i)) % 997;
  return SUBJECT_COLORS[Math.abs(h) % SUBJECT_COLORS.length];
}

function statutConfig(s: string) {
  const u = s?.toUpperCase() ?? "";
  if (u.includes("PUBLI"))     return { bg: T.blueSoft,  text: T.blue,   border: "#BFDBFE", label: "Publiée" };
  if (u.includes("VALID"))     return { bg: T.greenSoft, text: T.green,  border: "#86EFAC", label: "Validée" };
  if (u.includes("BROUILLON")) return { bg: T.amberSoft, text: T.amber,  border: "#FDE68A", label: "Brouillon" };
  return { bg: T.grayLight, text: T.slate, border: T.border, label: s };
}

// ─── Hook ──────────────────────────────────────────────────────────────────────

function useSessions() {
  const [sessions, setSessions] = useState<SessionOut[]>([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetch(`${API_BASE}/api/sessions/`, {
        cache: "no-cache",
        headers: { "Cache-Control": "no-cache" },
      });
      setSessions(r.ok ? await r.json() : []);
    } catch (e: unknown) { setError(e instanceof Error ? e.message : "Erreur réseau"); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { load(); }, [load]);
  return { sessions, loading, error, refresh: load };
}

// ─── Composants de base ────────────────────────────────────────────────────────

function Divider() {
  return <div style={{ height: 1, background: T.border, margin: "0" }} />;
}

function Badge({ children, bg, text, border }: { children: React.ReactNode; bg: string; text: string; border: string }) {
  return (
    <span style={{
      fontSize: 10, fontWeight: 600, padding: "2px 8px",
      borderRadius: 3, background: bg, color: text,
      border: `1px solid ${border}`, letterSpacing: "0.06em",
      textTransform: "uppercase" as const, whiteSpace: "nowrap" as const,
    }}>{children}</span>
  );
}

function Btn({
  children, onClick, variant = "default", disabled, loading: busy, small,
}: {
  children: React.ReactNode; onClick: () => void;
  variant?: "default" | "primary" | "success" | "warning" | "danger";
  disabled?: boolean; loading?: boolean; small?: boolean;
}) {
  const map = {
    default: { bg: T.white,   border: T.border,    color: T.textMid },
    primary: { bg: T.navy,    border: T.navy,      color: T.white   },
    success: { bg: T.green,   border: T.green,     color: T.white   },
    warning: { bg: T.amber,   border: T.amber,     color: T.white   },
    danger:  { bg: T.red,     border: T.red,       color: T.white   },
  }[variant];

  return (
    <button
      onClick={onClick}
      disabled={disabled || busy}
      style={{
        padding: small ? "4px 10px" : "7px 14px",
        fontSize: small ? 11 : 12,
        fontWeight: 600,
        borderRadius: T.radius,
        border: `1px solid ${map.border}`,
        background: map.bg,
        color: map.color,
        cursor: disabled || busy ? "not-allowed" : "pointer",
        opacity: disabled || busy ? 0.5 : 1,
        letterSpacing: "0.02em",
        whiteSpace: "nowrap" as const,
        transition: "opacity 0.15s",
        fontFamily: "'Georgia', serif",
      }}
    >
      {busy ? "…" : children}
    </button>
  );
}

// ─── Carte matière ─────────────────────────────────────────────────────────────

function CarteMatiere({ p }: { p: PlanificationOut }) {
  const col = colorFor(p.matiere ?? "");
  const sc  = statutConfig(p.statut);

  return (
    <div style={{
      background: T.white,
      border: `1px solid ${T.border}`,
      borderLeft: `3px solid ${col.border}`,
      borderRadius: T.radiusMd,
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        padding: "10px 14px",
        background: col.bg,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 8,
        borderBottom: `1px solid ${T.border}`,
      }}>
        <span style={{
          fontSize: 12, fontWeight: 700, color: col.accent,
          fontFamily: "'Georgia', serif", letterSpacing: "0.01em",
        }}>
          {fmtHeure(p.heure_debut)} – {fmtHeure(p.heure_fin)}
        </span>
        <Badge bg={sc.bg} text={sc.text} border={sc.border}>{sc.label}</Badge>
      </div>

      {/* Corps */}
      <div style={{ padding: "12px 14px", display: "flex", flexDirection: "column", gap: 8 }}>
        <p style={{
          margin: 0, fontSize: 13, fontWeight: 700, color: T.text,
          fontFamily: "'Georgia', serif", lineHeight: 1.4,
        }}>{p.matiere ?? "—"}</p>

        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" as const }}>
          {p.duree && (
            <span style={{
              fontSize: 11, color: T.slate,
              background: T.grayLight, border: `1px solid ${T.border}`,
              borderRadius: T.radius, padding: "2px 7px", fontWeight: 500,
            }}>{p.duree} min</span>
          )}
          {p.coefficient && (
            <span style={{
              fontSize: 11, color: T.slate,
              background: T.grayLight, border: `1px solid ${T.border}`,
              borderRadius: T.radius, padding: "2px 7px", fontWeight: 500,
            }}>Coeff. {p.coefficient}</span>
          )}
          {p.type_epreuve && (
            <Badge bg={col.bg} text={col.tag} border={col.border}>
              {p.type_epreuve.replace("_", " ")}
            </Badge>
          )}
        </div>

        {p.salles && p.salles.length > 0 && (
          <>
            <Divider />
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {p.salles.map((s, i) => (
                <div key={i} style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  fontSize: 11, color: T.slate, gap: 6,
                }}>
                  <span style={{ fontWeight: 600, color: T.textMid }}>
                    Salle {s.salle_id}
                    {s.salle_batiment && (
                      <span style={{ fontWeight: 400, color: T.gray, marginLeft: 5 }}>
                        – {s.salle_batiment}
                      </span>
                    )}
                  </span>
                  <span style={{
                    fontWeight: 600, color: T.slate,
                    background: T.grayLight, border: `1px solid ${T.border}`,
                    borderRadius: T.radius, padding: "1px 6px", whiteSpace: "nowrap" as const,
                  }}>{s.groupe_effectif} étudiants</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function CelluleVide() {
  return (
    <div style={{
      minHeight: 60,
      border: `1px dashed ${T.border}`,
      borderRadius: T.radiusMd,
      display: "flex", alignItems: "center", justifyContent: "center",
      background: T.grayLight,
    }}>
      <span style={{ fontSize: 11, color: T.borderStrong, fontStyle: "italic" }}>—</span>
    </div>
  );
}

// ─── Emploi du temps ───────────────────────────────────────────────────────────

function EmploiDuTemps({ planifs, sectionNom, onValider, onPublier, saving }: {
  planifs: PlanificationOut[];
  sectionNom: string;
  onValider: (ids: number[]) => void;
  onPublier: (ids: number[]) => void;
  saving: boolean;
}) {
  const byDate: Record<string, PlanificationOut[]> = {};
  for (const p of planifs) {
    const d = p.date_examen ?? "sans-date";
    if (!byDate[d]) byDate[d] = [];
    byDate[d].push(p);
  }
  const dates    = Object.keys(byDate).sort();
  const creneaux = Array.from(new Set(planifs.map(p => p.heure_debut ?? "").filter(Boolean))).sort();
  const allIds   = planifs.map(p => p.id);

  const nbBrouillon = planifs.filter(p => p.statut?.toUpperCase() === "BROUILLON").length;
  const nbValide    = planifs.filter(p => p.statut?.toUpperCase() === "VALIDEE").length;
  const nbPublie    = planifs.filter(p => p.statut?.toUpperCase() === "PUBLIEE").length;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0, border: `1px solid ${T.border}`, borderRadius: T.radiusMd, overflow: "hidden" }}>

      {/* En-tête institutionnel */}
      <div style={{
        background: T.navy,
        padding: "18px 24px",
        display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12,
      }}>
        <div>
          <div style={{
            fontSize: 10, letterSpacing: "0.12em", textTransform: "uppercase",
            color: "rgba(255,255,255,0.55)", fontWeight: 600, marginBottom: 4,
          }}>
            Calendrier des examens
          </div>
          <h2 style={{
            fontSize: 17, fontWeight: 700, margin: 0, color: T.white,
            fontFamily: "'Georgia', serif", letterSpacing: "0.01em",
          }}>
            Section {sectionNom}
          </h2>
          <p style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", margin: "3px 0 0" }}>
            {planifs.length} matière{planifs.length > 1 ? "s" : ""} · {dates.length} jour{dates.length > 1 ? "s" : ""}
          </p>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" as const }}>
          <div style={{ display: "flex", gap: 8 }}>
            {[
              { label: "Brouillon", count: nbBrouillon, ...statutConfig("BROUILLON") },
              { label: "Validées",  count: nbValide,    ...statutConfig("VALIDEE") },
              { label: "Publiées",  count: nbPublie,    ...statutConfig("PUBLIEE") },
            ].filter(s => s.count > 0).map(s => (
              <Badge key={s.label} bg="rgba(255,255,255,0.12)" text="rgba(255,255,255,0.85)" border="rgba(255,255,255,0.2)">
                {s.count} {s.label}
              </Badge>
            ))}
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <Btn variant="success" onClick={() => onValider(allIds)} loading={saving} small>Valider tout</Btn>
            <Btn variant="warning" onClick={() => onPublier(allIds)} loading={saving} small>Publier tout</Btn>
          </div>
        </div>
      </div>

      {/* Tableau */}
      <div style={{ overflowX: "auto" as const }}>
        <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 560 }}>
          <thead>
            <tr style={{ background: "#F9FAFB", borderBottom: `2px solid ${T.border}` }}>
              <th style={{
                width: 180, padding: "11px 18px", textAlign: "left",
                fontSize: 10, fontWeight: 700, color: T.gray,
                textTransform: "uppercase", letterSpacing: "0.1em",
                borderRight: `1px solid ${T.border}`,
              }}>Date</th>
              {creneaux.map(h => (
                <th key={h} style={{
                  padding: "11px 18px", textAlign: "center",
                  fontSize: 10, fontWeight: 700, color: T.gray,
                  textTransform: "uppercase", letterSpacing: "0.1em",
                  borderLeft: `1px solid ${T.border}`, minWidth: 240,
                }}>
                  Créneau {fmtHeure(h)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dates.map((date, di) => {
              const jour = byDate[date];
              return (
                <tr key={date} style={{ background: di % 2 === 0 ? T.white : "#FAFAFA", borderBottom: `1px solid ${T.border}` }}>
                  <td style={{
                    padding: "14px 18px", verticalAlign: "middle",
                    borderRight: `1px solid ${T.border}`,
                  }}>
                    <div style={{
                      fontSize: 13, fontWeight: 700, color: T.text,
                      fontFamily: "'Georgia', serif", textTransform: "capitalize", lineHeight: 1.4,
                    }}>{fmtDate(date)}</div>
                    <div style={{ fontSize: 11, color: T.gray, marginTop: 3 }}>
                      {jour.length} examen{jour.length > 1 ? "s" : ""}
                    </div>
                  </td>
                  {creneaux.map(h => {
                    const p = jour.find(x => (x.heure_debut ?? "").startsWith(h));
                    return (
                      <td key={h} style={{
                        padding: "10px 12px", verticalAlign: "top",
                        borderLeft: `1px solid ${T.border}`, minWidth: 240,
                      }}>
                        {p ? <CarteMatiere p={p} /> : <CelluleVide />}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Légende */}
      <div style={{
        padding: "10px 18px",
        background: T.grayLight,
        borderTop: `1px solid ${T.border}`,
        display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap",
      }}>
        <span style={{ fontSize: 10, color: T.gray, fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase" }}>
          Légende :
        </span>
        {(["BROUILLON", "VALIDEE", "PUBLIEE"] as const).map(s => {
          const sc = statutConfig(s);
          return (
            <Badge key={s} bg={sc.bg} text={sc.text} border={sc.border}>{sc.label}</Badge>
          );
        })}
      </div>
    </div>
  );
}

// ─── Modal de génération ───────────────────────────────────────────────────────

function GenerationModal({ sessions, onClose, onGenerate }: {
  sessions: SessionOut[];
  onClose: () => void;
  onGenerate: (sessionId: number, params: GenerationParams) => void;
}) {
  const valid = sessions.filter(s => s.annee_universitaire !== "string");
  const [sel, setSel]   = useState<number | "">(valid[0]?.id ?? "");
  const [nom, setNom]   = useState("");
  const [annee, setAnnee] = useState("2025/2026");
  const ok = sel !== "" && nom.trim() !== "";

  const inputStyle: React.CSSProperties = {
    width: "100%", padding: "8px 10px",
    borderRadius: T.radius,
    border: `1px solid ${T.border}`,
    fontSize: 13, background: T.white, color: T.text,
    boxSizing: "border-box", outline: "none",
    fontFamily: "inherit",
  };

  const labelStyle: React.CSSProperties = {
    fontSize: 11, fontWeight: 600, color: T.gray,
    textTransform: "uppercase", letterSpacing: "0.08em",
    marginBottom: 5, display: "block",
  };

  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(17,24,39,0.6)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200,
      backdropFilter: "blur(2px)",
    }}>
      <div style={{
        background: T.white, borderRadius: T.radiusMd, width: 440,
        border: `1px solid ${T.border}`,
        boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
        overflow: "hidden",
      }}>
        {/* Titre modal */}
        <div style={{
          background: T.navy, padding: "16px 20px",
          display: "flex", justifyContent: "space-between", alignItems: "center",
        }}>
          <div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 2 }}>
              Planification automatique
            </div>
            <h2 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: T.white, fontFamily: "'Georgia', serif" }}>
              Générer l'emploi du temps
            </h2>
          </div>
          <button onClick={onClose} style={{
            background: "none", border: "none", color: "rgba(255,255,255,0.6)",
            cursor: "pointer", fontSize: 20, lineHeight: 1, padding: 0,
          }}>×</button>
        </div>

        {/* Formulaire */}
        <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label style={labelStyle}>Session d'examen</label>
            <select value={sel} onChange={e => setSel(Number(e.target.value))} style={inputStyle}>
              {valid.map(s => (
                <option key={s.id} value={s.id}>{s.type_session} — {s.annee_universitaire}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={labelStyle}>Section <span style={{ color: T.red }}>*</span></label>
            <input
              type="text" placeholder="ex. IGL3"
              value={nom}
              onChange={e => setNom(e.target.value.toUpperCase())}
              style={inputStyle}
            />
          </div>

          <div>
            <label style={labelStyle}>Année universitaire</label>
            <input
              type="text" value={annee}
              onChange={e => setAnnee(e.target.value)}
              style={inputStyle}
            />
          </div>

          <Divider />

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
            <Btn onClick={onClose}>Annuler</Btn>
            <Btn
              variant="primary"
              disabled={!ok}
              onClick={() => ok && onGenerate(Number(sel), { section_id: Number(sel), section_nom: nom, annee })}
            >
              Générer
            </Btn>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Page principale ───────────────────────────────────────────────────────────

export default function PlanificationPage() {
  const { sessions, loading, error, refresh } = useSessions();
  const [showModal, setShowModal]             = useState(false);
  const [generating, setGenerating]           = useState(false);
  const [saving, setSaving]                   = useState(false);
  const [conflits, setConflits]               = useState<string[]>([]);
  const [successMsg, setSuccessMsg]           = useState<string | null>(null);
  const [emploi, setEmploi]                   = useState<PlanificationOut[]>([]);
  const [currentSection, setCurrentSection]   = useState("");
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [lastParams, setLastParams]           = useState<{ sessionId: number; params: GenerationParams } | null>(null);
  const [refreshKey, setRefreshKey]           = useState(0);

  const getSectionIdByName = useCallback((sectionNom: string): number | null => {
    const map: Record<string, number> = { "IGL3": 2, "IGL4": 3, "IGL2": 4, "INF/IOT": 1 };
    return map[sectionNom] ?? null;
  }, []);

  const loadEmploi = useCallback(async (sessionId: number, forceSectionNom?: string) => {
    try {
      const ts = Date.now();
      let url = `${API_BASE}/api/sessions/${sessionId}/emploi-du-temps?t=${ts}`;
      const nom = forceSectionNom ?? currentSection;
      if (nom) {
        const sid = getSectionIdByName(nom);
        if (sid) url += `&section_id=${sid}`;
      }
      const res = await fetch(url, {
        cache: "no-cache",
        headers: { "Cache-Control": "no-cache, no-store, must-revalidate", Pragma: "no-cache" },
      });
      setEmploi(res.ok ? await res.json() : []);
      setRefreshKey(prev => prev + 1);
    } catch { setEmploi([]); }
  }, [currentSection, getSectionIdByName]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      caches.keys().then(keys => keys.forEach(k => caches.delete(k)));
    }
  }, []);

  const handleGenerate = async (sessionId: number, params: GenerationParams) => {
    setShowModal(false);
    setGenerating(true);
    setConflits([]);
    setSuccessMsg(null);
    setLastParams({ sessionId, params });
    try {
      const url = new URL(`${API_BASE}/api/sessions/${sessionId}/generer-auto`);
      url.searchParams.set("section_nom", params.section_nom);
      url.searchParams.set("annee", params.annee);
      const res = await fetch(url.toString(), { method: "POST", cache: "no-cache" });
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail ?? `Erreur ${res.status}`); }
      const result: GenerationResult = await res.json();
      const tousC12 = result.conflits?.length > 0 && result.conflits.every((c: string) => c.includes("[C12]"));
      if (result.conflits?.length && !tousC12) setConflits(result.conflits);
      setCurrentSection(params.section_nom);
      setCurrentSessionId(sessionId);
      await loadEmploi(sessionId, params.section_nom);
      setSuccessMsg(
        result.nb_crees > 0
          ? `${result.nb_crees} matière(s) planifiée(s) pour la section ${params.section_nom}`
          : `Emploi du temps chargé pour la section ${params.section_nom}`
      );
    } catch (e) {
      setConflits([e instanceof Error ? e.message : "Erreur de génération"]);
    } finally {
      setGenerating(false);
    }
  };

  const handleValider = async (ids: number[]) => {
    setSaving(true);
    try {
      await Promise.all(ids.map(id => fetch(`${API_BASE}/api/planifications/${id}/valider`, { method: "POST" })));
      setSuccessMsg(`${ids.length} planification(s) validée(s).`);
      if (currentSessionId) await loadEmploi(currentSessionId);
    } catch (e) { setConflits([e instanceof Error ? e.message : "Erreur"]); }
    finally { setSaving(false); }
  };

  const handlePublier = async (ids: number[]) => {
    setSaving(true);
    try {
      await Promise.all(ids.map(id => fetch(`${API_BASE}/api/planifications/${id}/publier`, { method: "POST" })));
      setSuccessMsg(`${ids.length} planification(s) publiée(s).`);
      if (currentSessionId) await loadEmploi(currentSessionId);
    } catch (e) { setConflits([e instanceof Error ? e.message : "Erreur"]); }
    finally { setSaving(false); }
  };

  const sessionsValides = sessions.filter(s => s.annee_universitaire !== "string");

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 280 }}>
      <p style={{ color: T.gray, fontSize: 13 }}>Chargement en cours…</p>
    </div>
  );

  if (error) return (
    <div style={{ padding: "3rem", textAlign: "center" }}>
      <p style={{ color: T.red, fontSize: 13 }}>Erreur : {error}</p>
      <button onClick={refresh}>Réessayer</button>
    </div>
  );

  return (
    <div key={refreshKey} style={{
      padding: "1.5rem 2rem", display: "flex", flexDirection: "column",
      gap: "1.5rem", maxWidth: 1200,
      fontFamily: "'Georgia', serif",
    }}>

      {/* En-tête */}
      <div style={{ borderBottom: `2px solid ${T.navy}`, paddingBottom: "1rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 12 }}>
          <div>
            <div style={{
              fontSize: 10, fontWeight: 700, color: T.gray,
              letterSpacing: "0.14em", textTransform: "uppercase",
              marginBottom: 4, fontFamily: "system-ui, sans-serif",
            }}>
              Université · Gestion pédagogique
            </div>
            <h1 style={{
              fontSize: 22, fontWeight: 700, margin: 0, color: T.navy,
              fontFamily: "'Georgia', serif", letterSpacing: "-0.01em",
            }}>
              Planification des examens
            </h1>
            <p style={{
              fontSize: 12, color: T.gray, margin: "4px 0 0",
              fontFamily: "system-ui, sans-serif", fontStyle: "italic",
            }}>
              Génération automatique des calendriers d'examens par section
            </p>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <Btn onClick={refresh}>Actualiser</Btn>
            <Btn
              variant="primary"
              loading={generating}
              disabled={sessionsValides.length === 0}
              onClick={() => setShowModal(true)}
            >
              Générer l'emploi du temps
            </Btn>
          </div>
        </div>
      </div>

      {showModal && (
        <GenerationModal
          sessions={sessions}
          onClose={() => setShowModal(false)}
          onGenerate={handleGenerate}
        />
      )}

      {/* Succès */}
      {successMsg && (
        <div style={{
          padding: "10px 14px", borderRadius: T.radiusMd,
          background: T.greenSoft, color: T.green,
          border: `1px solid #86EFAC`,
          fontSize: 12, fontFamily: "system-ui, sans-serif",
          display: "flex", justifyContent: "space-between", alignItems: "center",
        }}>
          <span>✓ {successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} style={{
            background: "none", border: "none", cursor: "pointer",
            color: T.green, fontSize: 16, lineHeight: 1, padding: 0,
          }}>×</button>
        </div>
      )}

      {/* Conflits */}
      {conflits.length > 0 && (
        <div style={{
          border: `1px solid #FCA5A5`, borderRadius: T.radiusMd,
          background: T.redSoft, padding: "14px 18px",
          fontFamily: "system-ui, sans-serif",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: T.red }}>
              {conflits.length} matière{conflits.length > 1 ? "s" : ""} non planifiée{conflits.length > 1 ? "s" : ""}
            </span>
            <div style={{ display: "flex", gap: 6 }}>
              <Btn small variant="warning" onClick={() => lastParams && handleGenerate(lastParams.sessionId, lastParams.params)}>
                Regénérer
              </Btn>
              <Btn small onClick={() => setConflits([])}>Fermer</Btn>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
            {conflits.map((c, i) => (
              <div key={i} style={{
                fontSize: 11, padding: "5px 10px", borderRadius: T.radius,
                background: "#FEE2E2", color: T.red, fontFamily: "monospace",
              }}>{c}</div>
            ))}
          </div>
        </div>
      )}

      {/* Emploi du temps ou placeholder */}
      {emploi.length > 0 ? (
        <EmploiDuTemps
          planifs={emploi}
          sectionNom={currentSection}
          onValider={handleValider}
          onPublier={handlePublier}
          saving={saving}
        />
      ) : !generating && (
        <div style={{
          border: `1px solid ${T.border}`,
          borderRadius: T.radiusMd,
          padding: "4rem 2rem",
          textAlign: "center",
          background: T.grayLight,
        }}>
          <div style={{
            width: 48, height: 48, borderRadius: "50%",
            background: T.blueSoft, border: `1px solid #BFDBFE`,
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 14px", fontSize: 22,
          }}>📅</div>
          <p style={{
            fontSize: 15, fontWeight: 700, margin: "0 0 6px", color: T.navy,
            fontFamily: "'Georgia', serif",
          }}>
            Aucun emploi du temps généré
          </p>
          <p style={{
            fontSize: 12, color: T.gray, margin: "0 0 20px",
            fontFamily: "system-ui, sans-serif", fontStyle: "italic",
          }}>
            Sélectionnez une session et une section pour générer automatiquement l'emploi du temps
          </p>
          <Btn variant="primary" disabled={sessionsValides.length === 0} onClick={() => setShowModal(true)}>
            Générer l'emploi du temps
          </Btn>
        </div>
      )}

      {/* Sessions disponibles */}
      {sessionsValides.length > 0 && (
        <div>
          <h2 style={{
            fontSize: 10, fontWeight: 700, margin: "0 0 10px",
            color: T.gray, textTransform: "uppercase", letterSpacing: "0.1em",
            fontFamily: "system-ui, sans-serif",
          }}>
            Sessions disponibles
          </h2>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(210px, 1fr))",
            gap: 8,
          }}>
            {sessionsValides.map(s => {
              const active = currentSessionId === s.id;
              const sc = statutConfig(s.statut);
              return (
                <div
                  key={s.id}
                  onClick={async () => {
                    setCurrentSessionId(s.id);
                    await loadEmploi(s.id);
                  }}
                  style={{
                    border: active ? `2px solid ${T.navy}` : `1px solid ${T.border}`,
                    borderRadius: T.radiusMd,
                    padding: "12px 14px",
                    background: active ? T.blueSoft : T.white,
                    cursor: "pointer",
                    transition: "all 0.1s",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, alignItems: "flex-start", gap: 6 }}>
                    <span style={{
                      fontWeight: 700, fontSize: 13, color: T.navy,
                      fontFamily: "'Georgia', serif",
                    }}>{s.type_session}</span>
                    <Badge bg={sc.bg} text={sc.text} border={sc.border}>{sc.label}</Badge>
                  </div>
                  <p style={{ fontSize: 11, color: T.slate, margin: "0 0 2px", fontFamily: "system-ui" }}>
                    {s.date_debut} → {s.date_fin}
                  </p>
                  <p style={{ fontSize: 11, color: T.gray, margin: 0, fontStyle: "italic", fontFamily: "system-ui" }}>
                    {s.annee_universitaire}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}