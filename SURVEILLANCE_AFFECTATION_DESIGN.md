# 🎯 Design de l'Affectation des Surveillants

## Vue d'Ensemble

Ce document décrit la solution **user-friendly** pour l'affectation automatique des surveillants avec résolution manuelle des conflits.

---

## 🎨 Workflow en 3 Étapes

### **Étape 1 : Sélection & Lancement**

```
┌─────────────────────────────────────────────────────────┐
│  📋 Sélection                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Session: [Principale 2025/2026 ▼]                     │
│  Section: [Toutes les sections ▼]  (optionnel)         │
│                                                         │
│  [🤖 Affecter Automatiquement]                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Actions:**
- Sélectionner la session d'examens
- Optionnellement filtrer par section
- Cliquer sur "Affecter Automatiquement"

**Backend:**
- Appelle `POST /surveillances/affecter-session`
- L'algorithme traite tous les examens de la session
- Applique les 5 contraintes automatiquement

---

### **Étape 2 : Résumé Visuel**

Après l'affectation automatique, affichage d'un résumé coloré :

```
┌─────────────────────────────────────────────────────────┐
│  ℹ️ Résumé de l'affectation                             │
├─────────────────────────────────────────────────────────┤
│  Affectation automatique terminée pour 24 examens      │
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │   24    │  │   18    │  │    6    │                │
│  │  Total  │  │ Complets│  │ Conflits│                │
│  └─────────┘  └─────────┘  └─────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Indicateurs:**
- 🟢 **Complets** : Tous les surveillants affectés
- 🔴 **Conflits** : Manque de surveillants

---

### **Étape 3 : Tableau des Résultats**

Tableau détaillé avec code couleur pour identifier rapidement les problèmes :

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Statut    │ Matière           │ Section │ Date & Heure      │ Surveillants │
├──────────────────────────────────────────────────────────────────────────────┤
│  ✓ Complet │ Big Data          │ IGL3    │ 2026-01-07 08:00  │ 2 / 2        │
│  ⚠ Partiel │ Sécurité IOT      │ IGL3    │ 2026-01-07 10:30  │ 1 / 2  [→]   │
│  ✗ Conflit │ Optimisation      │ IGL4    │ 2026-01-08 08:00  │ 0 / 3  [→]   │
│  ✓ Complet │ Cloud Computing   │ IGL3    │ 2026-01-08 10:30  │ 2 / 2        │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Code Couleur:**
- 🟢 **Vert** : Complet (tous affectés)
- 🟡 **Jaune** : Partiel (manque quelques surveillants)
- 🔴 **Rouge** : Conflit (aucun ou très peu affectés)

**Actions:**
- Cliquer sur `[→]` pour résoudre manuellement

---

## 🔧 Modal de Résolution Manuelle

Quand l'utilisateur clique sur "Résoudre" pour un examen en conflit :

```
┌─────────────────────────────────────────────────────────────────────┐
│  Résolution Manuelle du Conflit                              [✕]   │
├─────────────────────────────────────────────────────────────────────┤
│  Optimisation Combinatoire - IGL4                                  │
│  2026-01-08 • 08:00 - 10:00                                        │
│                                                                     │
│  ⚠️ Besoin de surveillants                                          │
│  3 surveillants manquants sur 3 requis                             │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Rechercher: [_________________]  Département: [Tous ▼]      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  12 enseignants disponibles (2 sélectionnés)                       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ ☑ Abed Rahma                                    12.5h        │  │
│  │   Professeur • Département Informatique         restant      │  │
│  │                                                               │  │
│  │ ☑ Ben Ali Mohamed                               8.0h         │  │
│  │   Maître Assistant • Département Informatique   restant      │  │
│  │   ⚠ Indisponibilité déclarée ce jour                         │  │
│  │                                                               │  │
│  │ ☐ Trabelsi Fatma                                15.0h        │  │
│  │   Professeur • Département Informatique         restant      │  │
│  │                                                               │  │
│  │ ☐ Gharbi Ahmed                                  3.5h         │  │
│  │   Maître de Conférences • Département Math      restant      │  │
│  │   ⚠ Département externe                                      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  [Annuler]                      [Affecter 2 enseignants]          │
└─────────────────────────────────────────────────────────────────────┘
```

### Fonctionnalités du Modal

#### 1. **Informations Contextuelles**
- Nom de la matière et section
- Date et heure de l'examen
- Nombre de surveillants manquants

#### 2. **Filtres Intelligents**
- **Recherche** : Par nom, prénom, département
- **Département** : Filtrer par département spécifique

#### 3. **Liste des Enseignants Disponibles**

Chaque enseignant affiche :
- ☑ Checkbox pour sélection
- **Nom complet** et **grade**
- **Département**
- **Volume horaire restant** (en heures)
- **Avertissements** si applicable :
  - ⚠ Indisponibilité déclarée ce jour
  - ⚠ Département externe
  - ⚠ Volume horaire faible

#### 4. **Tri Automatique**
Les enseignants sont triés par :
1. **Volume restant** (décroissant) - priorité aux plus disponibles
2. **Département** - internes en premier
3. **Nom** alphabétique

#### 5. **Validation Intelligente**
- Bouton désactivé si aucun enseignant sélectionné
- Affiche le nombre d'enseignants sélectionnés
- Validation en temps réel

---

## 🎯 Avantages de cette Solution

### ✅ **Pour l'Utilisateur**

1. **Simplicité**
   - 3 étapes claires et logiques
   - Pas de configuration complexe
   - Interface intuitive

2. **Visibilité**
   - Code couleur immédiat
   - Résumé visuel des résultats
   - Identification rapide des problèmes

3. **Contrôle**
   - Affectation automatique pour gagner du temps
   - Résolution manuelle pour les cas complexes
   - Filtres puissants pour trouver le bon enseignant

4. **Transparence**
   - Affichage du volume horaire restant
   - Avertissements clairs
   - Raisons d'exclusion visibles

### ✅ **Pour le Système**

1. **Performance**
   - Algorithme optimisé backend
   - Chargement progressif des données
   - Pagination automatique

2. **Fiabilité**
   - Validation des contraintes
   - Gestion des erreurs
   - Rollback en cas d'échec

3. **Maintenabilité**
   - Code modulaire
   - API RESTful claire
   - Documentation complète

---

## 🔄 Flux de Données

```
┌─────────────┐
│  Frontend   │
│  (React)    │
└──────┬──────┘
       │
       │ 1. POST /surveillances/affecter-session
       │    { session_id: 1, section_nom: "IGL3" }
       │
       ▼
┌─────────────────────────────────────────────────┐
│  Backend API                                    │
│  /surveillances/affecter-session                │
└──────┬──────────────────────────────────────────┘
       │
       │ 2. Appelle SurvService
       │
       ▼
┌─────────────────────────────────────────────────┐
│  Service Layer                                  │
│  SurvService.affecter_session_automatique()     │
└──────┬──────────────────────────────────────────┘
       │
       │ 3. Appelle Algorithme
       │
       ▼
┌─────────────────────────────────────────────────┐
│  Algorithm Layer                                │
│  AutomaticAffectationAlgorithm                  │
│                                                 │
│  Pour chaque planification:                    │
│  1. Récupérer enseignants du département       │
│  2. Filtrer selon 5 contraintes                │
│  3. Trier par volume restant                   │
│  4. Sélectionner N surveillants                │
│  5. Insérer en BD                              │
└──────┬──────────────────────────────────────────┘
       │
       │ 4. Retourne résultats
       │
       ▼
┌─────────────────────────────────────────────────┐
│  Response                                       │
│  {                                              │
│    total_planifications: 24,                    │
│    affectees_automatiquement: 18,               │
│    en_conflit: 6,                               │
│    resultats: [...]                             │
│  }                                              │
└──────┬──────────────────────────────────────────┘
       │
       │ 5. Affichage Frontend
       │
       ▼
┌─────────────┐
│  UI Update  │
│  - Résumé   │
│  - Tableau  │
│  - Conflits │
└─────────────┘
```

---

## 🚀 Résolution Manuelle - Flux

```
User clique "Résoudre" sur un examen en conflit
       │
       │ 1. GET /surveillances/enseignants-disponibles/{planif_id}
       │
       ▼
┌─────────────────────────────────────────────────┐
│  Backend vérifie:                               │
│  - Contrainte 4 (non-simultanéité) STRICTE      │
│  - Indisponibilité le même JOUR (avertissement) │
│  - Volume horaire (avertissement si faible)     │
└──────┬──────────────────────────────────────────┘
       │
       │ 2. Retourne liste groupée par département
       │
       ▼
┌─────────────────────────────────────────────────┐
│  Modal s'ouvre avec:                            │
│  - Liste des enseignants disponibles            │
│  - Filtres (recherche, département)             │
│  - Avertissements visibles                      │
└──────┬──────────────────────────────────────────┘
       │
       │ 3. User sélectionne enseignants
       │
       ▼
┌─────────────────────────────────────────────────┐
│  User clique "Affecter"                         │
│                                                 │
│  POST /surveillances/manual-assignment          │
│  {                                              │
│    session_id: 1,                               │
│    planification_id: 8,                         │
│    groupe_id: 5,                                │
│    salle_id: 12,                                │
│    enseignant_ids: [22, 45]                     │
│  }                                              │
└──────┬──────────────────────────────────────────┘
       │
       │ 4. Backend valide et insère
       │
       ▼
┌─────────────────────────────────────────────────┐
│  Validation:                                    │
│  - Contrainte 4 (non-simultanéité) STRICTE      │
│  - Si échec → Rollback + Erreur 409             │
│  - Si succès → Insertion BD                     │
└──────┬──────────────────────────────────────────┘
       │
       │ 5. Succès
       │
       ▼
┌─────────────────────────────────────────────────┐
│  Frontend:                                      │
│  - Ferme modal                                  │
│  - Rafraîchit tableau                           │
│  - Affiche message succès                       │
└─────────────────────────────────────────────────┘
```

---

## 📊 Exemples d'Utilisation

### Cas 1 : Affectation Complète

```
Session: Principale 2025/2026
Section: IGL3

Résultat:
✓ 12 examens traités
✓ 12 examens complets
✓ 0 conflit

→ Aucune action manuelle nécessaire
```

### Cas 2 : Quelques Conflits

```
Session: Principale 2025/2026
Section: IGL4

Résultat:
✓ 15 examens traités
✓ 12 examens complets
⚠ 3 conflits

→ User clique "Résoudre" sur les 3 examens
→ Sélectionne manuellement les enseignants
→ Affectation terminée
```

### Cas 3 : Beaucoup de Conflits

```
Session: Rattrapage 2025/2026
Section: Toutes

Résultat:
✓ 30 examens traités
✓ 18 examens complets
⚠ 12 conflits

Raisons:
- Volume horaire épuisé pour plusieurs enseignants
- Indisponibilités déclarées
- Conflits de simultanéité

→ User résout les conflits un par un
→ Peut utiliser des enseignants externes si nécessaire
→ Système affiche avertissements pour décisions éclairées
```

---

## 🎨 Design Patterns Utilisés

### 1. **Progressive Disclosure**
- Affiche d'abord le résumé
- Détails disponibles sur demande (modal)
- Évite la surcharge cognitive

### 2. **Visual Hierarchy**
- Code couleur pour statuts
- Tailles de police différentes
- Espacement cohérent

### 3. **Immediate Feedback**
- Compteur de sélection en temps réel
- Boutons désactivés si invalide
- Messages de succès/erreur clairs

### 4. **Forgiving Format**
- Filtres optionnels
- Recherche flexible
- Annulation possible à tout moment

### 5. **Smart Defaults**
- Tri par volume restant
- Département interne en priorité
- Sélection de la première session

---

## 🔐 Contraintes Appliquées

### Mode Automatique

| # | Contrainte | Type | Description |
|---|------------|------|-------------|
| C1 | Volume horaire | HARD | Enseignant doit avoir du volume restant |
| C2 | Conflit matière | SOFT | Évite de surveiller sa propre matière |
| C3 | Disponibilité | HARD | Pas d'indisponibilité sur le créneau |
| C4 | Non-simultanéité | HARD | Pas déjà affecté au même créneau |
| C5 | Département | HARD | Priorité aux enseignants du même département |

### Mode Manuel

| # | Contrainte | Type | Description |
|---|------------|------|-------------|
| C4 | Non-simultanéité | HARD | Seule contrainte stricte |
| * | Autres | AVERTISSEMENT | Affichées mais non bloquantes |

---

## 📱 Responsive Design

La solution est responsive et fonctionne sur :
- 💻 **Desktop** : Tableau complet avec tous les détails
- 📱 **Tablet** : Tableau adapté avec colonnes essentielles
- 📱 **Mobile** : Vue carte empilée

---

## 🚀 Prochaines Améliorations Possibles

1. **Vue Calendrier**
   - Afficher les examens dans un calendrier visuel
   - Drag & drop des enseignants

2. **Statistiques Temps Réel**
   - Graphique de charge par enseignant
   - Prédiction de conflits

3. **Notifications**
   - Alertes pour conflits critiques
   - Rappels pour résolution

4. **Export**
   - PDF des affectations
   - Excel pour analyse

5. **Historique**
   - Voir les modifications
   - Annuler/Refaire

---

## ✅ Checklist de Validation

- [x] API backend complète
- [x] Client API frontend
- [x] Page d'affectation avec 3 étapes
- [x] Modal de résolution manuelle
- [x] Filtres et recherche
- [x] Code couleur pour statuts
- [x] Avertissements visibles
- [x] Gestion des erreurs
- [x] Responsive design
- [x] Documentation complète

---

## 📚 Fichiers Créés

1. **Backend** (déjà existant)
   - `server/app/routers/surveillances.py`
   - `server/app/services/surv_service.py`
   - `server/app/algorithms/surv_auto.py`
   - `server/app/crud/crud_surv.py`

2. **Frontend** (nouveaux)
   - `frontend/src/lib/api/surveillance.ts`
   - `frontend/src/app/(admin)/surveillance/affectation/page.tsx`

3. **Documentation**
   - `SURVEILLANCE_AFFECTATION_DESIGN.md` (ce fichier)

---

## 🎉 Conclusion

Cette solution offre un **équilibre parfait** entre :
- ⚡ **Automatisation** : Gain de temps avec l'algorithme
- 🎯 **Contrôle** : Résolution manuelle pour cas complexes
- 👁️ **Visibilité** : Interface claire et intuitive
- 🛡️ **Fiabilité** : Validation des contraintes

L'utilisateur peut affecter automatiquement des dizaines d'examens en quelques secondes, puis résoudre les quelques conflits restants de manière ciblée et éclairée.
