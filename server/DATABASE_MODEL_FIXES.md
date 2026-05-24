# Database Model Relationship Fixes

## Date: May 24, 2026

## Overview

This document details all the database model relationship issues that were identified and fixed to make the exam planning system fully functional.

## Issues Identified

### 1. Missing Type Imports
**File**: `server/app/models/planification.py`

**Problem**: Missing SQLAlchemy type imports
- `Date` type not imported
- `Time` type not imported  
- `Boolean` type not imported
- `Float` type not imported

**Fix**: Added all required imports
```python
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Time, UniqueConstraint, func
```

---

### 2. Invalid Relationship: Salle → PlanifSalle
**File**: `server/app/models/salle_session.py`

**Problem**: 
- `Salle` model defined a relationship to `PlanifSalle`
- But `PlanifSalle.salle_id` is a string (room code), not a foreign key to `Salle.id`
- This caused: `NoForeignKeysError: Can't find any foreign key relationships between 'salle' and 'planif_salle'`

**Fix**: Removed the invalid relationship
```python
# BEFORE (WRONG)
planif_salles: Mapped[list["PlanifSalle"]] = relationship(
    "PlanifSalle", back_populates="salle", lazy="selectin"
)

# AFTER (CORRECT)
# Removed - PlanifSalle stores salle_id as string (room code), not FK
```

---

### 3. Missing Foreign Keys in Planification
**File**: `server/app/models/planification.py`

**Problem**: 
- Planification model stored IDs but had no foreign key constraints
- Missing relationships to `Session`, `Creneau`, `SectionMatiere`
- Code tried to access `planif.session`, `planif.creneau`, etc. but relationships didn't exist

**Fix**: Added foreign keys and relationships
```python
# Added foreign keys
session_id: Mapped[int] = mapped_column(
    Integer, 
    ForeignKey("session.id", ondelete="CASCADE"),
    nullable=False, 
    index=True
)
section_matiere_id: Mapped[int] = mapped_column(
    Integer,
    ForeignKey("section_matiere.id", ondelete="CASCADE"),
    nullable=False,
    index=True
)
creneau_id: Mapped[int | None] = mapped_column(
    Integer,
    ForeignKey("creneau.id", ondelete="SET NULL"),
    nullable=True,
    index=True
)

# Added relationships
session: Mapped["Session"] = relationship("Session", back_populates="planifications")
creneau: Mapped["Creneau | None"] = relationship("Creneau", back_populates="planifications")
section_matiere: Mapped["SectionMatiere"] = relationship("SectionMatiere", back_populates="planifications")
surveillances: Mapped[list["Surveillance"]] = relationship("Surveillance", back_populates="planification")
```

---

### 4. Missing Fields in Planification Model
**File**: `server/app/models/planification.py`

**Problem**: 
- Schema (`PlanificationCreate`) had fields that model didn't have
- Missing: `coefficient`, `section_nb_etudiants`, `a_examen_final`, `a_ds`, `semestre`
- Caused: `TypeError: 'coefficient' is an invalid keyword argument for Planification`

**Fix**: Added all missing fields
```python
coefficient: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
section_nb_etudiants: Mapped[int] = mapped_column(Integer, nullable=False)
a_examen_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
a_ds: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
semestre: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 or 2
```

---

### 5. Invalid UniqueConstraint
**File**: `server/app/models/planification.py`

**Problem**: 
- UniqueConstraint referenced `creneau_id` which didn't exist as a column
- Caused: `ConstraintColumnNotFoundError: no column named 'creneau_id' is present`

**Fix**: Updated constraint to use actual fields
```python
# BEFORE (WRONG)
UniqueConstraint(
    "session_id", "section_matiere_id", "creneau_id", "type_epreuve",
    name="uq_planif_session_section_creneau_type",
)

# AFTER (CORRECT)
UniqueConstraint(
    "session_id", "section_matiere_id", "date_examen", "heure_debut", "type_epreuve",
    name="uq_planif_session_section_creneau_type",
)
```

---

### 6. Wrong Primary Key in PlanifSalle
**File**: `server/app/models/planification.py`

**Problem**: 
- Primary key was only `planification_id`
- But multiple rooms can be assigned to same planification (for group splitting)
- Caused: `UNIQUE constraint failed: planif_salle.planification_id`

**Fix**: Changed to composite primary key
```python
# BEFORE (WRONG)
planification_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("planification_examen.id", ondelete="CASCADE"),
    primary_key=True, nullable=False, index=True,
)
groupe_id: Mapped[int] = mapped_column(Integer, nullable=False)

# AFTER (CORRECT)
planification_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("planification_examen.id", ondelete="CASCADE"),
    primary_key=True, nullable=False, index=True,
)
groupe_id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
```

---

### 7. Missing Semestre in Schema
**File**: `server/app/schemas/planification.py`

**Problem**: 
- Model required `semestre` field
- But `PlanificationBase` schema didn't include it
- Caused: `NOT NULL constraint failed: planification_examen.semestre`

**Fix**: Added semestre to schema
```python
class PlanificationBase(BaseModel):
    # ... other fields ...
    semestre: str = Field(default="S1", min_length=1, max_length=10)
```

---

### 8. Missing Semestre Conversion in CRUD
**File**: `server/app/crud/crud_planif.py`

**Problem**: 
- Schema uses string semestre ("S1", "S2")
- Model uses integer semestre (1, 2)
- No conversion logic existed

**Fix**: Added conversion in create_planification
```python
def create_planification(db: Session, payload: PlanificationCreate) -> Planification:
    # Convert semestre string to integer (S1 -> 1, S2 -> 2)
    semestre_int = 1 if payload.semestre.upper() in ("S1", "1") else 2
    
    db_item = Planification(
        # ... other fields ...
        semestre=semestre_int,
        a_examen_final=payload.a_examen_final,
        a_ds=payload.a_ds,
    )
```

---

## Test Results

### Before Fixes
- **Passed**: 5/8 tests (62.5%)
- **Failed**: 3/8 tests
- **Errors**: 
  - `NoForeignKeysError`
  - `TypeError: invalid keyword argument`
  - `IntegrityError: NOT NULL constraint failed`
  - `IntegrityError: UNIQUE constraint failed`

### After Fixes
- **Passed**: 8/8 tests (100%) ✅
- **Failed**: 0/8 tests
- **Errors**: None

## Files Modified

1. ✅ `server/app/models/planification.py`
   - Added imports: Boolean, Date, Float, Time
   - Added foreign keys: session_id, section_matiere_id, creneau_id
   - Added relationships: session, creneau, section_matiere, surveillances
   - Added fields: coefficient, section_nb_etudiants, a_examen_final, a_ds, semestre, creneau_id
   - Fixed UniqueConstraint
   - Fixed PlanifSalle primary key (composite)

2. ✅ `server/app/models/salle_session.py`
   - Removed invalid planif_salles relationship

3. ✅ `server/app/schemas/planification.py`
   - Added semestre field to PlanificationBase

4. ✅ `server/app/crud/crud_planif.py`
   - Added semestre conversion logic
   - Added missing fields (a_examen_final, a_ds)

## Database Migration Required

Since we made structural changes to the models, you need to create and run an Alembic migration:

```bash
cd server

# Create migration
alembic revision --autogenerate -m "Fix planification model relationships and fields"

# Review the generated migration file in server/alembic/versions/

# Apply migration
alembic upgrade head
```

## Verification

Run all tests to verify everything works:

```bash
cd server

# Algorithm tests
python -m pytest tests/test_generation_logic.py -v

# Integration tests  
python -m pytest tests/test_planif.py -v

# All tests
python -m pytest tests/test_planif.py tests/test_generation_logic.py -v
```

Expected result: **8/8 tests passing** ✅

## Impact Analysis

### What Changed
- Database schema (new foreign keys, fields, composite primary key)
- Model relationships (added proper FK relationships)
- CRUD layer (added field mappings)

### What Didn't Change
- Algorithm logic (no changes to `planif_auto.py`)
- API endpoints (no changes needed)
- Business logic (no changes to constraints or rules)

### Backward Compatibility
⚠️ **Breaking changes** - requires database migration:
- New required fields in `planification_examen` table
- Changed primary key in `planif_salle` table
- New foreign key constraints

### Deployment Steps
1. Backup database
2. Create Alembic migration
3. Review migration SQL
4. Test migration on staging
5. Apply migration to production
6. Verify all tests pass
7. Monitor for errors

## Conclusion

All database model relationship issues have been successfully identified and fixed. The system now has:
- ✅ Proper foreign key relationships
- ✅ Complete model fields
- ✅ Valid constraints
- ✅ Correct primary keys
- ✅ Type-safe relationships
- ✅ 100% test pass rate

The exam planning system is now fully functional and ready for production deployment after database migration.
