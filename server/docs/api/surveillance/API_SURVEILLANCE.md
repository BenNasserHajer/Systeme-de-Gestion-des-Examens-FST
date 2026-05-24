# 📡 API Surveillance - Documentation Complète

## 📋 Vue d'Ensemble

Cette API gère l'affectation automatique et manuelle des surveillants aux examens,
le suivi des présences, les remplacements et les statistiques de charge horaire.

**Base URL** : `http://127.0.0.1:8000`

**Préfixe** : `/surveillances`

**Format** : JSON

**Authentication** : Aucune (à implémenter en production)

---

## 🗂️ Liste des Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/surveillances/affecter-session` | Affectation automatique (algorithme v3) |
| POST | `/surveillances/manual-assignment` | Affectation manuelle — planif unique |
| POST | `/surveillances/manual-assignment-batch` | Affectation manuelle — batch session |
| GET | `/surveillances/enseignant/{id}/toutes-surveillances` | Profil complet enseignant |
| GET | `/surveillances/getallsurveillants` | Tous les enseignants avec volumes |
| GET | `/surveillances/enseignants-disponibles/{planif_id}` | Enseignants disponibles pour une planif |
| GET | `/surveillances/{session_id}` | Liste surveillances d'une session |
| GET | `/surveillances/{surveillance_id}/full-details` | Détail complet d'une surveillance |
| PATCH | `/surveillances/edit/{surveillance_id}` | Modifier une surveillance |
| POST | `/surveillances/{surveillance_id}/reassign` | Remplacer un enseignant |
| DELETE | `/surveillances/{surveillance_id}` | Supprimer une surveillance |
| DELETE | `/surveillances/session/{session_id}/reset` | Réinitialiser une session |
| GET | `/surveillances/session/{session_id}/rapport` | Rapport complet session |
| GET | `/surveillances/session/{session_id}/conflits` | Conflits d'une session |
| GET | `/surveillances/statistiques` | Statistiques globales annuelles |
| GET | `/surveillances/enseignant/{id}/disponibilites` | Indisponibilités d'un enseignant |

---

## 🎯 Endpoints Détaillés

---

### 1. Affectation Automatique ⭐ PRINCIPAL

**POST** `/surveillances/affecter-session`

Lance l'algorithme v3 d'affectation automatique des surveillants pour une session.

#### Body (JSON)

```json
{
  "session_id": 1,
  "section_nom": "IGL3",
  "periode": "2025/2026-S1",
  "type_epreuve": "EXAMEN_FINAL"
}
```

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `session_id` | int | ✅ | ID de la session d'examens |
| `section_nom` | str | ✅ | Nom exact de la section ex: "IGL3", "INF/IOT" |
| `periode` | str | ✅ | Année + semestre ex: "2025/2026-S1" |
| `type_epreuve` | str | ✅ | "DS" ou "EXAMEN_FINAL" |

#### Contraintes de l'algorithme

| Contrainte | Type | Description |
|-----------|------|-------------|
| C1 | HARD | Volume horaire restant suffisant (±0.05%) |
| C2 | HARD | Disponibilité déclarée sur le créneau |
| C3 | SOFT | Pas de conflit de matière (enseignant ne surveille pas sa propre matière) |
| C4 | HARD | Non-simultanéité (pas déjà affecté au même créneau) |
| C5 | SOFT | Priorité département interne > externe |
| C6 | SOFT | Équité de fréquence dans la session (critère de tri) |

#### Réponse (200 OK)

```json
{
  "session_id": 1,
  "session": {
    "id": 1,
    "type_session": "NORMALE",
    "annee_universitaire": "2025/2026",
    "date_debut": "2026-01-07",
    "date_fin": "2026-01-20",
    "statut": "EN_COURS"
  },
  "total_planifications": 5,
  "affectees_automatiquement": 4,
  "en_conflit": 1,
  "message": "Traitement terminé : 4 planification(s) entièrement affectée(s), 1 en conflit.",
  "resultats": [
    {
      "planification_id": 12,
      "type_epreuve": "EXAMEN_FINAL",
      "semestre": 1,
      "duree": 120,
      "statut_planif": "VALIDEE",
      "nb_surveillants_requis": 2,
      "matiere": {
        "id": 5,
        "code": "ALGO3",
        "intitule": "Algorithmique 3",
        "coefficient": 2.0,
        "credit": 3,
        "duree_examen": 120,
        "duree_ds": 90
      },
      "section": {
        "id": 3,
        "nom": "IGL3",
        "niveau": {
          "id": 2,
          "libelle": "L3",
          "type_formation": "LMD"
        }
      },
      "departement_examen": {
        "id": 2,
        "nom": "Informatique",
        "code": "INFO"
      },
      "creneau": {
        "id": 7,
        "date": "2026-01-08",
        "heure_debut": "08:30:00",
        "heure_fin": "10:30:00",
        "libelle": "Matin 1"
      },
      "session": { "id": 1, "type_session": "NORMALE", "annee_universitaire": "2025/2026", "date_debut": "2026-01-07", "date_fin": "2026-01-20", "statut": "EN_COURS" },
      "statut": "AFFECTEE",
      "surveillants_requis": 4,
      "surveillants_affectes": 4,
      "manquants": 0,
      "groupes": [
        {
          "groupe": { "id": 7, "numero": 1, "effectif": 35, "nb_etudiants": 35, "annee": "2025/2026" },
          "salle": { "id": 4, "code": "A101", "designation": "Amphi A", "capacite": 120, "batiment": "A" },
          "statut": "AFFECTEE",
          "surveillants_requis": 2,
          "manquants": 0,
          "surveillants_affectes": [
            {
              "surveillance_id": 201,
              "enseignant_id": 12,
              "nom": "Benali",
              "prenom": "Ali",
              "grade": "MCB",
              "email": "a.benali@univ.dz",
              "telephone": "0555000001",
              "departement": { "id": 2, "nom": "Informatique", "code": "INFO" },
              "groupe": { "id": 7, "numero": 1, "effectif": 35, "nb_etudiants": 35, "annee": "2025/2026" },
              "salle": { "id": 4, "code": "A101", "designation": "Amphi A", "capacite": 120, "batiment": "A" },
              "charge": 2.0,
              "mode_affectation": "AUTOMATIQUE",
              "statut_surveillance": "AFFECTE",
              "presence": false,
              "est_externe": false,
              "motif_externe": null
            }
          ]
        }
      ],
      "raisons_exclusion": [
        {
          "enseignant_id": 8,
          "nom": "Khelil",
          "prenom": "Nadia",
          "raison": "INDISPONIBLE",
          "details": null
        },
        {
          "enseignant_id": 15,
          "nom": "Saadi",
          "prenom": "Omar",
          "raison": "VOLUME_EPUISE",
          "details": "Restant: -0.50h (limite: -0.0010h)"
        }
      ]
    }
  ],
  "non_affectees": [
    {
      "planification_id": 17,
      "statut": "CONFLIT",
      "manquants": 2,
      "groupes": [...]
    }
  ]
}
```

#### Erreurs

- **400** : session non trouvée, aucune planification VALIDEE pour les critères

---

### 2. Affectation Manuelle — Planif Unique

**POST** `/surveillances/manual-assignment`

Affecte manuellement un ou plusieurs enseignants à une planification précise.

#### Body (JSON)

```json
{
  "session_id": 1,
  "planification_id": 12,
  "groupe_id": 7,
  "salle_id": 4,
  "enseignant_ids": [12, 17],
  "motifs_externes": {}
}
```

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `session_id` | int | ✅ | ID de la session |
| `planification_id` | int | ✅ | ID de la planification |
| `groupe_id` | int | ✅ | ID du groupe |
| `salle_id` | int | ✅ | ID de la salle |
| `enseignant_ids` | list[int] | ✅ | IDs des enseignants à affecter |
| `motifs_externes` | dict | ❌ | `{enseignant_id: "motif"}` pour les externes |

#### Réponse (200 OK)

```json
{
  "planification_id": 12,
  "statut": "CONFLIT_RESOLU",
  "surveillants_requis": 2,
  "surveillants_inseres": 2,
  "manquants": 0,
  "surveillances": [
    {
      "surveillance": { "id": 201, "statut_surveillance": "AFFECTE", "mode_affectation": "MANUELLE", "charge": 2.0, "presence": false, "est_externe": false, "motif_externe": null, "created_at": "2026-01-07T10:00:00", "updated_at": null },
      "enseignant": { "id": 12, "nom": "Benali", "prenom": "Ali", "nom_complet": "Ali Benali", "grade": "MCB", "email": "a.benali@univ.dz", "telephone": "0555000001", "volume_horaire": 20.0, "volume_consomme": 6.0, "volume_restant": 14.0, "departement": { "id": 2, "nom": "Informatique", "code": "INFO" } },
      "planification": { "id": 12, "type_epreuve": "EXAMEN_FINAL", "duree": 120, "semestre": 1, "statut": "VALIDEE", "nb_groupes": 2, "nb_surveillants_requis": 2, "mode_affectation": "MANUEL" },
      "session": { "id": 1, "type_session": "NORMALE", "annee_universitaire": "2025/2026", "date_debut": "2026-01-07", "date_fin": "2026-01-20", "statut": "EN_COURS" },
      "creneau": { "id": 7, "date": "2026-01-08", "heure_debut": "08:30:00", "heure_fin": "10:30:00", "libelle": "Matin 1" },
      "matiere": { "id": 5, "code": "ALGO3", "intitule": "Algorithmique 3", "coefficient": 2.0, "credit": 3, "duree_examen": 120, "duree_ds": 90 },
      "section": { "id": 3, "nom": "IGL3" },
      "niveau": { "id": 2, "libelle": "L3", "type_formation": "LMD" },
      "groupe": { "id": 7, "numero": 1, "effectif": 35, "nb_etudiants": 35, "annee": "2025/2026" },
      "salle": { "id": 4, "code": "A101", "designation": "Amphi A", "capacite": 120, "batiment": "A" },
      "departement_examen": { "id": 2, "nom": "Informatique", "code": "INFO" }
    }
  ]
}
```

**Statuts possibles** : `"CONFLIT_RESOLU"` (complet) ou `"INCOMPLET"` (manque de surveillants)

#### Erreurs

- **409** : enseignant déjà affecté au même créneau (C4 violée) — rollback total
- **400** : planification non trouvée dans la session

---

### 3. Affectation Manuelle — Batch Session

**POST** `/surveillances/manual-assignment-batch`

Affecte manuellement plusieurs planifications en une seule requête.

#### Body (JSON)

```json
{
  "session_id": 1,
  "affectations": [
    {
      "planification_id": 12,
      "groupe_id": 7,
      "salle_id": 4,
      "enseignant_ids": [12, 17]
    },
    {
      "planification_id": 13,
      "groupe_id": 8,
      "salle_id": 5,
      "enseignant_ids": [20]
    }
  ],
  "motifs_externes": {
    "20": "Manque de personnel dans le département"
  }
}
```

#### Réponse — Succès (200 OK)

```json
{
  "session_id": 1,
  "statut": "SUCCES",
  "total_surveillances_inserees": 3,
  "surveillances": [...]
}
```

#### Réponse — Avertissement (200 OK)

```json
{
  "session_id": 1,
  "statut": "AVERTISSEMENT",
  "message": "Certaines planifications sont incomplètes",
  "planifications_non_affectees": [13]
}
```

#### Erreurs

- **409** : conflit de simultanéité détecté
- **400** : erreur inattendue

---

### 4. Profil Complet Enseignant

**GET** `/surveillances/enseignant/{enseignant_id}/toutes-surveillances`

Retourne le profil complet d'un enseignant avec toutes ses surveillances.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `enseignant_id` | int | ID de l'enseignant |

#### Query Params (tous optionnels)

| Paramètre | Type | Description | Exemple |
|-----------|------|-------------|---------|
| `annee_universitaire` | str | Filtrer par année | `2025/2026` |
| `semestre` | int | Filtrer par semestre | `1` ou `2` |
| `type_epreuve` | str | Filtrer par type | `DS` ou `EXAMEN_FINAL` |

#### Réponse (200 OK)

```json
{
  "enseignant": {
    "id": 12,
    "nom": "Benali",
    "prenom": "Ali",
    "nom_complet": "Ali Benali",
    "grade": "MCB",
    "email": "a.benali@univ.dz",
    "telephone": "0555000001",
    "departement": { "id": 2, "nom": "Informatique", "code": "INFO" }
  },
  "charge_horaire": {
    "annee_universitaire": "2025/2026",
    "volume_horaire": 20.0,
    "volume_consomme": 6.0,
    "volume_restant": 14.0,
    "taux_utilisation": 30.0
  },
  "statistiques": {
    "total_surveillances": 3,
    "charge_totale": 6.0,
    "nb_confirmees": 2,
    "nb_presences": 2,
    "nb_externes": 0,
    "taux_utilisation": 30.0
  },
  "surveillances": [
    {
      "surveillance": { "id": 201, "statut_surveillance": "CONFIRME", "mode_affectation": "AUTOMATIQUE", "charge": 2.0, "presence": true, "est_externe": false, "motif_externe": null, "created_at": "2026-01-07T10:00:00", "updated_at": "2026-01-08T09:00:00" },
      "session": { "id": 1, "type_session": "NORMALE", "annee_universitaire": "2025/2026", "date_debut": "2026-01-07", "date_fin": "2026-01-20", "statut": "EN_COURS" },
      "planification": { "id": 12, "type_epreuve": "EXAMEN_FINAL", "semestre": 1, "duree": 120, "nb_surveillants_requis": 2, "statut": "VALIDEE" },
      "departement_examen": { "id": 2, "nom": "Informatique", "code": "INFO" },
      "creneau": { "id": 7, "date": "2026-01-08", "heure_debut": "08:30:00", "heure_fin": "10:30:00", "libelle": "Matin 1" },
      "matiere": { "id": 5, "code": "ALGO3", "intitule": "Algorithmique 3" },
      "section": { "id": 3, "nom": "IGL3" },
      "niveau": { "id": 2, "libelle": "L3", "type_formation": "LMD" },
      "groupe": { "id": 7, "numero": 1, "effectif": 35, "nb_etudiants": 35, "annee": "2025/2026" },
      "salle": { "id": 4, "code": "A101", "designation": "Amphi A", "capacite": 120, "batiment": "A" }
    }
  ]
}
```

#### Erreurs

- **404** : enseignant non trouvé

---

### 5. Tous les Surveillants

**GET** `/surveillances/getallsurveillants`

Retourne la liste de tous les enseignants avec leur volume horaire pour une session.

#### Query Params

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `session_id` | int | ✅ | ID de la session (déduit l'année universitaire) |
| `page` | int | ❌ | Numéro de page (défaut: 1) |
| `limit` | int | ❌ | Taille de page max 100 (défaut: 20) |
| `sort` | str | ❌ | `volume_restant`, `volume_consomme`, `nb_surveillances` |
| `order` | str | ❌ | `asc` ou `desc` (défaut: `desc`) |

#### Réponse (200 OK)

```json
{
  "data": [
    {
      "enseignant_id": 12,
      "nom": "Benali",
      "prenom": "Ali",
      "grade": "MCB",
      "departement": { "id": 2, "nom": "Informatique", "code": "INFO" },
      "volume_horaire": 20.0,
      "volume_consomme": 6.0,
      "volume_restant": 14.0,
      "nb_surveillances": 3
    },
    {
      "enseignant_id": 17,
      "nom": "Meziane",
      "prenom": "Sara",
      "grade": "MAA",
      "departement": { "id": 3, "nom": "Mathématiques", "code": "MATH" },
      "volume_horaire": 15.0,
      "volume_consomme": 4.0,
      "volume_restant": 11.0,
      "nb_surveillances": 2
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

#### Erreurs

- **404** : session non trouvée

---

### 6. Enseignants Disponibles pour une Planification

**GET** `/surveillances/enseignants-disponibles/{planif_id}`

Retourne les enseignants éligibles pour surveiller une planification, groupés par département.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `planif_id` | int | ID de la planification |

#### Logique

- **Exclus strictement** : enseignants déjà affectés au même créneau (C4)
- **Inclus avec avertissement** : enseignants ayant une indisponibilité déclarée le même jour

#### Réponse (200 OK)

```json
{
  "planification_id": 12,
  "date_planification": "2026-01-08",
  "total_disponibles": 18,
  "total_avec_avertissement": 2,
  "departements": [
    {
      "departement_id": 2,
      "departement_nom": "Informatique",
      "departement_code": "INFO",
      "total": 10,
      "enseignants": [
        {
          "enseignant_id": 12,
          "nom": "Benali",
          "prenom": "Ali",
          "grade": "MCB",
          "email": "a.benali@univ.dz",
          "telephone": "0555000001",
          "volume_horaire": 20.0,
          "volume_consomme": 4.0,
          "volume_restant": 16.0,
          "nb_surveillances": 2,
          "a_avertissement": false,
          "avertissements": []
        },
        {
          "enseignant_id": 19,
          "nom": "Hamidi",
          "prenom": "Leila",
          "grade": "MAA",
          "email": "l.hamidi@univ.dz",
          "telephone": null,
          "volume_horaire": 18.0,
          "volume_consomme": 2.0,
          "volume_restant": 16.0,
          "nb_surveillances": 1,
          "a_avertissement": true,
          "avertissements": [
            {
              "date": "2026-01-08",
              "heure_debut": "07:00:00",
              "heure_fin": "09:00:00",
              "type_dispo": "COURS_PREVU",
              "motif": "TD Algorithmique L2"
            }
          ]
        }
      ]
    },
    {
      "departement_id": 3,
      "departement_nom": "Mathématiques",
      "departement_code": "MATH",
      "total": 8,
      "enseignants": [...]
    }
  ]
}
```

#### Erreurs

- **404** : planification non trouvée

---

### 7. Liste des Surveillances d'une Session

**GET** `/surveillances/{session_id}`

Retourne la liste paginée et filtrée de toutes les surveillances d'une session.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `session_id` | int | ID de la session |

#### Query Params (tous optionnels)

| Paramètre | Type | Description |
|-----------|------|-------------|
| `departement_id` | int | Filtrer par département de l'examen |
| `groupe_id` | int | Filtrer par groupe |
| `salle_id` | int | Filtrer par salle |
| `type_epreuve` | str | `DS` ou `EXAMEN_FINAL` |
| `statut` | str | `AFFECTE` ou `CONFIRME` |
| `semestre` | int | `1` ou `2` |
| `section_id` | int | Filtrer par section |
| `enseignant_id` | int | Filtrer par enseignant |
| `skip` | int | Offset pagination (défaut: 0) |
| `limit` | int | Taille page max 200 (défaut: 50) |

#### Réponse (200 OK)

```json
{
  "session": {
    "id": 1,
    "type_session": "NORMALE",
    "annee_universitaire": "2025/2026",
    "date_debut": "2026-01-07",
    "date_fin": "2026-01-20",
    "statut": "EN_COURS"
  },
  "total": 42,
  "skip": 0,
  "limit": 50,
  "data": [
    {
      "surveillance": { "id": 201, "statut_surveillance": "CONFIRME", "mode_affectation": "AUTOMATIQUE", "charge": 2.0, "presence": true, "est_externe": false, "motif_externe": null, "created_at": "2026-01-07T10:00:00", "updated_at": "2026-01-08T09:00:00" },
      "enseignant": { "id": 12, "nom": "Benali", "prenom": "Ali", "nom_complet": "Ali Benali", "grade": "MCB", "email": "a.benali@univ.dz", "telephone": "0555000001", "volume_horaire": 20.0, "volume_consomme": 6.0, "volume_restant": 14.0, "departement": { "id": 2, "nom": "Informatique", "code": "INFO" } },
      "planification": { "id": 12, "type_epreuve": "EXAMEN_FINAL", "duree": 120, "semestre": 1, "statut": "VALIDEE", "nb_groupes": 2, "nb_surveillants_requis": 2, "mode_affectation": "AUTOMATIQUE" },
      "session": { "id": 1, "type_session": "NORMALE", "annee_universitaire": "2025/2026", "date_debut": "2026-01-07", "date_fin": "2026-01-20", "statut": "EN_COURS" },
      "departement_examen": { "id": 2, "nom": "Informatique", "code": "INFO" },
      "creneau": { "id": 7, "date": "2026-01-08", "heure_debut": "08:30:00", "heure_fin": "10:30:00", "libelle": "Matin 1" },
      "matiere": { "id": 5, "code": "ALGO3", "intitule": "Algorithmique 3", "coefficient": 2.0, "credit": 3, "duree_examen": 120, "duree_ds": 90 },
      "section": { "id": 3, "nom": "IGL3" },
      "niveau": { "id": 2, "libelle": "L3", "type_formation": "LMD" },
      "groupe": { "id": 7, "numero": 1, "effectif": 35, "nb_etudiants": 35, "annee": "2025/2026" },
      "salle": { "id": 4, "code": "A101", "designation": "Amphi A", "capacite": 120, "batiment": "A" }
    }
  ]
}
```

#### Erreurs

- **404** : session non trouvée

---

### 8. Détail Complet d'une Surveillance

**GET** `/surveillances/{surveillance_id}/full-details`

Retourne toutes les informations d'une surveillance.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `surveillance_id` | int | ID de la surveillance |

#### Réponse (200 OK)

Même structure qu'un élément de `data` dans l'endpoint liste (section 7).

#### Erreurs

- **404** : surveillance non trouvée

---

### 9. Modifier une Surveillance

**PATCH** `/surveillances/edit/{surveillance_id}`

Modifie partiellement une surveillance (PATCH sémantique — seuls les champs fournis sont mis à jour).

> ℹ️ Cet endpoint remplace à la fois `/confirmer/{id}` et `/marquer-presence/{id}`.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `surveillance_id` | int | ID de la surveillance |

#### Body (JSON — tous les champs optionnels)

```json
{
  "presence": true,
  "statut_surveillance": "CONFIRME",
  "charge": 1.5,
  "motif_externe": "Absence d'enseignants disponibles"
}
```

| Champ | Type | Description |
|-------|------|-------------|
| `presence` | bool | `true` = présent, `false` = absent |
| `statut_surveillance` | str | `"AFFECTE"` ou `"CONFIRME"` |
| `charge` | float | Heures imputées ex: `1.5` |
| `motif_externe` | str | Motif si enseignant externe |

#### Réponse (200 OK)

Surveillance enrichie complète (même structure que `/full-details`).

#### Erreurs

- **404** : surveillance non trouvée

---

### 10. Remplacer un Enseignant

**POST** `/surveillances/{surveillance_id}/reassign`

Remplace l'enseignant d'une surveillance. L'ancienne est supprimée et une nouvelle créée.

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `surveillance_id` | int | ID de la surveillance à remplacer |

#### Body (JSON)

```json
{
  "nouvel_enseignant_id": 20,
  "motif": "Indisponibilité médicale"
}
```

#### Réponse (200 OK)

```json
{
  "ancienne_surveillance_id": 201,
  "ancien_enseignant_id": 12,
  "motif": "Indisponibilité médicale",
  "nouvelle_surveillance": {
    "surveillance": { "id": 215, "statut_surveillance": "AFFECTE", "mode_affectation": "AUTOMATIQUE", "charge": 2.0, "presence": false, "est_externe": true, "motif_externe": "Remplacement: Indisponibilité médicale", "created_at": "2026-01-08T07:30:00", "updated_at": null },
    "enseignant": { "id": 20, "nom": "Rahmani", "prenom": "Karim", "nom_complet": "Karim Rahmani", "grade": "MCB", ... },
    "..."
  }
}
```

#### Erreurs

- **404** : surveillance non trouvée
- **400** : erreur inattendue

---

### 11. Supprimer une Surveillance

**DELETE** `/surveillances/{surveillance_id}`

#### Réponse (200 OK)

```json
{
  "message": "Surveillance supprimée avec succès",
  "id": 201
}
```

#### Erreurs

- **404** : surveillance non trouvée

---

### 12. Réinitialiser une Session

**DELETE** `/surveillances/session/{session_id}/reset`

Supprime TOUTES les surveillances d'une session. Action irréversible.

#### Réponse (200 OK)

```json
{
  "session_id": 1,
  "surveillances_supprimees": 42,
  "message": "42 surveillance(s) supprimée(s)"
}
```

---

### 13. Rapport Complet d'une Session

**GET** `/surveillances/session/{session_id}/rapport`

Génère un rapport complet avec statistiques et classement des enseignants.

#### Query Params (optionnel)

| Paramètre | Type | Description |
|-----------|------|-------------|
| `departement_id` | int | Filtrer par département |

#### Réponse (200 OK)

```json
{
  "session": {
    "id": 1,
    "type_session": "NORMALE",
    "annee_univ": "2025/2026",
    "date_debut": "2026-01-07",
    "date_fin": "2026-01-20",
    "statut": "EN_COURS"
  },
  "statistiques": {
    "total_planifications": 12,
    "completes": 8,
    "partielles": 3,
    "non_affectees": 1,
    "total_surveillances": 22,
    "total_presences": 15,
    "total_externes": 2
  },
  "planifications": [
    {
      "planification_id": 12,
      "type_epreuve": "EXAMEN_FINAL",
      "semestre": 1,
      "duree": 120,
      "departement_examen": { "id": 2, "nom": "Informatique", "code": "INFO" },
      "matiere": { "id": 5, "code": "ALGO3", "intitule": "Algorithmique 3" },
      "section": { "id": 3, "nom": "IGL3" },
      "creneau": { "date": "2026-01-08", "heure_debut": "08:30:00", "heure_fin": "10:30:00", "libelle": "Matin 1" },
      "nb_surveillants_requis": 2,
      "nb_surveillants_trouves": 2,
      "complet": true,
      "surveillants": [
        {
          "surveillance_id": 201,
          "enseignant": { "id": 12, "nom_complet": "Ali Benali", "grade": "MCB", "email": "a.benali@univ.dz", "departement": { "id": 2, "nom": "Informatique", "code": "INFO" } },
          "groupe": { "id": 7, "numero": 1, "effectif": 35 },
          "salle": { "id": 4, "code": "A101", "designation": "Amphi A", "batiment": "A", "capacite": 120 },
          "charge_imputee": 2.0,
          "mode_affectation": "AUTOMATIQUE",
          "statut": "CONFIRME",
          "presence": true,
          "est_externe": false,
          "motif_externe": null
        }
      ]
    }
  ],
  "en_conflit": [
    {
      "planification_id": 17,
      "nb_surveillants_requis": 2,
      "nb_surveillants_trouves": 1,
      "manquants": 1,
      "..."
    }
  ],
  "classement_enseignants": [
    {
      "enseignant_id": 12,
      "nom_complet": "Ali Benali",
      "grade": "MCB",
      "departement": { "id": 2, "nom": "Informatique", "code": "INFO" },
      "charge_totale": 6.0,
      "nb_surveillances": 3,
      "nb_presences": 3,
      "volume_horaire": 20.0,
      "taux_utilisation": 30.0
    }
  ],
  "date_generation": "2026-01-25T14:32:10.123456"
}
```

---

### 14. Conflits d'une Session

**GET** `/surveillances/session/{session_id}/conflits`

Détecte les groupes/salles avec moins de surveillants que requis.

#### Query Params (tous optionnels)

| Paramètre | Type | Description |
|-----------|------|-------------|
| `semestre` | int | `1` ou `2` |
| `type_epreuve` | str | `DS` ou `EXAMEN_FINAL` |
| `section_nom` | str | Ex: `"IGL3"` |

#### Réponse (200 OK)

```json
{
  "session_id": 1,
  "total_conflits": 2,
  "conflits": [
    {
      "planification_id": 17,
      "type_epreuve": "EXAMEN_FINAL",
      "semestre": 1,
      "departement_examen": { "id": 2, "nom": "Informatique", "code": "INFO" },
      "matiere": { "id": 9, "code": "BD2", "intitule": "Bases de Données 2" },
      "section": { "id": 3, "nom": "IGL3" },
      "creneau": { "date": "2026-01-15", "heure_debut": "14:00:00", "heure_fin": "16:00:00", "libelle": "Après-midi 1" },
      "groupe": { "id": 8, "numero": 2, "effectif": 30 },
      "salle": { "id": 5, "code": "B202", "designation": "Salle B202", "batiment": "B", "capacite": 40 },
      "surveillants_requis": 2,
      "surveillants_trouves": 0,
      "manquants": 2,
      "statut_resolution": "NON_RESOLU"
    }
  ]
}
```

---

### 15. Statistiques Globales

**GET** `/surveillances/statistiques`

#### Query Params

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `annee_univ` | str | ✅ | Ex: `"2025/2026"` |

#### Réponse (200 OK)

```json
{
  "annee_universitaire": "2025/2026",
  "total_surveillances": 185,
  "total_heures": 370.0,
  "unique_enseignants": 42,
  "count_externes": 8,
  "taux_externe": 4.32,
  "taux_remplissage": 92.5
}
```

---

### 16. Indisponibilités d'un Enseignant

**GET** `/surveillances/enseignant/{enseignant_id}/disponibilites`

#### Paramètres Path

| Paramètre | Type | Description |
|-----------|------|-------------|
| `enseignant_id` | int | ID de l'enseignant |

#### Query Params (obligatoires)

| Paramètre | Type | Description |
|-----------|------|-------------|
| `date_debut` | str | Format `YYYY-MM-DD` ex: `2026-01-07` |
| `date_fin` | str | Format `YYYY-MM-DD` ex: `2026-01-20` |

#### Réponse (200 OK)

```json
{
  "enseignant_id": 12,
  "date_debut": "2026-01-07",
  "date_fin": "2026-01-20",
  "disponibilites": [
    {
      "date": "2026-01-08",
      "heure_debut": "07:00:00",
      "heure_fin": "09:00:00",
      "type": "COURS_PREVU",
      "motif": "TD Algorithmique L2"
    },
    {
      "date": "2026-01-12",
      "heure_debut": "00:00:00",
      "heure_fin": "23:59:00",
      "type": "CONGE",
      "motif": "Congé exceptionnel"
    }
  ]
}
```

**Types d'indisponibilité** : `DISPONIBLE`, `INDISPONIBLE`, `COURS_PREVU`, `MISSION`, `CONGE`

#### Erreurs

- **400** : format de date invalide

---

## 📊 Codes de Statut HTTP

| Code | Signification | Quand |
|------|---------------|-------|
| 200 | OK | Requête réussie |
| 400 | Bad Request | Données invalides, session/planification introuvable |
| 404 | Not Found | Ressource non trouvée |
| 409 | Conflict | Enseignant déjà affecté en simultané (C4) |
| 422 | Unprocessable Entity | Validation Pydantic échouée |

---

## 🔧 Modèles de Données

### Surveillance

```typescript
interface Surveillance {
  id: number;
  planification_id: number;
  enseignant_id: number;
  groupe_id: number | null;
  salle_id: number | null;
  charge: number;           // heures imputées
  presence: boolean;
  mode_affectation: "AUTOMATIQUE" | "MANUELLE";
  statut_surveillance: "AFFECTE" | "CONFIRME";
  est_externe: boolean;
  motif_externe: string | null;
  created_at: string;
  updated_at: string | null;
}
```

### EnseignantDisponible

```typescript
interface EnseignantDisponible {
  enseignant_id: number;
  nom: string;
  prenom: string;
  grade: string | null;
  email: string | null;
  telephone: string | null;
  volume_horaire: number;
  volume_consomme: number;
  volume_restant: number;
  nb_surveillances: number;
  a_avertissement: boolean;
  avertissements: Avertissement[];
}
```

### AffecterSessionRequest

```typescript
interface AffecterSessionRequest {
  session_id: number;
  section_nom: string;   // Ex: "IGL3"
  periode: string;       // Ex: "2025/2026-S1"
  type_epreuve: string;  // "DS" | "EXAMEN_FINAL"
}
```

---

## 📞 Support

- **Documentation Swagger** : http://127.0.0.1:8000/docs
- **Documentation ReDoc** : http://127.0.0.1:8000/redoc
- **Health Check** : http://127.0.0.1:8000/health

---

**📡 API Surveillance complète et documentée !**