BEGIN;

-- ============================================================
-- Seed data v2 (idempotent)
-- Compatible with schema_v2.sql
-- ============================================================

-- 1) DEPARTEMENT
INSERT INTO departement (nom, code)
VALUES ('Departement Informatique', 'DSI')
ON CONFLICT (code) DO UPDATE
SET nom = EXCLUDED.nom;

-- 2) NIVEAU
INSERT INTO niveau (libelle, annee, type_formation, departement_id)
SELECT 'Cycle Ingenieur', 3, 'IGL', d.id
FROM departement d
WHERE d.code = 'DSI'
  AND NOT EXISTS (
      SELECT 1
      FROM niveau n
      WHERE n.libelle = 'Cycle Ingenieur'
        AND n.annee = 3
        AND n.type_formation = 'IGL'
        AND n.departement_id = d.id
  );

INSERT INTO niveau (libelle, annee, type_formation, departement_id)
SELECT 'Cycle Ingenieur', 4, 'IGL', d.id
FROM departement d
WHERE d.code = 'DSI'
  AND NOT EXISTS (
      SELECT 1
      FROM niveau n
      WHERE n.libelle = 'Cycle Ingenieur'
        AND n.annee = 4
        AND n.type_formation = 'IGL'
        AND n.departement_id = d.id
  );

-- 3) SECTION
INSERT INTO section (nom, niveau_id)
SELECT 'IGL3', n.id
FROM niveau n
WHERE n.libelle = 'Cycle Ingenieur'
  AND n.annee = 3
  AND n.type_formation = 'IGL'
  AND NOT EXISTS (
      SELECT 1
      FROM section s
      WHERE s.nom = 'IGL3'
        AND s.niveau_id = n.id
  );

INSERT INTO section (nom, niveau_id)
SELECT 'IGL4', n.id
FROM niveau n
WHERE n.libelle = 'Cycle Ingenieur'
  AND n.annee = 4
  AND n.type_formation = 'IGL'
  AND NOT EXISTS (
      SELECT 1
      FROM section s
      WHERE s.nom = 'IGL4'
        AND s.niveau_id = n.id
  );

-- 4) GROUPE
INSERT INTO groupe (numero, effectif, nb_etudiants, annee, section_id)
SELECT 1, 30, 30, '2025/2026', s.id
FROM section s
WHERE s.nom = 'IGL3'
ON CONFLICT (section_id, numero) DO UPDATE
SET effectif = EXCLUDED.effectif,
    nb_etudiants = EXCLUDED.nb_etudiants,
    annee = EXCLUDED.annee;

INSERT INTO groupe (numero, effectif, nb_etudiants, annee, section_id)
SELECT 2, 30, 30, '2025/2026', s.id
FROM section s
WHERE s.nom = 'IGL3'
ON CONFLICT (section_id, numero) DO UPDATE
SET effectif = EXCLUDED.effectif,
    nb_etudiants = EXCLUDED.nb_etudiants,
    annee = EXCLUDED.annee;

INSERT INTO groupe (numero, effectif, nb_etudiants, annee, section_id)
SELECT 1, 53, 53, '2025/2026', s.id
FROM section s
WHERE s.nom = 'IGL4'
ON CONFLICT (section_id, numero) DO UPDATE
SET effectif = EXCLUDED.effectif,
    nb_etudiants = EXCLUDED.nb_etudiants,
    annee = EXCLUDED.annee;

-- 5) SALLE (avec id_departement)
INSERT INTO salle (code, designation, capacite, batiment, id_departement)
SELECT 'AMPHI-INFO', 'Amphi Informatique', 150, 'Principal', d.id
FROM departement d
WHERE d.code = 'DSI'
ON CONFLICT (code) DO UPDATE
SET designation = EXCLUDED.designation,
    capacite = EXCLUDED.capacite,
    batiment = EXCLUDED.batiment,
    id_departement = EXCLUDED.id_departement;

INSERT INTO salle (code, designation, capacite, batiment, id_departement)
SELECT 'S22', 'Salle 22', 25, 'Informatique', d.id
FROM departement d
WHERE d.code = 'DSI'
ON CONFLICT (code) DO UPDATE
SET designation = EXCLUDED.designation,
    capacite = EXCLUDED.capacite,
    batiment = EXCLUDED.batiment,
    id_departement = EXCLUDED.id_departement;

INSERT INTO salle (code, designation, capacite, batiment, id_departement)
SELECT 'S31', 'Salle 31', 30, 'Principal', d.id
FROM departement d
WHERE d.code = 'DSI'
ON CONFLICT (code) DO UPDATE
SET designation = EXCLUDED.designation,
    capacite = EXCLUDED.capacite,
    batiment = EXCLUDED.batiment,
    id_departement = EXCLUDED.id_departement;

-- 6) SESSION
-- Session S1 (Semestre 1)
INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut)
SELECT 'PRINCIPALE', '2025/2026', DATE '2026-01-07', DATE '2026-01-15', 'VALIDEE'
WHERE NOT EXISTS (
    SELECT 1
    FROM session s
    WHERE s.type_session = 'PRINCIPALE'
      AND s.annee_universitaire = '2025/2026'
      AND s.date_debut = DATE '2026-01-07'
);

-- Session S2 (Semestre 2)
INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut)
SELECT 'PRINCIPALE', '2025/2026', DATE '2026-05-11', DATE '2026-05-23', 'BROUILLON'
WHERE NOT EXISTS (
    SELECT 1
    FROM session s
    WHERE s.type_session = 'PRINCIPALE'
      AND s.annee_universitaire = '2025/2026'
      AND s.date_debut = DATE '2026-05-11'
);

-- 7) CRENEAU
-- Créneaux pour Session S1 (Janvier 2026)
INSERT INTO creneau (date, heure_debut, heure_fin, libelle)
VALUES
    (DATE '2026-01-07', TIME '08:30', TIME '10:30', 'Mer 07/01 Matin'),
    (DATE '2026-01-07', TIME '11:00', TIME '13:00', 'Mer 07/01 Midi'),
    (DATE '2026-01-08', TIME '08:30', TIME '10:30', 'Jeu 08/01 Matin'),
    (DATE '2026-01-08', TIME '11:00', TIME '13:00', 'Jeu 08/01 Midi')
ON CONFLICT (date, heure_debut) DO NOTHING;

-- Créneaux pour Session S2 (Mai 2026 - du 11 au 23 mai)
-- Semaine 1: 11-16 mai (Lundi à Samedi)
INSERT INTO creneau (date, heure_debut, heure_fin, libelle)
VALUES
    -- Lundi 11 mai
    (DATE '2026-05-11', TIME '08:00', TIME '10:00', 'Lun 11/05 Matin'),
    (DATE '2026-05-11', TIME '10:30', TIME '12:30', 'Lun 11/05 Midi'),
    (DATE '2026-05-11', TIME '14:00', TIME '16:00', 'Lun 11/05 Après-midi'),
    -- Mardi 12 mai
    (DATE '2026-05-12', TIME '08:00', TIME '10:00', 'Mar 12/05 Matin'),
    (DATE '2026-05-12', TIME '10:30', TIME '12:30', 'Mar 12/05 Midi'),
    (DATE '2026-05-12', TIME '14:00', TIME '16:00', 'Mar 12/05 Après-midi'),
    -- Mercredi 13 mai
    (DATE '2026-05-13', TIME '08:00', TIME '10:00', 'Mer 13/05 Matin'),
    (DATE '2026-05-13', TIME '10:30', TIME '12:30', 'Mer 13/05 Midi'),
    (DATE '2026-05-13', TIME '14:00', TIME '16:00', 'Mer 13/05 Après-midi'),
    -- Jeudi 14 mai
    (DATE '2026-05-14', TIME '08:00', TIME '10:00', 'Jeu 14/05 Matin'),
    (DATE '2026-05-14', TIME '10:30', TIME '12:30', 'Jeu 14/05 Midi'),
    (DATE '2026-05-14', TIME '14:00', TIME '16:00', 'Jeu 14/05 Après-midi'),
    -- Vendredi 15 mai
    (DATE '2026-05-15', TIME '08:00', TIME '10:00', 'Ven 15/05 Matin'),
    (DATE '2026-05-15', TIME '10:30', TIME '12:30', 'Ven 15/05 Midi'),
    (DATE '2026-05-15', TIME '14:00', TIME '16:00', 'Ven 15/05 Après-midi'),
    -- Samedi 16 mai
    (DATE '2026-05-16', TIME '08:00', TIME '10:00', 'Sam 16/05 Matin'),
    (DATE '2026-05-16', TIME '10:30', TIME '12:30', 'Sam 16/05 Midi'),
    
    -- Semaine 2: 18-23 mai (Lundi à Samedi, pas de dimanche)
    -- Lundi 18 mai
    (DATE '2026-05-18', TIME '08:00', TIME '10:00', 'Lun 18/05 Matin'),
    (DATE '2026-05-18', TIME '10:30', TIME '12:30', 'Lun 18/05 Midi'),
    (DATE '2026-05-18', TIME '14:00', TIME '16:00', 'Lun 18/05 Après-midi'),
    -- Mardi 19 mai
    (DATE '2026-05-19', TIME '08:00', TIME '10:00', 'Mar 19/05 Matin'),
    (DATE '2026-05-19', TIME '10:30', TIME '12:30', 'Mar 19/05 Midi'),
    (DATE '2026-05-19', TIME '14:00', TIME '16:00', 'Mar 19/05 Après-midi'),
    -- Mercredi 20 mai
    (DATE '2026-05-20', TIME '08:00', TIME '10:00', 'Mer 20/05 Matin'),
    (DATE '2026-05-20', TIME '10:30', TIME '12:30', 'Mer 20/05 Midi'),
    (DATE '2026-05-20', TIME '14:00', TIME '16:00', 'Mer 20/05 Après-midi'),
    -- Jeudi 21 mai
    (DATE '2026-05-21', TIME '08:00', TIME '10:00', 'Jeu 21/05 Matin'),
    (DATE '2026-05-21', TIME '10:30', TIME '12:30', 'Jeu 21/05 Midi'),
    (DATE '2026-05-21', TIME '14:00', TIME '16:00', 'Jeu 21/05 Après-midi'),
    -- Vendredi 22 mai
    (DATE '2026-05-22', TIME '08:00', TIME '10:00', 'Ven 22/05 Matin'),
    (DATE '2026-05-22', TIME '10:30', TIME '12:30', 'Ven 22/05 Midi'),
    (DATE '2026-05-22', TIME '14:00', TIME '16:00', 'Ven 22/05 Après-midi'),
    -- Samedi 23 mai
    (DATE '2026-05-23', TIME '08:00', TIME '10:00', 'Sam 23/05 Matin'),
    (DATE '2026-05-23', TIME '10:30', TIME '12:30', 'Sam 23/05 Midi')
ON CONFLICT (date, heure_debut) DO NOTHING;

-- 8) ENSEIGNANT
INSERT INTO enseignant (nom, prenom, grade, email, telephone, departement_id)
SELECT 'Younes', 'Sana', 'Maitre de Conferences', 'sana.younes@fst.utm.tn', '00000001', d.id
FROM departement d
WHERE d.code = 'DSI'
ON CONFLICT (email) DO UPDATE
SET nom = EXCLUDED.nom,
    prenom = EXCLUDED.prenom,
    grade = EXCLUDED.grade,
    telephone = EXCLUDED.telephone,
    departement_id = EXCLUDED.departement_id;

INSERT INTO enseignant (nom, prenom, grade, email, telephone, departement_id)
SELECT 'Ben Hassine', 'Med Ali', 'Professeur', 'medali.benhassine@fst.utm.tn', '00000002', d.id
FROM departement d
WHERE d.code = 'DSI'
ON CONFLICT (email) DO UPDATE
SET nom = EXCLUDED.nom,
    prenom = EXCLUDED.prenom,
    grade = EXCLUDED.grade,
    telephone = EXCLUDED.telephone,
    departement_id = EXCLUDED.departement_id;

INSERT INTO enseignant (nom, prenom, grade, email, telephone, departement_id)
SELECT 'Ochi', 'Wejda', 'Maitre Assistante', 'wejda.ochi@fst.utm.tn', '00000003', d.id
FROM departement d
WHERE d.code = 'DSI'
ON CONFLICT (email) DO UPDATE
SET nom = EXCLUDED.nom,
    prenom = EXCLUDED.prenom,
    grade = EXCLUDED.grade,
    telephone = EXCLUDED.telephone,
    departement_id = EXCLUDED.departement_id;

-- 9) CHARGE_HORAIRE
INSERT INTO charge_horaire (enseignant_id, annee_univ, volume_horaire)
SELECT e.id, '2025/2026', 128
FROM enseignant e
WHERE e.email = 'sana.younes@fst.utm.tn'
ON CONFLICT (enseignant_id, annee_univ) DO UPDATE
SET volume_horaire = EXCLUDED.volume_horaire;

INSERT INTO charge_horaire (enseignant_id, annee_univ, volume_horaire)
SELECT e.id, '2025/2026', 128
FROM enseignant e
WHERE e.email = 'medali.benhassine@fst.utm.tn'
ON CONFLICT (enseignant_id, annee_univ) DO UPDATE
SET volume_horaire = EXCLUDED.volume_horaire;

-- 10) MATIERE
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
VALUES
    ('IGL4-ML-DL', 'Machine Learning and Deep Learning', 2.5, 3, TRUE, TRUE, 120, 60),
    ('IGL4-DEV-JEE', 'Developpement JEE', 2.0, 2, TRUE, TRUE, 120, 60),
    ('IGL4-BIG-DATA', 'Big Data', 2.5, 3, TRUE, TRUE, 120, 60),
    ('IGL4-ENTREPRENEUR', 'Entreprenariat', 1.5, 2, TRUE, TRUE, 90, 60)
ON CONFLICT (code) DO UPDATE
SET intitule = EXCLUDED.intitule,
    coefficient = EXCLUDED.coefficient,
    credit = EXCLUDED.credit,
    a_examen_final = EXCLUDED.a_examen_final,
    a_ds = EXCLUDED.a_ds,
    duree_examen = EXCLUDED.duree_examen,
    duree_ds = EXCLUDED.duree_ds;

-- 11) SECTION_MATIERE
INSERT INTO section_matiere (
    section_id,
    matiere_id,
    annee_sem,
    a_examen_final,
    a_ds,
    duree_examen,
    duree_ds
)
SELECT
    s.id,
    m.id,
    '2025/2026-S1',
    m.a_examen_final,
    m.a_ds,
    m.duree_examen,
    m.duree_ds
FROM section s
JOIN matiere m ON m.code IN ('IGL4-ML-DL', 'IGL4-DEV-JEE')
WHERE s.nom = 'IGL4'
ON CONFLICT (section_id, matiere_id, annee_sem) DO UPDATE
SET a_examen_final = EXCLUDED.a_examen_final,
    a_ds = EXCLUDED.a_ds,
    duree_examen = EXCLUDED.duree_examen,
    duree_ds = EXCLUDED.duree_ds;

INSERT INTO section_matiere (
    section_id,
    matiere_id,
    annee_sem,
    a_examen_final,
    a_ds,
    duree_examen,
    duree_ds
)
SELECT
    s.id,
    m.id,
    '2025/2026-S2',
    m.a_examen_final,
    m.a_ds,
    m.duree_examen,
    m.duree_ds
FROM section s
JOIN matiere m ON m.code IN ('IGL4-BIG-DATA', 'IGL4-ENTREPRENEUR')
WHERE s.nom = 'IGL4'
ON CONFLICT (section_id, matiere_id, annee_sem) DO UPDATE
SET a_examen_final = EXCLUDED.a_examen_final,
    a_ds = EXCLUDED.a_ds,
    duree_examen = EXCLUDED.duree_examen,
    duree_ds = EXCLUDED.duree_ds;

-- 12) ENSEIGNEMENT
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025/2026-S1'
FROM enseignant e
JOIN matiere m ON m.code = 'IGL4-ML-DL'
WHERE e.email = 'sana.younes@fst.utm.tn'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement, annee_sem) DO UPDATE
SET nb_heures = EXCLUDED.nb_heures;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025/2026-S2'
FROM enseignant e
JOIN matiere m ON m.code = 'IGL4-BIG-DATA'
WHERE e.email = 'medali.benhassine@fst.utm.tn'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement, annee_sem) DO UPDATE
SET nb_heures = EXCLUDED.nb_heures;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025/2026-S2'
FROM enseignant e
JOIN matiere m ON m.code = 'IGL4-ENTREPRENEUR'
WHERE e.email = 'wejda.ochi@fst.utm.tn'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement, annee_sem) DO UPDATE
SET nb_heures = EXCLUDED.nb_heures;

-- 13) JEU DE CHARGE (benchmark algorithmique)

-- 13.1) Groupes supplementaires pour augmenter le volume a planifier
INSERT INTO groupe (numero, effectif, nb_etudiants, annee, section_id)
SELECT v.numero, v.effectif, v.effectif, '2025/2026', s.id
FROM section s
CROSS JOIN (VALUES (2, 26), (3, 27)) AS v(numero, effectif)
WHERE s.nom = 'IGL4'
ON CONFLICT (section_id, numero) DO UPDATE
SET effectif = EXCLUDED.effectif,
  nb_etudiants = EXCLUDED.nb_etudiants,
  annee = EXCLUDED.annee;

INSERT INTO groupe (numero, effectif, nb_etudiants, annee, section_id)
SELECT v.numero, v.effectif, v.effectif, '2025/2026', s.id
FROM section s
CROSS JOIN (VALUES (3, 20), (4, 20)) AS v(numero, effectif)
WHERE s.nom = 'IGL3'
ON CONFLICT (section_id, numero) DO UPDATE
SET effectif = EXCLUDED.effectif,
  nb_etudiants = EXCLUDED.nb_etudiants,
  annee = EXCLUDED.annee;

-- 13.2) Salles supplementaires (avec id_departement)
INSERT INTO salle (code, designation, capacite, batiment, id_departement)
SELECT
  format('INF-%02s', g)::VARCHAR(30),
  format('Salle Test %s', g)::VARCHAR(100),
  (20 + (g % 8) * 10),
  CASE
    WHEN g % 3 = 0 THEN 'Bloc A'
    WHEN g % 3 = 1 THEN 'Bloc B'
    ELSE 'Bloc C'
  END,
  d.id
FROM generate_series(1, 18) AS g
CROSS JOIN departement d
WHERE d.code = 'DSI'
ON CONFLICT (code) DO UPDATE
SET designation = EXCLUDED.designation,
  capacite = EXCLUDED.capacite,
  batiment = EXCLUDED.batiment,
  id_departement = EXCLUDED.id_departement;

-- 13.3) Creneaux supplementaires sur une plage large
WITH jours AS (
  SELECT gs::DATE AS d
  FROM generate_series(DATE '2026-01-07', DATE '2026-01-24', INTERVAL '1 day') AS gs
  WHERE EXTRACT(ISODOW FROM gs) <= 6
),
slots AS (
  SELECT *
  FROM (VALUES
    (TIME '08:30', TIME '10:30', 'M1'),
    (TIME '11:00', TIME '13:00', 'M2'),
    (TIME '14:00', TIME '16:00', 'M3')
  ) AS v(heure_debut, heure_fin, suffixe)
)
INSERT INTO creneau (date, heure_debut, heure_fin, libelle)
SELECT
  j.d,
  s.heure_debut,
  s.heure_fin,
  to_char(j.d, 'YYYY-MM-DD') || ' ' || s.suffixe
FROM jours j
CROSS JOIN slots s
ON CONFLICT (date, heure_debut) DO UPDATE
SET heure_fin = EXCLUDED.heure_fin,
  libelle = EXCLUDED.libelle;

-- 13.4) Enseignants supplementaires pour alimenter enseignement
INSERT INTO enseignant (nom, prenom, grade, email, telephone, departement_id)
SELECT
  'Bench',
  format('Teacher%02s', g)::VARCHAR(60),
  'Vacataire',
  format('bench.teacher%02s@fst.utm.tn', g)::VARCHAR(100),
  ('9' || lpad(g::TEXT, 7, '0'))::VARCHAR(20),
  d.id
FROM generate_series(1, 16) AS g
CROSS JOIN departement d
WHERE d.code = 'DSI'
ON CONFLICT (email) DO UPDATE
SET nom = EXCLUDED.nom,
  prenom = EXCLUDED.prenom,
  grade = EXCLUDED.grade,
  telephone = EXCLUDED.telephone,
  departement_id = EXCLUDED.departement_id;

INSERT INTO charge_horaire (enseignant_id, annee_univ, volume_horaire)
SELECT e.id, '2025/2026', 192
FROM enseignant e
WHERE e.email LIKE 'bench.teacher%@fst.utm.tn'
ON CONFLICT (enseignant_id, annee_univ) DO UPDATE
SET volume_horaire = EXCLUDED.volume_horaire;

-- 13.5) Matieres supplementaires (48 matieres auto)
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
SELECT
  t.code,
  t.intitule,
  t.coefficient,
  t.credit,
  TRUE,
  TRUE,
  120,
  60
FROM (
  SELECT
    format('I3S1M%02s', g)::VARCHAR(20) AS code,
    format('IGL3 S1 Matiere Test %s', g)::VARCHAR(150) AS intitule,
    (1 + (g % 3) * 0.5)::NUMERIC(4,2) AS coefficient,
    (2 + (g % 2)) AS credit
  FROM generate_series(1, 12) AS g

  UNION ALL

  SELECT
    format('I3S2M%02s', g)::VARCHAR(20),
    format('IGL3 S2 Matiere Test %s', g)::VARCHAR(150),
    (1 + (g % 3) * 0.5)::NUMERIC(4,2),
    (2 + (g % 2))
  FROM generate_series(1, 12) AS g

  UNION ALL

  SELECT
    format('I4S1M%02s', g)::VARCHAR(20),
    format('IGL4 S1 Matiere Test %s', g)::VARCHAR(150),
    (1 + (g % 3) * 0.5)::NUMERIC(4,2),
    (2 + (g % 2))
  FROM generate_series(1, 12) AS g

  UNION ALL

  SELECT
    format('I4S2M%02s', g)::VARCHAR(20),
    format('IGL4 S2 Matiere Test %s', g)::VARCHAR(150),
    (1 + (g % 3) * 0.5)::NUMERIC(4,2),
    (2 + (g % 2))
  FROM generate_series(1, 12) AS g
) AS t
ON CONFLICT (code) DO UPDATE
SET intitule = EXCLUDED.intitule,
  coefficient = EXCLUDED.coefficient,
  credit = EXCLUDED.credit,
  a_examen_final = EXCLUDED.a_examen_final,
  a_ds = EXCLUDED.a_ds,
  duree_examen = EXCLUDED.duree_examen,
  duree_ds = EXCLUDED.duree_ds;

-- 13.6) Liens section_matiere supplementaires
INSERT INTO section_matiere (
  section_id,
  matiere_id,
  annee_sem,
  a_examen_final,
  a_ds,
  duree_examen,
  duree_ds
)
SELECT s.id, m.id, '2025/2026-S1', m.a_examen_final, m.a_ds, m.duree_examen, m.duree_ds
FROM section s
JOIN matiere m ON m.code LIKE 'I3S1M%'
WHERE s.nom = 'IGL3'
ON CONFLICT (section_id, matiere_id, annee_sem) DO UPDATE
SET a_examen_final = EXCLUDED.a_examen_final,
  a_ds = EXCLUDED.a_ds,
  duree_examen = EXCLUDED.duree_examen,
  duree_ds = EXCLUDED.duree_ds;

INSERT INTO section_matiere (
  section_id,
  matiere_id,
  annee_sem,
  a_examen_final,
  a_ds,
  duree_examen,
  duree_ds
)
SELECT s.id, m.id, '2025/2026-S2', m.a_examen_final, m.a_ds, m.duree_examen, m.duree_ds
FROM section s
JOIN matiere m ON m.code LIKE 'I3S2M%'
WHERE s.nom = 'IGL3'
ON CONFLICT (section_id, matiere_id, annee_sem) DO UPDATE
SET a_examen_final = EXCLUDED.a_examen_final,
  a_ds = EXCLUDED.a_ds,
  duree_examen = EXCLUDED.duree_examen,
  duree_ds = EXCLUDED.duree_ds;

INSERT INTO section_matiere (
  section_id,
  matiere_id,
  annee_sem,
  a_examen_final,
  a_ds,
  duree_examen,
  duree_ds
)
SELECT s.id, m.id, '2025/2026-S1', m.a_examen_final, m.a_ds, m.duree_examen, m.duree_ds
FROM section s
JOIN matiere m ON m.code LIKE 'I4S1M%'
WHERE s.nom = 'IGL4'
ON CONFLICT (section_id, matiere_id, annee_sem) DO UPDATE
SET a_examen_final = EXCLUDED.a_examen_final,
  a_ds = EXCLUDED.a_ds,
  duree_examen = EXCLUDED.duree_examen,
  duree_ds = EXCLUDED.duree_ds;

INSERT INTO section_matiere (
  section_id,
  matiere_id,
  annee_sem,
  a_examen_final,
  a_ds,
  duree_examen,
  duree_ds
)
SELECT s.id, m.id, '2025/2026-S2', m.a_examen_final, m.a_ds, m.duree_examen, m.duree_ds
FROM section s
JOIN matiere m ON m.code LIKE 'I4S2M%'
WHERE s.nom = 'IGL4'
ON CONFLICT (section_id, matiere_id, annee_sem) DO UPDATE
SET a_examen_final = EXCLUDED.a_examen_final,
  a_ds = EXCLUDED.a_ds,
  duree_examen = EXCLUDED.duree_examen,
  duree_ds = EXCLUDED.duree_ds;

-- 13.7) Enseignement auto genere pour les matieres de benchmark
WITH matieres_auto AS (
  SELECT
    m.id,
    m.code,
    CASE
      WHEN m.code LIKE 'I3S1M%' OR m.code LIKE 'I4S1M%' THEN '2025/2026-S1'
      ELSE '2025/2026-S2'
    END AS annee_sem,
    row_number() OVER (ORDER BY m.code) AS rn
  FROM matiere m
  WHERE m.code LIKE 'I3S1M%'
     OR m.code LIKE 'I3S2M%'
     OR m.code LIKE 'I4S1M%'
     OR m.code LIKE 'I4S2M%'
),
enseignants_pool AS (
  SELECT
    e.id,
    row_number() OVER (ORDER BY e.email) AS rn,
    count(*) OVER () AS total
  FROM enseignant e
  WHERE e.email LIKE 'bench.teacher%@fst.utm.tn'
)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT
  ep.id,
  ma.id,
  'COURS',
  21,
  ma.annee_sem
FROM matieres_auto ma
JOIN enseignants_pool ep
  ON ep.rn = ((ma.rn - 1) % ep.total) + 1
ON CONFLICT (enseignant_id, matiere_id, type_enseignement, annee_sem) DO UPDATE
SET nb_heures = EXCLUDED.nb_heures;

WITH matieres_auto AS (
  SELECT
    m.id,
    m.code,
    CASE
      WHEN m.code LIKE 'I3S1M%' OR m.code LIKE 'I4S1M%' THEN '2025/2026-S1'
      ELSE '2025/2026-S2'
    END AS annee_sem,
    row_number() OVER (ORDER BY m.code) AS rn
  FROM matiere m
  WHERE m.code LIKE 'I3S1M%'
     OR m.code LIKE 'I3S2M%'
     OR m.code LIKE 'I4S1M%'
     OR m.code LIKE 'I4S2M%'
),
enseignants_pool AS (
  SELECT
    e.id,
    row_number() OVER (ORDER BY e.email) AS rn,
    count(*) OVER () AS total
  FROM enseignant e
  WHERE e.email LIKE 'bench.teacher%@fst.utm.tn'
)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT
  ep.id,
  ma.id,
  'TP',
  14,
  ma.annee_sem
FROM matieres_auto ma
JOIN enseignants_pool ep
  ON ep.rn = ((ma.rn + 2) % ep.total) + 1
ON CONFLICT (enseignant_id, matiere_id, type_enseignement, annee_sem) DO UPDATE
SET nb_heures = EXCLUDED.nb_heures;

COMMIT;

-- ============================================================
-- Verification rapide
-- ============================================================
SELECT 'departement' AS table_name, COUNT(*) AS nb FROM departement UNION ALL
SELECT 'niveau', COUNT(*) FROM niveau UNION ALL
SELECT 'section', COUNT(*) FROM section UNION ALL
SELECT 'groupe', COUNT(*) FROM groupe UNION ALL
SELECT 'salle', COUNT(*) FROM salle UNION ALL
SELECT 'creneau', COUNT(*) FROM creneau UNION ALL
SELECT 'enseignant', COUNT(*) FROM enseignant UNION ALL
SELECT 'charge_horaire', COUNT(*) FROM charge_horaire UNION ALL
SELECT 'matiere', COUNT(*) FROM matiere UNION ALL
SELECT 'section_matiere', COUNT(*) FROM section_matiere UNION ALL
SELECT 'enseignement', COUNT(*) FROM enseignement
ORDER BY table_name;
