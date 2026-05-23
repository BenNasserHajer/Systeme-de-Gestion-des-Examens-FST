# ✅ Implémentation de la Contrainte C5bis

## 📋 Résumé

La contrainte **C5bis "Préférence salle du département"** a été implémentée avec succès.

**Date:** 2026-04-25  
**Statut:** ✅ Implémentée et testée  
**Type:** Contrainte souple (optimisation)

## 🎯 Description

**C5bis:** Préférer les salles du département de la section lors de l'affectation.

**Objectif:** Optimiser l'affectation des salles en privilégiant celles qui appartiennent au même département que la section, réduisant ainsi les déplacements et facilitant la logistique.

## 📊 Scoring

| Condition | Score | Description |
|-----------|-------|-------------|
| Salle du même département | **-3** | Bonus (préféré) |
| Salle partagée (dept = null) | **-1** | Petit bonus |
| Salle d'un autre département | **0** | Neutre |

**Note:** Un score négatif est meilleur (bonus), un score positif est une pénalité.

## 🔧 Modifications Apportées

### 1. Classe de Contrainte (`contraintes.py`)

```python
class ContrainteDepartementSalle(Contrainte):
    """C5bis soft preference: prefer rooms from section's department."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        section_departement_id = contexte.get("section_departement_id")
        
        if section_departement_id is None:
            return True
        
        if not planif.salles:
            return True
        
        for salle in planif.salles:
            departement_id = getattr(salle, "departement_id", None)
            if departement_id is None or departement_id == section_departement_id:
                return True
        
        return False

    def get_message(self) -> str:
        return "C5bis (souple): preferer les salles du departement de la section."
```

### 2. Enregistrement dans le Moteur (`contraintes.py`)

```python
def build_default_engine() -> ContrainteEngine:
    return ContrainteEngine([
        # ... contraintes dures ...
        ContrainteBatimentConsecutif(priorite=2, dure=False),
        ContrainteDepartementSalle(priorite=2, dure=False),  # ← Nouvelle
        ContrainteEquilibrageGroupes(priorite=2, dure=False),
        # ... autres contraintes souples ...
    ])
```

### 3. Scoring dans l'Algorithme (`planif_auto.py`)

```python
def score_souples(...) -> int:
    score = 0
    
    # ... autres pénalités ...
    
    # C5bis: Bonus if room is from section's department
    if sm.section.departement_id is not None:
        for attr in attributions:
            if attr.salle.departement_id == sm.section.departement_id:
                score -= 3  # Bonus pour salle du département
            elif attr.salle.departement_id is None:
                score -= 1  # Petit bonus pour salle partagée
    
    return score
```

### 4. Schémas Pydantic (`schemas/planification.py`)

```python
class PlanifSalleBase(BaseModel):
    salle_id: str
    salle_capacite: int
    salle_batiment: str | None
    salle_departement_id: int | None = None  # ← Nouveau champ
    groupe_id: int
    groupe_effectif: int

class PlanificationBase(BaseModel):
    # ... autres champs ...
    section_departement_id: int | None = None  # ← Nouveau champ
```

### 5. Modèles ORM (`models/planification.py`)

```python
class Planification(Base):
    # ... autres champs ...
    section_departement_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

class PlanifSalle(Base):
    # ... autres champs ...
    salle_departement_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
```

### 6. Migration Alembic (`004_add_departement_fields.py`)

```python
def upgrade() -> None:
    op.add_column('planifications', 
        sa.Column('section_departement_id', sa.Integer(), nullable=True))
    op.add_column('planif_salle', 
        sa.Column('salle_departement_id', sa.Integer(), nullable=True))
```

### 7. CRUD (`crud/crud_planif.py`)

```python
def create_planification(db: Session, payload: PlanificationCreate) -> Planification:
    db_item = Planification(
        # ... autres champs ...
        section_departement_id=payload.section_departement_id,
    )
    # ...

def _build_planif_salle_rows(...) -> list[PlanifSalle]:
    return [
        PlanifSalle(
            # ... autres champs ...
            salle_departement_id=item.salle_departement_id,
        )
        for item in salles
    ]
```

### 8. Service (`services/planif_service.py`)

```python
def _validate_payload(...) -> list[str]:
    errors, warnings = self.engine.verifier_toutes(
        payload,
        {
            "existing_planifs": existing,
            "exclude_planif_id": exclude_planif_id,
            "known_section_matiere_ids": None,
            "section_departement_id": payload.section_departement_id,  # ← Nouveau
        },
        self.db,
    )
```

### 9. Types TypeScript (`frontend/src/lib/types/planification.ts`)

```typescript
export type PlanifSalle = {
  // ... autres champs ...
  salle_departement_id: number | null;
};

export type Planification = {
  // ... autres champs ...
  section_departement_id: number | null;
};
```

## 🧪 Tests

### Test de la Contrainte

```bash
cd PFA/server
python test_generation_logic.py
```

**Résultat:**
```
✅ Contraintes configurées: 16
✅ Contraintes dures: 11/11
✅ Contraintes souples: 5/7
✅ C5bis implémentée et fonctionnelle
```

### Test d'Intégration

```python
# Exemple de planification avec département
payload = PlanificationCreate(
    section_id=101,
    section_departement_id=1,  # Département Informatique
    # ... autres champs ...
    salles=[
        PlanifSalleAssign(
            salle_id="S20A",
            salle_capacite=20,
            salle_departement_id=1,  # Même département → bonus -3
            groupe_id=1,
            groupe_effectif=18,
        ),
    ],
)
```

## 📈 Impact

### Avant C5bis
- **Contraintes:** 15 (11 dures + 4 souples)
- **Scoring:** Basé sur bâtiment, charge, espacement
- **Affectation:** Optimale mais sans considération du département

### Après C5bis
- **Contraintes:** 16 (11 dures + 5 souples)
- **Scoring:** Inclut la préférence département
- **Affectation:** Optimale avec priorité aux salles du département
- **Bonus:** -3 points pour salle du département, -1 pour salle partagée

### Exemple de Scoring

| Scénario | Score C5 | Score C5bis | Score Total |
|----------|----------|-------------|-------------|
| Même bâtiment + même département | -5 | -3 | **-8** (optimal) |
| Même bâtiment + salle partagée | -5 | -1 | **-6** (bon) |
| Même bâtiment + autre département | -5 | 0 | **-5** (acceptable) |
| Autre bâtiment + même département | 0 | -3 | **-3** (acceptable) |
| Autre bâtiment + autre département | 0 | 0 | **0** (neutre) |

## 🔄 Migration de la Base de Données

### Appliquer la Migration

```bash
cd PFA/server
alembic upgrade head
```

**Sortie attendue:**
```
INFO  [alembic.runtime.migration] Running upgrade 003 -> 004, add departement fields
```

### Vérifier la Migration

```sql
-- Vérifier les nouvelles colonnes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name IN ('planifications', 'planif_salle')
  AND column_name LIKE '%departement%';
```

**Résultat attendu:**
```
column_name              | data_type | is_nullable
-------------------------+-----------+-------------
section_departement_id   | integer   | YES
salle_departement_id     | integer   | YES
```

## ✅ Checklist d'Implémentation

- [x] Classe `ContrainteDepartementSalle` créée
- [x] Contrainte enregistrée dans `build_default_engine()`
- [x] Scoring mis à jour dans `score_souples()`
- [x] Champ `section_departement_id` ajouté à `PlanificationBase`
- [x] Champ `salle_departement_id` ajouté à `PlanifSalleBase`
- [x] Modèle ORM `Planification` mis à jour
- [x] Modèle ORM `PlanifSalle` mis à jour
- [x] Migration Alembic créée (`004_add_departement_fields.py`)
- [x] CRUD `create_planification` mis à jour
- [x] CRUD `_build_planif_salle_rows` mis à jour
- [x] Service `_validate_payload` mis à jour
- [x] Types TypeScript mis à jour
- [x] Tests passés avec succès
- [x] Documentation mise à jour

## 📚 Documentation Mise à Jour

- ✅ `CLARIFICATION_CONTRAINTES.md` - État des contraintes
- ✅ `test_generation_logic.py` - Tests mis à jour
- ✅ `IMPLEMENTATION_C5BIS.md` - Ce document

## 🎯 Prochaines Étapes

### Court Terme
1. ✅ Tester avec des données réelles
2. ✅ Vérifier l'impact sur les performances
3. ✅ Documenter les cas d'usage

### Moyen Terme
1. Identifier les 2 contraintes souples manquantes (C? #6 et #7)
2. Implémenter si nécessaire
3. Mettre à jour le README pour refléter 16 contraintes

### Long Terme
1. Ajouter des métriques de scoring dans les rapports
2. Interface admin pour configurer les poids des contraintes
3. Visualisation de l'impact des contraintes souples

## 🎉 Conclusion

La contrainte **C5bis** a été implémentée avec succès et est maintenant opérationnelle:

- ✅ **16 contraintes** au total (11 dures + 5 souples)
- ✅ **Scoring optimisé** avec préférence département
- ✅ **Tests passés** avec succès
- ✅ **Migration prête** pour la base de données
- ✅ **Frontend synchronisé** avec les nouveaux types

**L'algorithme de génération automatique est maintenant encore plus intelligent!**

---

**Date:** 2026-04-25  
**Version:** 1.1.0  
**Statut:** ✅ Implémenté et Testé
