# 📅 P3 - Affichage de l'Emploi du Temps

## 🎯 Objectif

Créer une interface frontend pour **afficher l'emploi du temps** généré automatiquement par l'algorithme de planification (P1).

## 📋 Fonctionnalités

### Vue Principale
- ✅ Affichage de l'emploi du temps sous forme de grille
- ✅ Filtrage par session, section, type d'épreuve
- ✅ Vue par jour, semaine, ou période complète
- ✅ Codes couleur par matière ou section
- ✅ Export PDF de l'emploi du temps

### Détails des Examens
- ✅ Matière et type d'épreuve (DS/Examen Final)
- ✅ Date et horaires (début - fin)
- ✅ Salles affectées avec capacités
- ✅ Nombre de groupes et effectifs
- ✅ Surveillants requis
- ✅ Statut (Brouillon/Validé/Publié)

### Actions Disponibles
- ✅ Voir les détails d'un examen
- ✅ Modifier une planification
- ✅ Valider/Publier un emploi du temps
- ✅ Détecter les conflits
- ✅ Régénérer si nécessaire

## 🏗️ Architecture

### Structure des Composants

```
src/
├── app/
│   └── (admin)/
│       └── emploi-du-temps/
│           ├── page.tsx                    # Page principale
│           └── [session_id]/
│               └── page.tsx                # Emploi du temps par session
│
├── components/
│   └── emploi-du-temps/
│       ├── EmploiDuTempsGrid.tsx          # Grille principale
│       ├── EmploiDuTempsFilters.tsx       # Filtres
│       ├── ExamenCard.tsx                 # Carte d'examen
│       ├── ExamenDetails.tsx              # Détails d'un examen
│       ├── ConflictAlert.tsx              # Alerte de conflit
│       └── ExportButton.tsx               # Export PDF
│
├── lib/
│   ├── api/
│   │   └── emploi-du-temps.ts             # API calls
│   ├── types/
│   │   └── emploi-du-temps.ts             # Types TypeScript
│   └── utils/
│       ├── calendar.ts                     # Utilitaires calendrier
│       └── colors.ts                       # Codes couleur
│
└── hooks/
    └── useEmploiDuTemps.ts                # Hook personnalisé
```

## 📊 API Endpoints Utilisés

### 1. Récupérer l'Emploi du Temps

```typescript
GET /api/sessions/{session_id}/emploi-du-temps

Query Parameters:
- section_id?: number
- type_epreuve?: "EXAMEN_FINAL" | "DS"
- statut?: "BROUILLON" | "VALIDEE" | "PUBLIEE"

Response: Planification[]
```

### 2. Récupérer une Planification

```typescript
GET /api/planifications/{id}

Response: Planification
```

### 3. Mettre à Jour une Planification

```typescript
PUT /api/planifications/{id}

Body: PlanificationUpdatePayload

Response: Planification
```

### 4. Valider une Planification

```typescript
POST /api/planifications/{id}/valider

Response: Planification
```

### 5. Publier une Planification

```typescript
POST /api/planifications/{id}/publier

Response: Planification
```

## 🎨 Design de l'Interface

### 1. Grille de l'Emploi du Temps

```
┌─────────────────────────────────────────────────────────────┐
│  Emploi du Temps - Session Normale Juin 2026                │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ Filtres: │ Section  │ Type     │ Statut   │ Export   │  │
│  │          │ [Tous]▼  │ [Tous]▼  │ [Tous]▼  │ [PDF]    │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
│                                                               │
│  ┌─────────┬──────────────────────────────────────────────┐ │
│  │ Heure   │ Lundi 02/06  │ Mardi 03/06  │ Mercredi 04/06│ │
│  ├─────────┼──────────────┼──────────────┼───────────────┤ │
│  │ 08:30   │ ┌──────────┐ │ ┌──────────┐ │               │ │
│  │   -     │ │ Algo Av. │ │ │ Base DD  │ │               │ │
│  │ 10:30   │ │ INFO-L3-A│ │ │ INFO-L3-A│ │               │ │
│  │         │ │ S20A,S20B│ │ │ S20A,S20B│ │               │ │
│  │         │ └──────────┘ │ └──────────┘ │               │ │
│  ├─────────┼──────────────┼──────────────┼───────────────┤ │
│  │ 11:00   │              │              │ ┌──────────┐  │ │
│  │   -     │              │              │ │ Systèmes │  │ │
│  │ 13:00   │              │              │ │ INFO-L3-B│  │ │
│  │         │              │              │ │ S30      │  │ │
│  │         │              │              │ └──────────┘  │ │
│  └─────────┴──────────────┴──────────────┴───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2. Carte d'Examen

```
┌─────────────────────────────────────────┐
│ 🎓 Algorithmique Avancée               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                         │
│ 📅 Lundi 02 Juin 2026                  │
│ ⏰ 08:30 - 10:30 (120 min)             │
│                                         │
│ 👥 Section: INFO-L3-A (35 étudiants)   │
│ 📝 Type: Examen Final                  │
│                                         │
│ 🏢 Salles:                              │
│   • S20A (Groupe 1: 18 étudiants)      │
│   • S20B (Groupe 2: 17 étudiants)      │
│                                         │
│ 👨‍🏫 Surveillants requis: 2              │
│                                         │
│ ✅ Statut: Validée                      │
│                                         │
│ [Détails] [Modifier] [Valider]         │
└─────────────────────────────────────────┘
```

### 3. Codes Couleur

| Statut | Couleur | Description |
|--------|---------|-------------|
| BROUILLON | 🟡 Jaune | En cours de planification |
| VALIDEE | 🟢 Vert | Validée par l'admin |
| PUBLIEE | 🔵 Bleu | Publiée aux étudiants |

| Type | Couleur | Description |
|------|---------|-------------|
| EXAMEN_FINAL | 🔴 Rouge clair | Examen final |
| DS | 🟠 Orange | Devoir surveillé |

## 💻 Implémentation

### 1. Types TypeScript

```typescript
// lib/types/emploi-du-temps.ts

export type EmploiDuTempsFilters = {
  session_id: number;
  section_id?: number;
  type_epreuve?: "EXAMEN_FINAL" | "DS";
  statut?: "BROUILLON" | "VALIDEE" | "PUBLIEE";
};

export type EmploiDuTempsView = "day" | "week" | "period";

export type TimeSlot = {
  date: string;
  heure_debut: string;
  heure_fin: string;
  examens: Planification[];
};

export type EmploiDuTempsData = {
  session: {
    id: number;
    date_debut: string;
    date_fin: string;
  };
  planifications: Planification[];
  timeSlots: TimeSlot[];
};
```

### 2. Hook Personnalisé

```typescript
// hooks/useEmploiDuTemps.ts

import { useState, useEffect } from "react";
import { getEmploiDuTemps } from "@/lib/api/emploi-du-temps";
import type { EmploiDuTempsFilters, EmploiDuTempsData } from "@/lib/types/emploi-du-temps";

export function useEmploiDuTemps(filters: EmploiDuTempsFilters) {
  const [data, setData] = useState<EmploiDuTempsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const planifications = await getEmploiDuTemps(
          filters.session_id,
          {
            section_id: filters.section_id,
            type_epreuve: filters.type_epreuve,
            statut: filters.statut,
          }
        );

        // Organiser par créneaux
        const timeSlots = organizeByTimeSlots(planifications);

        setData({
          session: {
            id: filters.session_id,
            date_debut: planifications[0]?.session_date_debut || "",
            date_fin: planifications[0]?.session_date_fin || "",
          },
          planifications,
          timeSlots,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur inconnue");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [filters]);

  return { data, loading, error };
}

function organizeByTimeSlots(planifications: Planification[]): TimeSlot[] {
  const slotsMap = new Map<string, TimeSlot>();

  planifications.forEach((planif) => {
    const key = `${planif.date_examen}_${planif.heure_debut}_${planif.heure_fin}`;
    
    if (!slotsMap.has(key)) {
      slotsMap.set(key, {
        date: planif.date_examen,
        heure_debut: planif.heure_debut,
        heure_fin: planif.heure_fin,
        examens: [],
      });
    }

    slotsMap.get(key)!.examens.push(planif);
  });

  return Array.from(slotsMap.values()).sort((a, b) => {
    const dateCompare = a.date.localeCompare(b.date);
    if (dateCompare !== 0) return dateCompare;
    return a.heure_debut.localeCompare(b.heure_debut);
  });
}
```

### 3. Composant Principal

```typescript
// components/emploi-du-temps/EmploiDuTempsGrid.tsx

"use client";

import { useState } from "react";
import { useEmploiDuTemps } from "@/hooks/useEmploiDuTemps";
import { EmploiDuTempsFilters } from "./EmploiDuTempsFilters";
import { ExamenCard } from "./ExamenCard";
import { ExportButton } from "./ExportButton";
import type { EmploiDuTempsFilters as Filters } from "@/lib/types/emploi-du-temps";

interface Props {
  sessionId: number;
}

export function EmploiDuTempsGrid({ sessionId }: Props) {
  const [filters, setFilters] = useState<Filters>({
    session_id: sessionId,
  });

  const { data, loading, error } = useEmploiDuTemps(filters);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Erreur: {error}</p>
      </div>
    );
  }

  if (!data || data.planifications.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
        <p className="text-yellow-800 text-lg">
          Aucun examen planifié pour cette session.
        </p>
        <p className="text-yellow-600 mt-2">
          Utilisez la génération automatique pour créer l'emploi du temps.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Emploi du Temps
          </h1>
          <p className="text-gray-600 mt-1">
            Session du {formatDate(data.session.date_debut)} au{" "}
            {formatDate(data.session.date_fin)}
          </p>
        </div>
        <ExportButton data={data} />
      </div>

      {/* Filtres */}
      <EmploiDuTempsFilters
        filters={filters}
        onFiltersChange={setFilters}
      />

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Examens"
          value={data.planifications.length}
          icon="📝"
        />
        <StatCard
          label="Brouillon"
          value={countByStatus(data.planifications, "BROUILLON")}
          icon="🟡"
        />
        <StatCard
          label="Validés"
          value={countByStatus(data.planifications, "VALIDEE")}
          icon="🟢"
        />
        <StatCard
          label="Publiés"
          value={countByStatus(data.planifications, "PUBLIEE")}
          icon="🔵"
        />
      </div>

      {/* Grille des examens */}
      <div className="space-y-6">
        {data.timeSlots.map((slot, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-4 mb-4 pb-4 border-b border-gray-200">
              <div className="text-lg font-semibold text-gray-900">
                📅 {formatDate(slot.date)}
              </div>
              <div className="text-gray-600">
                ⏰ {slot.heure_debut} - {slot.heure_fin}
              </div>
              <div className="ml-auto text-sm text-gray-500">
                {slot.examens.length} examen(s)
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {slot.examens.map((examen) => (
                <ExamenCard key={examen.id} examen={examen} />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StatCard({ label, value, icon }: { label: string; value: number; icon: string }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <p className="text-sm text-gray-600">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );
}

function countByStatus(planifications: Planification[], status: string): number {
  return planifications.filter((p) => p.statut === status).length;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("fr-FR", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
```

### 4. Carte d'Examen

```typescript
// components/emploi-du-temps/ExamenCard.tsx

"use client";

import { useState } from "react";
import type { Planification } from "@/lib/types/planification";
import { ExamenDetails } from "./ExamenDetails";

interface Props {
  examen: Planification;
}

export function ExamenCard({ examen }: Props) {
  const [showDetails, setShowDetails] = useState(false);

  const statusColors = {
    BROUILLON: "bg-yellow-100 text-yellow-800 border-yellow-300",
    VALIDEE: "bg-green-100 text-green-800 border-green-300",
    PUBLIEE: "bg-blue-100 text-blue-800 border-blue-300",
  };

  const typeColors = {
    EXAMEN_FINAL: "bg-red-50 border-red-200",
    DS: "bg-orange-50 border-orange-200",
  };

  return (
    <>
      <div
        className={`rounded-lg border-2 p-4 cursor-pointer hover:shadow-md transition-shadow ${
          typeColors[examen.type_epreuve]
        }`}
        onClick={() => setShowDetails(true)}
      >
        {/* En-tête */}
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-semibold text-gray-900 text-sm line-clamp-2">
            {examen.matiere}
          </h3>
          <span
            className={`px-2 py-1 rounded text-xs font-medium border ${
              statusColors[examen.statut]
            }`}
          >
            {examen.statut}
          </span>
        </div>

        {/* Informations */}
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <span>📝</span>
            <span>{examen.type_epreuve === "EXAMEN_FINAL" ? "Examen Final" : "DS"}</span>
          </div>

          <div className="flex items-center gap-2">
            <span>⏰</span>
            <span>
              {examen.heure_debut} - {examen.heure_fin}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span>👥</span>
            <span>{examen.section_nb_etudiants} étudiants</span>
          </div>

          <div className="flex items-center gap-2">
            <span>🏢</span>
            <span>
              {examen.nb_groupes} groupe(s) - {examen.salles.length} salle(s)
            </span>
          </div>
        </div>

        {/* Salles */}
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="flex flex-wrap gap-1">
            {examen.salles.slice(0, 3).map((salle) => (
              <span
                key={salle.id}
                className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
              >
                {salle.salle_id}
              </span>
            ))}
            {examen.salles.length > 3 && (
              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                +{examen.salles.length - 3}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Modal de détails */}
      {showDetails && (
        <ExamenDetails
          examen={examen}
          onClose={() => setShowDetails(false)}
        />
      )}
    </>
  );
}
```

## 🎨 Styles Tailwind

```typescript
// tailwind.config.ts

export default {
  theme: {
    extend: {
      colors: {
        // Statuts
        brouillon: {
          50: "#fefce8",
          100: "#fef9c3",
          200: "#fef08a",
        },
        validee: {
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
        },
        publiee: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
        },
        // Types
        examen: {
          50: "#fef2f2",
          100: "#fee2e2",
          200: "#fecaca",
        },
        ds: {
          50: "#fff7ed",
          100: "#ffedd5",
          200: "#fed7aa",
        },
      },
    },
  },
};
```

## 📱 Responsive Design

### Mobile (< 768px)
- Vue liste verticale
- Une carte par ligne
- Filtres en accordéon
- Actions en menu contextuel

### Tablet (768px - 1024px)
- Grille 2 colonnes
- Filtres en ligne
- Actions visibles

### Desktop (> 1024px)
- Grille 3 colonnes
- Tous les filtres visibles
- Vue calendrier disponible

## 🚀 Démarrage Rapide

### 1. Installation

```bash
cd PFA/frontend
npm install
```

### 2. Configuration

```env
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

### 3. Développement

```bash
npm run dev
```

### 4. Accès

```
http://localhost:3000/emploi-du-temps
```

## 📋 Checklist d'Implémentation

### Phase 1: Structure de Base
- [ ] Créer la structure des dossiers
- [ ] Définir les types TypeScript
- [ ] Créer les fonctions API
- [ ] Créer le hook `useEmploiDuTemps`

### Phase 2: Composants Principaux
- [ ] `EmploiDuTempsGrid` - Grille principale
- [ ] `ExamenCard` - Carte d'examen
- [ ] `EmploiDuTempsFilters` - Filtres
- [ ] `ExamenDetails` - Modal de détails

### Phase 3: Fonctionnalités Avancées
- [ ] Export PDF
- [ ] Détection de conflits
- [ ] Actions (Valider/Publier)
- [ ] Vue calendrier

### Phase 4: Optimisations
- [ ] Responsive design
- [ ] Loading states
- [ ] Error handling
- [ ] Caching des données

### Phase 5: Tests
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] Tests E2E

## 🎯 Prochaines Étapes

1. **Implémenter la structure de base**
2. **Créer les composants principaux**
3. **Ajouter les filtres et actions**
4. **Implémenter l'export PDF**
5. **Tester et optimiser**

## 📚 Ressources

- **API Documentation**: http://localhost:8000/docs
- **Types Backend**: `PFA/server/app/schemas/planification.py`
- **Exemples**: `PFA/frontend/src/components/planification/`

---

**Date**: 2026-04-25  
**Version**: 1.0.0  
**Statut**: 📝 Spécification Prête
