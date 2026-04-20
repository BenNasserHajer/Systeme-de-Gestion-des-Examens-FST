-- ============================================================================
-- Script de Seed — Section IGL3 (Cycle Ingénieur) — 2025/2026
-- CORRIGÉ pour l'erreur 22001 (value too long)
-- ============================================================================

-- ============================================================================
-- ÉTAPE 0 : Augmenter la taille de matiere.code pour éviter les erreurs
-- ============================================================================
ALTER TABLE matiere ALTER COLUMN code TYPE VARCHAR(30);

BEGIN;

-- ============================================================================
-- 1, 2, 3. NIVEAU, SECTION, GROUPES (inchangés)
-- ============================================================================
-- ... (copier-coller le code précédent pour ces sections, il est correct) ...

INSERT INTO niveau (libelle, annee, type_formation, departement_id)
SELECT 'Cycle Ingénieur', 3, 'IGL', 1
WHERE NOT EXISTS (
    SELECT 1 FROM niveau
    WHERE libelle = 'Cycle Ingénieur' AND annee = 3 AND type_formation = 'IGL'
);

INSERT INTO section (nom, nb_etudiants, niveau_id)
SELECT 'IGL3', 60, n.id
FROM niveau n
WHERE n.libelle = 'Cycle Ingénieur' AND n.annee = 3 AND n.type_formation = 'IGL'
AND NOT EXISTS (
    SELECT 1 FROM section s
    WHERE s.nom = 'IGL3' AND s.niveau_id = n.id
);

INSERT INTO groupe (numero, effectif, section_id)
SELECT 1, 30, s.id
FROM section s
JOIN niveau n ON n.id = s.niveau_id
WHERE s.nom = 'IGL3' AND n.libelle = 'Cycle Ingénieur'
ON CONFLICT (section_id, numero) DO NOTHING;

INSERT INTO groupe (numero, effectif, section_id)
SELECT 2, 30, s.id
FROM section s
JOIN niveau n ON n.id = s.niveau_id
WHERE s.nom = 'IGL3' AND n.libelle = 'Cycle Ingénieur'
ON CONFLICT (section_id, numero) DO NOTHING;

-- ============================================================================
-- 4. MATIÈRES — CORRECTION : Ordre des colonnes
-- L'erreur venait probablement d'une inversion entre `code` et `intitule`
-- dans un précédent INSERT.
-- ============================================================================
INSERT INTO matiere (
    code, intitule, coefficient, credit,
    a_examen_final, a_ds, duree_examen, duree_ds
)
VALUES
    ('IGL3-PROJET-NT',
     'Projet d''application nouvelles technologies',
     2.5, 3, TRUE, TRUE, 120, 60),

    ('IGL3-TECH-COMPILATION',
     'Techniques de Compilation',
     2.0, 2, TRUE, TRUE, 120, 60),

    ('IGL3-ANGLAIS',
     'Anglais',
     1.0, 1, FALSE, TRUE, NULL, 60),

    ('IGL3-ADMIN-BD',
     'Administration des bases de données',
     2.0, 2, TRUE, TRUE, 120, 60),

    ('IGL3-ARCHI-LOGICIELLE',
     'Architecture Logicielle',
     2.0, 2, TRUE, TRUE, 120, 60),

    ('IGL3-ENTREPOTS',
     'Entrepôts de données',
     2.0, 2, TRUE, TRUE, 120, 60),

    ('IGL3-FRANCAIS',
     'Français',
     1.0, 1, FALSE, TRUE, NULL, 60),

    ('IGL3-PROG-LINEAIRE',
     'Programmation linéaire',
     2.0, 2, TRUE, TRUE, 120, 60),

    ('IGL3-ALGORITHMIQUE',
     'Algorithmique et complexité',
     2.5, 3, TRUE, TRUE, 120, 60),

    ('IGL3-ING-SYSTEMES',
     'Ingénierie des systèmes',
     2.5, 3, TRUE, TRUE, 120, 60),

    ('IGL3-TECH-WEB',
     'Technologie Web et multimédia',
     2.0, 2, TRUE, TRUE, 120, 60),

    ('IGL3-MICROECONOMIE',
     'Introduction à la microéconomie',
     1.5, 2, TRUE, TRUE, 90, 60)

ON CONFLICT (code) DO NOTHING;


-- ============================================================================
-- 5, 6, 7. SECTION_MATIERE, ENSEIGNANTS, ENSEIGNEMENT (inchangés)
-- ============================================================================
-- ... (copier-coller le reste du script précédent, il est correct) ...

-- 5. SECTION_MATIERE
INSERT INTO section_matiere (section_id, matiere_id, a_examen_final, a_ds, duree_examen, duree_ds)
SELECT
    s.id,
    m.id,
    m.a_examen_final,
    m.a_ds,
    m.duree_examen,
    m.duree_ds
FROM section s
JOIN niveau n ON n.id = s.niveau_id
CROSS JOIN matiere m
WHERE s.nom = 'IGL3'
  AND n.libelle = 'Cycle Ingénieur'
  AND m.code LIKE 'IGL3-%'
ON CONFLICT (section_id, matiere_id) DO NOTHING;

-- 6. ENSEIGNANTS
INSERT INTO enseignant (nom, prenom, grade, email, departement_id)
VALUES
    ('Moussa',    'Faouzi',   'Prof.',                  'faouzi.moussa@fst.utm.tn',    1),
    ('Hiaoui',    'Y.',       'Maître de Conférences',  'y.hiaoui@fst.utm.tn',         1),
    ('Abbassi',   'F.',       'Maître de Conférences',  'f.abbassi@fst.utm.tn',        1),
    ('Amdouni',   'Asma',     'Maître Ass.',            'asma.amdouni@fst.utm.tn',     1),
    ('Agrebi',    'Adel',     'Ass-Info',               'adel.agrebi@fst.utm.tn',      1),
    ('Zekri',     'Manel',    'Maître Ass.',            'manel.zekri@fst.utm.tn',      1),
    ('Krichen',   'N.',       'Maître de Conférences',  'n.krichen@fst.utm.tn',        1),
    ('Fayech',    'Ines',     'Maître Ass.',            'ines.fayech@fst.utm.tn',      1),
    ('Hamzaoui',  'M.',       'Maître de Conférences',  'm.hamzaoui@fst.utm.tn',       1),
    ('Blanco',    'Rym',      'PES-Français',           'rym.blanco@fst.utm.tn',       1),
    ('Omrane',    'Anissa',   'Maître Ass.',            'anissa.omrane@fst.utm.tn',    1),
    ('Jaballah',  'Soumaya',  'Economiste',             'jaballahsoumaya@hotmail.fr',  1)
ON CONFLICT (email) DO NOTHING;

-- 7. ENSEIGNEMENT
-- Projet NT : TP (Faouzi Moussa)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'faouzi.moussa@fst.utm.tn' AND m.code = 'IGL3-PROJET-NT'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Techniques Compilation : Cours (Y. Hiaoui) + TD (F. Abbassi)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'y.hiaoui@fst.utm.tn' AND m.code = 'IGL3-TECH-COMPILATION'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'f.abbassi@fst.utm.tn' AND m.code = 'IGL3-TECH-COMPILATION'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Anglais : TD (N. Krichen)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'n.krichen@fst.utm.tn' AND m.code = 'IGL3-ANGLAIS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Admin BD : Cours + TD (Adel Agrebi)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'adel.agrebi@fst.utm.tn' AND m.code = 'IGL3-ADMIN-BD'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'adel.agrebi@fst.utm.tn' AND m.code = 'IGL3-ADMIN-BD'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Architecture Logicielle : Cours + TD (Asma Amdouni) + TD (F. Abbassi si souhaité)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'asma.amdouni@fst.utm.tn' AND m.code = 'IGL3-ARCHI-LOGICIELLE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'asma.amdouni@fst.utm.tn' AND m.code = 'IGL3-ARCHI-LOGICIELLE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'f.abbassi@fst.utm.tn' AND m.code = 'IGL3-ARCHI-LOGICIELLE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Entrepôts : Cours + TD (Manel Zekri)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'manel.zekri@fst.utm.tn' AND m.code = 'IGL3-ENTREPOTS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'manel.zekri@fst.utm.tn' AND m.code = 'IGL3-ENTREPOTS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'manel.zekri@fst.utm.tn' AND m.code = 'IGL3-ENTREPOTS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Français : TD (Rym Blanco)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'rym.blanco@fst.utm.tn' AND m.code = 'IGL3-FRANCAIS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Programmation linéaire : COURS + TD (Ines Fayech)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-PROG-LINEAIRE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-PROG-LINEAIRE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Algorithmique : COURS + TD + TP (Ines Fayech)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-ALGORITHMIQUE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-ALGORITHMIQUE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-ALGORITHMIQUE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Ingénierie des systèmes : COURS (Anissa Omrane)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'anissa.omrane@fst.utm.tn' AND m.code = 'IGL3-ING-SYSTEMES'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Technologie Web : COURS + TP (M. Hamzaoui)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'm.hamzaoui@fst.utm.tn' AND m.code = 'IGL3-TECH-WEB'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'm.hamzaoui@fst.utm.tn' AND m.code = 'IGL3-TECH-WEB'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Microéconomie : COURS (Soumaya Jaballah)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'jaballahsoumaya@hotmail.fr' AND m.code = 'IGL3-MICROECONOMIE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;


COMMIT;