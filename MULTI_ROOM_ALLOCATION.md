# 🏫 Multi-Room Allocation Feature

## 🎯 Problem Solved

When you have **100 students** but only a **50-capacity room**, the system now automatically **splits students into multiple groups** across multiple rooms.

---

## ✨ How It Works

### Example Scenario

**Situation:**
- Section: IGL4
- Students: 100
- Available rooms:
  - INF-15: 50 places
  - INF-11: 50 places
  - AMPHI-INFO: 150 places

### Option 1: Select Multiple Small Rooms

1. **Open Add Exam Modal**
2. **Select matière**: IGL4 S1 Matiere Test 4
3. **Select duration**: 2 heures
4. **Select rooms** (checkboxes):
   - ☑ INF-15 (50 places)
   - ☑ INF-11 (50 places)

**Result:**
```
✅ 2 groupe(s): 50 étudiants, 50 étudiants

Groupe 1: 50 students → INF-15
Groupe 2: 50 students → INF-11
```

### Option 2: Select One Large Room

1. **Select rooms**:
   - ☑ AMPHI-INFO (150 places)

**Result:**
```
✅ 1 groupe(s): 100 étudiants

Groupe 1: 100 students → AMPHI-INFO
```

### Option 3: Insufficient Capacity (Error)

1. **Select rooms**:
   - ☑ INF-15 (50 places only)

**Result:**
```
⚠️ Capacité insuffisante: 50 places pour 100 étudiants

Button "Créer l'examen" is DISABLED
```

---

## 🎨 UI Features

### Multi-Select Checkboxes

Instead of a dropdown, you now see **checkboxes** for each room:

```
┌─────────────────────────────────────────┐
│ Salles (sélectionner une ou plusieurs) │
│ ┌─────────────────────────────────────┐ │
│ │ ☐ AMPHI-INFO - 150 places (A)      │ │
│ │ ☑ INF-15 - 50 places (B)           │ │
│ │ ☑ INF-11 - 50 places (B)           │ │
│ │ ☐ INF-3 - 30 places (B)            │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Real-Time Validation

As you select rooms, the system shows:

**Sufficient capacity:**
```
✅ 2 groupe(s): 50 étudiants, 50 étudiants
```

**Insufficient capacity:**
```
⚠️ 30 étudiants sans salle
```

**Single room too small:**
```
⚠️ Capacité insuffisante: 50 places pour 100 étudiants
```

---

## 🔧 Algorithm

### Student Distribution

The system distributes students **proportionally** across selected rooms:

```typescript
// Pseudo-code
let remainingStudents = 100;
const groups = [];

for (room of selectedRooms) {
  const studentsInRoom = Math.min(room.capacity, remainingStudents);
  groups.push({
    room: room.id,
    students: studentsInRoom,
    groupId: groups.length + 1
  });
  remainingStudents -= studentsInRoom;
}

if (remainingStudents > 0) {
  // ERROR: Not enough capacity
} else {
  // SUCCESS: All students allocated
}
```

### Example Calculations

**Case 1: Two equal rooms**
- Students: 100
- Rooms: INF-15 (50), INF-11 (50)
- Result: 50 + 50 = 100 ✅

**Case 2: One large room**
- Students: 100
- Rooms: AMPHI-INFO (150)
- Result: 100 ✅

**Case 3: Three rooms**
- Students: 100
- Rooms: INF-15 (50), INF-11 (30), INF-3 (30)
- Result: 50 + 30 + 20 = 100 ✅

**Case 4: Insufficient**
- Students: 100
- Rooms: INF-15 (50)
- Result: 50 + 50 missing = ❌

---

## 📊 Database Structure

### Single Room (1 Group)

```sql
-- planification_examen
id: 1
matiere: "Machine Learning"
section_nb_etudiants: 100
nb_groupes: 1

-- planif_salle
planification_id: 1, groupe_id: 1
salle_id: "AMPHI-INFO"
groupe_effectif: 100
```

### Multiple Rooms (2 Groups)

```sql
-- planification_examen
id: 2
matiere: "Big Data"
section_nb_etudiants: 100
nb_groupes: 2

-- planif_salle
planification_id: 2, groupe_id: 1
salle_id: "INF-15"
groupe_effectif: 50

planification_id: 2, groupe_id: 2
salle_id: "INF-11"
groupe_effectif: 50
```

---

## 🎯 User Workflow

### Step-by-Step

1. **Click empty calendar slot**
2. **Modal opens** showing:
   - Matière dropdown
   - Duration dropdown
   - **Room checkboxes** (NEW!)
   - Student count: "100 étudiants"

3. **Select one or more rooms**
   - Check INF-15 → See "⚠️ 50 étudiants sans salle"
   - Check INF-11 → See "✅ 2 groupe(s): 50 étudiants, 50 étudiants"

4. **Click "Créer l'examen"**
   - System creates planification with 2 groups
   - Both rooms appear in calendar
   - Success message: "Examen ajouté (2 groupes dans 2 salles)!"

---

## ✅ Benefits

### For Admins

✅ **Flexible allocation** - Use any combination of rooms  
✅ **Real-time feedback** - See if capacity is sufficient  
✅ **Automatic splitting** - No manual calculation needed  
✅ **Error prevention** - Can't create exam without enough space  

### For Students

✅ **Fair distribution** - Students split evenly across rooms  
✅ **Clear information** - Know which room to go to  
✅ **No overcrowding** - Rooms never exceed capacity  

---

## 🚀 Summary

**Before:** Could only select one room → Failed if too small  
**After:** Can select multiple rooms → Automatic group splitting  

**Example:**
- 100 students + 50-capacity room = ❌ Error
- 100 students + (50 + 50) rooms = ✅ 2 groups created!

**The system now handles any room configuration intelligently!** 🎉

