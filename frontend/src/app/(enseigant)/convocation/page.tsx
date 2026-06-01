"use client";

import { useState, useEffect, useMemo, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ConvocationCard } from "@/components/surveillance/ConvocationCard";
import { getCatalogue, type Catalogue } from "@/lib/api/referentiel";
import { useConvocation } from "@/hooks/useConvocation";
import { usePDFExport } from "@/hooks/usePDFExport";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

const API_ENDPOINTS = {
  AUTH_ME: `${API_BASE_URL}/auth/me`,
  AUTH_LOGOUT: `${API_BASE_URL}/auth/logout`,
};

const FST_LOGO = "/assets/fst.jpg";
const UTM_LOGO = "/assets/ut.jpg";

interface UserInfo {
  nom: string;
  prenom: string;
  email: string;
  enseignant_id: number;
}

function ConvocationContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<UserInfo | null>(null);
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [selectedSemestre, setSelectedSemestre] = useState<number | "">("");

  useEffect(() => {
    fetch(API_ENDPOINTS.AUTH_ME, { credentials: "include" })
      .then(r => { if (!r.ok) { router.replace("/login"); return null; } return r.json(); })
      .then(data => {
        if (!data) return;
        if (data.type !== "ENSEIGNANT") { router.replace("/login"); return; }
        setUser({ nom: data.nom, prenom: data.prenom, email: data.email, enseignant_id: data.enseignant_id });
      })
      .catch(() => router.replace("/login"));
  }, [router]);

  useEffect(() => {
    getCatalogue()
      .then(setCatalogue)
      .catch(() => setCatalogue(null));
  }, []);

  useEffect(() => {
    if (selectedSemestre) {
      return;
    }
    const param = searchParams.get("semestre");
    if (param) {
      const parsed = Number(param);
      if (parsed === 1 || parsed === 2) {
        setSelectedSemestre(parsed);
        return;
      }
    }
    if (catalogue?.semestres?.length) {
      setSelectedSemestre(catalogue.semestres.includes("S2") ? 2 : 1);
    }
  }, [catalogue, searchParams, selectedSemestre]);

  const validEnseignantId = user?.enseignant_id ?? null;

  const filters = useMemo(
    () => ({
      annee_universitaire: searchParams.get("annee_universitaire") ?? undefined,
      semestre: selectedSemestre ? Number(selectedSemestre) : undefined,
      type_epreuve: searchParams.get("type_epreuve") ?? undefined,
    }),
    [searchParams, selectedSemestre],
  );

  const { data, loading, error } = useConvocation(validEnseignantId, filters);
  const { exportPDF, loading: exporting, error: exportError } = usePDFExport();

  const enseignant = (data?.enseignant ?? {}) as {
    nom?: string;
    prenom?: string;
    grade?: string | null;
    departement?: { nom?: string | null } | string | null;
    email?: string | null;
  };

  const sessionFromSurveillances = Array.isArray(data?.surveillances) && data.surveillances.length > 0
    ? (data.surveillances[0] as any)?.session
    : null;

  const chargeYear = (data as any)?.charge_horaire?.annee_universitaire ?? null;
  const catalogueSessions = catalogue?.sessions ?? [];
  const sessionsByDate = [...catalogueSessions].sort((a, b) => a.date_debut.localeCompare(b.date_debut));
  const matchingSessions = chargeYear
    ? sessionsByDate.filter((s) => s.label.includes(chargeYear))
    : sessionsByDate;
  const fallbackSession = matchingSessions.length
    ? matchingSessions[matchingSessions.length - 1]
    : null;
  const semesterSession = selectedSemestre
    ? (selectedSemestre === 1 ? matchingSessions[0] : matchingSessions[matchingSessions.length - 1])
    : null;

  const session = (sessionFromSurveillances ?? {
    type_session: semesterSession?.label ?? fallbackSession?.label ?? "Session",
    annee_universitaire: chargeYear ?? null,
  }) as {
    type_session?: string | null;
    annee_universitaire?: string | null;
  };

  const assignments = Array.isArray(data?.surveillances)
    ? data.surveillances.map((item: Record<string, any>) => ({
        matiere: item?.matiere?.intitule ?? item?.matiere?.code ?? "—",
        date: item?.creneau?.date ?? "—",
        heure_debut: item?.creneau?.heure_debut ?? undefined,
        heure_fin: item?.creneau?.heure_fin ?? undefined,
        salle: item?.salle?.code ?? item?.salle?.designation ?? "—",
        groupe: item?.groupe?.numero ? `G${item.groupe.numero}` : "—",
        charge: item?.surveillance?.charge ?? item?.charge ?? undefined,
      }))
    : [];

  const canExport = validEnseignantId && enseignant.nom && enseignant.prenom;

  const handleLogout = async () => {
    await fetch(API_ENDPOINTS.AUTH_LOGOUT, { method: "POST", credentials: "include" });
    router.replace("/login");
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#f8fafc",
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    }}>
      <nav style={{
        background: "#ffffff",
        borderBottom: "1px solid #e9eef3",
        padding: "0 40px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: 80,
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <img src={UTM_LOGO} alt="UTM" style={{ height: 48, width: "auto", objectFit: "contain" }} />
            <div style={{ width: 1, height: 36, background: "#e9eef3" }} />
            <img src={FST_LOGO} alt="FST" style={{ height: 48, width: "auto", objectFit: "contain" }} />
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 500, color: "#94a3b8", letterSpacing: "0.5px", textTransform: "uppercase" }}>
              Université de Tunis El Manar
            </div>
            <div style={{ fontSize: 14, fontWeight: 600, color: "#1e293b" }}>
              Faculté des Sciences de Tunis
            </div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 28 }}>
          {/* Navigation Links */}
          <div style={{ display: "flex", gap: "24px", marginRight: "32px" }}>
            <a href="/convocation" style={{
              textDecoration: "none",
              color: "#4f46e5",
              fontWeight: 600,
              fontSize: "15px",
              paddingBottom: "4px",
              borderBottom: "2px solid #4f46e5"
            }}>
              Mes Convocations
            </a>
            <a href="/indisponibilite" style={{
              textDecoration: "none",
              color: "#64748b",
              fontWeight: 500,
              fontSize: "15px",
              paddingBottom: "4px",
              borderBottom: "2px solid transparent",
              transition: "all 0.2s"
            }} onMouseEnter={(e) => e.currentTarget.style.color = "#4f46e5"}
               onMouseLeave={(e) => e.currentTarget.style.color = "#64748b"}>
              Mes Indisponibilités
            </a>
          </div>
          {user && (
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: "#1e293b" }}>{user.prenom} {user.nom}</div>
              <div style={{ fontSize: 12, color: "#94a3b8" }}>Enseignant</div>
            </div>
          )}
          <button
            onClick={handleLogout}
            style={{
              background: "transparent",
              border: "1px solid #e2e8f0",
              borderRadius: 40,
              padding: "8px 22px",
              color: "#64748b",
              fontSize: 13,
              fontWeight: 500,
              cursor: "pointer",
              fontFamily: "inherit",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={e => { e.currentTarget.style.background = "#afd6fc"; e.currentTarget.style.borderColor = "#cbd5e1"; }}
            onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#e2e8f0"; }}
          >
            Déconnexion
          </button>
        </div>
      </nav>

      <main style={{ maxWidth: 1120, margin: "0 auto", padding: "40px 40px" }}>
        <div style={{ marginBottom: 48 }}>
          <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", flexWrap: "wrap", gap: 24 }}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 500, color: "#4f46e5", marginBottom: 8, letterSpacing: "0.3px" }}>
                Gestion des examens
              </div>
              <h1 style={{ margin: 0, fontSize: 36, fontWeight: 700, color: "#0f172a", letterSpacing: "-0.02em", lineHeight: 1.2 }}>
                Mes convocations
              </h1>
              <p style={{ margin: "12px 0 0", fontSize: 15, color: "#64748b", fontWeight: 400 }}>
                Consultez votre emploi du temps de surveillance
              </p>
            </div>
            <div style={{ minWidth: 200 }}>
              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 6 }}>
                Semestre
              </label>
              <select
                value={selectedSemestre}
                onChange={(event) => {
                  const value = event.target.value ? Number(event.target.value) : "";
                  setSelectedSemestre(value === 1 || value === 2 ? value : "");
                }}
                style={{
                  height: 38,
                  width: "100%",
                  borderRadius: 12,
                  border: "1px solid #e2e8f0",
                  padding: "0 12px",
                  fontSize: 14,
                  color: "#0f172a",
                  background: "#ffffff",
                  boxShadow: "0 1px 2px rgba(15,23,42,0.04)",
                }}
              >
                <option value="">Tous</option>
                <option value={1}>S1</option>
                <option value={2}>S2</option>
              </select>
            </div>
          </div>
        </div>

        {user ? (
          <div>
            {loading && <p className="text-sm text-slate-600">Chargement...</p>}
            {error && <p className="text-sm text-red-600">{error}</p>}
            {exportError && <p className="text-sm text-red-600">{exportError}</p>}
            
            <ConvocationCard
              enseignant={{
                nom: enseignant.nom ?? user.nom ?? "—",
                prenom: enseignant.prenom ?? user.prenom ?? "—",
                grade: enseignant.grade ?? null,
                departement:
                  typeof enseignant.departement === "string"
                    ? enseignant.departement
                    : enseignant.departement?.nom ?? null,
                email: enseignant.email ?? user.email ?? null,
              }}
              session={session}
              assignments={assignments}
              onExport={
                canExport
                  ? () =>
                      exportPDF({
                        enseignant: {
                          nom: enseignant.nom ?? user.nom ?? "—",
                          prenom: enseignant.prenom ?? user.prenom ?? "—",
                          grade: enseignant.grade ?? null,
                          departement:
                            typeof enseignant.departement === "string"
                              ? enseignant.departement
                              : enseignant.departement?.nom ?? null,
                          email: enseignant.email ?? user.email ?? null,
                        },
                        session,
                        assignments,
                      })
                  : undefined
              }
            />
            {exporting && <p className="text-xs text-slate-500 mt-2">Génération du PDF en cours...</p>}
          </div>
        ) : (
          <p className="text-sm text-slate-600">Chargement des informations utilisateur...</p>
        )}
      </main>
    </div>
  );
}

export default function ConvocationPage() {
  return (
    <Suspense fallback={<div>Chargement...</div>}>
      <ConvocationContent />
    </Suspense>
  );
}
