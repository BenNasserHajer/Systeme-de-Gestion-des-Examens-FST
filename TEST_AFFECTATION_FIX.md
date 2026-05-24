# Testing Guide: Surveillance Affectation Fix

## What Was Fixed

Fixed critical bug where backend was querying `Salle` table by integer `id` field when it should use string `code` field. This caused the error:

```
ERREUR: syntaxe en entrée invalide pour le type integer : « AMPHI-INFO »
```

## Files Fixed

✅ `server/app/routers/surveillances.py` (2 locations)
✅ `server/app/gradio_surveillance_draft.py` (1 location)

## Testing Steps

### 1. Restart Backend Server

```bash
cd server
.venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

Wait for: `Application startup complete.`

### 2. Start Frontend (in new terminal)

```bash
cd frontend
npm run dev
```

Wait for: `Ready on http://localhost:3000`

### 3. Test Affectation Automatique

1. Open browser: http://localhost:3000/surveillance/affectation
2. Select **Session 1** (or your test session)
3. Click **"Lancer l'affectation automatique"**
4. **Expected Result:**
   - ✅ No more "AMPHI-INFO" error
   - ✅ Algorithm processes 12 planifications
   - ✅ Shows results (even if all in conflict due to data issues)

### 4. Check Backend Logs

Backend should show:
```
INFO: POST /api/surveillances/affecter-session HTTP/1.1 200 OK
```

**NOT:**
```
ERROR: sqlalchemy.exc.DataError: invalid input syntax for type integer: "AMPHI-INFO"
```

### 5. Verify Response Structure

The response should include:
```json
{
  "session_id": 1,
  "total_planifications": 12,
  "affectees_automatiquement": 0,
  "en_conflit": 12,
  "message": "...",
  "resultats": [...],
  "non_affectees": [...]
}
```

## Expected Behavior After Fix

### ✅ What Should Work Now

1. **No crash** - Algorithm runs to completion
2. **Processes all VALIDEE planifications** in the session
3. **Returns structured results** with groupes, salles, surveillants
4. **Shows conflicts** with reasons (e.g., "VOLUME_INSUFFISANT", "DEPT_EXTERNE")

### ⚠️ Known Data Issues (Not Related to This Fix)

All 12 planifications show conflicts because:
- `section_departement_id` is NULL in database
- Enseignants don't match department requirements
- Volume horaire insufficient

**To fix data issues, run:**
```sql
-- Set department for all VALIDEE planifications
UPDATE planification_examen 
SET section_departement_id = 1 
WHERE session_id = 1 AND statut = 'VALIDEE';

-- Verify
SELECT id, type_epreuve, section_departement_id, statut 
FROM planification_examen 
WHERE session_id = 1 AND statut = 'VALIDEE';
```

## Troubleshooting

### Issue: Still getting "failed to fetch"

**Check:**
1. Backend is running on port 8000
2. Frontend is running on port 3000
3. No firewall blocking localhost connections

**Test backend directly:**
```bash
curl -X POST http://localhost:8000/api/surveillances/affecter-session \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1}'
```

### Issue: "Aucune planification VALIDEE"

**Check database:**
```sql
SELECT COUNT(*) 
FROM planification_examen 
WHERE session_id = 1 AND statut = 'VALIDEE';
```

Should return > 0. If 0, you need to create test data.

### Issue: All conflicts, 0 surveillants affectés

This is a **data issue**, not a bug. The algorithm is working correctly but rejecting all enseignants due to:
- Department mismatch (section_departement_id is NULL)
- Insufficient volume horaire
- No disponibilités declared

**Solution:** Fix data as shown above.

## Success Criteria

✅ Backend doesn't crash with "AMPHI-INFO" error
✅ Algorithm processes all planifications
✅ Returns structured JSON response
✅ Frontend displays results (even if conflicts)
✅ Can open conflict resolution modal
✅ Can see list of available enseignants

## Next Steps After Successful Test

1. ✅ Verify fix works
2. 🔄 Fix database data (section_departement_id)
3. 🔄 Test with corrected data
4. 🔄 Verify surveillants are assigned
5. 🔄 Test manual conflict resolution
6. 🔄 Test complete workflow end-to-end

## Status

🔧 **READY FOR TESTING** - Code fixed, awaiting verification
