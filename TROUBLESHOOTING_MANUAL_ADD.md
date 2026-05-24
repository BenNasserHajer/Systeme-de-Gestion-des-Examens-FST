# 🔧 Troubleshooting: Manual Exam Addition

## ❌ Error: "Method Not Allowed"

### Problem
When clicking on an empty calendar slot and trying to create an exam, you get:
```
Method Not Allowed
```

### Root Cause
The frontend was calling `/planifications/` (with trailing slash) but the backend route is `/planifications` (without trailing slash).

### Solution
Fixed in `frontend/src/lib/api/planification.ts`:

**Before:**
```typescript
const response = await fetch(`${API_BASE}/planifications/`, {
```

**After:**
```typescript
const response = await fetch(`${API_BASE}/planifications`, {
```

---

## ✅ How to Test

### Step 1: Verify Backend is Running
```bash
cd server
uvicorn app.main:app --reload
```

Check: `http://localhost:8000/docs` should show API documentation

### Step 2: Verify Frontend is Running
```bash
cd frontend
npm run dev
```

Check: `http://localhost:3000/planification` should load

### Step 3: Test Manual Addition

1. **Generate schedule** with conflicts
2. **Click empty calendar slot**
3. **Fill form:**
   - Matière: Select from dropdown
   - Durée: 2 heures
   - Salles: Check one or more rooms
4. **Verify validation:**
   - Should show: "✅ X groupe(s): Y étudiants, Z étudiants"
5. **Click "Créer l'examen"**
6. **Check result:**
   - Should see success alert
   - Exam should appear in calendar

---

## 🐛 Common Issues

### Issue 1: "Section introuvable"

**Cause:** `sectionId` is null or invalid

**Solution:**
- Make sure you generated a schedule first
- Check that `sectionId` is set in the page state

### Issue 2: "Session introuvable"

**Cause:** `sessionId` is null or invalid

**Solution:**
- Make sure catalogue loaded correctly
- Check browser console for errors

### Issue 3: "Capacité insuffisante"

**Cause:** Selected rooms don't have enough capacity

**Solution:**
- Select more rooms (checkboxes)
- Or select a larger room
- System shows real-time validation

### Issue 4: Button Disabled

**Cause:** Form validation failed

**Check:**
- Matière selected?
- At least one room selected?
- Rooms have sufficient capacity?

---

## 🔍 Debugging

### Check API Call

Open browser DevTools (F12) → Network tab:

1. Click "Créer l'examen"
2. Look for POST request to `/planifications`
3. Check:
   - **Status**: Should be 201 Created
   - **Request payload**: Should have all fields
   - **Response**: Should return created planification

### Check Console Errors

Open browser DevTools (F12) → Console tab:

Look for:
- ❌ Network errors
- ❌ JavaScript errors
- ❌ API errors

### Check Backend Logs

In the terminal running `uvicorn`:

Look for:
- POST /api/planifications
- Status code (should be 201)
- Any error messages

---

## ✅ Expected Behavior

### Successful Creation

**Frontend:**
```
Alert: "Examen 'Machine Learning' ajouté avec succès (2 groupes dans 2 salles)!"
```

**Backend Log:**
```
INFO: POST /api/planifications 201 Created
```

**Database:**
```sql
-- New row in planification_examen
SELECT * FROM planification_examen WHERE mode_affectation = 'MANUEL';

-- New rows in planif_salle (one per group)
SELECT * FROM planif_salle WHERE planification_id = X;
```

**Calendar:**
- Exam card appears in the selected time slot
- Shows matière name, room(s), student count
- Can be dragged to different time
- Can be clicked to edit room

---

## 📝 Verification Checklist

After creating an exam manually:

- [ ] Success alert appears
- [ ] Exam card visible in calendar
- [ ] Correct time slot (date + hour)
- [ ] Correct duration (card height)
- [ ] Shows correct room(s)
- [ ] Shows correct student count
- [ ] Can drag to different time
- [ ] Can click to edit
- [ ] Status is BROUILLON
- [ ] Database has new row

---

## 🎯 Quick Fix Summary

**Problem:** Method Not Allowed  
**Cause:** Trailing slash in API URL  
**Fix:** Remove trailing slash from `/planifications/` → `/planifications`  
**File:** `frontend/src/lib/api/planification.ts`  
**Status:** ✅ Fixed

**Now try creating an exam again - it should work!** 🎉

