# 🔧 Handling Exam Planning Conflicts

## 🎯 Understanding Conflicts

When you see conflicts like:
```
16 conflit(s) detecte(s)
[C1/C7/C8] No slot satisfies all hard constraints
```

This means the algorithm couldn't find available time slots for some exams due to:

### Constraint Types

**C1 - Room Conflict**: Salle already occupied at that time  
**C7 - Section Conflict**: Section already has an exam at that time  
**C8 - Insufficient Rooms**: Not enough rooms to split large groups  

---

## 🆕 New Feature: Manual Exam Addition

### What's New

When conflicts occur, you'll now see an **"Examens non planifiés"** (Unscheduled Exams) section showing:

```
┌─────────────────────────────────────────────────────────┐
│ ⚠️  Examens non planifiés (16)                          │
│                                                         │
│ Ces examens n'ont pas pu être planifiés automatiquement│
│ Cliquez sur un créneau vide pour les ajouter.          │
│                                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ IGL4 S1 Matiere Test 4  [Ajouter manuellement] │   │
│ └─────────────────────────────────────────────────┘   │
│ ┌─────────────────────────────────────────────────┐   │
│ │ IGL4 S1 Matiere Test 7  [Ajouter manuellement] │   │
│ └─────────────────────────────────────────────────┘   │
│ ...                                                     │
└─────────────────────────────────────────────────────────┘
```

### How to Add Exams Manually

**Option 1: Click "Ajouter manuellement" button**
1. Click the button next to the unscheduled exam
2. You'll be prompted to click on an empty calendar slot

**Option 2: Future Enhancement (Coming Soon)**
1. Click on an empty slot in the calendar
2. Modal opens with form to add exam
3. Select matière, duration, and room
4. Click "Créer l'examen"

---

## 💡 Solutions for Common Conflicts

### Problem: Not Enough Time Slots

**Symptoms:**
- Many exams unscheduled
- All available days are full

**Solutions:**

1. **Extend the session dates**
   ```sql
   UPDATE session 
   SET date_fin = '2026-01-20'  -- Add more days
   WHERE id = 1;
   ```

2. **Add more time slots (créneaux)**
   ```sql
   -- Add afternoon slots
   INSERT INTO creneau (session_id, date, heure_debut, heure_fin)
   VALUES 
     (1, '2026-01-07', '14:00:00', '16:00:00'),
     (1, '2026-01-07', '16:00:00', '18:00:00');
   ```

3. **Use more days**
   - Add Saturday slots if needed
   - Spread exams over more days


### Problem: Not Enough Rooms

**Symptoms:**
- [C8] Insufficient rooms error
- Large sections (100+ students)

**Solutions:**

1. **Add more rooms to the session**
   ```sql
   -- Check available rooms
   SELECT * FROM salle WHERE capacite >= 50;
   
   -- Add rooms to session
   INSERT INTO salle_session (session_id, salle_id)
   SELECT 1, code FROM salle WHERE capacite >= 50;
   ```

2. **Use larger amphitheaters**
   - Prioritize AMPHI rooms for large sections
   - Reserve smaller rooms for smaller groups

3. **Split exams into multiple time slots**
   - Manually schedule some exams at different times
   - Use morning and afternoon slots

### Problem: Section Already Busy

**Symptoms:**
- [C7] Section conflict
- Multiple exams scheduled at same time

**Solutions:**

1. **Drag exams to different times**
   - Use the calendar drag & drop
   - Move conflicting exams to empty slots

2. **Spread exams across more days**
   - Don't schedule too many exams per day
   - Leave gaps between exams

---

## 🎯 Best Practices

### Before Generation

1. **Check available resources**
   ```sql
   -- Count time slots
   SELECT COUNT(*) FROM creneau WHERE session_id = 1;
   
   -- Count rooms
   SELECT COUNT(*) FROM salle_session WHERE session_id = 1;
   
   -- Count matières to schedule
   SELECT COUNT(*) FROM section_matiere WHERE section_id = 2;
   ```

2. **Ensure sufficient capacity**
   - Time slots needed ≈ Number of matières
   - Rooms needed ≈ Max(section size / room capacity)

3. **Plan session duration**
   - 1 week = ~25 time slots (5 days × 5 slots/day)
   - 2 weeks = ~50 time slots

### During Generation

1. **Review conflicts immediately**
   - Check the "Examens non planifiés" section
   - Note which matières couldn't be scheduled

2. **Prioritize important exams**
   - Schedule high-coefficient exams first
   - Leave optional exams for manual addition

### After Generation

1. **Add unscheduled exams manually**
   - Use the "Ajouter manuellement" feature
   - Click on empty calendar slots

2. **Optimize the schedule**
   - Drag exams to better times
   - Balance the load across days

3. **Validate when ready**
   - Only validate when all exams are scheduled
   - Check for any remaining conflicts


---

## 🛠️ Quick Fixes

### Add More Time Slots (SQL)

```sql
-- Add a full week of morning slots (8-10, 10-12)
DO $$
DECLARE
  d DATE;
BEGIN
  FOR d IN 
    SELECT generate_series(
      '2026-01-07'::date, 
      '2026-01-15'::date, 
      '1 day'::interval
    )::date
  LOOP
    -- Morning slots
    INSERT INTO creneau (session_id, date, heure_debut, heure_fin)
    VALUES 
      (1, d, '08:00:00', '10:00:00'),
      (1, d, '10:00:00', '12:00:00')
    ON CONFLICT DO NOTHING;
    
    -- Afternoon slots (optional)
    INSERT INTO creneau (session_id, date, heure_debut, heure_fin)
    VALUES 
      (1, d, '14:00:00', '16:00:00'),
      (1, d, '16:00:00', '18:00:00')
    ON CONFLICT DO NOTHING;
  END LOOP;
END $$;
```

### Add All Available Rooms (SQL)

```sql
-- Add all rooms with capacity >= 30 to session
INSERT INTO salle_session (session_id, salle_id)
SELECT 1, code 
FROM salle 
WHERE capacite >= 30
ON CONFLICT DO NOTHING;
```

### Check Current Resources (SQL)

```sql
-- Summary of available resources
SELECT 
  (SELECT COUNT(*) FROM creneau WHERE session_id = 1) as creneaux,
  (SELECT COUNT(*) FROM salle_session WHERE session_id = 1) as salles,
  (SELECT COUNT(*) FROM section_matiere WHERE section_id = 2) as matieres,
  (SELECT SUM(nb_etudiants) FROM groupe WHERE section_id = 2) as etudiants;
```

---

## 📊 Example Scenario

### Situation
- Section: IGL4 (106 students)
- Matières: 28
- Available slots: 10
- Available rooms: 5
- **Result**: 16 conflicts

### Analysis
```
Required slots: 28
Available slots: 10
Missing: 18 slots ❌
```

### Solution Steps

1. **Add more time slots**
   ```sql
   -- Add 3 more days
   -- Each day = 4 slots (8-10, 10-12, 14-16, 16-18)
   -- Total new slots = 12
   ```

2. **Regenerate schedule**
   - Now have 22 slots total
   - Still need 6 more slots

3. **Add weekend or extend hours**
   ```sql
   -- Add Saturday
   INSERT INTO creneau (session_id, date, heure_debut, heure_fin)
   VALUES 
     (1, '2026-01-11', '08:00:00', '10:00:00'),
     (1, '2026-01-11', '10:00:00', '12:00:00'),
     (1, '2026-01-11', '14:00:00', '16:00:00');
   ```

4. **Regenerate again**
   - Now have 25 slots
   - Only 3 conflicts remaining

5. **Add remaining exams manually**
   - Use "Ajouter manuellement" for last 3 exams
   - Place in optimal time slots

6. **Validate**
   - All exams scheduled ✅
   - Click "Valider"

---

## 🎯 Summary

**When you see conflicts:**

1. ✅ **Check the "Examens non planifiés" section**
2. ✅ **Add more time slots or rooms to database**
3. ✅ **Regenerate the schedule**
4. ✅ **Use "Ajouter manuellement" for remaining exams**
5. ✅ **Drag & drop to optimize**
6. ✅ **Validate when complete**

**The new UI feature helps you:**
- See which exams are unscheduled
- Add them manually to empty slots
- Complete the schedule even with conflicts

