# 🎨 Guide P3 - Intégration Frontend Planification

## 📋 Vue d'Ensemble

Ce guide est destiné à l'équipe P3 (Frontend) pour intégrer la planification automatique des examens dans l'interface Next.js.

**Objectif** : Créer une interface utilisateur pour gérer la planification des examens en utilisant l'API backend.

---

## 🎯 Fonctionnalités à Implémenter

### 1. Page de Planification (`/planification`)

#### Vue Liste
- ✅ Afficher toutes les planifications d'une session
- ✅ Filtrer par section, type d'épreuve, statut
- ✅ Trier par date, heure, matière
- ✅ Actions : Modifier, Supprimer, Valider, Publier

#### Vue Calendrier/Emploi du Temps
- ✅ Affichage en grille (jours × créneaux)
- ✅ Couleurs par section ou type d'épreuve
- ✅ Tooltip avec détails au survol
- ✅ Drag & drop pour modifier (optionnel)

### 2. Page de Génération Automatique (`/planification/generer`)

#### Formulaire de Génération
- ✅ Sélection de la session
- ✅ Sélection des sections à planifier
- ✅ Sélection du type d'épreuve
- ✅ Aperçu des créneaux et salles disponibles
- ✅ Bouton "Générer"

#### Résultats de Génération
- ✅ Nombre de planifications créées
- ✅ Liste des conflits (si présents)
- ✅ Aperçu de l'emploi du temps généré
- ✅ Actions : Valider, Régénérer, Modifier

### 3. Page de Détail (`/planification/[id]`)

#### Informations
- ✅ Matière, section, type d'épreuve
- ✅ Date, heure, durée
- ✅ Salles affectées avec capacités
- ✅ Nombre de groupes
- ✅ Statut

#### Actions
- ✅ Modifier la date/heure
- ✅ Changer les salles
- ✅ Valider/Publier
- ✅ Supprimer

---

## 🔌 Intégration API

### Configuration

Créer un fichier `src/lib/api/planification.ts` :

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const planificationApi = {
  baseUrl: `${API_BASE_URL}/api`,
  
  // Endpoints
  endpoints: {
    list: '/planifications',
    detail: (id: number) => `/planifications/${id}`,
    create: '/planifications',
    update: (id: number) => `/planifications/${id}`,
    delete: (id: number) => `/planifications/${id}`,
    generate: (sessionId: number) => `/sessions/${sessionId}/generer`,
    emploiDuTemps: (sessionId: number) => `/sessions/${sessionId}/emploi-du-temps`,
    validate: (id: number) => `/planifications/${id}/valider`,
    publish: (id: number) => `/planifications/${id}/publier`,
    assignRooms: (id: number) => `/planifications/${id}/salles`,
  }
};
```

### Fonctions API

```typescript
// src/lib/api/planification.ts

import { planificationApi } from './config';

export interface Planification {
  id: number;
  session_id: number;
  section_id: number;
  section_matiere_id: number;
  type_epreuve: 'EXAMEN_FINAL' | 'DS' | 'RATTRAPAGE';
  date_examen: string;
  heure_debut: string;
  heure_fin: string;
  duree: number;
  statut: 'BROUILLON' | 'VALIDEE' | 'PUBLIEE';
  nb_groupes: number;
  salles: PlanifSalle[];
  matiere?: Matiere;
  section?: Section;
}

export interface PlanifSalle {
  id: number;
  salle_id: string;
  salle_code: string;
  salle_designation: string;
  salle_capacite: number;
  groupe_numero: number;
  groupe_effectif: number;
}

// 1. Lister les planifications
export async function getPlanifications(params?: {
  session_id?: number;
  section_id?: number;
  type_epreuve?: string;
  statut?: string;
}): Promise<Planification[]> {
  const queryParams = new URLSearchParams();
  if (params?.session_id) queryParams.append('session_id', params.session_id.toString());
  if (params?.section_id) queryParams.append('section_id', params.section_id.toString());
  if (params?.type_epreuve) queryParams.append('type_epreuve', params.type_epreuve);
  if (params?.statut) queryParams.append('statut', params.statut);
  
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.list}?${queryParams}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Erreur ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
}

// 2. Récupérer une planification
export async function getPlanification(id: number): Promise<Planification> {
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.detail(id)}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Erreur ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
}

// 3. Créer une planification
export async function createPlanification(data: Partial<Planification>): Promise<Planification> {
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.create}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Erreur ${response.status}`);
  }
  
  return response.json();
}

// 4. Mettre à jour une planification
export async function updatePlanification(id: number, data: Partial<Planification>): Promise<Planification> {
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.update(id)}`;
  const response = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Erreur ${response.status}`);
  }
  
  return response.json();
}

// 5. Supprimer une planification
export async function deletePlanification(id: number): Promise<void> {
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.delete(id)}`;
  const response = await fetch(url, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Erreur ${response.status}`);
  }
}

// 6. Générer automatiquement (⭐ PRINCIPAL)
export async function generatePlanifications(sessionId: number, data: GenerationRequest): Promise<GenerationResponse> {
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.generate(sessionId)}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Erreur ${response.status}`);
  }
  
  return response.json();
}

// 7. Récupérer l'emploi du temps
export async function getEmploiDuTemps(sessionId: number, params?: {
  section_id?: number;
  type_epreuve?: string;
}): Promise<EmploiDuTemps[]> {
  const queryParams = new URLSearchParams();
  if (params?.section_id) queryParams.append('section_id', params.section_id.toString());
  if (params?.type_epreuve) queryParams.append('type_epreuve', params.type_epreuve);
  
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.emploiDuTemps(sessionId)}?${queryParams}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Erreur ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
}

// 8. Valider une planification
export async function validatePlanification(id: number): Promise<Planification> {
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.validate(id)}`;
  const response = await fetch(url, {
    method: 'POST',
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Erreur ${response.status}`);
  }
  
  return response.json();
}

// 9. Publier une planification
export async function publishPlanification(id: number): Promise<Planification> {
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.publish(id)}`;
  const response = await fetch(url, {
    method: 'POST',
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Erreur ${response.status}`);
  }
  
  return response.json();
}

// 10. Affecter des salles
export async function assignRooms(id: number, salles: PlanifSalle[]): Promise<Planification> {
  const url = `${planificationApi.baseUrl}${planificationApi.endpoints.assignRooms(id)}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ salles }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || `Erreur ${response.status}`);
  }
  
  return response.json();
}
```

---

## 🎨 Composants React Recommandés

### 1. Composant Liste de Planifications

```typescript
// src/components/planification/PlanificationList.tsx

'use client';

import { useState, useEffect } from 'react';
import { getPlanifications, deletePlanification } from '@/lib/api/planification';
import type { Planification } from '@/lib/api/planification';

export default function PlanificationList({ sessionId }: { sessionId: number }) {
  const [planifications, setPlanifications] = useState<Planification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPlanifications();
  }, [sessionId]);

  async function loadPlanifications() {
    try {
      setLoading(true);
      const data = await getPlanifications({ session_id: sessionId });
      setPlanifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de chargement');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Supprimer cette planification ?')) return;
    
    try {
      await deletePlanification(id);
      await loadPlanifications(); // Recharger
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Erreur de suppression');
    }
  }

  if (loading) return <div>Chargement...</div>;
  if (error) return <div className="text-red-500">Erreur : {error}</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Planifications</h2>
      
      <div className="grid gap-4">
        {planifications.map((planif) => (
          <div key={planif.id} className="border rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-semibold">{planif.matiere?.intitule}</h3>
                <p className="text-sm text-gray-600">
                  {planif.section?.nom} - {planif.type_epreuve}
                </p>
                <p className="text-sm">
                  📅 {planif.date_examen} | ⏰ {planif.heure_debut} - {planif.heure_fin}
                </p>
                <p className="text-sm">
                  🏛️ {planif.salles.map(s => s.salle_code).join(', ')}
                </p>
              </div>
              
              <div className="flex gap-2">
                <span className={`px-2 py-1 rounded text-xs ${
                  planif.statut === 'PUBLIEE' ? 'bg-green-100 text-green-800' :
                  planif.statut === 'VALIDEE' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {planif.statut}
                </span>
                
                <button
                  onClick={() => handleDelete(planif.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  Supprimer
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 2. Composant Génération Automatique

```typescript
// src/components/planification/GenerationForm.tsx

'use client';

import { useState } from 'react';
import { generatePlanifications } from '@/lib/api/planification';
import type { GenerationRequest, GenerationResponse } from '@/lib/api/planification';

export default function GenerationForm({ sessionId }: { sessionId: number }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    
    const formData = new FormData(e.currentTarget);
    
    // Construire la requête (simplifié)
    const request: GenerationRequest = {
      session_id: sessionId,
      session_date_debut: formData.get('date_debut') as string,
      session_date_fin: formData.get('date_fin') as string,
      session_statut: 'BROUILLON',
      mode: 'AUTO',
      tasks: [], // À remplir avec les matières sélectionnées
      creneaux: [], // À charger depuis l'API
      salles: [], // À charger depuis l'API
    };

    try {
      setLoading(true);
      setError(null);
      const response = await generatePlanifications(sessionId, request);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de génération');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Génération Automatique</h2>
      
      <form onSubmit={handleGenerate} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            Date de début
          </label>
          <input
            type="date"
            name="date_debut"
            required
            className="w-full border rounded px-3 py-2"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">
            Date de fin
          </label>
          <input
            type="date"
            name="date_fin"
            required
            className="w-full border rounded px-3 py-2"
          />
        </div>
        
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Génération en cours...' : 'Générer'}
        </button>
      </form>
      
      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}
      
      {result && (
        <div className="bg-green-50 border border-green-200 rounded p-4">
          <h3 className="font-semibold text-green-800 mb-2">Résultat</h3>
          <p>✅ Planifications créées : {result.nb_crees}</p>
          <p>⚠️ Conflits détectés : {result.nb_conflits}</p>
          
          {result.conflits.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium">Conflits :</h4>
              <ul className="list-disc list-inside text-sm">
                {result.conflits.map((conflit, i) => (
                  <li key={i}>{conflit}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 3. Composant Emploi du Temps

```typescript
// src/components/planification/EmploiDuTemps.tsx

'use client';

import { useState, useEffect } from 'react';
import { getEmploiDuTemps } from '@/lib/api/planification';
import type { EmploiDuTemps } from '@/lib/api/planification';

export default function EmploiDuTempsView({ sessionId }: { sessionId: number }) {
  const [emploi, setEmploi] = useState<EmploiDuTemps[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEmploi();
  }, [sessionId]);

  async function loadEmploi() {
    try {
      setLoading(true);
      const data = await getEmploiDuTemps(sessionId);
      setEmploi(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Chargement...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Emploi du Temps</h2>
      
      {emploi.map((jour) => (
        <div key={jour.date_examen} className="border rounded-lg p-4">
          <h3 className="font-semibold text-lg mb-4">
            📅 {new Date(jour.date_examen).toLocaleDateString('fr-FR', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}
          </h3>
          
          <div className="space-y-3">
            {jour.examens.map((examen, i) => (
              <div key={i} className="bg-gray-50 rounded p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">
                      ⏰ {examen.heure_debut} - {examen.heure_fin}
                    </p>
                    <p className="text-lg">{examen.matiere}</p>
                    <p className="text-sm text-gray-600">
                      {examen.section} - {examen.type_epreuve}
                    </p>
                    <p className="text-sm">
                      🏛️ {examen.salles.map(s => 
                        `${s.code} (${s.effectif}/${s.capacite})`
                      ).join(', ')}
                    </p>
                  </div>
                  
                  <span className={`px-2 py-1 rounded text-xs ${
                    examen.statut === 'PUBLIEE' ? 'bg-green-100 text-green-800' :
                    examen.statut === 'VALIDEE' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {examen.statut}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 🎨 Design Recommandations

### Couleurs par Statut

```css
/* BROUILLON */
.status-brouillon {
  background: #f3f4f6; /* gray-100 */
  color: #374151; /* gray-800 */
}

/* VALIDEE */
.status-validee {
  background: #dbeafe; /* blue-100 */
  color: #1e40af; /* blue-800 */
}

/* PUBLIEE */
.status-publiee {
  background: #dcfce7; /* green-100 */
  color: #166534; /* green-800 */
}
```

### Couleurs par Type d'Épreuve

```css
/* EXAMEN_FINAL */
.type-examen-final {
  background: #fef3c7; /* yellow-100 */
  border-left: 4px solid #f59e0b; /* yellow-500 */
}

/* DS */
.type-ds {
  background: #e0e7ff; /* indigo-100 */
  border-left: 4px solid #6366f1; /* indigo-500 */
}

/* RATTRAPAGE */
.type-rattrapage {
  background: #fce7f3; /* pink-100 */
  border-left: 4px solid #ec4899; /* pink-500 */
}
```

---

## 🧪 Tests Recommandés

### Test 1 : Charger les Planifications

```typescript
// Test dans la console du navigateur
import { getPlanifications } from '@/lib/api/planification';

const planifs = await getPlanifications({ session_id: 1 });
console.log('Planifications:', planifs);
```

### Test 2 : Générer Automatiquement

```typescript
import { generatePlanifications } from '@/lib/api/planification';

const result = await generatePlanifications(1, {
  session_id: 1,
  session_date_debut: '2026-01-07',
  session_date_fin: '2026-01-15',
  session_statut: 'BROUILLON',
  mode: 'AUTO',
  tasks: [...],
  creneaux: [...],
  salles: [...]
});

console.log('Résultat:', result);
```

---

## 📞 Support Backend

### Endpoints Disponibles

- **Documentation Swagger** : http://127.0.0.1:8000/docs
- **Documentation ReDoc** : http://127.0.0.1:8000/redoc
- **Health Check** : http://127.0.0.1:8000/health

### Contact

- **Documentation API** : `docs/api/API_PLANIFICATION.md`
- **Exemples** : Voir la documentation Swagger

---

## ✅ Checklist d'Intégration

- [ ] Configurer `NEXT_PUBLIC_API_URL` dans `.env.local`
- [ ] Créer `src/lib/api/planification.ts` avec toutes les fonctions
- [ ] Créer les types TypeScript pour les modèles
- [ ] Implémenter le composant `PlanificationList`
- [ ] Implémenter le composant `GenerationForm`
- [ ] Implémenter le composant `EmploiDuTempsView`
- [ ] Ajouter la gestion des erreurs
- [ ] Ajouter les états de chargement
- [ ] Tester avec l'API backend
- [ ] Ajouter les validations de formulaire
- [ ] Implémenter la pagination (si nécessaire)
- [ ] Ajouter les filtres et recherche
- [ ] Tester sur mobile (responsive)

---

**🎨 Bon développement frontend !**
