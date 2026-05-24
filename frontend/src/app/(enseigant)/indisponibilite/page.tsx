"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";


const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

const API_ENDPOINTS = {
  AUTH_ME: `${API_BASE_URL}/auth/me`,
  AUTH_LOGOUT: `${API_BASE_URL}/auth/logout`,
  INDISPONIBILITES: `${API_BASE_URL}/indisponibilites`,
  INDISPONIBILITES_BY_ENSEIGNANT: (id: number) => `${API_BASE_URL}/indisponibilites/enseignant/${id}`,
  INDISPONIBILITE_BY_ID: (id: number) => `${API_BASE_URL}/indisponibilites/${id}`,
};

const FST_LOGO = "/assets/fst.jpg";
const UTM_LOGO = "/assets/ut.jpg";

type TypeDispo = "INDISPONIBLE" | "MISSION" | "CONGE" | "COURS_PREVU";

interface Indisponibilite {
  id: number;
  date: string;
  heure_debut: string;
  heure_fin: string;
  type_dispo: TypeDispo;
  motif: string;
  confirme: boolean;
}

interface UserInfo {
  nom: string;
  prenom: string;
  email: string;
  enseignant_id: number;
}

const TYPE_STYLES: Record<TypeDispo, { label: string; icon: string; color: string; bg: string }> = {
  INDISPONIBLE: { label: "Indisponible", icon: "⛔", color: "#dc2626", bg: "#fef2f2" },
  MISSION: { label: "Mission", icon: "✈️", color: "#ea580c", bg: "#fff7ed" },
  CONGE: { label: "Congé", icon: "🏖️", color: "#059669", bg: "#ecfdf5" },
  COURS_PREVU: { label: "Cours prévu", icon: "📚", color: "#4f46e5", bg: "#eef2ff" },
};

const EMPTY_FORM = {
  date: "", heure_debut: "", heure_fin: "",
  type_dispo: "INDISPONIBLE" as TypeDispo, motif: "",
};

export default function IndisponibilitePage() {
  const router = useRouter();

  const [user, setUser] = useState<UserInfo | null>(null);
  const [list, setList] = useState<Indisponibilite[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);

  useEffect(() => {
    fetch(API_ENDPOINTS.AUTH_ME, { credentials: "include" })
      .then(r => { if (!r.ok) { router.replace("/"); return null; } return r.json(); })
      .then(data => {
        if (!data) return;
        if (data.type !== "ENSEIGNANT") { router.replace("/"); return; }
        setUser({ nom: data.nom, prenom: data.prenom, email: data.email, enseignant_id: data.enseignant_id });
        fetchList(data.enseignant_id);
      })
      .catch(() => router.replace("/"));
  }, []);

  const fetchList = (eid: number) => {
    setLoading(true);
    fetch(API_ENDPOINTS.INDISPONIBILITES_BY_ENSEIGNANT(eid), { credentials: "include" })
      .then(r => r.json())
      .then(data => {
        setList(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  const handleLogout = async () => {
    await fetch(API_ENDPOINTS.AUTH_LOGOUT, { method: "POST", credentials: "include" });
    router.replace("/");
  };

  const openCreate = () => {
    setEditId(null);
    setForm(EMPTY_FORM);
    setError(""); setSuccess("");
    setShowForm(true);
  };

  const openEdit = (item: Indisponibilite) => {
    setEditId(item.id);
    setForm({
      date: item.date,
      heure_debut: item.heure_debut.slice(0, 5),
      heure_fin: item.heure_fin.slice(0, 5),
      type_dispo: item.type_dispo,
      motif: item.motif || "",
    });
    setError(""); setSuccess("");
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const closeForm = () => {
    setShowForm(false);
    setEditId(null);
    setForm(EMPTY_FORM);
    setError(""); setSuccess("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    if (form.heure_debut >= form.heure_fin) {
      setError("L'heure de fin doit être supérieure à l'heure de début"); return;
    }
    setSubmitting(true); setError(""); setSuccess("");

    try {
      let res: Response;

      if (editId !== null) {
        res = await fetch(API_ENDPOINTS.INDISPONIBILITE_BY_ID(editId), {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            date: form.date,
            heure_debut: form.heure_debut,
            heure_fin: form.heure_fin,
            type_dispo: form.type_dispo,
            motif: form.motif || null,
          }),
        });
        if (!res.ok) { const d = await res.json(); setError(d.detail || "Erreur"); return; }
        setSuccess("Indisponibilité modifiée avec succès");
      } else {
        res = await fetch(API_ENDPOINTS.INDISPONIBILITES, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ ...form, enseignant_id: user.enseignant_id, confirme: true }),
        });
        if (!res.ok) { const d = await res.json(); setError(d.detail || "Erreur"); return; }
        setSuccess("Indisponibilité enregistrée avec succès");
      }

      closeForm();
      fetchList(user.enseignant_id);
    } catch {
      setError("Erreur de connexion au serveur");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!user) return;
    try {
      await fetch(API_ENDPOINTS.INDISPONIBILITE_BY_ID(id), { method: "DELETE", credentials: "include" });
      setList(prev => prev.filter(i => i.id !== id));
      setDeleteId(null);
      setSuccess("Indisponibilité supprimée");
    } catch { setError("Erreur lors de la suppression"); }
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
              color: "#64748b",
              fontWeight: 500,
              fontSize: "15px",
              paddingBottom: "4px",
              borderBottom: "2px solid transparent",
              transition: "all 0.2s"
            }} onMouseEnter={(e) => e.currentTarget.style.color = "#4f46e5"}
               onMouseLeave={(e) => e.currentTarget.style.color = "#64748b"}>
              Mes Convocations
            </a>
            <a href="/indisponibilite" style={{
              textDecoration: "none",
              color: "#4f46e5",
              fontWeight: 600,
              fontSize: "15px",
              paddingBottom: "4px",
              borderBottom: "2px solid #4f46e5"
            }}>
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
                Mes indisponibilités
              </h1>
              <p style={{ margin: "12px 0 0", fontSize: 15, color: "#64748b", fontWeight: 400 }}>
                Déclarez et gérez vos périodes d'indisponibilité
              </p>
            </div>
            {!showForm && (
              <button
                onClick={openCreate}
                style={{
                  background: "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)",
                  border: "none",
                  borderRadius: 10,
                  padding: "12px 28px",
                  color: "#ffffff",
                  fontSize: 14,
                  fontWeight: 500,
                  cursor: "pointer",
                  fontFamily: "inherit",
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  transition: "all 0.2s ease",
                  boxShadow: "0 2px 8px rgba(79,70,229,0.25)",
                }}
                onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-2px)"; e.currentTarget.style.boxShadow = "0 6px 16px rgba(79,70,229,0.3)"; }}
                onMouseLeave={e => { e.currentTarget.style.transform = "translateY(0)"; e.currentTarget.style.boxShadow = "0 2px 8px rgba(79,70,229,0.25)"; }}
              >
                <span style={{ fontSize: 20 }}>+</span> Nouvelle déclaration
              </button>
            )}
          </div>
          <div style={{ marginTop: 32, height: 1, background: "#e9eef3" }} />
        </div>

        {error && (
          <div style={{
            marginBottom: 28,
            padding: "16px 20px",
            background: "#fef2f2",
            border: "1px solid #fee2e2",
            borderRadius: 16,
            color: "#dc2626",
            fontSize: 14,
            fontWeight: 500,
          }}>{error}</div>
        )}
        {success && (
          <div style={{
            marginBottom: 28,
            padding: "16px 20px",
            background: "#ecfdf5",
            border: "1px solid #d1fae5",
            borderRadius: 16,
            color: "#059669",
            fontSize: 14,
            fontWeight: 500,
          }}>{success}</div>
        )}

        {showForm && (
          <div style={{
            background: "#ffffff",
            borderRadius: 24,
            marginBottom: 48,
            boxShadow: "0 20px 35px -12px rgba(0,0,0,0.08)",
            border: "1px solid #e9eef3",
            overflow: "hidden",
          }}>
            <div style={{
              padding: "28px 36px",
              background: "#ffffff",
              borderBottom: "1px solid #e9eef3",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}>
              <div>
                <h2 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: "#0f172a", letterSpacing: "-0.01em" }}>
                  {editId !== null ? "Modifier une indisponibilité" : "Créer une indisponibilité"}
                </h2>
                <p style={{ margin: "6px 0 0", fontSize: 14, color: "#64748b" }}>
                  {editId !== null ? "Modifiez les informations ci-dessous" : "Remplissez le formulaire ci-dessous"}
                </p>
              </div>
              <button
                onClick={closeForm}
                style={{
                  background: "#f8fafc",
                  border: "1px solid #e2e8f0",
                  borderRadius: 40,
                  padding: "8px 20px",
                  color: "#64748b",
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: "pointer",
                  fontFamily: "inherit",
                  transition: "all 0.2s",
                }}
                onMouseEnter={e => { e.currentTarget.style.background = "#f1f5f9"; }}
                onMouseLeave={e => { e.currentTarget.style.background = "#f8fafc"; }}
              >
                Annuler
              </button>
            </div>

            <form onSubmit={handleSubmit} style={{ padding: "36px" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 28, marginBottom: 28 }}>
                <div>
                  <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#334155", marginBottom: 8 }}>Date</label>
                  <input
                    type="date"
                    required
                    value={form.date}
                    onChange={e => setForm(f => ({ ...f, date: e.target.value }))}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      border: "1.5px solid #e2e8f0",
                      borderRadius: 12,
                      fontSize: 14,
                      fontFamily: "inherit",
                      fontWeight: 450,
                      outline: "none",
                      transition: "all 0.2s",
                    }}
                    onFocus={e => { e.target.style.borderColor = "#4f46e5"; e.target.style.boxShadow = "0 0 0 3px rgba(79,70,229,0.08)"; }}
                    onBlur={e => { e.target.style.borderColor = "#e2e8f0"; e.target.style.boxShadow = "none"; }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#334155", marginBottom: 8 }}>Heure début</label>
                  <input
                    type="time"
                    required
                    value={form.heure_debut}
                    onChange={e => setForm(f => ({ ...f, heure_debut: e.target.value }))}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      border: "1.5px solid #e2e8f0",
                      borderRadius: 12,
                      fontSize: 14,
                      fontFamily: "inherit",
                      fontWeight: 450,
                      outline: "none",
                      transition: "all 0.2s",
                    }}
                    onFocus={e => { e.target.style.borderColor = "#4f46e5"; e.target.style.boxShadow = "0 0 0 3px rgba(79,70,229,0.08)"; }}
                    onBlur={e => { e.target.style.borderColor = "#e2e8f0"; e.target.style.boxShadow = "none"; }}
                  />
                </div>
                <div>
                  <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#334155", marginBottom: 8 }}>Heure fin</label>
                  <input
                    type="time"
                    required
                    value={form.heure_fin}
                    onChange={e => setForm(f => ({ ...f, heure_fin: e.target.value }))}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      border: "1.5px solid #e2e8f0",
                      borderRadius: 12,
                      fontSize: 14,
                      fontFamily: "inherit",
                      fontWeight: 450,
                      outline: "none",
                      transition: "all 0.2s",
                    }}
                    onFocus={e => { e.target.style.borderColor = "#4f46e5"; e.target.style.boxShadow = "0 0 0 3px rgba(79,70,229,0.08)"; }}
                    onBlur={e => { e.target.style.borderColor = "#e2e8f0"; e.target.style.boxShadow = "none"; }}
                  />
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 28, marginBottom: 36 }}>
                <div>
                  <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#334155", marginBottom: 8 }}>Type</label>
                  <select
                    value={form.type_dispo}
                    onChange={e => setForm(f => ({ ...f, type_dispo: e.target.value as TypeDispo }))}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      border: "1.5px solid #e2e8f0",
                      borderRadius: 12,
                      fontSize: 14,
                      fontFamily: "inherit",
                      fontWeight: 450,
                      backgroundColor: "#ffffff",
                      cursor: "pointer",
                      outline: "none",
                    }}
                  >
                    {Object.entries(TYPE_STYLES).map(([k, v]) => (
                      <option key={k} value={k}>{v.icon} {v.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "#334155", marginBottom: 8 }}>Motif <span style={{ fontWeight: 400, color: "#94a3b8" }}>(optionnel)</span></label>
                  <input
                    type="text"
                    value={form.motif}
                    placeholder="Ex: Rendez-vous médical, Formation, etc."
                    onChange={e => setForm(f => ({ ...f, motif: e.target.value }))}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      border: "1.5px solid #e2e8f0",
                      borderRadius: 12,
                      fontSize: 14,
                      fontFamily: "inherit",
                      fontWeight: 450,
                      outline: "none",
                      transition: "all 0.2s",
                    }}
                    onFocus={e => { e.target.style.borderColor = "#4f46e5"; e.target.style.boxShadow = "0 0 0 3px rgba(79,70,229,0.08)"; }}
                    onBlur={e => { e.target.style.borderColor = "#e2e8f0"; e.target.style.boxShadow = "none"; }}
                  />
                </div>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 12 }}>
                <button
                  type="button"
                  onClick={closeForm}
                  style={{
                    background: "#ffffff",
                    border: "1.5px solid #e2e8f0",
                    borderRadius: 40,
                    padding: "12px 28px",
                    color: "#64748b",
                    fontSize: 14,
                    fontWeight: 500,
                    cursor: "pointer",
                    fontFamily: "inherit",
                    transition: "all 0.2s",
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = "#f8fafc"; e.currentTarget.style.borderColor = "#cbd5e1"; }}
                  onMouseLeave={e => { e.currentTarget.style.background = "#ffffff"; e.currentTarget.style.borderColor = "#e2e8f0"; }}
                >
                  Retour
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  style={{
                    background: "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)",
                    border: "none",
                    borderRadius: 40,
                    padding: "12px 32px",
                    color: "#ffffff",
                    fontSize: 14,
                    fontWeight: 500,
                    cursor: submitting ? "not-allowed" : "pointer",
                    fontFamily: "inherit",
                    transition: "all 0.2s",
                    opacity: submitting ? 0.7 : 1,
                  }}
                >
                  {submitting
                    ? (editId !== null ? "Modification..." : "Enregistrement...")
                    : (editId !== null ? "Confirmer la modification" : "Enregistrer")}
                </button>
              </div>
            </form>
          </div>
        )}

        {!loading && list.length === 0 && !showForm && (
          <div style={{
            textAlign: "center",
            padding: "80px 48px",
            background: "#ffffff",
            borderRadius: 24,
            border: "1px solid #e9eef3",
          }}>
            <div style={{ fontSize: 56, marginBottom: 20, opacity: 0.5 }}>📋</div>
            <div style={{ fontSize: 20, fontWeight: 600, color: "#0f172a", marginBottom: 8 }}>Aucune indisponibilité</div>
            <div style={{ fontSize: 14, color: "#64748b", marginBottom: 32 }}>Vous n'avez pas encore déclaré d'indisponibilité</div>
            <button
              onClick={openCreate}
              style={{
                background: "linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)",
                border: "none",
                borderRadius: 40,
                padding: "12px 28px",
                color: "#ffffff",
                fontSize: 14,
                fontWeight: 500,
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              + Créer une indisponibilité
            </button>
          </div>
        )}

        {loading && (
          <div style={{ textAlign: "center", padding: 80 }}>
            <div style={{ fontSize: 14, color: "#94a3b8" }}>Chargement...</div>
          </div>
        )}

        {!loading && list.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {list.map(item => {
              const style = TYPE_STYLES[item.type_dispo] || TYPE_STYLES.INDISPONIBLE;
              const date = new Date(item.date);
              const isPast = date < new Date() && date.toDateString() !== new Date().toDateString();
              const isToday = date.toDateString() === new Date().toDateString();

              return (
                <div
                  key={item.id}
                  style={{
                    background: "#ffffff",
                    borderRadius: 20,
                    padding: "20px 28px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 20,
                    flexWrap: "wrap",
                    transition: "all 0.2s ease",
                    border: "1px solid #e9eef3",
                    opacity: isPast ? 0.7 : 1,
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.borderColor = "#cbd5e1";
                    e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.04)";
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.borderColor = "#e9eef3";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 18, flex: 1 }}>
                    <div style={{
                      width: 48,
                      height: 48,
                      borderRadius: 30,
                      background: style.bg,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 24,
                    }}>
                      {style.icon}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 6 }}>
                        <span style={{
                          display: "inline-block",
                          padding: "4px 12px",
                          borderRadius: 20,
                          fontSize: 11,
                          fontWeight: 600,
                          letterSpacing: "0.2px",
                          background: style.bg,
                          color: style.color,
                        }}>
                          {style.label}
                        </span>
                        {isToday && (
                          <span style={{
                            fontSize: 10,
                            fontWeight: 600,
                            color: "#4f46e5",
                            background: "#eef2ff",
                            padding: "2px 10px",
                            borderRadius: 20,
                          }}>Aujourd'hui</span>
                        )}
                        {isPast && (
                          <span style={{ fontSize: 10, fontWeight: 500, color: "#94a3b8" }}>Passé</span>
                        )}
                      </div>
                      <div style={{ fontSize: 16, fontWeight: 600, color: "#0f172a", marginBottom: 4 }}>
                        {date.toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
                      </div>
                      <div style={{ fontSize: 13, color: "#64748b", display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
                        <span>🕐 {item.heure_debut.slice(0, 5)} — {item.heure_fin.slice(0, 5)}</span>
                        {item.motif && <span style={{ color: "#4f46e5" }}>· {item.motif}</span>}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: 10 }}>
                    {deleteId === item.id ? (
                      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                        <span style={{ fontSize: 13, color: "#64748b" }}>Confirmer ?</span>
                        <button
                          onClick={() => handleDelete(item.id)}
                          style={{
                            background: "#dc2626",
                            border: "none",
                            borderRadius: 40,
                            padding: "7px 16px",
                            color: "#ffffff",
                            fontSize: 12,
                            fontWeight: 500,
                            cursor: "pointer",
                            fontFamily: "inherit",
                          }}
                        >Supprimer</button>
                        <button
                          onClick={() => setDeleteId(null)}
                          style={{
                            background: "#f8fafc",
                            border: "1px solid #e2e8f0",
                            borderRadius: 40,
                            padding: "7px 16px",
                            color: "#64748b",
                            fontSize: 12,
                            fontWeight: 500,
                            cursor: "pointer",
                            fontFamily: "inherit",
                          }}
                        >Annuler</button>
                      </div>
                    ) : (
                      <>
                        <button
                          onClick={() => openEdit(item)}
                          style={{
                            background: "transparent",
                            border: "1px solid #e2e8f0",
                            borderRadius: 40,
                            padding: "8px 18px",
                            color: "#4f46e5",
                            fontSize: 12,
                            fontWeight: 500,
                            cursor: "pointer",
                            fontFamily: "inherit",
                            transition: "all 0.2s",
                          }}
                          onMouseEnter={e => { e.currentTarget.style.background = "#eef2ff"; e.currentTarget.style.borderColor = "#c7d2fe"; }}
                          onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#e2e8f0"; }}
                        >Modifier</button>
                        <button
                          onClick={() => setDeleteId(item.id)}
                          style={{
                            background: "transparent",
                            border: "1px solid #e2e8f0",
                            borderRadius: 40,
                            padding: "8px 18px",
                            color: "#dc2626",
                            fontSize: 12,
                            fontWeight: 500,
                            cursor: "pointer",
                            fontFamily: "inherit",
                            transition: "all 0.2s",
                          }}
                          onMouseEnter={e => { e.currentTarget.style.background = "#fef2f2"; e.currentTarget.style.borderColor = "#fecaca"; }}
                          onMouseLeave={e => { e.currentTarget.style.background = "transparent"; e.currentTarget.style.borderColor = "#e2e8f0"; }}
                        >Supprimer</button>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {!loading && list.length > 0 && (
          <div style={{
            marginTop: 32,
            padding: "24px 32px",
            background: "#ffffff",
            borderRadius: 20,
            border: "1px solid #e9eef3",
            display: "flex",
            gap: 48,
            flexWrap: "wrap",
          }}>
            <div>
              <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 6, fontWeight: 500 }}>Total déclarations</div>
              <div style={{ fontSize: 32, fontWeight: 700, color: "#0f172a", letterSpacing: "-0.02em" }}>{list.length}</div>
            </div>
            {Object.entries(TYPE_STYLES).map(([k, v]) => {
              const count = list.filter(i => i.type_dispo === k).length;
              if (count === 0) return null;
              return (
                <div key={k}>
                  <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 6, fontWeight: 500 }}>{v.label}</div>
                  <div style={{ fontSize: 28, fontWeight: 600, color: "#0f172a" }}>{count}</div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
