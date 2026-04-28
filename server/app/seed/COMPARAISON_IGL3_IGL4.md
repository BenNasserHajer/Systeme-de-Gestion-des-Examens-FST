# 📊 Comparaison IGL3 vs IGL4

## 📋 Vue d'Ensemble

| Critère | IGL3 | IGL4 |
|---------|------|------|
| **Année** | 3ème année | 4ème année |
| **Effectif** | 60 étudiants | 53 étudiants |
| **Groupes** | 2 (G1: 30, G2: 30) | 1 (53) |
| **Matières totales** | 20 | 13 |
| **Matières avec examen** | 18 | 13 |
| **Matières sans examen** | 2 (Français, Anglais) | 0 |
| **Enseignants** | 12 | 12 |

---

## 🎓 Matières

### IGL3 - 20 Matières (18 avec examen)

#### Matières AVEC Examen Final (18)

| Code | Intitulé | Coef | Durée |
|------|----------|------|-------|
| IGL3-PROJET-NT | Projet d'application nouvelles technologies | 2.5 | 120 min |
| IGL3-TECH-COMPILATION | Techniques de Compilation | 2.0 | 120 min |
| IGL3-ADMIN-BD | Administration des BD | 2.0 | 120 min |
| IGL3-ARCHI-LOGICIELLE | Architecture Logicielle | 2.0 | 120 min |
| IGL3-ENTREPOTS | Entrepôts de données | 2.0 | 120 min |
| IGL3-ALGORITHMIQUE | Algorithmique et complexité | 2.5 | 120 min |
| IGL3-ING-SYSTEMES | Ingénierie des systèmes | 2.5 | 120 min |
| IGL3-TECH-WEB | Technologie Web et multimédia | 2.0 | 120 min |
| IGL3-PROG-LINEAIRE | Programmation linéaire | 2.0 | 120 min |
| IGL3-MICROECONOMIE | Introduction à la microéconomie | 1.5 | 90 min |
| ... | (+ 8 matières TD/TP) | ... | ... |

#### Matières SANS Examen Final (2)

| Code | Intitulé | DS | Examen Final |
|------|----------|----|--------------| 
| IGL3-ANGLAIS | Anglais | ✅ | ❌ |
| IGL3-FRANCAIS | Français | ✅ | ❌ |

**Note** : Ces matières ont des DS mais **ne passent pas d'examen final**.

---

### IGL4 - 13 Matières (toutes avec examen)

| Code | Intitulé | Coef | Durée |
|------|----------|------|-------|
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

**Note** : Toutes les matières IGL4 ont un examen final, y compris l'Anglais.

---

## 👨‍🏫 Enseignants

### IGL3 - 12 Enseignants

| Nom | Prénom | Grade |
|-----|--------|-------|
| Moussa | F. | Maître de Conférences |
| Hiaoui | Y. | Maître de Conférences |
| Abbassi | F. | Maître de Conférences |
| Amdouni | Asma | Maître de Conférences |
| Agrbi | A. | Maître Assistant |
| Zekri | M. | Maître de Conférences |
| Krichen | N. | Maître de Conférences |
| Faiech | Ines | Maître de Conférences |
| Hamzaoui | M. | Maître de Conférences |
| Blanco | R. | Maître de Conférences |
| Omrane | Amina | Maître de Conférences |
| Jdellah | Soumaya | Professeur |

### IGL4 - 12 Enseignants

| Nom | Prénom | Grade |
|-----|--------|-------|
| Younes | Sana | Maître de Conférences |
| Fourati | Hend | Maître Assistant |
| Alaya | Houda | Maître de Conférences |
| Dammak | Nawel | Maître Assistant |
| Gharbi | Asma | Maître de Conférences |
| Abed | Rahma | Maître de Conférences |
| Ben Hassine | Med Ali | Professeur |
| Ochi | Wejda | Maître de Conférences |
| Ben Othman | Leila | Maître de Conférences |
| Azzabi | Fares | Maître Assistant |
| Kchaou | Marwa | Maître de Conférences |
| Abbes | Heithem | Maître Assistant |

---

## 🎯 Génération Automatique

### IGL3 - Résultat Attendu

```bash
# Générer avec Gradio
python -m app.gradio_planif_draft

# Sélectionner : IGL3, Examen Final
# Résultat attendu :
# - Planifications générées : 18
# - Conflits : 0 (si ressources suffisantes)
# - Matières exclues : Français, Anglais
```

**Explication** :
- 20 matières au total
- 2 matières sans examen (Français, Anglais)
- **18 planifications** à générer

### IGL4 - Résultat Attendu

```bash
# Générer avec Gradio
python -m app.gradio_planif_draft

# Sélectionner : IGL4, Examen Final
# Résultat attendu :
# - Planifications générées : 13
# - Conflits : 0 (si ressources suffisantes)
# - Toutes les matières incluses
```

**Explication** :
- 13 matières au total
- 0 matière sans examen
- **13 planifications** à générer

---

## 🔍 Différences Clés

### 1. Gestion des Langues

| Aspect | IGL3 | IGL4 |
|--------|------|------|
| **Français** | DS uniquement, pas d'examen | Pas de cours de Français |
| **Anglais** | DS uniquement, pas d'examen | Examen final (90 min) |

### 2. Organisation des Groupes

| Aspect | IGL3 | IGL4 |
|--------|------|------|
| **Nombre de groupes** | 2 (G1, G2) | 1 |
| **Effectif par groupe** | 30 étudiants | 53 étudiants |
| **Découpage nécessaire** | Possible pour certaines matières | Probable pour la plupart des matières |

### 3. Complexité de Planification

| Critère | IGL3 | IGL4 |
|---------|------|------|
| **Matières à planifier** | 18 | 13 |
| **Groupes** | 2 | 1 |
| **Complexité** | Moyenne | Faible |
| **Découpage automatique** | Moins fréquent (30/groupe) | Plus fréquent (53 total) |

---

## 📊 Statistiques

### Charge de Travail

| Métrique | IGL3 | IGL4 |
|----------|------|------|
| **Créneaux nécessaires (min)** | 18 × 2h = 36h | 13 × 2h = 26h |
| **Salles nécessaires** | Variable (2 groupes) | Variable (découpage) |
| **Surveillants nécessaires** | ~36 (2 par créneau) | ~26 (2 par créneau) |

### Durée des Examens

| Durée | IGL3 | IGL4 |
|-------|------|------|
| **90 min** | 1 matière (Microéconomie) | 3 matières (Anglais, Droit, Entrepreneur) |
| **120 min** | 17 matières | 10 matières |

---

## 🧪 Tests Recommandés

### Test 1 : Génération IGL3 Seule

```bash
# 1. Charger IGL3
psql -d pfa_examens -f app/seed/seed_igl3.sql

# 2. Générer avec Gradio
python -m app.gradio_planif_draft

# 3. Vérifier : 18 planifications
```

### Test 2 : Génération IGL4 Seule

```bash
# 1. Charger IGL4
psql -d pfa_examens -f app/seed/seed_igl4.sql

# 2. Générer avec Gradio
python -m app.gradio_planif_draft

# 3. Vérifier : 13 planifications
```

### Test 3 : Génération IGL3 + IGL4 Simultanée

```bash
# 1. Charger les deux
psql -d pfa_examens -f app/seed/seed_igl3.sql
psql -d pfa_examens -f app/seed/seed_igl4.sql

# 2. Générer IGL3 d'abord
# 3. Générer IGL4 ensuite
# 4. Vérifier : 18 + 13 = 31 planifications totales
```

---

## 💡 Recommandations

### Pour IGL3

1. **Vérifier l'exclusion** : Confirmer que Français et Anglais ne sont pas planifiés
2. **Gérer les groupes** : Prévoir des salles pour 2 groupes de 30
3. **Créneaux suffisants** : Minimum 18 créneaux de 2h

### Pour IGL4

1. **Découpage automatique** : Prévoir plusieurs salles (53 étudiants)
2. **Salles de grande capacité** : Amphithéâtre recommandé
3. **Créneaux suffisants** : Minimum 13 créneaux de 2h

### Pour les Deux

1. **Créneaux distincts** : Éviter les chevauchements entre IGL3 et IGL4
2. **Salles partagées** : Planifier IGL3 et IGL4 à des moments différents
3. **Période suffisante** : Minimum 8 jours pour les deux sections

---

## 📞 Support

- **Documentation Seed** : `README_SEED.md`
- **Guide Gradio** : `../../docs/guides/GRADIO_GUIDE.md`
- **API Documentation** : `../../docs/api/API_PLANIFICATION.md`

---

**📊 Comparaison complète IGL3 vs IGL4 !**
