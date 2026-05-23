# 🔄 Guide d'Application de la Migration C5bis

**Date:** 2026-04-25  
**Migration:** `004_add_departement_fields.py`  
**Objectif:** Ajouter les champs département pour la contrainte C5bis

---

## 📋 Prérequis

### 1. Vérifier l'État Actuel

```bash
cd PFA/server
alembic current
```

**Sortie attendue:**
```
003 (head)
```

### 2. Vérifier les Migrations Disponibles

```bash
alembic history
```

**Sortie attendue:**
```
001 -> 002 -> 003 -> 004 (head)
```

---

## 🚀 Application de la Migration

### Étape 1: Sauvegarder la Base de Données (Recommandé)

```bash
# PostgreSQL
pg_dump -U postgres -d pfa_db > backup_before_004.sql

# Ou via psql
psql -U postgres -d pfa_db -c "\copy (SELECT * FROM planifications) TO 'planifications_backup.csv' CSV HEADER"
psql -U postgres -d pfa_db -c "\copy (SELECT * FROM planif_salle) TO 'planif_salle_backup.csv' CSV HEADER"
```

### Étape 2: Appliquer la Migration

```bash
cd PFA/server
alembic upgrade head
```

**Sortie attendue:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 003 -> 004, add departement fields
```

### Étape 3: Vérifier l'Application

```bash
alembic current
```

**Sortie attendue:**
```
004 (head)
```

---

## ✅ Vérification des Modifications

### 1. Vérifier les Colonnes Ajoutées

```sql
-- Se connecter à la base de données
psql -U postgres -d pfa_db

-- Vérifier la table planifications
\d planifications

-- Vérifier la table planif_salle
\d planif_salle

-- Ou via SQL
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'planifications' 
  AND column_name = 'section_departement_id';

SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'planif_salle' 
  AND column_name = 'salle_departement_id';
```

**Résultat attendu:**
```
column_name              | data_type | is_nullable
-------------------------+-----------+-------------
section_departement_id   | integer   | YES
salle_departement_id     | integer   | YES
```

### 2. Tester la Génération Automatique

```bash
cd PFA/server
python test_generation_logic.py
```

**Sortie attendue:**
```
✅ Contraintes configurées: 16
✅ Contraintes dures: 11/11
✅ Contraintes souples: 5/7
✅ C5bis implémentée et fonctionnelle
✅ Tests passés: 2/2 planifications générées
```

### 3. Tester l'API

```bash
# Démarrer le serveur
uvicorn app.main:app --reload

# Dans un autre terminal, tester l'endpoint
curl http://localhost:8000/health
```

**Ouvrir Swagger UI:**
```
http://localhost:8000/docs
```

---

## 🔄 Rollback (Si Nécessaire)

### Revenir à la Version Précédente

```bash
cd PFA/server
alembic downgrade -1
```

**Sortie attendue:**
```
INFO  [alembic.runtime.migration] Running downgrade 004 -> 003, add departement fields
```

### Vérifier le Rollback

```bash
alembic current
```

**Sortie attendue:**
```
003 (head)
```

### Restaurer depuis la Sauvegarde (Si Nécessaire)

```bash
# PostgreSQL
psql -U postgres -d pfa_db < backup_before_004.sql
```

---

## 📊 Impact de la Migration

### Tables Modifiées

| Table | Colonne Ajoutée | Type | Nullable |
|-------|-----------------|------|----------|
| `planifications` | `section_departement_id` | INTEGER | YES |
| `planif_salle` | `salle_departement_id` | INTEGER | YES |

### Données Existantes

- ✅ **Aucune perte de données** - Les colonnes sont nullable
- ✅ **Compatibilité ascendante** - Les anciennes planifications restent valides
- ✅ **Valeurs par défaut** - NULL pour les enregistrements existants

### Contrainte C5bis

**Comportement:**
- Si `section_departement_id` est NULL → Contrainte satisfaite (pas de préférence)
- Si `salle_departement_id` est NULL → Salle partagée (bonus -1)
- Si départements correspondent → Bonus -3
- Si départements différents → Score neutre (0)

---

## 🧪 Tests Post-Migration

### Test 1: Créer une Planification avec Département

```bash
# Via Swagger UI (http://localhost:8000/docs)
POST /api/planifications

{
  "session_id": 1,
  "section_id": 101,
  "section_matiere_id": 1001,
  "section_departement_id": 1,  // ← Nouveau champ
  "date_examen": "2026-06-02",
  "heure_debut": "08:30:00",
  "heure_fin": "10:30:00",
  "type_epreuve": "EXAMEN_FINAL",
  "salles": [
    {
      "salle_id": "S20A",
      "salle_capacite": 20,
      "salle_departement_id": 1,  // ← Nouveau champ (même département)
      "groupe_id": 1,
      "groupe_effectif": 18
    }
  ]
}
```

**Résultat attendu:**
- ✅ Planification créée avec succès
- ✅ Champs département enregistrés
- ✅ Contrainte C5bis appliquée (bonus -3)

### Test 2: Génération Automatique

```bash
POST /api/sessions/1/generer

{
  "type_epreuve": "EXAMEN_FINAL",
  "force": false
}
```

**Résultat attendu:**
- ✅ Planifications générées avec préférence département
- ✅ Salles du même département privilégiées
- ✅ Score optimisé avec C5bis

### Test 3: Vérifier les Données

```sql
-- Voir les planifications avec département
SELECT 
  id, 
  section_id, 
  section_departement_id, 
  date_examen, 
  matiere
FROM planifications
WHERE section_departement_id IS NOT NULL
LIMIT 5;

-- Voir les salles avec département
SELECT 
  ps.id,
  ps.planification_id,
  ps.salle_id,
  ps.salle_departement_id,
  p.section_departement_id
FROM planif_salle ps
JOIN planifications p ON ps.planification_id = p.id
WHERE ps.salle_departement_id IS NOT NULL
LIMIT 5;
```

---

## ⚠️ Problèmes Courants

### Problème 1: Migration Déjà Appliquée

**Erreur:**
```
alembic.util.exc.CommandError: Target database is not up to date.
```

**Solution:**
```bash
alembic current  # Vérifier la version actuelle
alembic history  # Voir l'historique
```

### Problème 2: Conflit de Colonne

**Erreur:**
```
sqlalchemy.exc.ProgrammingError: column "section_departement_id" already exists
```

**Solution:**
```bash
# La migration a déjà été appliquée
alembic current  # Confirmer la version
```

### Problème 3: Base de Données Non Accessible

**Erreur:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Vérifier les variables d'environnement
cat .env | grep DATABASE_URL
```

---

## 📚 Ressources

### Documentation
- **Implémentation C5bis:** `server/docs/demo/IMPLEMENTATION_C5BIS.md`
- **Contraintes:** `server/docs/demo/CLARIFICATION_CONTRAINTES.md`
- **Migration:** `server/alembic/versions/004_add_departement_fields.py`

### Commandes Utiles

```bash
# Voir l'historique complet
alembic history --verbose

# Voir le SQL généré (sans l'exécuter)
alembic upgrade head --sql

# Voir la version actuelle
alembic current

# Voir les migrations en attente
alembic heads

# Downgrade d'une version
alembic downgrade -1

# Downgrade à une version spécifique
alembic downgrade 003
```

---

## ✅ Checklist Post-Migration

- [ ] Migration appliquée avec succès (`alembic current` = 004)
- [ ] Colonnes vérifiées dans la base de données
- [ ] Tests de génération passés
- [ ] API démarrée sans erreur
- [ ] Swagger UI accessible
- [ ] Test de création de planification avec département
- [ ] Test de génération automatique
- [ ] Données existantes intactes
- [ ] Sauvegarde créée (recommandé)

---

## 🎉 Conclusion

Une fois la migration appliquée avec succès:

✅ **16 contraintes opérationnelles** (11 dures + 5 souples)  
✅ **C5bis fonctionnelle** avec scoring optimisé  
✅ **Compatibilité ascendante** préservée  
✅ **Prêt pour le développement P3**  

**La contrainte C5bis améliore l'affectation des salles en privilégiant celles du département de la section !**

---

**Date:** 2026-04-25  
**Version:** 1.0.0  
**Statut:** ✅ Prêt à Appliquer
