# 🎯 New Feature: Manual Exam Scheduling

## ✨ What's New

When automatic generation creates conflicts, you can now **manually add exams** to the calendar!

### 3 New Features

1. **📋 Unscheduled Exams List** - See which exams couldn't be scheduled
2. **➕ Click Empty Slots** - Click on calendar to add exams
3. **🎯 Add Exam Modal** - Form to create exams manually

---

## 📋 Feature 1: Unscheduled Exams List

### What It Shows

When conflicts occur, you'll see an orange alert box:

```
┌──────────────────────────────────────────────────────────┐
│ ⚠️  Examens non planifiés (16)                           │
│                                                          │
│ Ces examens n'ont pas pu être planifiés automatiquement │
│ Cliquez sur un créneau vide dans le calendrier pour     │
│ les ajouter manuellement.                                │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ IGL4 S1 Matiere Test 4  [Ajouter manuellement]    │  │
│ └────────────────────────────────────────────────────┘  │
│ ┌────────────────────────────────────────────────────┐  │
│ │ IGL4 S1 Matiere Test 7  [Ajouter manuellement]    │  │
│ └────────────────────────────────────────────────────┘  │
│ ...                                                      │
└──────────────────────────────────────────────────────────┘
```

### How to Use

1. **Review the list** - See which exams need manual scheduling
2. **Click "Ajouter manuellement"** - Get reminder to click calendar
3. **Or click directly on calendar** - Add exam to specific slot

---

## ➕ Feature 2: Click Empty Slots

### What It Does

Empty calendar slots are now **clickable** and show hover effects.

### Visual Feedback

- **Hover**: Slot background changes to light gray
- **Cursor**: Changes to pointer (hand icon)
- **Tooltip**: "Cliquer pour ajouter un examen"

### How to Use

1. **Find an empty slot** in the calendar
2. **Hover over it** - See the hover effect
3. **Click** - Modal opens to add exam

### Example

```
Calendar Grid:
┌─────────────────────────────────────────┐
│ Time │ Monday    │ Tuesday   │ Wednesday│
├──────┼───────────┼───────────┼──────────┤
│ 08AM │ [Exam]    │ [Empty]   │ [Exam]   │
│      │           │  ← Click! │          │
├──────┼───────────┼───────────┼──────────┤
│ 10AM │ [Empty]   │ [Exam]    │ [Empty]  │
│      │  ← Click! │           │  ← Click!│
└─────────────────────────────────────────┘
```

---

## 🎯 Feature 3: Add Exam Modal

### What It Shows

When you click an empty slot, a modal opens:

```
┌─────────────────────────────────────────┐
│ Ajouter un examen manuellement     [X]  │
│ 2026-01-08 à 10:00                      │
├─────────────────────────────────────────┤
│                                         │
│ Matière                                 │
│ [IGL4 S1 Matiere Test 4 ▼]            │
│                                         │
│ Durée (minutes)                         │
│ [2 heures ▼]                           │
│                                         │
│ Salle                                   │
│ [AMPHI-INFO (150 places) ▼]           │
│                                         │
│ Horaire: 10:00 - 12:00                 │
│                                         │
├─────────────────────────────────────────┤
│              [Annuler] [Créer l'examen] │
└─────────────────────────────────────────┘
```

### Form Fields

1. **Matière** - Dropdown with unscheduled exams only
2. **Durée** - Choose: 1h, 1h30, 2h, 2h30, 3h
3. **Salle** - Dropdown with available rooms and capacity
4. **Horaire** - Auto-calculated based on duration

### How to Use

1. **Select matière** from dropdown
2. **Choose duration** (default: 2 hours)
3. **Select room** with enough capacity
4. **Review time** - Shows start and end time
5. **Click "Créer l'examen"** - Exam is added to calendar


---

## 🔧 Complete Workflow

### Scenario: 16 Conflicts After Generation

**Step 1: Generate Schedule**
```
Section: IGL4
Session: Principale 2025/2026
Type: Examen Final
Semestre: S1

Result: 10 exams created, 16 conflicts
```

**Step 2: Review Unscheduled Exams**
```
⚠️ Examens non planifiés (16)

- IGL4 S1 Matiere Test 4
- IGL4 S1 Matiere Test 7
- IGL4 S1 Matiere Test 10
- ... (13 more)
```

**Step 3: Add Exams Manually**

For each unscheduled exam:

1. **Find empty slot** in calendar
2. **Click on slot** → Modal opens
3. **Fill form:**
   - Matière: IGL4 S1 Matiere Test 4
   - Durée: 2 heures (120 minutes)
   - Salle: AMPHI-INFO (150 places)
4. **Click "Créer l'examen"**
5. **Exam appears** in calendar

**Step 4: Repeat**
- Add all 16 unscheduled exams
- Place them in optimal time slots
- Avoid conflicts with existing exams

**Step 5: Validate**
- All exams now scheduled ✅
- Click "Valider" button
- Status changes to VALIDEE

---

## 💡 Tips for Manual Scheduling

### Choose Good Time Slots

✅ **Good:**
- Empty slots with no nearby exams
- Morning slots (students are fresh)
- Spread across different days

❌ **Avoid:**
- Slots right after another exam for same section
- Late afternoon slots
- Too many exams on same day

### Select Appropriate Rooms

✅ **Good:**
- Room capacity ≥ number of students
- Amphitheaters for large groups (100+)
- Nearby rooms for same section

❌ **Avoid:**
- Rooms too small (students won't fit)
- Rooms too large (waste of space)
- Rooms in different buildings

### Duration Selection

Common durations:
- **1 hour (60 min)**: Quiz, DS
- **1h30 (90 min)**: Short exam
- **2 hours (120 min)**: Standard exam ⭐ Most common
- **2h30 (150 min)**: Long exam
- **3 hours (180 min)**: Final project

---

## 🎯 API Integration

### Backend Endpoint

The feature uses the existing endpoint:

```http
POST /api/planifications/
Content-Type: application/json

{
  "session_id": 1,
  "section_id": 2,
  "section_matiere_id": 0,
  "matiere": "IGL4 S1 Matiere Test 4",
  "type_epreuve": "EXAMEN_FINAL",
  "date_examen": "2026-01-08",
  "heure_debut": "10:00:00",
  "heure_fin": "12:00:00",
  "duree": 120,
  "session_date_debut": "2026-01-07",
  "session_date_fin": "2026-01-15",
  "section_nb_etudiants": 106,
  "mode_affectation": "MANUEL",
  "statut": "BROUILLON",
  "salles": [
    {
      "salle_id": "AMPHI-INFO",
      "salle_capacite": 150,
      "salle_batiment": "A",
      "groupe_id": 1,
      "groupe_effectif": 106
    }
  ]
}
```

### Key Fields

- **duree**: Duration in minutes (60, 90, 120, 150, 180)
- **mode_affectation**: "MANUEL" (indicates manual creation)
- **statut**: "BROUILLON" (draft, can be edited)
- **section_matiere_id**: 0 (no link to section_matiere)

---

## ✅ Summary

### What You Can Do Now

1. ✅ **See unscheduled exams** in orange alert box
2. ✅ **Click empty calendar slots** to add exams
3. ✅ **Fill form** with matière, duration, and room
4. ✅ **Duration is included** in the form (60-180 minutes)
5. ✅ **Exam is created** and appears in calendar
6. ✅ **Drag & drop** to adjust if needed
7. ✅ **Validate** when all exams are scheduled

### Benefits

- **No more blocked by conflicts** - Add exams manually
- **Full control** - Choose exact time and room
- **Flexible duration** - Select appropriate exam length
- **Visual feedback** - See changes immediately
- **Complete workflow** - From generation to validation

---

## 🚀 Next Steps

After implementing this feature, you can:

1. **Test with real data** - Generate schedule with conflicts
2. **Add exams manually** - Use the new modal
3. **Verify in database** - Check planification_examen table
4. **Validate schedule** - Finalize the planning

**The system is now complete with full manual scheduling support!** 🎉

