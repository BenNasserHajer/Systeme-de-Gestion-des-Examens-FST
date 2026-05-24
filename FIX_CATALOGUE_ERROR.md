# 🔧 Fix: Catalogue Loading Error

## ❌ Error

```
psycopg2.errors.UndefinedColumn: ERREUR: la colonne s.nb_etudiants n'existe pas
LINE 6: COALESCE(s.nb_etudiants, 0) AS effectif
```

## 🔍 Root Cause

The `section` table in the database **does not have** an `nb_etudiants` column.

**Actual schema:**
```sql
section:
  - id
  - nom
  - niveau_id
```

The student count is stored in the `groupe` table instead:
```sql
groupe:
  - id
  - section_id
  - nb_etudiants
  - ...
```

## ✅ Solution

Modified `catalogue_service.py` to calculate `effectif` by **summing** `nb_etudiants` from the `groupe` table:

### Before (Incorrect)
```sql
SELECT
    s.id AS section_id,
    COALESCE(s.nom, CONCAT('Section-', s.id)) AS section_label,
    COALESCE(n.libelle, '') AS niveau,
    COALESCE(s.nb_etudiants, 0) AS effectif  -- ❌ Column doesn't exist
FROM section s
LEFT JOIN niveau n ON n.id = s.niveau_id
ORDER BY section_label
```

### After (Correct)
```sql
SELECT
    s.id AS section_id,
    COALESCE(s.nom, CONCAT('Section-', s.id)) AS section_label,
    COALESCE(n.libelle, '') AS niveau,
    COALESCE(SUM(g.nb_etudiants), 0) AS effectif  -- ✅ Sum from groupe table
FROM section s
LEFT JOIN niveau n ON n.id = s.niveau_id
LEFT JOIN groupe g ON g.section_id = s.id
GROUP BY s.id, s.nom, n.libelle
ORDER BY section_label
```


## 📊 Test Results

### Before Fix
```
❌ Error: la colonne s.nb_etudiants n'existe pas
Source: fallback-static
Message: Erreur chargement BD: ... Catalogue statique utilise.
```

### After Fix
```
✅ Catalogue loaded successfully!
Source: database
Message: 2 section(s) chargee(s) depuis la base.
Sessions: 1
Sections: 2
Salles: 29
Creneaux: 66

Sections loaded:
  - IGL3: 100 students (niveau: Cycle Ingenieur) - 27 matières
  - IGL4: 106 students (niveau: Cycle Ingenieur) - 28 matières
```

## 🔧 Files Modified

- `server/app/services/catalogue_service.py`
  - Updated `_load_sections_and_matieres()` function
  - Added JOIN with `groupe` table
  - Added GROUP BY clause to sum student counts

## ✅ Verification

### Test Script
```bash
cd server
python test_catalogue.py
```

### API Endpoint
```bash
curl http://localhost:8000/api/referentiel/catalogue
```

**Response:**
```json
{
  "source": "database",
  "message": "2 section(s) chargee(s) depuis la base.",
  "sessions": [...],
  "sections": [
    {
      "label": "IGL3",
      "section_id": 1,
      "effectif": 100,
      "niveau": "Cycle Ingenieur"
    },
    {
      "label": "IGL4",
      "section_id": 2,
      "effectif": 106,
      "niveau": "Cycle Ingenieur"
    }
  ],
  ...
}
```

## 🎯 Impact

✅ **Frontend can now load catalogue from database**  
✅ **Generation form shows correct student counts**  
✅ **No more fallback to static data**  
✅ **All sections and matières loaded correctly**

## 📝 Notes

The `effectif` (student count) is calculated as:
- **SUM of all groupe.nb_etudiants** for that section
- If no groups exist, defaults to 0
- This matches the actual database schema design

