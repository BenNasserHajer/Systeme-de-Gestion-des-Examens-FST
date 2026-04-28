-- ============================================================================
-- Script de Seed pour la Section IGL4 (Cycle Ingénieur)
-- Faculté des Sciences de Tunis - Année 2025-2026
-- Section : IGL4 (53 étudiants)
-- ============================================================================

-- ============================================================================
-- 1. NIVEAU
-- ============================================================================

-- Vérifier si le niveau existe déjà, sinon l'insérer
INSERT INTO niveau (libelle, annee, type_formation, departement_id)
SELECT 'Cycle Ingénieur', 4, 'IGL', 1
WHERE NOT EXISTS (
    SELECT 1 FROM niveau WHERE libelle = 'Cycle Ingénieur' AND annee = 4
)
RETURNING id;

-- Récupérer l'ID du niveau (pour référence)
-- ID sera utilisé dans les requêtes suivantes

-- ============================================================================
-- 2. SECTION IGL4
-- ============================================================================

-- Insérer la section IGL4
INSERT INTO section (nom, nb_etudiants, niveau_id)
SELECT 'IGL4', 53, n.id
FROM niveau n
WHERE n.libelle = 'Cycle Ingénieur' AND n.annee = 4
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 3. GROUPE (1 groupe de 53 étudiants)
-- ============================================================================

-- Insérer le groupe principal
INSERT INTO groupe (numero, effectif, section_id)
SELECT 1, 53, s.id
FROM section s
JOIN niveau n ON n.id = s.niveau_id
WHERE s.nom = 'IGL4' AND n.libelle = 'Cycle Ingénieur'
ON CONFLICT (section_id, numero) DO NOTHING;

-- ============================================================================
-- 4. MATIÈRES
-- ============================================================================

-- Matières du Lundi
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
VALUES 
    ('IGL4-ML-DL', 'Machine Learning & Deep Learning', 2.5, 3, TRUE, TRUE, 120, 60),
    ('IGL4-DEV-JEE', 'Développement JEE', 2.0, 2, TRUE, TRUE, 120, 60)
ON CONFLICT (code) DO NOTHING;

-- Matières du Mardi
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
VALUES 
    ('IGL4-OPT1-NOSQL', 'Option 1: NoSQL', 2.0, 2, TRUE, FALSE, 120, 60),
    ('IGL4-ANGLAIS', 'Anglais', 1.0, 1, FALSE, TRUE, 90, 60),
    ('IGL4-DROIT-ETH', 'Droit & Éthique Informatique', 1.5, 2, TRUE, TRUE, 90, 60)
ON CONFLICT (code) DO NOTHING;

-- Matières du Mercredi
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
VALUES 
    ('IGL4-ING-IMAGE', 'Ingénierie de l''Image', 2.0, 2, TRUE, TRUE, 120, 60),
    ('IGL4-PROJET-NT4', 'Projet d''application nouvelle technologie 4', 2.5, 3, TRUE, FALSE, 120, 0)
ON CONFLICT (code) DO NOTHING;

-- Matières du Jeudi
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
VALUES 
    ('IGL4-ENTREPRENEUR', 'Entreprenariat', 1.5, 2, TRUE, TRUE, 90, 60),
    ('IGL4-FOUILLE-DATA', 'Fouille de données', 2.0, 2, TRUE, TRUE, 120, 60)
ON CONFLICT (code) DO NOTHING;

-- Matières du Vendredi
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
VALUES 
    ('IGL4-BIG-DATA', 'Big Data', 2.5, 3, TRUE, TRUE, 120, 60),
ON CONFLICT (code) DO NOTHING;

-- Matières du Samedi
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
VALUES 
    ('IGL4-OPT2-GRAPHQL', 'Option 2: GraphQL', 2.0, 2, TRUE, FALSE, 120, 60),
    ('IGL4-ANALYSE-DATA', 'Analyse de données et application', 2.0, 2, TRUE, TRUE, 120, 60)
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- 5. SECTION_MATIERE (Liaison Section ↔ Matières)
-- ============================================================================

-- Lier toutes les matières à la section IGL4
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
WHERE s.nom = 'IGL4' 
  AND n.libelle = 'Cycle Ingénieur'
  AND m.code LIKE 'IGL4-%'
ON CONFLICT (section_id, matiere_id) DO NOTHING;

-- ============================================================================
-- 6. ENSEIGNANTS (Basé sur l'emploi du temps)
-- ============================================================================

-- Insérer les enseignants s'ils n'existent pas déjà
INSERT INTO enseignant (nom, prenom, grade, email, departement_id)
VALUES 
    -- Lundi
    ('Younes', 'Sana', 'Maître de Conférences', 'sana.younes@fst.utm.tn', 1),
    ('Fourati', 'Hend', 'Maître Assistant', 'hend.fourati@fst.utm.tn', 1),
    
    -- Mardi
    ('Alaya', 'Houda', 'Maître de Conférences', 'houda.alaya@fst.utm.tn', 1),
    ('Dammak', 'Nawel', 'Maître Assistant', 'nawel.dammak@fst.utm.tn', 1),
    ('Gharbi', 'Asma', 'Maître de Conférences', 'asma.gharbi@fst.utm.tn', 1),
    
    -- Mercredi
    ('Abed', 'Rahma', 'Maître de Conférences', 'rahma.abed@fst.utm.tn', 1),
    ('Ben Hassine', 'Med Ali', 'Professeur', 'medali.benhassine@fst.utm.tn', 1),
    
    -- Jeudi
    ('Ochi', 'Wejda', 'Maître de Conférences', 'wejda.ochi@fst.utm.tn', 1),
    ('Ben Othman', 'Leila', 'Maître de Conférences', 'leila.benothman@fst.utm.tn', 1),
    
    -- Samedi
    ('Azzabi', 'Fares', 'Maître Assistant', 'fares.azzabi@fst.utm.tn', 1),
    ('Kchaou', 'Marwa', 'Maître de Conférences', 'marwa.kchaou@fst.utm.tn', 1),
    
    -- Enseignant supplémentaire
    ('Abbes', 'Heithem', 'Maître Assistant', 'heithem.abbes@fst.utm.tn', 1)
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- 7. ENSEIGNEMENT (Liaison Enseignant ↔ Matière)
-- ============================================================================

-- Machine Learning & Deep Learning - Sana Younes (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'sana.younes@fst.utm.tn' AND m.code = 'IGL4-ML-DL'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Machine Learning & Deep Learning - Sana Younes (TD/TP)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'sana.younes@fst.utm.tn' AND m.code = 'IGL4-ML-DL'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Option 1: NoSQL - Houda Alaya (Cours + TP)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'houda.alaya@fst.utm.tn' AND m.code = 'IGL4-OPT1-NOSQL'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'houda.alaya@fst.utm.tn' AND m.code = 'IGL4-OPT1-NOSQL'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Ingénierie de l'Image - Rahma Abed (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'rahma.abed@fst.utm.tn' AND m.code = 'IGL4-ING-IMAGE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Entreprenariat - Wejda Ochi (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'wejda.ochi@fst.utm.tn' AND m.code = 'IGL4-ENTREPRENEUR'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Big Data - Med Ali Ben Hassine (Cours + TD/TP)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'medali.benhassine@fst.utm.tn' AND m.code = 'IGL4-BIG-DATA'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'medali.benhassine@fst.utm.tn' AND m.code = 'IGL4-BIG-DATA'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Développement JEE - Hend Fourati (TD/TP)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'hend.fourati@fst.utm.tn' AND m.code = 'IGL4-DEV-JEE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Anglais - Nawel Dammak (TD)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'nawel.dammak@fst.utm.tn' AND m.code = 'IGL4-ANGLAIS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Projet d'application NT4 - Med Ali Ben Hassine (TP G1)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'medali.benhassine@fst.utm.tn' AND m.code = 'IGL4-PROJET-NT4'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Fouille de données - Leila Ben Othman (Cours + TD/TP)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'leila.benothman@fst.utm.tn' AND m.code = 'IGL4-FOUILLE-DATA'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'leila.benothman@fst.utm.tn' AND m.code = 'IGL4-FOUILLE-DATA'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Projet d'application NT4 (Vendredi) - Med Ali Ben Hassine (TP G2)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'medali.benhassine@fst.utm.tn' AND m.code = 'IGL4-PROJET-NT4-V'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Option 2: GraphQL - Fares Azzabi (Cours + TP)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'fares.azzabi@fst.utm.tn' AND m.code = 'IGL4-OPT2-GRAPHQL'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'fares.azzabi@fst.utm.tn' AND m.code = 'IGL4-OPT2-GRAPHQL'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Droit & Éthique - Asma Gharbi (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'asma.gharbi@fst.utm.tn' AND m.code = 'IGL4-DROIT-ETH'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Analyse de données - Marwa Kchaou (Cours + TD/TP)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'marwa.kchaou@fst.utm.tn' AND m.code = 'IGL4-ANALYSE-DATA'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'marwa.kchaou@fst.utm.tn' AND m.code = 'IGL4-ANALYSE-DATA'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- ============================================================================
-- 8. VÉRIFICATION
-- ============================================================================

-- Afficher les informations de la section IGL4
SELECT 
    s.id AS section_id,
    s.nom AS section_nom,
    s.nb_etudiants,
    n.libelle AS niveau,
    n.annee,
    COUNT(DISTINCT sm.matiere_id) AS nb_matieres
FROM section s
JOIN niveau n ON n.id = s.niveau_id
LEFT JOIN section_matiere sm ON sm.section_id = s.id
WHERE s.nom = 'IGL4'
GROUP BY s.id, s.nom, s.nb_etudiants, n.libelle, n.annee;

-- Afficher les matières de la section IGL4
SELECT 
    m.code,
    m.intitule,
    m.coefficient,
    m.credit,
    m.duree_examen,
    m.a_examen_final,
    m.a_ds
FROM section_matiere sm
JOIN section s ON s.id = sm.section_id
JOIN matiere m ON m.id = sm.matiere_id
JOIN niveau n ON n.id = s.niveau_id
WHERE s.nom = 'IGL4' AND n.libelle = 'Cycle Ingénieur'
ORDER BY m.code;

-- Afficher les enseignants de la section IGL4
SELECT DISTINCT
    e.nom,
    e.prenom,
    e.grade,
    m.intitule AS matiere,
    en.type_enseignement
FROM enseignement en
JOIN enseignant e ON e.id = en.enseignant_id
JOIN matiere m ON m.id = en.matiere_id
WHERE m.code LIKE 'IGL4-%'
ORDER BY e.nom, e.prenom, m.intitule;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================

-- Résumé
SELECT 
    'Section IGL4 créée avec succès' AS message,
    (SELECT COUNT(*) FROM section WHERE nom = 'IGL4') AS nb_sections,
    (SELECT COUNT(*) FROM section_matiere sm 
     JOIN section s ON s.id = sm.section_id 
     WHERE s.nom = 'IGL4') AS nb_matieres,
    (SELECT COUNT(DISTINCT e.id) FROM enseignement en
     JOIN matiere m ON m.id = en.matiere_id
     JOIN enseignant e ON e.id = en.enseignant_id
     WHERE m.code LIKE 'IGL4-%') AS nb_enseignants;
