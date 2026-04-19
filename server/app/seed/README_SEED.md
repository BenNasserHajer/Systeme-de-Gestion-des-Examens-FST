# 📚 Guide d'Utilisation des Scripts de Seed

## 📋 Vue d'Ensemble

Ce dossier contient les scripts SQL pour initialiser la base de données avec des données de test.

---

## 📁 Scripts Disponibles

### 1. `seed_igl3.sql` - Section IGL3 (Cycle Ingénieur)

**Contenu** :
- ✅ Niveau : Cycle Ingénieur (3ème année)
- ✅ Section : IGL3 (60 étudiants)
- ✅ Groupes : 2 groupes (G1: 30 étudiants, G2: 30 étudiants)
- ✅ Matières : 20 matières (Algorithmique, Tech Web, Admin BD, etc.)
- ✅ Enseignants : 12 enseignants
- ✅ Enseignements : Liaisons enseignant ↔ matière

**Particularités** :
- ⚠️ **Français et Anglais ne passent PAS d'examen final** (a_examen_final = FALSE)
- ✅ Français et Anglais ont des DS uniquement
- ✅ 18 matières avec examen final
- ✅ 2 matières sans examen final (Français, Anglais)

**Exclusions** :
- ❌ Pas de planifications d'examens
- ❌ Pas de surveillances

---

### 2. `seed_igl4.sql` - Section IGL4 (Cycle Ingénieur)

**Contenu** :
- ✅ Niveau : Cycle Ingénieur (4ème année)
- ✅ Section : IGL4 (53 étudiants)
- ✅ Groupe : 1 groupe de 53 étudiants
- ✅ Matières : 13 matières (ML, Big Data, NoSQL, GraphQL, etc.)
- ✅ Enseignants : 12 enseignants
- ✅ Enseignements : Liaisons enseignant ↔ matière

**Exclusions** :
- ❌ Pas de planifications d'examens
- ❌ Pas de surveillances

---

## 🚀 Utilisation

### Méthode 1 : Via psql (Recommandé)

```bash
# Se connecter à la base de données
psql -d pfa_examens

# Exécuter le script
\i app/seed/seed_igl4.sql

# OU depuis le dossier seed
\i seed_igl4.sql

# Quitter
\q
```

### Méthode 2 : Via ligne de commande

```bash
# Depuis le dossier server
psql -d pfa_examens -f app/seed/seed_igl4.sql

# OU depuis le dossier seed
cd app/seed
psql -d pfa_examens -f seed_igl4.sql
```

### Méthode 3 : Via Python

```python
from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()
try:
    with open('app/seed/seed_igl4.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Exécuter le script
    db.execute(text(sql))
    db.commit()
    print("✅ Script exécuté avec succès")
except Exception as e:
    db.rollback()
    print(f"❌ Erreur : {e}")
finally:
    db.close()
```

---

## 📊 Données Créées

### IGL3 (60 étudiants)

#### Niveau

| Champ | Valeur |
|-------|--------|
| Libellé | Cycle Ingénieur |
| Année | 3 |
| Type Formation | IGL |
| Département | DSI (id=1) |

#### Section

| Champ | Valeur |
|-------|--------|
| Nom | IGL3 |
| Effectif | 60 étudiants |
| Niveau | Cycle Ingénieur (3ème année) |

#### Groupes

| Groupe | Effectif |
|--------|----------|
| G1 | 30 |
| G2 | 30 |

#### Matières (20 total, 18 avec examen)

| Code | Intitulé | Coef | Durée Examen | Examen Final |
|------|----------|------|--------------|--------------|
| IGL3-PROJET-NT | Projet d'application nouvelles technologies | 2.5 | 120 min | ✅ |
| IGL3-TECH-COMPILATION | Techniques de Compilation | 2.0 | 120 min | ✅ |
| IGL3-ADMIN-BD | Administration des BD | 2.0 | 120 min | ✅ |
| IGL3-ARCHI-LOGICIELLE | Architecture Logicielle | 2.0 | 120 min | ✅ |
| IGL3-ENTREPOTS | Entrepôts de données | 2.0 | 120 min | ✅ |
| IGL3-ALGORITHMIQUE | Algorithmique et complexité | 2.5 | 120 min | ✅ |
| IGL3-ING-SYSTEMES | Ingénierie des systèmes | 2.5 | 120 min | ✅ |
| IGL3-TECH-WEB | Technologie Web et multimédia | 2.0 | 120 min | ✅ |
| IGL3-PROG-LINEAIRE | Programmation linéaire | 2.0 | 120 min | ✅ |
| IGL3-MICROECONOMIE | Introduction à la microéconomie | 1.5 | 90 min | ✅ |
| IGL3-ANGLAIS | Anglais | 1.0 | 0 min | ❌ PAS D'EXAMEN |
| IGL3-FRANCAIS | Français | 1.0 | 0 min | ❌ PAS D'EXAMEN |
| ... | (+ 8 matières TD/TP) | ... | ... | ✅ |

**Note importante** : Français et Anglais ont des DS mais **PAS d'examen final**.

#### Enseignants (12)

| Nom | Prénom | Grade | Email |
|-----|--------|-------|-------|
| Moussa | F. | Maître de Conférences | f.moussa@fst.utm.tn |
| Hiaoui | Y. | Maître de Conférences | y.hiaoui@fst.utm.tn |
| Abbassi | F. | Maître de Conférences | f.abbassi@fst.utm.tn |
| Amdouni | Asma | Maître de Conférences | asma.amdouni@fst.utm.tn |
| Agrbi | A. | Maître Assistant | a.agrbi@fst.utm.tn |
| Zekri | M. | Maître de Conférences | m.zekri@fst.utm.tn |
| Krichen | N. | Maître de Conférences | n.krichen@fst.utm.tn |
| Faiech | Ines | Maître de Conférences | ines.faiech@fst.utm.tn |
| Hamzaoui | M. | Maître de Conférences | m.hamzaoui@fst.utm.tn |
| Blanco | R. | Maître de Conférences | r.blanco@fst.utm.tn |
| Omrane | Amina | Maître de Conférences | amina.omrane@fst.utm.tn |
| Jdellah | Soumaya | Professeur | soumaya.jdellah@fst.utm.tn |

---

### IGL4 (53 étudiants)

#### Niveau

| Champ | Valeur |
|-------|--------|
| Libellé | Cycle Ingénieur |
| Année | 4 |
| Type Formation | IGL |
| Département | DSI (id=1) |

### Section

| Champ | Valeur |
|-------|--------|
| Nom | IGL4 |
| Effectif | 53 étudiants |
| Niveau | Cycle Ingénieur (4ème année) |

### Groupe

| Champ | Valeur |
|-------|--------|
| Numéro | 1 |
| Effectif | 53 |
| Section | IGL4 |

### Matières (13)

| Code | Intitulé | Coef | Durée Examen |
|------|----------|------|--------------|
| IGL4-ML-DL | Machine Learning & Deep Learning | 2.5 | 120 min |
| IGL4-DEV-JEE | Développement JEE | 2.0 | 120 min |
| IGL4-OPT1-NOSQL | Option 1: NoSQL | 2.0 | 120 min |
| IGL4-ANGLAIS | Anglais | 1.0 | 90 min |
| IGL4-DROIT-ETH | Droit & Éthique Informatique | 1.5 | 90 min |
| IGL4-ING-IMAGE | Ingénierie de l'Image | 2.0 | 120 min |
| IGL4-PROJET-NT4 | Projet d'application NT4 | 2.5 | 120 min |
| IGL4-ENTREPRENEUR | Entreprenariat | 1.5 | 90 min |
| IGL4-FOUILLE-DATA | Fouille de données | 2.0 | 120 min |
| IGL4-BIG-DATA | Big Data | 2.5 | 120 min |
| IGL4-PROJET-NT4-V | Projet d'application NT4 (Vendredi) | 2.5 | 120 min |
| IGL4-OPT2-GRAPHQL | Option 2: GraphQL | 2.0 | 120 min |
| IGL4-ANALYSE-DATA | Analyse de données et application | 2.0 | 120 min |

### Enseignants (12)

| Nom | Prénom | Grade | Email |
|-----|--------|-------|-------|
| Younes | Sana | Maître de Conférences | sana.younes@fst.utm.tn |
| Fourati | Hend | Maître Assistant | hend.fourati@fst.utm.tn |
| Alaya | Houda | Maître de Conférences | houda.alaya@fst.utm.tn |
| Dammak | Nawel | Maître Assistant | nawel.dammak@fst.utm.tn |
| Gharbi | Asma | Maître de Conférences | asma.gharbi@fst.utm.tn |
| Abed | Rahma | Maître de Conférences | rahma.abed@fst.utm.tn |
| Ben Hassine | Med Ali | Professeur | medali.benhassine@fst.utm.tn |
| Ochi | Wejda | Maître de Conférences | wejda.ochi@fst.utm.tn |
| Ben Othman | Leila | Maître de Conférences | leila.benothman@fst.utm.tn |
| Azzabi | Fares | Maître Assistant | fares.azzabi@fst.utm.tn |
| Kchaou | Marwa | Maître de Conférences | marwa.kchaou@fst.utm.tn |
| Abbes | Heithem | Maître Assistant | heithem.abbes@fst.utm.tn |

---

## ✅ Vérification

### Vérifier IGL3

```sql
SELECT 
    s.id,
    s.nom,
    s.nb_etudiants,
    n.libelle AS niveau
FROM section s
JOIN niveau n ON n.id = s.niveau_id
WHERE s.nom = 'IGL3';
```

**Résultat Attendu** :
```
 id  | nom  | nb_etudiants |      niveau       
-----+------+--------------+-------------------
  X  | IGL3 |           60 | Cycle Ingénieur
```

### Vérifier les Matières IGL3

```sql
SELECT COUNT(*) AS nb_matieres_total,
       COUNT(CASE WHEN a_examen_final = TRUE THEN 1 END) AS nb_avec_examen,
       COUNT(CASE WHEN a_examen_final = FALSE THEN 1 END) AS nb_sans_examen
FROM section_matiere sm
JOIN section s ON s.id = sm.section_id
WHERE s.nom = 'IGL3';
```

**Résultat Attendu** :
```
 nb_matieres_total | nb_avec_examen | nb_sans_examen 
-------------------+----------------+----------------
                20 |             18 |              2
```

### Vérifier les Matières sans Examen (IGL3)

```sql
SELECT m.code, m.intitule
FROM section_matiere sm
JOIN section s ON s.id = sm.section_id
JOIN matiere m ON m.id = sm.matiere_id
WHERE s.nom = 'IGL3' AND sm.a_examen_final = FALSE;
```

**Résultat Attendu** :
```
     code      |  intitule  
---------------+------------
 IGL3-ANGLAIS  | Anglais
 IGL3-FRANCAIS | Français
```

### Vérifier IGL4

```sql
SELECT 
    s.id,
    s.nom,
    s.nb_etudiants,
    n.libelle AS niveau
FROM section s
JOIN niveau n ON n.id = s.niveau_id
WHERE s.nom = 'IGL4';
```

**Résultat Attendu** :
```
 id  | nom  | nb_etudiants |      niveau       
-----+------+--------------+-------------------
  X  | IGL4 |           53 | Cycle Ingénieur
```

### Vérifier les Matières IGL4

```sql
SELECT 
    s.id,
    s.nom,
    s.nb_etudiants,
    n.libelle AS niveau
FROM section s
JOIN niveau n ON n.id = s.niveau_id
WHERE s.nom = 'IGL4';
```

**Résultat Attendu** :
```
 id  | nom  | nb_etudiants |      niveau       
-----+------+--------------+-------------------
  X  | IGL4 |           53 | Cycle Ingénieur
```

### Vérifier les Matières

```sql
SELECT COUNT(*) AS nb_matieres
FROM section_matiere sm
JOIN section s ON s.id = sm.section_id
WHERE s.nom = 'IGL4';
```

**Résultat Attendu** :
```
 nb_matieres 
-------------
          13
```

### Vérifier les Enseignants

```sql
SELECT COUNT(DISTINCT e.id) AS nb_enseignants
FROM enseignement en
JOIN matiere m ON m.id = en.matiere_id
JOIN enseignant e ON e.id = en.enseignant_id
WHERE m.code LIKE 'IGL4-%';
```

**Résultat Attendu** :
```
 nb_enseignants 
----------------
             12
```

---

## 🧪 Test avec Gradio

### Test IGL3

Après avoir exécuté le script, testez avec Gradio :

```bash
# 1. Lancer Gradio
python -m app.gradio_planif_draft

# 2. Dans l'interface :
#    - Cliquer : "Charger données réelles (BD)"
#    - Sélectionner : Niveau "Cycle Ingénieur"
#    - Sélectionner : Section "IGL3"
#    - Sélectionner : Type "Examen Final"
#    - Générer en mode simulation

# 3. Résultat attendu :
#    - Planifications générées : 18 (Français et Anglais exclus)
#    - Conflits détectés : 0 (si créneaux et salles suffisants)
```

### Test IGL4

Après avoir exécuté le script, testez avec Gradio :

```bash
# 1. Lancer Gradio
python -m app.gradio_planif_draft

# 2. Dans l'interface :
#    - Cliquer : "Charger données réelles (BD)"
#    - Sélectionner : Niveau "Cycle Ingénieur"
#    - Sélectionner : Section "IGL4"
#    - Sélectionner : Type "Examen Final"
#    - Générer en mode simulation

# 3. Résultat attendu :
#    - Planifications générées : 13
#    - Conflits détectés : 0 (si créneaux et salles suffisants)
```

---

## 🔄 Réinitialisation

### Supprimer les Données IGL3

```sql
-- Supprimer les enseignements
DELETE FROM enseignement 
WHERE matiere_id IN (
    SELECT id FROM matiere WHERE code LIKE 'IGL3-%'
);

-- Supprimer les section_matiere
DELETE FROM section_matiere 
WHERE section_id IN (
    SELECT id FROM section WHERE nom = 'IGL3'
);

-- Supprimer les groupes
DELETE FROM groupe 
WHERE section_id IN (
    SELECT id FROM section WHERE nom = 'IGL3'
);

-- Supprimer la section
DELETE FROM section WHERE nom = 'IGL3';

-- Supprimer les matières
DELETE FROM matiere WHERE code LIKE 'IGL3-%';

-- Supprimer les enseignants (optionnel, si créés uniquement pour IGL3)
-- DELETE FROM enseignant WHERE email LIKE '%@fst.utm.tn';

-- Supprimer le niveau (optionnel)
-- DELETE FROM niveau WHERE libelle = 'Cycle Ingénieur' AND annee = 3;
```

### Supprimer les Données IGL4

```sql
-- Supprimer les enseignements
DELETE FROM enseignement 
WHERE matiere_id IN (
    SELECT id FROM matiere WHERE code LIKE 'IGL4-%'
);

-- Supprimer les section_matiere
DELETE FROM section_matiere 
WHERE section_id IN (
    SELECT id FROM section WHERE nom = 'IGL4'
);

-- Supprimer les groupes
DELETE FROM groupe 
WHERE section_id IN (
    SELECT id FROM section WHERE nom = 'IGL4'
);

-- Supprimer la section
DELETE FROM section WHERE nom = 'IGL4';

-- Supprimer les matières
DELETE FROM matiere WHERE code LIKE 'IGL4-%';

-- Supprimer les enseignants (optionnel, si créés uniquement pour IGL4)
-- DELETE FROM enseignant WHERE email LIKE '%@fst.utm.tn';

-- Supprimer le niveau (optionnel)
-- DELETE FROM niveau WHERE libelle = 'Cycle Ingénieur' AND annee = 4;
```

### Réexécuter les Scripts

```bash
# IGL3
psql -d pfa_examens -f app/seed/seed_igl3.sql

# IGL4
psql -d pfa_examens -f app/seed/seed_igl4.sql

# Les deux
psql -d pfa_examens -f app/seed/seed_igl3.sql
psql -d pfa_examens -f app/seed/seed_igl4.sql
```

---

## 📝 Notes Importantes

### Gestion des Conflits

Le script utilise `ON CONFLICT DO NOTHING` pour éviter les doublons :
- ✅ Peut être exécuté plusieurs fois sans erreur
- ✅ Ne crée pas de doublons
- ⚠️ Ne met pas à jour les données existantes

### Dépendances

Le script suppose que :
- ✅ La table `departement` existe avec `id=1` (DSI)
- ✅ Les tables `niveau`, `section`, `matiere`, etc. existent
- ✅ La base de données est migrée (Alembic)

### Encodage

Le script utilise l'encodage UTF-8 pour les caractères accentués :
- ✅ Fonctionne avec `psql` en UTF-8
- ⚠️ Vérifier l'encodage de la base : `SHOW client_encoding;`

---

## 🎯 Cas d'Usage

### Cas 1 : Initialisation Complète (IGL3 + IGL4)

```bash
# 1. Créer la base
createdb pfa_examens

# 2. Appliquer les migrations
alembic upgrade head

# 3. Charger les données de seed
psql -d pfa_examens -f app/seed/seed_igl3.sql
psql -d pfa_examens -f app/seed/seed_igl4.sql

# 4. Vérifier
psql -d pfa_examens -c "SELECT nom, nb_etudiants FROM section WHERE nom IN ('IGL3', 'IGL4');"
```

### Cas 2 : Ajout IGL3 à une Base Existante

```bash
# Exécuter le script sur une base existante
psql -d pfa_examens -f app/seed/seed_igl3.sql

# Le script ne créera que les données manquantes
```

### Cas 3 : Test de Génération IGL3

```bash
# 1. Charger les données
psql -d pfa_examens -f app/seed/seed_igl3.sql

# 2. Créer une session de test
psql -d pfa_examens -c "
INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut)
VALUES ('PRINCIPALE', '2025/2026', '2026-06-01', '2026-06-30', 'BROUILLON');
"

# 3. Créer des créneaux
psql -d pfa_examens -c "
INSERT INTO creneau (date, heure_debut, heure_fin, libelle)
VALUES 
    ('2026-06-02', '08:30', '10:30', 'Lundi 08:30-10:30'),
    ('2026-06-02', '11:00', '13:00', 'Lundi 11:00-13:00'),
    ('2026-06-03', '08:30', '10:30', 'Mardi 08:30-10:30');
"

# 4. Créer des salles
psql -d pfa_examens -c "
INSERT INTO salle (code, designation, capacite, batiment)
VALUES 
    ('AMPHI-INFO', 'Amphithéâtre Informatique', 150, 'Bâtiment Info'),
    ('S30A', 'Salle 30A', 30, 'Bâtiment A'),
    ('S30B', 'Salle 30B', 30, 'Bâtiment A');
"

# 5. Tester avec Gradio
python -m app.gradio_planif_draft
# Résultat attendu : 18 planifications (Français et Anglais exclus)
```

### Cas 4 : Test de Génération IGL4

```bash
# 1. Charger les données
psql -d pfa_examens -f app/seed/seed_igl4.sql

# 2. Créer une session de test
psql -d pfa_examens -c "
INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut)
VALUES ('PRINCIPALE', '2025/2026', '2026-06-01', '2026-06-30', 'BROUILLON');
"

# 3. Créer des créneaux
psql -d pfa_examens -c "
INSERT INTO creneau (date, heure_debut, heure_fin, libelle)
VALUES 
    ('2026-06-02', '08:30', '10:30', 'Lundi 08:30-10:30'),
    ('2026-06-02', '11:00', '13:00', 'Lundi 11:00-13:00'),
    ('2026-06-03', '08:30', '10:30', 'Mardi 08:30-10:30');
"

# 4. Créer des salles
psql -d pfa_examens -c "
INSERT INTO salle (code, designation, capacite, batiment)
VALUES 
    ('AMPHI-INFO', 'Amphithéâtre Informatique', 150, 'Bâtiment Info'),
    ('S30A', 'Salle 30A', 30, 'Bâtiment A'),
    ('S30B', 'Salle 30B', 30, 'Bâtiment A');
"

# 5. Tester avec Gradio
python -m app.gradio_planif_draft
```

---

## 📞 Support

- **Documentation** : Voir `QUICK_START.md`
- **Gradio** : Voir `GRADIO_GUIDE.md`
- **API** : http://127.0.0.1:8000/docs

---

**Bon seed ! 🌱**
