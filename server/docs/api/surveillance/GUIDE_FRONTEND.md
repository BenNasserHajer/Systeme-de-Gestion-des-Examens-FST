# 🎨 Guide Frontend - Intégration Module Surveillance

## 📋 Vue d'Ensemble

Ce guide est destiné à l'équipe Frontend pour intégrer le module de surveillance
des examens dans l'interface Next.js.

**Objectif** : Créer une interface complète pour gérer l'affectation des surveillants,
le suivi des présences, les remplacements et la consultation des statistiques.

---

## 🎯 Fonctionnalités à Implémenter

### 1. Page Affectation Automatique (`/surveillance/affecter`)
- ✅ Sélection session + section + période + type d'épreuve
- ✅ Lancement de l'algorithme v3
- ✅ Affichage résultats par planification → groupe → surveillant
- ✅ Liste des raisons d'exclusion
- ✅ Mise en évidence des conflits (manquants)

### 2. Page Affectation Manuelle (`/surveillance/manuelle`)
- ✅ Sélection session + planification + groupe + salle
- ✅ Liste des enseignants disponibles (triés, filtrés, avec avertissements)
- ✅ Sélection multiple d'enseignants
- ✅ Gestion des motifs pour enseignants externes

### 3. Page Session (`/surveillance/session/{id}`)
- ✅ Liste filtrée des surveillances (semestre, type, statut, groupe, salle, département)
- ✅ Rapport complet avec statistiques
- ✅ Tableau des conflits par groupe
- ✅ Classement des enseignants par charge

### 4. Page Enseignant (`/surveillance/enseignant/{id}`)
- ✅ Fiche complète avec charge horaire et taux d'utilisation
- ✅ Timeline des surveillances
- ✅ Filtres par année / semestre / type d'épreuve

### 5. Actions sur une Surveillance
- ✅ Modifier statut / présence / charge (PATCH)
- ✅ Remplacer l'enseignant (reassign)
- ✅ Supprimer une surveillance

---

## 🔌 Intégration API

### Configuration

```typescript
// src/lib/api/surveillance.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
const BASE = `${API_BASE_URL}/surveillances`;
```

### Types TypeScript

```typescript
// src/types/surveillance.ts

export type ModeAffectation = 'AUTOMATIQUE' | 'MANUELLE';
export type StatutSurveillance = 'AFFECTE' | 'CONFIRME';
export type TypeEpreuve = 'DS' | 'EXAMEN_FINAL';

export interface Departement {
  id: number | null;
  nom: string | null;
  code: string | null;
}

export interface Groupe {
  id: number | null;
  numero: number | null;
  effectif: number | null;
  nb_etudiants: number | null;
  annee: string | null;
}

export interface Salle {
  id: number | null;
  code: string | null;
  designation: string | null;
  capacite: number | null;
  batiment: string | null;
}

export interface Matiere {
  id: number | null;
  code: string | null;
  intitule: string | null;
  coefficient: number | null;
  credit: number | null;
  duree_examen: number | null;
  duree_ds: number | null;
}

export interface Creneau {
  id: number | null;
  date: string | null;
  heure_debut: string | null;
  heure_fin: string | null;
  libelle: string | null;
}

export interface SessionInfo {
  id: number | null;
  type_session: string | null;
  annee_universitaire: string | null;
  date_debut: string | null;
  date_fin: string | null;
  statut: string | null;
}

export interface EnseignantInfo {
  id: number | null;
  nom: string | null;
  prenom: string | null;
  nom_complet: string | null;
  grade: string | null;
  email: string | null;
  telephone: string | null;
  volume_horaire: number;
  volume_consomme: number;
  volume_restant: number;
  departement: Departement;
}

export interface SurveillanceDetail {
  id: number;
  statut_surveillance: StatutSurveillance;
  mode_affectation: ModeAffectation;
  charge: number;
  presence: boolean;
  est_externe: boolean;
  motif_externe: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface SurveillanceEnrichie {
  surveillance: SurveillanceDetail;
  enseignant: EnseignantInfo;
  planification: {
    id: number;
    type_epreuve: TypeEpreuve;
    duree: number;
    semestre: number;
    statut: string;
    nb_groupes: number;
    nb_surveillants_requis: number;
    mode_affectation: string;
  };
  session: SessionInfo;
  departement_examen: Departement;
  creneau: Creneau;
  matiere: Matiere;
  section: { id: number | null; nom: string | null };
  niveau: { id: number | null; libelle: string | null; type_formation: string | null };
  groupe: Groupe;
  salle: Salle;
}

// ── Affectation automatique ─────────────────────────────────────────────────

export interface AffecterSessionRequest {
  session_id: number;
  section_nom: string;
  periode: string;      // Ex: "2025/2026-S1"
  type_epreuve: TypeEpreuve;
}

export interface EnseignantAffecte {
  surveillance_id: number;
  enseignant_id: number;
  nom: string;
  prenom: string;
  grade: string | null;
  email: string | null;
  telephone: string | null;
  departement: Departement;
  groupe: Groupe | null;
  salle: Salle | null;
  charge: number;
  mode_affectation: string;
  statut_surveillance: string;
  presence: boolean;
  est_externe: boolean;
  motif_externe: string | null;
}

export interface GroupeResult {
  groupe: Groupe | null;
  salle: Salle | null;
  statut: string;
  surveillants_requis: number;
  manquants: number;
  surveillants_affectes: EnseignantAffecte[];
}

export interface RaisonExclusion {
  enseignant_id: number;
  nom: string;
  prenom: string;
  raison: string;
  details: string | null;
}

export interface AffecterSessionResult {
  planification_id: number;
  type_epreuve: string;
  semestre: number | null;
  duree: number | null;
  statut: string;
  surveillants_requis: number;
  surveillants_affectes: number;
  manquants: number;
  matiere: Matiere | null;
  section: { id: number | null; nom: string | null; niveau: any } | null;
  departement_examen: Departement | null;
  creneau: Creneau | null;
  groupes: GroupeResult[];
  raisons_exclusion: RaisonExclusion[];
}

export interface AffecterSessionResponse {
  session_id: number;
  session: SessionInfo | null;
  total_planifications: number;
  affectees_automatiquement: number;
  en_conflit: number;
  message: string;
  resultats: AffecterSessionResult[];
  non_affectees: AffecterSessionResult[];
}

// ── Enseignants disponibles ─────────────────────────────────────────────────

export interface Avertissement {
  date: string;
  heure_debut: string;
  heure_fin: string;
  type_dispo: string;
  motif: string | null;
}

export interface EnseignantDisponible {
  enseignant_id: number;
  nom: string;
  prenom: string;
  grade: string | null;
  email: string | null;
  telephone: string | null;
  volume_horaire: number;
  volume_consomme: number;
  volume_restant: number;
  nb_surveillances: number;
  a_avertissement: boolean;
  avertissements: Avertissement[];
}

export interface DepartementDisponibles {
  departement_id: number | null;
  departement_nom: string | null;
  departement_code: string | null;
  total: number;
  enseignants: EnseignantDisponible[];
}

export interface EnseignantsDisponiblesResponse {
  planification_id: number;
  date_planification: string;
  total_disponibles: number;
  total_avec_avertissement: number;
  departements: DepartementDisponibles[];
}

// ── Rapport ─────────────────────────────────────────────────────────────────

export interface ConflitGroupe {
  planification_id: number;
  type_epreuve: string;
  semestre: number;
  departement_examen: Departement;
  matiere: { id: number | null; code: string | null; intitule: string | null };
  section: { id: number | null; nom: string | null };
  creneau: Creneau;
  groupe: Groupe;
  salle: Salle;
  surveillants_requis: number;
  surveillants_trouves: number;
  manquants: number;
  statut_resolution: string;
}

export interface StatistiquesSession {
  total_planifications: number;
  completes: number;
  partielles: number;
  non_affectees: number;
  total_surveillances: number;
  total_presences: number;
  total_externes: number;
}

export interface RapportSession {
  session: { id: number; type_session: string; annee_univ: string; date_debut: string; date_fin: string; statut: string };
  statistiques: StatistiquesSession;
  planifications: any[];
  en_conflit: any[];
  classement_enseignants: any[];
  date_generation: string;
}
```

---

### Fonctions API

```typescript
// src/lib/api/surveillance.ts

import type {
  AffecterSessionRequest,
  AffecterSessionResponse,
  SurveillanceEnrichie,
  EnseignantsDisponiblesResponse,
  RapportSession,
  ConflitGroupe,
} from '@/types/surveillance';

const BASE = `${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/surveillances`;

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Erreur ${res.status}`);
  }
  return res.json();
}

// ── 1. Affectation automatique ───────────────────────────────────────────────

export async function affecterSession(
  data: AffecterSessionRequest
): Promise<AffecterSessionResponse> {
  const res = await fetch(`${BASE}/affecter-session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<AffecterSessionResponse>(res);
}

// ── 2. Affectation manuelle — planif unique ─────────────────────────────────

export async function affecterManuellementPlanif(data: {
  session_id: number;
  planification_id: number;
  groupe_id: number;
  salle_id: number;
  enseignant_ids: number[];
  motifs_externes?: Record<number, string>;
}): Promise<any> {
  const res = await fetch(`${BASE}/manual-assignment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

// ── 3. Affectation manuelle — batch ─────────────────────────────────────────

export async function affecterManuellementBatch(data: {
  session_id: number;
  affectations: {
    planification_id: number;
    groupe_id: number;
    salle_id: number;
    enseignant_ids: number[];
  }[];
  motifs_externes?: Record<number, string>;
}): Promise<any> {
  const res = await fetch(`${BASE}/manual-assignment-batch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

// ── 4. Profil enseignant ─────────────────────────────────────────────────────

export async function getProfilEnseignant(
  enseignantId: number,
  params?: {
    annee_universitaire?: string;
    semestre?: number;
    type_epreuve?: string;
  }
): Promise<any> {
  const q = new URLSearchParams();
  if (params?.annee_universitaire) q.set('annee_universitaire', params.annee_universitaire);
  if (params?.semestre)            q.set('semestre', String(params.semestre));
  if (params?.type_epreuve)        q.set('type_epreuve', params.type_epreuve);
  const res = await fetch(`${BASE}/enseignant/${enseignantId}/toutes-surveillances?${q}`);
  return handleResponse(res);
}

// ── 5. Tous les surveillants ─────────────────────────────────────────────────

export async function getAllSurveillants(params: {
  session_id: number;
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}): Promise<any> {
  const q = new URLSearchParams({ session_id: String(params.session_id) });
  if (params.page)  q.set('page',  String(params.page));
  if (params.limit) q.set('limit', String(params.limit));
  if (params.sort)  q.set('sort',  params.sort);
  if (params.order) q.set('order', params.order);
  const res = await fetch(`${BASE}/getallsurveillants?${q}`);
  return handleResponse(res);
}

// ── 6. Enseignants disponibles pour une planification ───────────────────────

export async function getEnseignantsDisponibles(
  planifId: number
): Promise<EnseignantsDisponiblesResponse> {
  const res = await fetch(`${BASE}/enseignants-disponibles/${planifId}`);
  return handleResponse<EnseignantsDisponiblesResponse>(res);
}

// ── 7. Liste surveillances session ──────────────────────────────────────────

export async function getSurveillancesSession(
  sessionId: number,
  params?: {
    departement_id?: number;
    groupe_id?: number;
    salle_id?: number;
    type_epreuve?: string;
    statut?: string;
    semestre?: number;
    section_id?: number;
    enseignant_id?: number;
    skip?: number;
    limit?: number;
  }
): Promise<{ session: any; total: number; skip: number; limit: number; data: SurveillanceEnrichie[] }> {
  const q = new URLSearchParams();
  if (params?.departement_id) q.set('departement_id', String(params.departement_id));
  if (params?.groupe_id)      q.set('groupe_id',      String(params.groupe_id));
  if (params?.salle_id)       q.set('salle_id',       String(params.salle_id));
  if (params?.type_epreuve)   q.set('type_epreuve',   params.type_epreuve);
  if (params?.statut)         q.set('statut',         params.statut);
  if (params?.semestre)       q.set('semestre',       String(params.semestre));
  if (params?.section_id)     q.set('section_id',     String(params.section_id));
  if (params?.enseignant_id)  q.set('enseignant_id',  String(params.enseignant_id));
  if (params?.skip  != null)  q.set('skip',           String(params.skip));
  if (params?.limit != null)  q.set('limit',          String(params.limit));
  const res = await fetch(`${BASE}/${sessionId}?${q}`);
  return handleResponse(res);
}

// ── 8. Détail complet d'une surveillance ────────────────────────────────────

export async function getSurveillanceDetail(
  surveillanceId: number
): Promise<SurveillanceEnrichie> {
  const res = await fetch(`${BASE}/${surveillanceId}/full-details`);
  return handleResponse<SurveillanceEnrichie>(res);
}

// ── 9. Modifier une surveillance ────────────────────────────────────────────

export async function modifierSurveillance(
  surveillanceId: number,
  payload: {
    presence?: boolean;
    statut_surveillance?: 'AFFECTE' | 'CONFIRME';
    charge?: number;
    motif_externe?: string;
  }
): Promise<SurveillanceEnrichie> {
  const res = await fetch(`${BASE}/edit/${surveillanceId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse<SurveillanceEnrichie>(res);
}

// ── 10. Remplacer un enseignant ──────────────────────────────────────────────

export async function reassignerSurveillance(
  surveillanceId: number,
  data: { nouvel_enseignant_id: number; motif?: string }
): Promise<any> {
  const res = await fetch(`${BASE}/${surveillanceId}/reassign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse(res);
}

// ── 11. Supprimer une surveillance ──────────────────────────────────────────

export async function supprimerSurveillance(surveillanceId: number): Promise<void> {
  const res = await fetch(`${BASE}/${surveillanceId}`, { method: 'DELETE' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Erreur ${res.status}`);
  }
}

// ── 12. Reset session ────────────────────────────────────────────────────────

export async function resetSession(sessionId: number): Promise<any> {
  const res = await fetch(`${BASE}/session/${sessionId}/reset`, { method: 'DELETE' });
  return handleResponse(res);
}

// ── 13. Rapport session ──────────────────────────────────────────────────────

export async function getRapportSession(
  sessionId: number,
  departementId?: number
): Promise<RapportSession> {
  const q = departementId ? `?departement_id=${departementId}` : '';
  const res = await fetch(`${BASE}/session/${sessionId}/rapport${q}`);
  return handleResponse<RapportSession>(res);
}

// ── 14. Conflits session ─────────────────────────────────────────────────────

export async function getConflitsSession(
  sessionId: number,
  params?: { semestre?: number; type_epreuve?: string; section_nom?: string }
): Promise<{ session_id: number; total_conflits: number; conflits: ConflitGroupe[] }> {
  const q = new URLSearchParams();
  if (params?.semestre)     q.set('semestre',     String(params.semestre));
  if (params?.type_epreuve) q.set('type_epreuve', params.type_epreuve);
  if (params?.section_nom)  q.set('section_nom',  params.section_nom);
  const res = await fetch(`${BASE}/session/${sessionId}/conflits?${q}`);
  return handleResponse(res);
}

// ── 15. Statistiques globales ────────────────────────────────────────────────

export async function getStatistiques(anneeUniv: string): Promise<any> {
  const res = await fetch(`${BASE}/statistiques?annee_univ=${encodeURIComponent(anneeUniv)}`);
  return handleResponse(res);
}

// ── 16. Disponibilités enseignant ────────────────────────────────────────────

export async function getDisponibilitesEnseignant(
  enseignantId: number,
  dateDebut: string,
  dateFin: string
): Promise<any> {
  const q = new URLSearchParams({ date_debut: dateDebut, date_fin: dateFin });
  const res = await fetch(`${BASE}/enseignant/${enseignantId}/disponibilites?${q}`);
  return handleResponse(res);
}
```

---

## 🎨 Composants React Recommandés

### 1. Composant Affectation Automatique

```typescript
// src/components/surveillance/AffectationAutoForm.tsx
'use client';

import { useState } from 'react';
import { affecterSession } from '@/lib/api/surveillance';
import type { AffecterSessionRequest, AffecterSessionResponse } from '@/types/surveillance';

interface Props {
  sessions:  { id: number; label: string }[];
  sections:  string[];
  periodes:  string[];
}

export default function AffectationAutoForm({ sessions, sections, periodes }: Props) {
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState<AffecterSessionResponse | null>(null);
  const [error,   setError]   = useState<string | null>(null);

  const [form, setForm] = useState<AffecterSessionRequest>({
    session_id: sessions[0]?.id,
    section_nom: sections[0] ?? '',
    periode: periodes[0] ?? '',
    type_epreuve: 'EXAMEN_FINAL',
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await affecterSession(form);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Affectation Automatique</h2>

      <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Session *</label>
          <select
            className="w-full border rounded px-3 py-2"
            value={form.session_id}
            onChange={e => setForm(f => ({ ...f, session_id: Number(e.target.value) }))}
          >
            {sessions.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Section *</label>
          <select
            className="w-full border rounded px-3 py-2"
            value={form.section_nom}
            onChange={e => setForm(f => ({ ...f, section_nom: e.target.value }))}
          >
            {sections.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Période *</label>
          <select
            className="w-full border rounded px-3 py-2"
            value={form.periode}
            onChange={e => setForm(f => ({ ...f, periode: e.target.value }))}
          >
            {periodes.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Type d'épreuve *</label>
          <select
            className="w-full border rounded px-3 py-2"
            value={form.type_epreuve}
            onChange={e => setForm(f => ({ ...f, type_epreuve: e.target.value as any }))}
          >
            <option value="EXAMEN_FINAL">Examen Final</option>
            <option value="DS">DS</option>
          </select>
        </div>

        <div className="col-span-2">
          <button
            type="submit"
            disabled={loading}
            className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Affectation en cours...' : '▶ Lancer l\'affectation automatique'}
          </button>
        </div>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4 text-red-800">{error}</div>
      )}

      {result && (
        <div className="space-y-4">
          {/* Résumé */}
          <div className="bg-green-50 border border-green-200 rounded p-4">
            <p className="font-semibold text-green-800">{result.message}</p>
            <div className="mt-2 grid grid-cols-3 gap-2 text-sm">
              <span>📊 Total : <strong>{result.total_planifications}</strong></span>
              <span>✅ Affectées : <strong>{result.affectees_automatiquement}</strong></span>
              <span>⚠️ Conflits : <strong>{result.en_conflit}</strong></span>
            </div>
          </div>

          {/* Résultats par planification */}
          {result.resultats.map(r => (
            <PlanifResultCard key={r.planification_id} result={r} />
          ))}

          {/* Non affectées */}
          {result.non_affectees.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded p-4">
              <h3 className="font-semibold text-red-800 mb-2">
                ❌ Planifications sans aucun surveillant ({result.non_affectees.length})
              </h3>
              {result.non_affectees.map(r => (
                <p key={r.planification_id} className="text-sm">
                  Planif #{r.planification_id} — {r.matiere?.intitule} | {r.creneau?.date}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function PlanifResultCard({ result }: { result: any }) {
  const isOk = result.statut === 'AFFECTEE';
  return (
    <div className={`border rounded p-4 ${isOk ? 'border-green-300 bg-green-50' : 'border-orange-300 bg-orange-50'}`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="font-semibold">
            {isOk ? '✅' : '⚠️'} Planif #{result.planification_id} — {result.matiere?.intitule}
          </p>
          <p className="text-sm text-gray-600">
            {result.section?.nom} | {result.type_epreuve} S{result.semestre} | {result.creneau?.date}
          </p>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${isOk ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'}`}>
          {result.surveillants_affectes}/{result.surveillants_requis} affectés
        </span>
      </div>

      {/* Groupes */}
      <div className="mt-3 space-y-2">
        {result.groupes?.map((g: any, i: number) => (
          <div key={i} className="bg-white rounded border p-2 text-sm">
            <p className="font-medium">
              Gr.{g.groupe?.numero} — Salle {g.salle?.code}
              {g.manquants > 0 && <span className="ml-2 text-red-600">({g.manquants} manquant(s))</span>}
            </p>
            {g.surveillants_affectes?.map((s: any, j: number) => (
              <p key={j} className="text-gray-600 ml-2">
                👤 {s.prenom} {s.nom} ({s.grade}) [{s.departement?.code}]
                — {s.charge}h
                {s.est_externe && <span className="ml-1 text-orange-600">⚠️ externe</span>}
              </p>
            ))}
          </div>
        ))}
      </div>

      {/* Exclusions */}
      {result.raisons_exclusion?.length > 0 && (
        <details className="mt-2">
          <summary className="text-xs text-gray-500 cursor-pointer">
            {result.raisons_exclusion.length} enseignant(s) écarté(s)
          </summary>
          <ul className="mt-1 text-xs text-gray-500 list-disc list-inside">
            {result.raisons_exclusion.map((r: any, i: number) => (
              <li key={i}>{r.prenom} {r.nom} → {r.raison}{r.details ? ` (${r.details})` : ''}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
```

### 2. Composant Sélecteur d'Enseignants Disponibles

```typescript
// src/components/surveillance/EnseignantPicker.tsx
'use client';

import { useState, useEffect } from 'react';
import { getEnseignantsDisponibles } from '@/lib/api/surveillance';
import type { EnseignantDisponible, DepartementDisponibles } from '@/types/surveillance';

interface Props {
  planifId: number;
  onSelect: (ids: number[]) => void;
}

export default function EnseignantPicker({ planifId, onSelect }: Props) {
  const [data,     setData]     = useState<any | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    getEnseignantsDisponibles(planifId)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [planifId]);

  function toggle(id: number) {
    setSelected(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      onSelect([...next]);
      return next;
    });
  }

  if (loading) return <p>Chargement des enseignants disponibles...</p>;
  if (!data)   return <p className="text-red-500">Planification introuvable.</p>;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold">
          Enseignants disponibles ({data.total_disponibles})
        </h3>
        {data.total_avec_avertissement > 0 && (
          <span className="text-xs text-orange-600">
            ⚠️ {data.total_avec_avertissement} avec indisponibilité ce jour
          </span>
        )}
      </div>

      {data.departements?.map((dept: DepartementDisponibles) => (
        <div key={dept.departement_id} className="border rounded p-3">
          <h4 className="font-medium text-sm mb-2">
            🏛️ {dept.departement_nom} ({dept.departement_code}) — {dept.total} enseignant(s)
          </h4>
          <div className="space-y-1">
            {dept.enseignants.map((ens: EnseignantDisponible) => (
              <label
                key={ens.enseignant_id}
                className={`flex items-center gap-3 p-2 rounded cursor-pointer hover:bg-gray-50 ${
                  selected.has(ens.enseignant_id) ? 'bg-indigo-50 border border-indigo-200' : ''
                }`}
              >
                <input
                  type="checkbox"
                  checked={selected.has(ens.enseignant_id)}
                  onChange={() => toggle(ens.enseignant_id)}
                />
                <div className="flex-1 text-sm">
                  <span className="font-medium">{ens.prenom} {ens.nom}</span>
                  <span className="text-gray-500 ml-1">({ens.grade})</span>
                  {ens.a_avertissement && (
                    <span className="ml-2 text-xs text-orange-600">⚠️ indispo. ce jour</span>
                  )}
                </div>
                <div className="text-xs text-gray-500 text-right">
                  <span className="font-medium text-green-600">{ens.volume_restant.toFixed(1)}h</span> restant
                  <br/>{ens.nb_surveillances} surv.
                </div>
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

### 3. Composant Tableau des Conflits

```typescript
// src/components/surveillance/ConflitsTable.tsx
'use client';

import { useState, useEffect } from 'react';
import { getConflitsSession } from '@/lib/api/surveillance';
import type { ConflitGroupe } from '@/types/surveillance';

export default function ConflitsTable({ sessionId }: { sessionId: number }) {
  const [conflits, setConflits] = useState<ConflitGroupe[]>([]);
  const [total,    setTotal]    = useState(0);
  const [loading,  setLoading]  = useState(true);
  const [filters,  setFilters]  = useState({ semestre: '', type_epreuve: '', section_nom: '' });

  useEffect(() => {
    setLoading(true);
    getConflitsSession(sessionId, {
      semestre:     filters.semestre     ? Number(filters.semestre)  : undefined,
      type_epreuve: filters.type_epreuve || undefined,
      section_nom:  filters.section_nom  || undefined,
    })
      .then(r => { setConflits(r.conflits); setTotal(r.total_conflits); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [sessionId, filters]);

  return (
    <div className="space-y-4">
      <div className="flex gap-3 items-center">
        <h2 className="text-xl font-bold">
          ⚠️ Conflits {total > 0 ? <span className="text-red-600">({total})</span> : <span className="text-green-600">(aucun)</span>}
        </h2>
        <select className="border rounded px-2 py-1 text-sm" value={filters.semestre}
          onChange={e => setFilters(f => ({ ...f, semestre: e.target.value }))}>
          <option value="">Tous sem.</option>
          <option value="1">S1</option>
          <option value="2">S2</option>
        </select>
        <select className="border rounded px-2 py-1 text-sm" value={filters.type_epreuve}
          onChange={e => setFilters(f => ({ ...f, type_epreuve: e.target.value }))}>
          <option value="">Tous types</option>
          <option value="EXAMEN_FINAL">Examen Final</option>
          <option value="DS">DS</option>
        </select>
        <input className="border rounded px-2 py-1 text-sm" placeholder="Section..."
          value={filters.section_nom}
          onChange={e => setFilters(f => ({ ...f, section_nom: e.target.value }))} />
      </div>

      {loading ? <p>Chargement...</p> : conflits.length === 0 ? (
        <p className="text-green-600">✅ Aucun conflit détecté.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="border px-3 py-2 text-left">Planif</th>
                <th className="border px-3 py-2 text-left">Matière</th>
                <th className="border px-3 py-2 text-left">Section</th>
                <th className="border px-3 py-2 text-left">Type</th>
                <th className="border px-3 py-2 text-left">Date / Horaire</th>
                <th className="border px-3 py-2 text-left">Groupe</th>
                <th className="border px-3 py-2 text-left">Salle</th>
                <th className="border px-3 py-2 text-center">Requis</th>
                <th className="border px-3 py-2 text-center">Trouvés</th>
                <th className="border px-3 py-2 text-center">Manquants</th>
              </tr>
            </thead>
            <tbody>
              {conflits.map((c, i) => (
                <tr key={i} className="hover:bg-red-50">
                  <td className="border px-3 py-2">#{c.planification_id}</td>
                  <td className="border px-3 py-2 font-medium">{c.matiere.code}</td>
                  <td className="border px-3 py-2">{c.section.nom}</td>
                  <td className="border px-3 py-2">{c.type_epreuve}</td>
                  <td className="border px-3 py-2">
                    {c.creneau.date}<br/>
                    <span className="text-xs text-gray-500">
                      {c.creneau.heure_debut?.slice(0,5)}–{c.creneau.heure_fin?.slice(0,5)}
                    </span>
                  </td>
                  <td className="border px-3 py-2">Gr.{c.groupe?.numero}</td>
                  <td className="border px-3 py-2">{c.salle?.code}</td>
                  <td className="border px-3 py-2 text-center">{c.surveillants_requis}</td>
                  <td className="border px-3 py-2 text-center">{c.surveillants_trouves}</td>
                  <td className="border px-3 py-2 text-center font-bold text-red-600">
                    ❌ {c.manquants}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
```

### 4. Composant Fiche Surveillance (modifier / confirmer / présence)

```typescript
// src/components/surveillance/SurveillanceFiche.tsx
'use client';

import { useState } from 'react';
import { modifierSurveillance, reassignerSurveillance, supprimerSurveillance } from '@/lib/api/surveillance';
import type { SurveillanceEnrichie } from '@/types/surveillance';

export default function SurveillanceFiche({
  data,
  onUpdated,
}: {
  data: SurveillanceEnrichie;
  onUpdated: () => void;
}) {
  const [loading, setLoading] = useState(false);
  const sv = data.surveillance;
  const ens = data.enseignant;

  async function confirmer() {
    setLoading(true);
    try {
      await modifierSurveillance(sv.id, { statut_surveillance: 'CONFIRME' });
      onUpdated();
    } finally { setLoading(false); }
  }

  async function marquerPresence(present: boolean) {
    setLoading(true);
    try {
      await modifierSurveillance(sv.id, { presence: present });
      onUpdated();
    } finally { setLoading(false); }
  }

  async function supprimer() {
    if (!confirm('Supprimer cette surveillance ?')) return;
    setLoading(true);
    try {
      await supprimerSurveillance(sv.id);
      onUpdated();
    } finally { setLoading(false); }
  }

  const pct = ens.volume_horaire > 0 ? (ens.volume_consomme / ens.volume_horaire * 100) : 0;

  return (
    <div className="border rounded-lg p-4 space-y-3">
      {/* En-tête */}
      <div className="flex justify-between items-start">
        <div>
          <p className="font-semibold text-lg">{ens.nom_complet}</p>
          <p className="text-sm text-gray-600">{ens.grade} — {ens.departement.nom}</p>
        </div>
        <div className="flex gap-2">
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            sv.statut_surveillance === 'CONFIRME' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
          }`}>
            {sv.statut_surveillance}
          </span>
          <span className={`px-2 py-1 rounded text-xs ${
            sv.presence ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
          }`}>
            {sv.presence ? '✅ Présent' : '❌ Absent'}
          </span>
        </div>
      </div>

      {/* Volume horaire */}
      <div>
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Volume consommé</span>
          <span>{ens.volume_consomme.toFixed(1)}h / {ens.volume_horaire.toFixed(1)}h ({pct.toFixed(0)}%)</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full">
          <div
            className={`h-2 rounded-full ${pct > 90 ? 'bg-red-500' : pct > 70 ? 'bg-orange-500' : 'bg-green-500'}`}
            style={{ width: `${Math.min(pct, 100)}%` }}
          />
        </div>
      </div>

      {/* Détails examen */}
      <div className="text-sm grid grid-cols-2 gap-1">
        <span className="text-gray-500">Matière :</span>
        <span>{data.matiere.intitule} ({data.matiere.code})</span>
        <span className="text-gray-500">Créneau :</span>
        <span>{data.creneau.date} {data.creneau.heure_debut?.slice(0,5)}–{data.creneau.heure_fin?.slice(0,5)}</span>
        <span className="text-gray-500">Groupe / Salle :</span>
        <span>Gr.{data.groupe.numero} — {data.salle.code}</span>
        <span className="text-gray-500">Charge :</span>
        <span>{sv.charge}h {sv.est_externe && <span className="text-orange-600">(externe)</span>}</span>
      </div>

      {/* Actions */}
      <div className="flex gap-2 flex-wrap">
        {sv.statut_surveillance !== 'CONFIRME' && (
          <button onClick={confirmer} disabled={loading}
            className="bg-green-600 text-white text-xs px-3 py-1 rounded hover:bg-green-700 disabled:opacity-50">
            ✅ Confirmer
          </button>
        )}
        <button onClick={() => marquerPresence(!sv.presence)} disabled={loading}
          className="bg-blue-600 text-white text-xs px-3 py-1 rounded hover:bg-blue-700 disabled:opacity-50">
          {sv.presence ? '❌ Marquer absent' : '✅ Marquer présent'}
        </button>
        <button onClick={supprimer} disabled={loading}
          className="bg-red-600 text-white text-xs px-3 py-1 rounded hover:bg-red-700 disabled:opacity-50">
          🗑️ Supprimer
        </button>
      </div>
    </div>
  );
}
```

---

## 🎨 Design — Couleurs et Conventions

### Statuts de surveillance

```css
/* AFFECTE */
.statut-affecte  { background: #fef3c7; color: #92400e; } /* yellow */

/* CONFIRME */
.statut-confirme { background: #dcfce7; color: #166534; } /* green */
```

### Présence

```css
.present { background: #dbeafe; color: #1e40af; }  /* blue */
.absent  { background: #f3f4f6; color: #6b7280; }  /* gray */
```

### Statuts de conflit

```css
.conflit-ok      { background: #dcfce7; border-left: 4px solid #16a34a; }
.conflit-partiel { background: #fef9c3; border-left: 4px solid #ca8a04; }
.conflit-total   { background: #fee2e2; border-left: 4px solid #dc2626; }
```

### Volume horaire (barre de progression)

```css
.volume-ok      { background: #22c55e; }  /* < 70% — vert */
.volume-warning { background: #f97316; }  /* 70–90% — orange */
.volume-danger  { background: #ef4444; }  /* > 90% — rouge */
```

---

## ✅ Checklist d'Intégration

- [ ] Configurer `NEXT_PUBLIC_API_URL` dans `.env.local`
- [ ] Créer `src/types/surveillance.ts` avec tous les types
- [ ] Créer `src/lib/api/surveillance.ts` avec toutes les fonctions
- [ ] Page affectation automatique avec sélecteurs session/section/période/type
- [ ] Page affectation manuelle avec `EnseignantPicker`
- [ ] Page liste surveillances avec tous les filtres (7 paramètres)
- [ ] Page rapport session avec statistiques + classement enseignants
- [ ] Tableau des conflits par groupe/salle avec filtres
- [ ] Fiche surveillance avec actions (confirmer, présence, supprimer, remplacer)
- [ ] Profil enseignant avec charge horaire et barre de progression
- [ ] Gestion des erreurs (409 conflit, 404 non trouvé)
- [ ] États de chargement sur toutes les actions
- [ ] Responsive mobile

---

**🎨 Bon développement !**