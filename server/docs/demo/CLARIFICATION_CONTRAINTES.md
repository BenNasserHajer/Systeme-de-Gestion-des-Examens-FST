# 📋 Clarification des Contraintes

## 🔍 État Actuel

### Contraintes Annoncées vs Implémentées

| Source | Dures | Souples | Total |
|--------|-------|---------|-------|
| **README.md** | 11 | 7 | **18** |
| **Code actuel** | 11 | 4 | **15** |
| **Différence** | 0 | -3 | **-3** |

## ✅ Contraintes Implémentées (15)

### 11 Contraintes Dures (100% implémentées)

| ID | Description | Classe | Statut |
|----|-------------|--------|--------|
| C1 | Salle unique par créneau | `ContrainteSalleOccupee` | ✅ |
| C2 | Capacité salle ≥ effectif | `ContrainteCapaciteSalle` | ✅ |
| C3/C18 | Créneau dans période session | `ContrainteCreneauSession` | ✅ |
| C4 | Pas d'examen le dimanche | `ContraintePasDimanche` | ✅ |
| C6/C12 | Unicité (section_matiere, session, type) | `ContrainteSectionMatiereUnique` | ✅ |
| C7/C14 | Pas de chevauchement section | `ContrainteSectionUnique` | ✅ |
| C8 | Découpage obligatoire si nécessaire | `ContrainteDecoupageObligatoire` | ✅ |
| C11 | Matière éligible pour type épreuve | `ContrainteMatiereEligible` | ✅ |
| C15 | Durée épreuve ≤ durée créneau | `ContrainteDureeCreneau` | ✅ |
| C16 | section_matiere doit exister | `ContrainteSectionMatiereExists` | ✅ |
| C17 | Session éditable (BROUILLON/VALIDEE) | `ContrainteSessionEditable` | ✅ |

### 4 Contraintes Souples (57% implémentées)

| ID | Description | Classe | Statut |
|----|-------------|--------|--------|
| C5 | Préférence même bâtiment | `ContrainteBatimentConsecutif` | ✅ |
| C9 | Équilibrage groupes (écart ≤ 1) | `ContrainteEquilibrageGroupes` | ✅ |
| C10 | Éviter examens consécutifs | `ContrainteEspacementExamens` | ✅ |
| C13 | Répartition uniforme période | `ContrainteRepartitionUniforme` | ✅ |

## ⚠️ Contraintes Manquantes (3)

### Contraintes Mentionnées mais Non Implémentées

| ID | Description | Mentionné dans | Statut |
|----|-------------|----------------|--------|
| C5bis | Préférence salle du département | `planif_auto.py`, `ALGORITHME_PLANIFICATION.md` | ⚠️ Non implémentée |
| C? | Contrainte souple #6 | README (7 souples annoncées) | ⚠️ Non documentée |
| C? | Contrainte souple #7 | README (7 souples annoncées) | ⚠️ Non documentée |

## 📊 Analyse

### C5bis: Préférence Salle du Département

**Statut:** Mentionnée dans le code mais pas implémentée

**Localisation:**
```python
# PFA/server/app/algorithms/planif_auto.py (ligne 56)
CONTRAINTES_SOUPLES: Set[str] = {
    "C5",
    "C5bis",  # ← Mentionnée ici
    "C9",
    "C10",
    "C13",
}
```

**Documentation:**
- Mentionnée dans `ALGORITHME_PLANIFICATION.md`
- Décrite comme: "Préférence salle du département de la section"
- Scoring: Bonus -3 au score si salle du même département

**Implémentation suggérée:**
```python
class ContrainteDepartementSalle(Contrainte):
    """C5bis soft preference: prefer rooms from section's department."""
    
    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        if not planif.salles:
            return True
        
        # Get section department
        section_dept = contexte.get("section_departement_id")
        if section_dept is None:
            return True
        
        # Check if at least one room is from the same department
        for salle in planif.salles:
            if salle.departement_id == section_dept:
                return True
        
        return False
    
    def get_message(self) -> str:
        return "C5bis (souple): preferer les salles du departement de la section."
```

### Contraintes Souples #6 et #7

**Statut:** Non documentées

**Hypothèses possibles:**
1. **C?: Éviter les examens en fin de journée** (fatigue étudiants)
2. **C?: Préférence pour les créneaux matinaux** (meilleure concentration)
3. **C?: Minimiser le nombre de jours d'examen** (réduire la période)
4. **C?: Équilibrer la charge par jour** (éviter surcharge)
5. **C?: Préférence pour les salles proches** (minimiser déplacements)

## 🎯 Recommandations

### Option 1: Corriger la Documentation (Recommandé)

Mettre à jour le README pour refléter l'état actuel:

```markdown
### Contraintes

**11 Contraintes Dures** (obligatoires) :
- C1 à C17 (liste actuelle)

**4 Contraintes Souples** (préférables) :
- C5 : Préférence même bâtiment
- C9 : Équilibrage groupes (écart ≤ 1)
- C10 : Éviter examens consécutifs
- C13 : Répartition uniforme période
```

### Option 2: Implémenter les Contraintes Manquantes

1. **Implémenter C5bis** (priorité haute)
   - Classe déjà documentée
   - Logique claire
   - Impact: Optimisation affectation salles

2. **Définir et implémenter 2 contraintes supplémentaires** (priorité basse)
   - Identifier les besoins métier
   - Documenter les règles
   - Implémenter les classes

### Option 3: Approche Hybride (Recommandé)

1. Corriger immédiatement la documentation (15 contraintes)
2. Planifier l'implémentation de C5bis pour v1.1
3. Identifier les besoins pour les contraintes futures

## 📝 Conclusion

### État Actuel
- ✅ **15 contraintes fonctionnelles** (11 dures + 4 souples)
- ✅ **Toutes les contraintes critiques implémentées**
- ✅ **Algorithme de génération opérationnel**
- ⚠️ **Documentation à mettre à jour**

### Impact
- ✅ **Aucun impact sur la fonctionnalité**
- ✅ **Génération automatique fonctionne correctement**
- ✅ **Toutes les contraintes métier essentielles respectées**
- ⚠️ **Incohérence documentation vs code**

### Actions Recommandées

**Immédiat:**
1. ✅ Mettre à jour README.md (15 contraintes au lieu de 18)
2. ✅ Clarifier la documentation
3. ✅ Ajouter cette note de clarification

**Court terme (v1.1):**
1. Implémenter C5bis (préférence département)
2. Ajouter tests pour C5bis
3. Mettre à jour la documentation

**Moyen terme (v1.2):**
1. Identifier 2 contraintes souples supplémentaires
2. Documenter les règles métier
3. Implémenter et tester

---

**Date:** 2026-04-25  
**Version:** 1.0.0  
**Statut:** ✅ Clarifié
