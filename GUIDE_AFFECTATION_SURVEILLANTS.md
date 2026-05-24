# 📘 Guide d'Affectation des Surveillants

## 🎯 Objectif

Créer une interface **user-friendly** pour affecter automatiquement les surveillants aux examens, avec possibilité de résoudre manuellement les conflits.

---

## 💡 Idée Principale

### Workflow en 3 Étapes

```
1️⃣ SÉLECTION          2️⃣ AFFECTATION AUTO      3️⃣ RÉSOLUTION MANUELLE
   ↓                      ↓                         ↓
Choisir session    →  Algorithme traite    →  Résoudre conflits
et section            tous les examens         un par un
```

---

## 🎨 Interface Proposée

### Étape 1 : Formulaire de Sélection

```
┌─────────────────────────────────────────────┐
│  Session:  [Principale 2025/2026 ▼]        │
│  Section:  [IGL3 ▼]  (optionnel)           │
│                                             │
│  [🤖 Affecter Automatiquement]              │
└─────────────────────────────────────────────┘
```

**Actions:**
- Sélectionner la session d'examens
- Optionnellement filtrer par section
- Cliquer pour lancer l'affectation automatique

---

### Étape 2 : Résumé Visuel

Après l'affectation, affichage d'un résumé coloré :

```
┌─────────────────────────────────────────────┐
│  ℹ️ Résumé de l'affectation                 │
│                                             │
│  Affectation terminée pour 24 examens      │
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │   24    │  │   18    │  │    6    │    │
│  │  Total  │  │ Complets│  │ Conflits│    │
│  └─────────┘  └─────────┘  └─────────┘    │
└─────────────────────────────────────────────┘
```

**Indicateurs:**
- 🟢 **Complets** : Tous les surveillants sont affectés
- 🔴 **Conflits** : Il manque des surveillants

---

### Étape 3 : Tableau des Résultats

Tableau avec code couleur pour identifier rapidement les problèmes :

```
┌────────────────────────────────────────────────────────────────────┐
│ Statut     │ Matière        │ Section │ Date/Heure  │ Surveillants │
├────────────────────────────────────────────────────────────────────┤
│ ✓ Complet  │ Big Data       │ IGL3    │ 07/01 08:00 │ 2 / 2        │
│ ⚠ Partiel  │ Sécurité IOT   │ IGL3    │ 07/01 10:30 │ 1 / 2  [→]   │
│ ✗ Conflit  │ Optimisation   │ IGL4    │ 08/01 08:00 │ 0 / 3  [→]   │
│ ✓ Complet  │ Cloud          │ IGL3    │ 08/01 10:30 │ 2 / 2        │
└────────────────────────────────────────────────────────────────────┘
```

**Code Couleur:**
- 🟢 **Vert** : Complet (tous les surveillants affectés)
- 🟡 **Jaune** : Partiel (manque quelques surveillants)
- 🔴 **Rouge** : Conflit (aucun ou très peu de surveillants)

**Action:**
- Cliquer sur `[→]` pour résoudre manuellement le conflit

---

## 🔧 Modal de Résolution Manuelle

Quand on clique sur "Résoudre" pour un examen en conflit :

```
┌──────────────────────────────────────────────────────────┐
│  Résolution Manuelle du Conflit                    [✕]  │
├──────────────────────────────────────────────────────────┤
│  Optimisation Combinatoire - IGL4                       │
│  2026-01-08 • 08:00 - 10:00                             │
│                                                          │
│  ⚠️ Besoin de 3 surveillants (0 affectés)               │
│                                                          │
│  Rechercher: [_____________]  Département: [Tous ▼]     │
│                                                          │
│  12 enseignants disponibles (2 sélectionnés)            │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ ☑ Abed Rahma                          12.5h        │ │
│  │   Professeur • Informatique           restant      │ │
│  │                                                     │ │
│  │ ☑ Ben Ali Mohamed                     8.0h         │ │
│  │   Maître Assistant • Informatique     restant      │ │
│  │   ⚠ Indisponibilité déclarée ce jour               │ │
│  │                                                     │ │
│  │ ☐ Trabelsi Fatma                      15.0h        │ │
│  │   Professeur • Informatique           restant      │ │
│  │                                                     │ │
│  │ ☐ Gharbi Ahmed                        3.5h         │ │
│  │   Maître de Conférences • Math        restant      │ │
│  │   ⚠ Département externe                            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  [Annuler]              [Affecter 2 enseignants]        │
└──────────────────────────────────────────────────────────┘
```

### Fonctionnalités du Modal

1. **Informations de l'Examen**
   - Matière et section
   - Date et heure
   - Nombre de surveillants manquants

2. **Filtres**
   - **Recherche** : Chercher par nom, prénom, département
   - **Département** : Filtrer par département spécifique

3. **Liste des Enseignants**
   - Checkbox pour sélectionner
   - Nom, grade, département
   - **Volume horaire restant** (en heures)
   - **Avertissements** si nécessaire :
     - ⚠ Indisponibilité déclarée
     - ⚠ Département externe
     - ⚠ Volume horaire faible

4. **Tri Intelligent**
   - Par volume restant (décroissant)
   - Enseignants du même département en premier
   - Ordre alphabétique

5. **Validation**
   - Bouton désactivé si aucune sélection
   - Affiche le nombre d'enseignants sélectionnés
   - Validation en temps réel

---

## 🚀 Comment ça Marche ?

### 1. Affectation Automatique

```
User clique "Affecter Automatiquement"
         ↓
Backend reçoit la requête
         ↓
Algorithme traite chaque examen:
  1. Récupère les enseignants du département
  2. Applique les 5 contraintes:
     - C1: Volume horaire suffisant
     - C2: Pas de conflit de matière
     - C3: Disponibilité temporelle
     - C4: Non-simultanéité
     - C5: Département de l'examen
  3. Trie par volume restant
  4. Sélectionne N surveillants
  5. Insère en base de données
         ↓
Retourne les résultats
         ↓
Frontend affiche:
  - Résumé (total, complets, conflits)
  - Tableau avec code couleur
```

### 2. Résolution Manuelle

```
User clique "Résoudre" sur un conflit
         ↓
Backend récupère les enseignants disponibles:
  - Vérifie contrainte C4 (non-simultanéité) STRICTE
  - Vérifie indisponibilité (avertissement)
  - Calcule volume restant
         ↓
Modal s'ouvre avec la liste
         ↓
User sélectionne des enseignants
         ↓
User clique "Affecter"
         ↓
Backend valide et insère:
  - Si conflit → Erreur + Rollback
  - Si OK → Insertion en BD
         ↓
Frontend rafraîchit le tableau
```

---

## ✅ Avantages de cette Solution

### Pour l'Utilisateur

1. **Simplicité**
   - Interface en 3 étapes claires
   - Pas de configuration complexe
   - Workflow intuitif

2. **Rapidité**
   - Affectation automatique en quelques secondes
   - Résolution manuelle ciblée uniquement sur les conflits
   - Filtres pour trouver rapidement le bon enseignant

3. **Visibilité**
   - Code couleur immédiat
   - Résumé visuel
   - Avertissements clairs

4. **Contrôle**
   - Automatisation pour gagner du temps
   - Résolution manuelle pour les cas complexes
   - Décisions éclairées grâce aux informations affichées

### Pour le Système

1. **Fiabilité**
   - Validation des contraintes
   - Gestion des erreurs
   - Rollback en cas d'échec

2. **Performance**
   - Algorithme optimisé
   - Chargement progressif
   - Pagination automatique

3. **Maintenabilité**
   - Code modulaire
   - API RESTful
   - Documentation complète

---

## 📊 Exemples Concrets

### Exemple 1 : Tout se Passe Bien

```
Session: Principale 2025/2026
Section: IGL3

Action: Clic sur "Affecter Automatiquement"

Résultat:
✓ 12 examens traités
✓ 12 examens complets
✓ 0 conflit

→ Aucune action manuelle nécessaire !
→ Tous les surveillants sont affectés automatiquement
```

### Exemple 2 : Quelques Conflits

```
Session: Principale 2025/2026
Section: IGL4

Action: Clic sur "Affecter Automatiquement"

Résultat:
✓ 15 examens traités
✓ 12 examens complets
⚠ 3 conflits

Raisons des conflits:
- Examen 1: Volume horaire épuisé pour 2 enseignants
- Examen 2: Indisponibilité déclarée
- Examen 3: Conflit de simultanéité

Action manuelle:
1. Clic sur "Résoudre" pour Examen 1
2. Sélection de 2 enseignants avec volume restant
3. Affectation réussie
4. Répéter pour Examens 2 et 3

→ Tous les conflits résolus en quelques minutes !
```

### Exemple 3 : Beaucoup de Conflits

```
Session: Rattrapage 2025/2026
Section: Toutes

Action: Clic sur "Affecter Automatiquement"

Résultat:
✓ 30 examens traités
✓ 18 examens complets
⚠ 12 conflits

Raisons:
- Volume horaire épuisé (fin d'année)
- Nombreuses indisponibilités
- Conflits de simultanéité

Action manuelle:
1. Filtrer par département pour chaque conflit
2. Utiliser des enseignants externes si nécessaire
3. Système affiche avertissements pour décisions éclairées
4. Résolution progressive des 12 conflits

→ Tous les conflits résolus avec aide du système !
```

---

## 🎯 Contraintes Appliquées

### Mode Automatique (Strict)

| # | Contrainte | Description | Type |
|---|------------|-------------|------|
| C1 | Volume horaire | Enseignant doit avoir du volume restant | HARD |
| C2 | Conflit matière | Évite de surveiller sa propre matière | SOFT |
| C3 | Disponibilité | Pas d'indisponibilité sur le créneau | HARD |
| C4 | Non-simultanéité | Pas déjà affecté au même créneau | HARD |
| C5 | Département | Priorité aux enseignants du même département | HARD |

### Mode Manuel (Flexible)

| # | Contrainte | Description | Type |
|---|------------|-------------|------|
| C4 | Non-simultanéité | Pas déjà affecté au même créneau | HARD |
| * | Autres | Affichées comme avertissements | SOFT |

**Note:** En mode manuel, seule la contrainte C4 est stricte. Les autres sont affichées comme avertissements pour aider l'utilisateur à prendre une décision éclairée.

---

## 🔄 Flux Complet

```
┌─────────────────────────────────────────────────────────┐
│                    DÉBUT                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Étape 1: Sélection                                     │
│  - Choisir session                                      │
│  - Choisir section (optionnel)                          │
│  - Cliquer "Affecter Automatiquement"                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Algorithme Backend                                     │
│  - Traite tous les examens                              │
│  - Applique les 5 contraintes                           │
│  - Affecte automatiquement les surveillants             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Étape 2: Résumé                                        │
│  - Affiche total, complets, conflits                    │
│  - Code couleur pour identification rapide              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              ┌──────┴──────┐
              │             │
              ▼             ▼
    ┌─────────────┐   ┌─────────────┐
    │  Complets   │   │  Conflits   │
    │  (Vert)     │   │  (Rouge)    │
    └──────┬──────┘   └──────┬──────┘
           │                 │
           │                 ▼
           │      ┌─────────────────────────────────────┐
           │      │  Étape 3: Résolution Manuelle       │
           │      │  - Clic sur "Résoudre"              │
           │      │  - Modal avec enseignants dispos    │
           │      │  - Sélection manuelle               │
           │      │  - Affectation                      │
           │      └──────┬──────────────────────────────┘
           │             │
           └─────────────┴──────────────┐
                                        ▼
                         ┌──────────────────────────────┐
                         │  FIN - Tous affectés         │
                         └──────────────────────────────┘
```

---

## 📱 Responsive

La solution fonctionne sur tous les appareils :
- 💻 **Desktop** : Tableau complet avec tous les détails
- 📱 **Tablet** : Tableau adapté
- 📱 **Mobile** : Vue carte empilée

---

## 🚀 Améliorations Futures Possibles

1. **Vue Calendrier**
   - Afficher les examens dans un calendrier visuel
   - Drag & drop des enseignants

2. **Statistiques**
   - Graphique de charge par enseignant
   - Prédiction de conflits

3. **Export**
   - PDF des affectations
   - Excel pour analyse

4. **Notifications**
   - Alertes pour conflits critiques
   - Rappels pour résolution

5. **Historique**
   - Voir les modifications
   - Annuler/Refaire

---

## 📚 Fichiers Créés

### Backend (déjà existant)
- ✅ `server/app/routers/surveillances.py` - API endpoints
- ✅ `server/app/services/surv_service.py` - Logique métier
- ✅ `server/app/algorithms/surv_auto.py` - Algorithme d'affectation
- ✅ `server/app/crud/crud_surv.py` - Opérations base de données

### Frontend (nouveaux)
- ✅ `frontend/src/lib/api/surveillance.ts` - Client API
- ✅ `frontend/src/app/(admin)/surveillance/affectation/page.tsx` - Page principale

### Documentation
- ✅ `SURVEILLANCE_AFFECTATION_DESIGN.md` - Design technique
- ✅ `GUIDE_AFFECTATION_SURVEILLANTS.md` - Ce guide

---

## 🎉 Conclusion

Cette solution offre le **meilleur des deux mondes** :

1. **Automatisation** ⚡
   - Gain de temps considérable
   - Traitement de dizaines d'examens en secondes
   - Application automatique des contraintes

2. **Contrôle Manuel** 🎯
   - Résolution ciblée des conflits
   - Décisions éclairées grâce aux avertissements
   - Flexibilité pour cas complexes

3. **Interface Intuitive** 👁️
   - Workflow en 3 étapes claires
   - Code couleur pour identification rapide
   - Filtres puissants pour recherche

4. **Fiabilité** 🛡️
   - Validation des contraintes
   - Gestion des erreurs
   - Rollback automatique

**Résultat:** L'utilisateur peut affecter automatiquement la majorité des examens, puis résoudre les quelques conflits restants de manière rapide et efficace !
