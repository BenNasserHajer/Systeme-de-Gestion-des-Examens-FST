# ⚡ CHEAT SHEET - Sessions Backend

## 🎯 TL;DR (Too Long; Didn't Read)

```
Sessions: S1 (7-15 jan), S2 (11-23 may)
API: GET /referentiel/catalogue → .sessions[]
Dates: Always YYYY-MM-DD format
Key: date_examen ∈ [session.date_debut, session.date_fin]
```

---

## 📍 Sessions Actuelles

```sql
SELECT * FROM session;
-- id | type_session | annee_universitaire | date_debut | date_fin   | statut
-- 1  | PRINCIPALE   | 2025/2026           | 2026-01-07 | 2026-01-15 | VALIDEE
-- 2  | PRINCIPALE   | 2025/2026           | 2026-05-11 | 2026-05-23 | BROUILLON
```

---

## 🔌 API One-Liners

```bash
# Get all sessions
curl http://localhost:8000/api/referentiel/catalogue | jq '.sessions'

# Get creneaux
curl http://localhost:8000/api/referentiel/catalogue | jq '.creneaux'

# Create planification
curl -X POST http://localhost:8000/api/planifications \
  -H "Content-Type: application/json" \
  -d '{"session_id":1,"section_id":5,"date_examen":"2026-01-10",...}'

# Auto-generate planifications
curl -X POST http://localhost:8000/api/planifications/generate \
  -H "Content-Type: application/json" \
  -d '{"session_id":1,"scope_section_ids":[5,6,7],...}'

# Auto-assign surveillants
curl -X POST http://localhost:8000/api/surveillances/affecter-session \
  -H "Content-Type: application/json" \
  -d '{"session_id":1,"save":true}'
```

---

## 🐍 Python ORM One-Liners

```python
from app.models.salle_session import Session, Creneau
from app.database import SessionLocal

db = SessionLocal()

# Get all sessions
sessions = db.query(Session).all()

# Get session by ID
session = db.query(Session).filter(Session.id == 1).first()

# Get creneaux for session
creneaux = [c for c in db.query(Creneau).all() 
            if session.date_debut <= c.date <= session.date_fin]

# Create session
new_session = Session(
    type_session="PRINCIPALE",
    annee_universitaire="2025/2026",
    date_debut=date(2026, 9, 15),
    date_fin=date(2026, 9, 25),
    statut="BROUILLON"
)
db.add(new_session)
db.commit()

# Update session
session.date_fin = date(2026, 1, 20)
db.commit()

# Delete session (careful!)
db.delete(session)
db.commit()
```

---

## 📋 TypeScript/React One-Liners

```typescript
// Get sessions
const { sessions } = await fetch('/api/referentiel/catalogue').then(r => r.json());

// Find session by ID
const session = sessions.find(s => s.session_id === 1);

// Format dates
console.log(`${session.date_debut} → ${session.date_fin}`);

// Filter creneaux by session
const creneaux = catalogue.creneaux.filter(c => 
  c.date_examen >= session.date_debut && 
  c.date_examen <= session.date_fin
);

// Create planification
await fetch('/api/planifications', {
  method: 'POST',
  body: JSON.stringify({
    session_id: session.session_id,
    date_examen: "2026-01-10",
    // ...
  })
});
```

---

## 📁 File Quick Links

| File | Purpose | Key Line |
|------|---------|----------|
| models/salle_session.py | Session ORM | 44-58 |
| routers/referentiel.py | /catalogue endpoint | 17-20 |
| services/catalogue_service.py | Load sessions | 153-177 |
| schemas/session_schema.py | SessionOut | 1-15 |
| app/seed/seed_data_v2.sql | S1 + S2 data | 130-208 |
| add_session_s2.py | Create S2 script | Full file |

---

## ✅ Validation Checklist

```javascript
// Before creating planification:
✓ Get session: SELECT * FROM session WHERE id = ?
✓ Check statut ≠ "PUBLIEE"
✓ Verify date: session.date_debut <= date_examen <= session.date_fin
✓ Check creneau available: SELECT * FROM creneau WHERE date = ? AND ...
✓ Create planification

// Before assigning surveillants:
✓ Get planifications: SELECT * FROM planifications WHERE session_id = ?
✓ For each planif:
  ✓ Get enseignants: SELECT * FROM enseignant WHERE ...
  ✓ Check indisponibilites: SELECT * FROM indisponibilite WHERE ...
  ✓ Assign 2-4 survs per planif

// Before publishing session:
✓ Check all planifications have status = "VALIDEE"
✓ Check all planifications have assigned surveillants
✓ Update session.statut = "PUBLIEE"
```

---

## 🔍 Debug Quick Reference

```sql
-- Check sessions
SELECT id, annee_universitaire, date_debut, date_fin, statut FROM session;

-- Check creneaux for session 1
SELECT * FROM creneau 
WHERE date BETWEEN 
  (SELECT date_debut FROM session WHERE id = 1)
  AND (SELECT date_fin FROM session WHERE id = 1)
ORDER BY date, heure_debut;

-- Count planifications per session
SELECT session_id, COUNT(*) as count FROM planifications GROUP BY session_id;

-- Count surveillances per session
SELECT s.id, COUNT(distinct surv.id) 
FROM session s 
LEFT JOIN planifications p ON p.session_id = s.id 
LEFT JOIN surveillance surv ON surv.planification_id = p.id 
GROUP BY s.id;

-- Find date conflicts
SELECT p1.id, p1.matiere, p1.date_examen, p1.heure_debut
FROM planifications p1
JOIN planifications p2 ON p1.date_examen = p2.date_examen 
  AND p1.heure_debut = p2.heure_debut
  AND p1.id != p2.id;
```

---

## 🚀 Common Tasks

### Create New Session
```python
from datetime import date
from app.models.salle_session import Session
from app.database import SessionLocal

db = SessionLocal()
session = Session(
    type_session="PRINCIPALE",
    annee_universitaire="2025/2026",
    date_debut=date(2026, 9, 15),
    date_fin=date(2026, 9, 25),
    statut="BROUILLON"
)
db.add(session)
db.commit()
print(f"Created: Session {session.id}")
```

### Add Creneaux
```python
from datetime import date, time
from app.models.salle_session import Creneau

creneaux = [
    (date(2026, 9, 15), time(8, 30), time(10, 30)),
    (date(2026, 9, 15), time(11, 0), time(13, 0)),
]

for d, h_start, h_end in creneaux:
    creneau = Creneau(date=d, heure_debut=h_start, heure_fin=h_end, libelle="...")
    db.add(creneau)
db.commit()
```

### Modify Session Dates
```python
session = db.query(Session).filter(Session.id == 1).first()
session.date_debut = date(2026, 1, 5)
session.date_fin = date(2026, 1, 20)
db.commit()
```

### Get Sessions with Counts
```python
from sqlalchemy import func
result = db.query(
    Session.id,
    Session.annee_universitaire,
    func.count(Planification.id).label('planif_count')
).join(Planification).group_by(Session.id).all()
```

---

## 🎯 Status Codes

| Status | Meaning | Can Edit | Can Generate |
|--------|---------|----------|--------------|
| BROUILLON | Draft | ✓ Yes | ✓ Yes |
| VALIDEE | Finalized | ✓ Yes | ✓ Yes |
| PUBLIEE | Published | ✗ No | ✗ No |

---

## 📐 Data Validation Rules

```
✓ type_session: "PRINCIPALE" or "RATTRAPAGE"
✓ annee_universitaire: Format "YYYY/YYYY" (e.g., "2025/2026")
✓ date_debut: YYYY-MM-DD format, ≤ date_fin
✓ date_fin: YYYY-MM-DD format, ≥ date_debut
✓ statut: "BROUILLON", "VALIDEE", or "PUBLIEE"

❌ date_debut > date_fin: Invalid
❌ statut = "PUBLIEE" during generation: Error
❌ date_examen outside [date_debut, date_fin]: Validation error
```

---

## 🔗 Relationships

```
Session (1) ──── Planifications (N)
         ├──── Creneaux (J) [filtered by dates]
         └──── Surveillances (K) [via Planifications]

Planification (1) ──── Surveillance (N)
              ├──── PlanifSalle (M)
              └──── Section (1)
```

---

## 🧪 Quick Test

```bash
# Check sessions exist
python3 << 'EOF'
from app.models.salle_session import Session
from app.database import SessionLocal
db = SessionLocal()
for s in db.query(Session).all():
    print(f"Session {s.id}: {s.date_debut} → {s.date_fin}")
EOF

# Test API
curl http://localhost:8000/api/referentiel/catalogue | \
  jq '.sessions[] | {id:.session_id, label:.label, dates:.date_debut}'
```

---

## 🎓 Key Constants

```python
SEMESTRES = ["S1", "S2"]

TYPE_EPREUVE_OPTIONS = [
    {"value": "EXAMEN_FINAL", "label": "Examen Final"},
    {"value": "DS", "label": "DS"},
]

STATUTS = ["BROUILLON", "VALIDEE", "PUBLIEE"]
```

---

## ⚡ Pro Tips

1. **Always use ISO date format**: `YYYY-MM-DD`
2. **Check session status before operations**: `if session.statut != "PUBLIEE"`
3. **Filter creneaux by session period**: `date BETWEEN session.date_debut AND session.date_fin`
4. **Validate exam date**: `session.date_debut <= date_examen <= session.date_fin`
5. **Don't modify published sessions**: Requires special permission
6. **Use `db.query(...).first()` not `[0]`**: Avoids IndexError
7. **Always call `db.commit()`** after changes
8. **Use transaction rollback** on errors: `db.rollback()`

---

## 🆘 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Session not found | Wrong ID | Verify session.id in DB |
| Date out of range | date_examen ∉ [start, end] | Check session dates |
| Cannot generate | Session PUBLIEE | Use different session or un-publish |
| Creneau conflict | Same slot occupied | Check unique constraint |
| No surveillants | Insufficient enseignants | Add more teachers or reduce requirements |

---

## 📞 Quick Contact Points

- **ORM Models**: server/app/models/salle_session.py
- **APIs**: server/app/routers/referentiel.py + planifications.py
- **Services**: server/app/services/catalogue_service.py
- **Database**: server/app/seed/seed_data_v2.sql
- **Tests**: server/tests/*.py

---

## 🎯 Done Checklist

- ✅ Found where sessions are defined (SQL seed + Python ORM)
- ✅ Found session dates (date_debut, date_fin)
- ✅ Found API endpoint (/referentiel/catalogue)
- ✅ Found table structure (Session model + SQL)
- ✅ Created examples and documentation
- ✅ Provided quick reference guide

**You're all set! 🚀**

