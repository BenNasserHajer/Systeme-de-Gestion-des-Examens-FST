# 🚀 Quick Start: Exam Planning System

## 📋 What You Need to Know

The exam planning system lets you:
1. Enter 4 parameters (Section, Session, Type, Semestre)
2. Generate exam schedule automatically
3. Adjust manually with drag & drop
4. Validate and save to database

---

## 🎯 Step-by-Step Guide

### 1️⃣ Start the Application

**Terminal 1 - Backend:**
```bash
cd server
.venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 2️⃣ Open the Planification Page

Navigate to: `http://localhost:3000/planification`

### 3️⃣ Fill the Form

Select these 4 fields:
- **Niveau**: IGL4, IGL3, etc.
- **Section**: The section within the niveau
- **Session**: Principale 2025/2026, Rattrapage, etc.
- **Type d'épreuve**: Examen Final or DS

Click **"Generer automatiquement"**

### 4️⃣ View the Calendar

You'll see a weekly calendar with exam cards showing:
- Matière name
- Room (salle)
- Number of students

### 5️⃣ Make Adjustments (Optional)

**Change Date/Time:**
- Click and drag exam card to new day/time

**Change Room:**
- Click on exam card
- Select new room from dropdown
- Click "Enregistrer"

### 6️⃣ Validate

Click **"Valider"** button at the top

Status changes: BROUILLON → VALIDEE

---

## 🎨 Calendar Features

### Drag & Drop
- **Grab**: Click and hold exam card
- **Drag**: Move to different day/time
- **Drop**: Release to save new position

### Visual Indicators
- **Blue cards**: Draft exams (BROUILLON)
- **Hover effect**: Shows card is interactive
- **Cursor changes**: Grab cursor when hovering


---

## 🔧 Troubleshooting

### Backend Not Starting

**Error**: `ModuleNotFoundError`
**Solution**: Install dependencies
```bash
cd server
pip install -r requirements.txt
```

### Frontend Not Starting

**Error**: `Module not found`
**Solution**: Install dependencies
```bash
cd frontend
npm install
```

### Database Connection Error

**Error**: `could not connect to server`
**Solution**: Check PostgreSQL is running and `.env` file exists

```bash
# server/.env should contain:
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### No Exams Generated

**Possible causes:**
1. No matières in database for selected section
2. No available rooms (salles)
3. No time slots (créneaux)

**Solution**: Check database has required data:
```sql
SELECT * FROM section_matiere WHERE section_id = ?;
SELECT * FROM salle_session WHERE session_id = ?;
SELECT * FROM creneau WHERE session_id = ?;
```

---

## 📊 API Endpoints Reference

### Generate Schedule
```http
POST /api/sessions/{session_id}/generer-simple
Content-Type: application/json

{
  "section_label": "IGL4",
  "niveau": "IGL4",
  "type_epreuve_label": "Examen Final"
}
```

### Get Schedule
```http
GET /api/sessions/{session_id}/emploi-du-temps?section_id={section_id}
```

### Update Exam
```http
PUT /api/planifications/{id}
Content-Type: application/json

{
  "date_examen": "2026-01-08",
  "heure_debut": "11:00:00",
  "heure_fin": "13:00:00"
}
```

### Change Room
```http
POST /api/planifications/{id}/salles
Content-Type: application/json

[
  {
    "salle_id": "AMPHI-INFO",
    "salle_capacite": 150,
    "groupe_id": 1,
    "groupe_effectif": 106
  }
]
```

### Validate Session
```http
POST /api/sessions/{session_id}/valider
Content-Type: application/json

{
  "section_id": 2
}
```


---

## 💡 Tips & Best Practices

### 1. Generate First, Adjust Later
- Let the algorithm do the heavy lifting
- Only manually adjust conflicts or preferences

### 2. Check Conflicts
- Red warnings indicate constraint violations
- Resolve by changing time or room

### 3. Validate When Ready
- BROUILLON status allows unlimited edits
- VALIDEE status locks the schedule
- Only validate when you're sure

### 4. Use Appropriate Rooms
- Algorithm assigns rooms based on capacity
- Manually change if you need specific rooms

### 5. Plan Ahead
- Generate schedule early in the session
- Leave time for manual adjustments
- Validate before publishing to students

---

## 📱 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Tab` | Navigate between form fields |
| `Enter` | Submit form / Save modal |
| `Esc` | Close modal |
| `Click + Drag` | Move exam card |
| `Click` | Open edit modal |

---

## 🎯 Common Workflows

### Workflow 1: Standard Generation
1. Select section, session, type, semestre
2. Click "Generer automatiquement"
3. Review calendar
4. Click "Valider"

### Workflow 2: With Manual Adjustments
1. Generate schedule
2. Identify conflicts (red warnings)
3. Drag exam to different time
4. Or click to change room
5. Verify no more conflicts
6. Click "Valider"

### Workflow 3: Regenerate
1. If not satisfied, change form parameters
2. Click "Generer automatiquement" again
3. Old BROUILLON exams are replaced
4. VALIDEE exams are preserved

---

## 📞 Support

**Documentation:**
- `IMPLEMENTATION_COMPLETE.md` - Full technical details
- `server/WORKFLOW_PLANIFICATION.md` - Backend workflow
- `server/TEST_RESULTS.md` - Test documentation

**Testing:**
```bash
# Run backend tests
cd server
pytest tests/test_planif.py -v

# Test with real data
python test_real_data_auto.py
```

**API Documentation:**
- Open `http://localhost:8000/docs` when backend is running
- Interactive API explorer with all endpoints

---

## ✅ Checklist

Before using the system, ensure:

- [ ] PostgreSQL is running
- [ ] Database has required data (sections, matières, salles, créneaux)
- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 3000
- [ ] `.env` file configured correctly
- [ ] Dependencies installed (backend and frontend)

---

**Ready to start?** Follow Step 1 above! 🚀

