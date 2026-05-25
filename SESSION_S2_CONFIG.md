# Configuration Session S2 - Examens Semestre 2

## ✅ Session créée avec succès

### 📅 Informations de la session

- **ID Session**: 2
- **Type**: PRINCIPALE
- **Année universitaire**: 2025/2026
- **Période d'examens**: **11 mai 2026 → 23 mai 2026** (13 jours)
- **Statut**: BROUILLON
- **Nombre de créneaux**: 34 créneaux disponibles

---

## 📆 Calendrier des examens S2

### Semaine 1 : 11-16 mai 2026

| Jour | Date | Créneaux disponibles |
|------|------|---------------------|
| **Lundi** | 11 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Mardi** | 12 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Mercredi** | 13 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Jeudi** | 14 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Vendredi** | 15 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Samedi** | 16 mai | 08:00-10:00 · 10:30-12:30 |
| **Dimanche** | 17 mai | ❌ Pas d'examens (contrainte C4) |

### Semaine 2 : 18-23 mai 2026

| Jour | Date | Créneaux disponibles |
|------|------|---------------------|
| **Lundi** | 18 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Mardi** | 19 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Mercredi** | 20 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Jeudi** | 21 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Vendredi** | 22 mai | 08:00-10:00 · 10:30-12:30 · 14:00-16:00 |
| **Samedi** | 23 mai | 08:00-10:00 · 10:30-12:30 |

---

## 🎯 Caractéristiques des créneaux

- **Durée des créneaux**: 2 heures (120 minutes)
- **Créneaux par jour** (lun-ven): 3 créneaux
- **Créneaux par jour** (samedi): 2 créneaux
- **Horaires**:
  - Matin: 08:00 - 10:00
  - Midi: 10:30 - 12:30
  - Après-midi: 14:00 - 16:00 (sauf samedi)

---

## 🚀 Utilisation dans l'interface

### Pour planifier des examens S2 :

1. **Accéder à la planification** : `/planification`
2. **Sélectionner** :
   - Session : "PRINCIPALE 2025/2026" (ID: 2)
   - Semestre : **S2**
   - Section : Choisir la section
3. **Générer automatiquement** : L'algorithme utilisera les 34 créneaux disponibles
4. **Ajuster manuellement** : Glisser-déposer les examens si nécessaire
5. **Modifier** : Cliquer sur le bouton "✏️" qui apparaît au survol de chaque examen

---

## 📊 Capacité de planification

Avec 34 créneaux disponibles sur 13 jours :

- **Capacité théorique** : 34 examens maximum (1 examen par créneau)
- **Avec contrainte C10b** (max 2 examens/jour/section) :
  - Une section peut avoir jusqu'à 26 examens (2 × 13 jours)
- **Optimisation** : L'algorithme répartit automatiquement les examens en respectant :
  - Disponibilité des salles
  - Pas de conflits de créneaux
  - Préférence pour le même bâtiment (C5)
  - Préférence pour les salles du département (C5bis)
  - Espacement entre examens (C10)

---

## 🔧 Modifications apportées

### Fichiers modifiés :

1. **`server/app/seed/seed_data_v2.sql`**
   - Ajout de la session S2
   - Ajout de 34 créneaux pour mai 2026

2. **`server/add_session_s2.py`**
   - Script Python pour créer la session et les créneaux
   - Peut être réexécuté sans problème (idempotent)

3. **`frontend/src/components/planification/ExamEventCard.tsx`**
   - Ajout d'un bouton de modification visible au survol
   - Icône d'édition pour chaque examen

4. **`frontend/src/components/planification/EditExamModal.tsx`**
   - Modal amélioré avec 2 modes :
     - **Changer la salle** : Sélection parmi les salles disponibles
     - **Changer date/heure** : Modification de la date, heure et durée
   - Validation automatique des contraintes

---

## ✨ Nouvelles fonctionnalités

### Bouton de modification d'examen

- **Apparence** : Bouton "✏️" visible au survol de chaque carte d'examen
- **Couleur adaptative** : Change selon le statut (BROUILLON/VALIDEE/PUBLIEE)
- **Accès rapide** : Clic direct pour modifier sans glisser-déposer

### Modal d'édition amélioré

#### Mode 1 : Changer la salle
- Liste des salles disponibles pour le créneau
- Indication de disponibilité
- Capacité et bâtiment affichés

#### Mode 2 : Changer date/heure
- Sélection de la nouvelle date
- Modification de l'heure de début
- Ajustement de la durée (30-300 minutes)
- Validation automatique des contraintes

---

## 📝 Notes importantes

1. **Semestre dans les données** : Les matières doivent avoir `semestre = 2` ou `annee_sem` contenant "S2"
2. **Statut BROUILLON** : La session S2 est en brouillon, permettant toutes les modifications
3. **Pas d'examens le dimanche** : Le 17 mai est automatiquement exclu (contrainte C4)
4. **Réexécution** : Le script `add_session_s2.py` peut être réexécuté sans créer de doublons

---

## 🎓 Prochaines étapes

1. **Vérifier les matières S2** : S'assurer que les matières du semestre 2 sont bien configurées
2. **Tester la génération** : Générer un emploi du temps pour une section en S2
3. **Valider** : Une fois satisfait, passer le statut de BROUILLON à VALIDEE
4. **Publier** : Publier l'emploi du temps pour le rendre visible aux étudiants

---

## 🔍 Vérification

Pour vérifier que la session S2 est bien créée :

```sql
-- Vérifier la session
SELECT * FROM session WHERE date_debut = '2026-05-11';

-- Compter les créneaux S2
SELECT COUNT(*) FROM creneau 
WHERE date BETWEEN '2026-05-11' AND '2026-05-23';

-- Voir tous les créneaux S2
SELECT date, heure_debut, heure_fin, libelle 
FROM creneau 
WHERE date BETWEEN '2026-05-11' AND '2026-05-23'
ORDER BY date, heure_debut;
```

---

**Date de création** : 25 mai 2026  
**Statut** : ✅ Opérationnel
