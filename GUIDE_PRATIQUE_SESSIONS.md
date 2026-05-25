# 🎯 Guide Pratique - Utilisation des Sessions (S1/S2)

## 📌 Résumé Rapide

```
API Base: http://localhost:8000/api

GET /referentiel/catalogue
├─ sessions: [
│   { session_id: 1, label: "Principale 2025/2026", date_debut: "2026-01-07", ... },
│   { session_id: 2, label: "Principale 2025/2026", date_debut: "2026-05-11", ... }
│  ]
├─ creneaux: [
│   { date_examen: "2026-01-07", heure_debut: "08:30:00", heure_fin: "10:30:00" },
│   ...
│  ]
└─ ... autres données
```

---

## 1️⃣ Frontend - Récupérer les Sessions

### TypeScript/React

```typescript
// src/lib/api/referentiel.ts

export async function getCatalogue(): Promise<CatalogueData> {
  const response = await fetch(`${API_BASE}/referentiel/catalogue`);
  return handleResponse<CatalogueData>(response);
}

interface SessionItem {
  session_id: number;
  label: string;
  date_debut: string;
  date_fin: string;
  statut: "BROUILLON" | "VALIDEE" | "PUBLIEE";
}

interface CatalogueData {
  sessions: SessionItem[];
  creneaux: CreneauItem[];
  sections: SectionItem[];
  // ... autres champs
}

// Utilisation dans composant
const catalogue = await getCatalogue();
const sessions = catalogue.sessions;

// Afficher les sessions
sessions.forEach(session => {
  console.log(`${session.label}: ${session.date_debut} → ${session.date_fin}`);
});
```

---

## 2️⃣ Backend - Requête SQL Brute

```sql
-- Récupérer toutes les sessions
SELECT id, type_session, annee_universitaire, date_debut, date_fin, statut
FROM session
ORDER BY date_debut, id;

-- Résultat:
-- id | type_session | annee_universitaire | date_debut | date_fin   | statut
-- ---|--------------|---------------------|------------|------------|--------
-- 1  | PRINCIPALE   | 2025/2026           | 2026-01-07 | 2026-01-15 | VALIDEE
-- 2  | PRINCIPALE   | 2025/2026           | 2026-05-11 | 2026-05-23 | BROUILLON
```

---

## 3️⃣ Backend - Requête Python ORM

```python
from app.models.salle_session import Session as SessionModel
from app.database import SessionLocal

db = SessionLocal()

# Récupérer toutes les sessions
sessions = db.query(SessionModel).order_by(SessionModel.date_debut).all()

for session in sessions:
    print(f"Session {session.id}")
    print(f"  Année: {session.annee_universitaire}")
    print(f"  Période: {session.date_debut} → {session.date_fin}")
    print(f"  Statut: {session.statut}")
    print(f"  Planifications: {len(session.planifications)} items")

# Récupérer une session spécifique
session_s2 = db.query(SessionModel).filter(
    SessionModel.annee_universitaire == "2025/2026",
    SessionModel.date_debut == date(2026, 5, 11)
).first()

if session_s2:
    print(f"Trouvé: {session_s2.type_session} {session_s2.annee_universitaire}")
```

---

## 4️⃣ Récupérer les Créneaux d'une Session

### 🔍 Logique de Filtrage

```python
from app.models.salle_session import Creneau, Session as SessionModel
from app.database import SessionLocal

db = SessionLocal()

# Récupérer session S2
session_s2 = db.query(SessionModel).filter(
    SessionModel.id == 2
).first()

# Récupérer tous les créneaux
all_creneaux = db.query(Creneau).order_by(Creneau.date, Creneau.heure_debut).all()

# Filtrer par période de session
creneaux_session_s2 = [
    c for c in all_creneaux
    if session_s2.date_debut <= c.date <= session_s2.date_fin
]

print(f"Créneaux S2: {len(creneaux_session_s2)}")
for creneau in creneaux_session_s2[:5]:
    print(f"  {creneau.date} {creneau.heure_debut}-{creneau.heure_fin} ({creneau.libelle})")
```

### 📊 Résultat Attendu

```
Créneaux S2: 36
  2026-05-11 08:00:00-10:00:00 (Lun 11/05 Matin)
  2026-05-11 10:30:00-12:30:00 (Lun 11/05 Midi)
  2026-05-11 14:00:00-16:00:00 (Lun 11/05 Après-midi)
  2026-05-12 08:00:00-10:00:00 (Mar 12/05 Matin)
  2026-05-12 10:30:00-12:30:00 (Mar 12/05 Midi)
  ...
```

---

## 5️⃣ Créer une Nouvelle Session

### 🐍 Script Python

```python
from datetime import date, time
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.salle_session import Session as SessionModel, Creneau

def create_session(
    type_session: str = "PRINCIPALE",
    annee_universitaire: str = "2025/2026",
    date_debut: date = date(2026, 9, 15),
    date_fin: date = date(2026, 9, 25),
    statut: str = "BROUILLON"
) -> SessionModel:
    """Crée une nouvelle session."""
    db: Session = SessionLocal()
    
    # Créer la session
    session = SessionModel(
        type_session=type_session,
        annee_universitaire=annee_universitaire,
        date_debut=date_debut,
        date_fin=date_fin,
        statut=statut
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    print(f"✓ Session créée: ID {session.id}")
    print(f"  Période: {session.date_debut} → {session.date_fin}")
    
    return session

def add_creneaux_for_session(
    session_id: int,
    start_date: date,
    end_date: date,
    slots_per_day: list[tuple] = None
) -> int:
    """Ajoute les créneaux pour une session."""
    
    if slots_per_day is None:
        # Créneaux par défaut: 08:30-10:30, 11:00-13:00, 14:00-16:00
        slots_per_day = [
            (time(8, 30), time(10, 30)),
            (time(11, 0), time(13, 0)),
            (time(14, 0), time(16, 0))
        ]
    
    db: Session = SessionLocal()
    current = start_date
    added_count = 0
    
    from datetime import timedelta
    
    while current <= end_date:
        # Skip Sunday (weekday=6)
        if current.weekday() < 6:
            for idx, (h_debut, h_fin) in enumerate(slots_per_day, 1):
                # Vérifier si le créneau existe déjà
                existing = db.query(Creneau).filter(
                    Creneau.date == current,
                    Creneau.heure_debut == h_debut
                ).first()
                
                if not existing:
                    jour_semaine = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"][current.weekday()]
                    libelle = f"{jour_semaine} {current.strftime('%d/%m')} M{idx}"
                    
                    creneau = Creneau(
                        date=current,
                        heure_debut=h_debut,
                        heure_fin=h_fin,
                        libelle=libelle
                    )
                    db.add(creneau)
                    added_count += 1
        
        current += timedelta(days=1)
    
    db.commit()
    db.close()
    
    print(f"✓ {added_count} créneaux ajoutés")
    return added_count

# Utilisation
session = create_session(
    annee_universitaire="2025/2026",
    date_debut=date(2026, 9, 15),
    date_fin=date(2026, 9, 25)
)

add_creneaux_for_session(
    session.id,
    date_debut=date(2026, 9, 15),
    end_date=date(2026, 9, 25)
)

print("✅ Session complète avec créneaux créée!")
```

---

## 6️⃣ Modifier une Session

```python
from app.models.salle_session import Session as SessionModel
from app.database import SessionLocal
from datetime import date

db = SessionLocal()

# Récupérer session S2
session_s2 = db.query(SessionModel).filter(SessionModel.id == 2).first()

if session_s2:
    # Modifier dates
    session_s2.date_debut = date(2026, 5, 10)  # Un jour plus tôt
    session_s2.date_fin = date(2026, 5, 24)    # Un jour plus tard
    
    # Modifier statut
    session_s2.statut = "VALIDEE"
    
    db.commit()
    print(f"✓ Session S2 modifiée")
    print(f"  Nouvelle période: {session_s2.date_debut} → {session_s2.date_fin}")
    print(f"  Nouveau statut: {session_s2.statut}")
```

---

## 7️⃣ Frontend - Afficher les Sessions

### React Component

```tsx
// src/components/SessionSelector.tsx

import { useState, useEffect } from "react";
import { getCatalogue } from "@/lib/api/referentiel";

interface SessionItem {
  session_id: number;
  label: string;
  date_debut: string;
  date_fin: string;
  statut: string;
}

export function SessionSelector() {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [selectedSession, setSelectedSession] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  async function loadSessions() {
    try {
      const catalogue = await getCatalogue();
      setSessions(catalogue.sessions);
      if (catalogue.sessions.length > 0) {
        setSelectedSession(catalogue.sessions[0].session_id);
      }
    } catch (error) {
      console.error("Erreur chargement sessions:", error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Chargement...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">Sélectionnez une session</h2>
      
      <select
        value={selectedSession || ""}
        onChange={(e) => setSelectedSession(Number(e.target.value))}
        className="w-full border rounded px-3 py-2"
      >
        <option value="">-- Choisir --</option>
        {sessions.map((session) => (
          <option key={session.session_id} value={session.session_id}>
            {session.label} ({session.date_debut} → {session.date_fin})
          </option>
        ))}
      </select>

      {selectedSession && (
        <div className="border-l-4 border-blue-500 pl-4 py-2">
          <p className="text-sm text-gray-600">
            Sessions: {sessions.find((s) => s.session_id === selectedSession)?.date_debut} →{" "}
            {sessions.find((s) => s.session_id === selectedSession)?.date_fin}
          </p>
          <p className="text-xs text-gray-500">
            Statut: {sessions.find((s) => s.session_id === selectedSession)?.statut}
          </p>
        </div>
      )}
    </div>
  );
}
```

---

## 8️⃣ Test - Vérifier les Sessions

### Via API REST (curl)

```bash
# Récupérer le catalogue complet
curl -X GET http://localhost:8000/api/referentiel/catalogue

# Filtrer juste les sessions (avec jq)
curl -X GET http://localhost:8000/api/referentiel/catalogue | jq '.sessions'

# Résultat:
# [
#   {
#     "session_id": 1,
#     "label": "Principale 2025/2026",
#     "date_debut": "2026-01-07",
#     "date_fin": "2026-01-15",
#     "statut": "VALIDEE"
#   },
#   {
#     "session_id": 2,
#     "label": "Principale 2025/2026",
#     "date_debut": "2026-05-11",
#     "date_fin": "2026-05-23",
#     "statut": "BROUILLON"
#   }
# ]
```

### Via Script Python

```bash
# Vérifier les sessions depuis la BDD
cd server
python -m pytest tests/test_sessions.py -v

# Ou via la REPL Python
python3 << EOF
from app.models.salle_session import Session
from app.database import SessionLocal

db = SessionLocal()
for s in db.query(Session).all():
    print(f"Session {s.id}: {s.date_debut} → {s.date_fin} ({s.statut})")
EOF
```

---

## 9️⃣ Tableau Récapitulatif

| Concept | SQL | ORM Python | Endpoint | Frontend |
|---------|-----|-----------|----------|----------|
| **Récupérer sessions** | SELECT * FROM session | Session.query().all() | GET /catalogue | getCatalogue().sessions |
| **Récupérer créneaux** | SELECT * FROM creneau | Creneau.query().all() | GET /catalogue | getCatalogue().creneaux |
| **Filtrer par session** | ... WHERE date BETWEEN | [c for c in all if ...] | Intégré dans load_catalogue() | Filtrer côté client |
| **Créer session** | INSERT INTO session | SessionModel(...); db.add() | POST /sessions | Pas API actuellement |
| **Modifier session** | UPDATE session SET | session.field = ...; db.commit() | PATCH /sessions/{id} | Pas API actuellement |

---

## 🔟 Calendrier des Sessions 2025/2026

```
2025/2026
├─ S1 (Semestre 1)
│  └─ Examens: 7 janvier → 15 janvier 2026 (8 jours)
│     24 créneaux (3 par jour)
│     Statut: VALIDEE
│
└─ S2 (Semestre 2)
   └─ Examens: 11 mai → 23 mai 2026 (12 jours)
      36 créneaux (3 par jour)
      Statut: BROUILLON
```

---

## Notes

- **Dates**: Toujours au format `YYYY-MM-DD` (ISO 8601)
- **Créneaux**: Filtrés automatiquement par la période de session
- **Statut**: BROUILLON (en cours d'édition) → VALIDEE (finalisé) → PUBLIEE (publié)
- **API centralisée**: Tout passe par `/referentiel/catalogue`

