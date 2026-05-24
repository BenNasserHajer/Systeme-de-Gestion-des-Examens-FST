# Fix: Salle ID Bug in Surveillance Affectation

## Problem

Backend crashed with error when trying to auto-assign surveillants:

```
sqlalchemy.exc.DataError: (psycopg2.errors.InvalidTextRepresentation) 
ERREUR: syntaxe en entrée invalide pour le type integer : « AMPHI-INFO »
LINE 3: WHERE salle.id = 'AMPHI-INFO'
```

## Root Cause

In `server/app/routers/surveillances.py` line 141, the code was querying `Salle` by `id` field (integer), but `g.salle_id` contains **string codes** like 'AMPHI-INFO', not integer IDs.

This is because in the `PlanifSalle` model, `salle_id` is stored as a **string code**, not a foreign key to the integer ID.

## Solution

Changed line 141 in `server/app/routers/surveillances.py`:

**BEFORE (incorrect):**
```python
salle_orm = db.query(Salle).filter(Salle.id == g.salle_id).first()
```

**AFTER (correct):**
```python
salle_orm = db.query(Salle).filter(Salle.code == g.salle_id).first()
```

## Files Modified

- `server/app/routers/surveillances.py` (lines 141 and 1111)
- `server/app/gradio_surveillance_draft.py` (line 913)

**Note:** `server/app/crud/crud_salle.py` correctly uses both `Salle.id` (for integer ID lookups) and `Salle.code` (for string code lookups) - no changes needed.

## Testing

After this fix:
1. Restart the backend server
2. Test the affectation endpoint: `POST /api/surveillances/affecter-session`
3. The algorithm should now process planifications without crashing

## Next Steps

After confirming the fix works:
1. Fix data in database to resolve conflicts (all 12 planifications show conflicts):
   ```sql
   UPDATE planification_examen 
   SET section_departement_id = 1 
   WHERE session_id = 1 AND statut = 'VALIDEE';
   ```
2. Test complete workflow in frontend
3. Verify surveillants are correctly assigned

## Status

✅ **FIXED** - Backend code corrected, ready for testing
