# Workflow de Planification d'Examens

## Vue d'ensemble

L'utilisateur entre 4 paramètres et le système génère automatiquement l'emploi du temps d'examen avec possibilité de modification manuelle via drag & drop.

## Étape 1 : Formulaire de Génération

### Entrées utilisateur (4 champs)

1. **Section** : Sélection de la section (ex: IGL4, IGL3)
2. **Session** : Sélection de la session d'examen (ex: Principale 2025/2026)
3. **Type d'épreuve** : EXAMEN_FINAL ou DS
4. **Niveau/Semestre** : S1 ou S2

### Endpoint API

```
POST /api/planification/generer-auto
```

**Request Body:**
```json
{
  "section_id": 2,
  "session_id": 1,
  "type_epreuve": "EXAMEN_FINAL",
  "semestre": "S1"
}
```

**Response:**
```json
{
  "success": true,
  "nb_crees": 15,
  "nb_conflits": 2,
  "planifications": [
    {
      "id": 1,
      "matiere": "Machine Learning",
      "date_examen": "2026-01-07",
      "heure_debut": "08:30",
      "heure_fin": "10:30",
      "salles": ["AMPHI-INFO"],
      "nb_etudiants": 106,
      "statut": "BROUILLON"
    }
  ],
  "conflits": [
    {
      "matiere": "Big Data",
      "contrainte": "C1",
      "message": "Pas assez de salles disponibles",
      "suggestion": "Ajouter des créneaux ou des salles"
    }
  ]
}
```

## Étape 2 : Affichage Calendrier avec Drag & Drop

### Vue Calendrier

Le calendrier affiche les examens générés avec :
- **Vue hebdomadaire** : Lundi à Vendredi (+ Samedi si nécessaire)
- **Plages horaires** : 08:00 AM à 06:00 PM
- **Cartes d'examen** : Affichent matière, salle, nombre d'étudiants

### Fonctionnalités Drag & Drop

#### 1. Déplacer un examen (changer date/heure)
```
PATCH /api/planification/{id}/deplacer
```

**Request:**
```json
{
  "nouvelle_date": "2026-01-08",
  "nouvelle_heure_debut": "11:00",
  "nouvelle_heure_fin": "13:00"
}
```

**Response:**
```json
{
  "success": true,
  "planification": { ... },
  "warnings": [
    "Cette section a déjà 2 examens ce jour-là"
  ]
}
```

#### 2. Changer la salle
```
PATCH /api/planification/{id}/changer-salle
```

**Request:**
```json
{
  "groupe_id": 1,
  "nouvelle_salle_id": "INF-15"
}
```

**Response:**
```json
{
  "success": true,
  "planification": { ... },
  "warnings": []
}
```

#### 3. Redimensionner (changer durée)
```
PATCH /api/planification/{id}/changer-duree
```

**Request:**
```json
{
  "nouvelle_duree": 90,
  "nouvelle_heure_fin": "10:00"
}
```

## Étape 3 : Validation et Sauvegarde

### Valider l'emploi du temps

```
POST /api/planification/valider-session
```

**Request:**
```json
{
  "session_id": 1,
  "section_id": 2
}
```

**Actions:**
1. Vérifie toutes les contraintes
2. Change le statut de BROUILLON → VALIDEE
3. Envoie des notifications (optionnel)
4. Génère le PDF de l'emploi du temps

**Response:**
```json
{
  "success": true,
  "nb_planifications": 15,
  "statut": "VALIDEE",
  "pdf_url": "/api/planification/emploi-du-temps/1/2/pdf",
  "erreurs": []
}
```

## Structure des Données

### Planification (Table principale)

```sql
CREATE TABLE planification_examen (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    section_matiere_id INTEGER NOT NULL,
    
    -- Informations de l'examen
    matiere VARCHAR(120) NOT NULL,
    type_epreuve VARCHAR(24) NOT NULL,
    semestre INTEGER NOT NULL,
    
    -- Date et heure
    date_examen DATE NOT NULL,
    heure_debut TIME NOT NULL,
    heure_fin TIME NOT NULL,
    duree INTEGER NOT NULL,
    
    -- Métadonnées
    coefficient FLOAT,
    section_nb_etudiants INTEGER NOT NULL,
    nb_groupes INTEGER DEFAULT 1,
    nb_surveillants_requis INTEGER DEFAULT 2,
    
    -- Statut
    statut VARCHAR(50) DEFAULT 'BROUILLON',
    mode_affectation VARCHAR(50) DEFAULT 'AUTO',
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### PlanifSalle (Salles affectées)

```sql
CREATE TABLE planif_salle (
    planification_id INTEGER NOT NULL,
    groupe_id INTEGER NOT NULL,
    
    -- Informations de la salle (dénormalisé pour historique)
    salle_id VARCHAR(80) NOT NULL,
    salle_capacite INTEGER NOT NULL,
    salle_batiment VARCHAR(64),
    
    -- Groupe
    groupe_effectif INTEGER NOT NULL,
    
    -- Référence temporelle
    creneau_date DATE NOT NULL,
    heure_debut TIME NOT NULL,
    
    PRIMARY KEY (planification_id, groupe_id)
);
```

## Composants Frontend

### 1. Formulaire de Génération

```tsx
// GenerationForm.tsx
interface GenerationFormProps {
  onGenerate: (params: GenerationParams) => void;
}

interface GenerationParams {
  section_id: number;
  session_id: number;
  type_epreuve: 'EXAMEN_FINAL' | 'DS';
  semestre: 'S1' | 'S2';
}
```

### 2. Calendrier Drag & Drop

```tsx
// ExamCalendar.tsx
interface ExamCalendarProps {
  planifications: Planification[];
  onDrop: (planifId: number, newDate: Date, newTime: string) => void;
  onResize: (planifId: number, newDuration: number) => void;
  onChangeSalle: (planifId: number, groupeId: number, newSalleId: string) => void;
}
```

### 3. Carte d'Examen

```tsx
// ExamCard.tsx
interface ExamCardProps {
  planification: Planification;
  draggable: boolean;
  onEdit: () => void;
}

// Affichage :
// ┌─────────────────────┐
// │ Physics 101         │
// │ 🏫 Room 302         │
// │ 👥 45 Students      │
// └─────────────────────┘
```

## Bibliothèques Recommandées

### Frontend
- **FullCalendar** : Calendrier avec drag & drop
- **React DnD** : Alternative pour drag & drop personnalisé
- **date-fns** : Manipulation de dates

### Backend
- **FastAPI** : Déjà utilisé ✅
- **SQLAlchemy** : Déjà utilisé ✅
- **Pydantic** : Validation des données ✅

## Flux de Données Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. GÉNÉRATION AUTOMATIQUE                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Formulaire (4)   │
                    │ - Section        │
                    │ - Session        │
                    │ - Type épreuve   │
                    │ - Semestre       │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ POST /generer    │
                    │ - Algorithme     │
                    │ - Contraintes    │
                    └──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    2. AFFICHAGE CALENDRIER                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Calendrier       │
                    │ - Vue semaine    │
                    │ - Cartes examen  │
                    │ - Drag & Drop    │
                    └──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    3. MODIFICATIONS MANUELLES                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          ┌──────────────────┐  ┌──────────────────┐
          │ Déplacer         │  │ Changer salle    │
          │ PATCH /deplacer  │  │ PATCH /changer   │
          └──────────────────┘  └──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    4. VALIDATION & SAUVEGARDE                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Bouton "Valider" │
                    │ POST /valider    │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Statut: VALIDEE  │
                    │ PDF généré       │
                    │ Notifications    │
                    └──────────────────┘
```

## Gestion des Conflits

### Types de conflits

1. **C1 - Salle occupée** : Une salle est déjà utilisée
2. **C7 - Section occupée** : La section a déjà un examen
3. **C8 - Pas assez de salles** : Impossible de diviser en groupes

### Résolution manuelle

Quand un conflit est détecté :
1. L'examen est marqué en **rouge** dans le calendrier
2. Un message d'erreur s'affiche
3. L'admin peut :
   - Déplacer l'examen vers un autre créneau
   - Changer la salle
   - Diviser en plus de groupes

## Statuts de Planification

```
BROUILLON → VALIDEE → PUBLIEE
    ↓          ↓
 Modifiable  Figée
```

- **BROUILLON** : Peut être modifié librement
- **VALIDEE** : Approuvé par l'admin, modifications limitées
- **PUBLIEE** : Visible par les étudiants, non modifiable

## Exemple de Workflow Complet

### Scénario : Planifier les examens de IGL4 S1

1. **Admin remplit le formulaire**
   - Section: IGL4
   - Session: Principale 2025/2026
   - Type: EXAMEN_FINAL
   - Semestre: S1

2. **Système génère automatiquement**
   - 15 matières planifiées
   - 2 conflits détectés (Big Data, Entreprenariat)

3. **Admin visualise le calendrier**
   - Voit les 15 examens répartis sur la semaine
   - Les 2 conflits sont en rouge

4. **Admin résout les conflits**
   - Déplace "Big Data" du mercredi au jeudi
   - Change la salle de "Entreprenariat" : INF-15 → AMPHI-INFO

5. **Admin valide**
   - Clique sur "Valider"
   - Système vérifie toutes les contraintes
   - Statut passe à VALIDEE
   - PDF généré automatiquement

## Prochaines Étapes d'Implémentation

### Backend
1. ✅ Algorithme de génération (déjà fait)
2. ✅ Modèles de données (déjà fait)
3. ⏳ Endpoint `/generer-auto`
4. ⏳ Endpoints de modification (déplacer, changer salle)
5. ⏳ Endpoint de validation

### Frontend
1. ⏳ Formulaire de génération (4 champs)
2. ⏳ Intégration FullCalendar
3. ⏳ Drag & Drop handlers
4. ⏳ Modal de résolution de conflits
5. ⏳ Bouton de validation

Voulez-vous que je commence par implémenter les endpoints backend ou le composant frontend du calendrier ?
