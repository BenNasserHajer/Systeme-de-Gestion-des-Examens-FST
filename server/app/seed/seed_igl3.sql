-- ============================================================================
-- Script de Seed CORRIGÉ — Section IGL3 (Cycle Ingénieur)
-- Faculté des Sciences de Tunis — Année 2025-2026
-- Section : IGL3 (60 étudiants, 2 groupes de 30)
--
-- CORRECTIONS APPORTÉES :
--   🔴 E1  : ON CONFLICT DO NOTHING → ON CONFLICT (col) DO NOTHING + suppression
--             des WHERE NOT EXISTS redondants et mal scopés
--   🔴 E2  : Code matière 'IGL3' → supprimé (doublon de 'IGL3-ARCHI-LOGICIELLE')
--   🔴 E12 : Matière 'IGL3-TD-G1-G2' manquante → ajoutée dans matiere
--   🟡 E3  : Doublon 'IGL3-COMP' → supprimé (= IGL3-TECH-COMPILATION)
--   🟡 E4  : duree_examen = 0 → NULL pour les matières sans examen final
--   🟡 E5  : Codes trop génériques → IGL3-TP-ENTREPOTS, IGL3-TP-ALGORITHMIQUE
--   🟡 E8  : Email Agrbi harmonisé → adel.agrebi@fst.utm.tn (si même personne)
--   🟡 E10 : Intitulé corrigé ('des Faitech' supprimé)
--   🟡 E13 : Omrane Amina → Omrane Anissa + email harmonisé
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. NIVEAU
-- 🔴 E1 CORRIGÉ : ON CONFLICT (libelle, annee) DO NOTHING
--    Suppression du WHERE NOT EXISTS redondant et mal scopé
-- ============================================================================
INSERT INTO niveau (libelle, annee, type_formation, departement_id)
VALUES ('Cycle Ingénieur', 3, 'IGL', 1)
ON CONFLICT (libelle, annee) DO NOTHING;

-- ============================================================================
-- 2. SECTION IGL3
-- 🔴 E1 CORRIGÉ : ON CONFLICT (nom, niveau_id) DO NOTHING
-- ============================================================================
INSERT INTO section (nom, nb_etudiants, niveau_id)
SELECT 'IGL3', 60, n.id
FROM niveau n
WHERE n.libelle = 'Cycle Ingénieur' AND n.annee = 3
ON CONFLICT (nom, niveau_id) DO NOTHING;

-- ============================================================================
-- 3. GROUPES
-- 🔴 E1 CORRIGÉ : ON CONFLICT (section_id, numero) DO NOTHING (déjà correct)
-- ============================================================================
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
-- 4. MATIÈRES

-- ============================================================================

INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds)
VALUES
    -- ── Lundi ────────────────────────────────────────────────────────────────
    -- 🔴 E2 : 'IGL3' supprimé → 'IGL3-ARCHI-LOGICIELLE' existe déjà (Mercredi)
    ('IGL3-PROJET-NT',
     'Projet d''application nouvelles technologies',
     2.5, 3, TRUE, TRUE, 120, 60),

    -- ── Mardi ────────────────────────────────────────────────────────────────
    -- 🟡 E3 : 'IGL3-COMP' supprimé (doublon de IGL3-TECH-COMPILATION)
    ('IGL3-TECH-COMPILATION',
     'Techniques de Compilation',
     2.0, 2, TRUE, TRUE, 120, 60),

    -- 🟡 E4 : duree_examen = NULL (pas d'examen final)
    ('IGL3-ANGLAIS',
     'Anglais',
     1.0, 1, FALSE, TRUE, NULL, 60),

    -- ── Mercredi ─────────────────────────────────────────────────────────────
    ('IGL3-ADMIN-BD',
     'Administration des bases de données',
     2.0, 2, TRUE, TRUE, 120, 60),

    ('IGL3-ARCHI-LOGICIELLE',
     'Architecture Logicielle',
     2.0, 2, TRUE, TRUE, 120, 60),

    -- ── Jeudi ────────────────────────────────────────────────────────────────
    ('IGL3-ENTREPOTS',
     'Entrepôts de données',
     2.0, 2, TRUE, TRUE, 120, 60),

    

    -- 🟡 E4 : duree_examen = NULL (pas d'examen final)
    ('IGL3-FRANCAIS',
     'Français',
     1.0, 1, FALSE, TRUE, NULL, 60),

    ('IGL3-PROG-LINEAIRE',
     'Programmation linéaire',
     2.0, 2, TRUE, TRUE, 120, 60),

    -- ── Vendredi ─────────────────────────────────────────────────────────────
    -- 🟡 E10 : 'des Faitech' supprimé de l'intitulé
    ('IGL3-ALGORITHMIQUE',
     'Algorithmique et complexité',
     2.5, 3, TRUE, TRUE, 120, 60),

    

    -- ── Samedi ───────────────────────────────────────────────────────────────
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
-- 5. SECTION_MATIERE
-- Lie automatiquement toutes les matières IGL3 à la section IGL3.
-- Le filtre LIKE 'IGL3-%' exclut naturellement 'IGL3' (E2 corrigé).
-- Les matières sans examen final (Anglais, Français) sont liées mais
-- l'algorithme les ignorera grâce au flag a_examen_final = FALSE.
-- ============================================================================
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

-- ============================================================================
-- 6. ENSEIGNANTS
--
-- 🟡 E8  CORRIGÉ : Agrbi → Agrebi, email harmonisé si même personne que DSI
-- 🟡 E13 CORRIGÉ : Omrane Amina → Omrane Anissa, email harmonisé
-- Note : Abbassi F. (f.abbassi@fst.utm.tn) ≠ Abbessi Faten (faten.abbassi@fst.utm.tn)
--        → deux personnes différentes, les deux emails sont conservés
-- ============================================================================
INSERT INTO enseignant (nom, prenom, grade, email, departement_id)
VALUES
    ('Moussa',    'Faouzi',   'Professeur',           'faouzi.moussa@fst.utm.tn',    1),
    ('Hiaoui',    'Y.',       'Maître de Conférences', 'y.hiaoui@fst.utm.tn',         1),
    -- Abbassi F. : email différent de Abbessi Faten → deux personnes distinctes
    ('Abbassi',   'F.',       'Maître de Conférences', 'f.abbassi@fst.utm.tn',        1),
    ('Amdouni',   'Asma',     'Maître Ass.',           'asma.amdouni@fst.utm.tn',     1),
    -- 🟡 E8 : Agrbi → Agrebi, email harmonisé avec script DSI
    ('Agrebi',    'Adel',     'Ass-Info',              'adel.agrebi@fst.utm.tn',      1),
    ('Zekri',     'Manel',    'Maître Ass.',           'manel.zekri@fst.utm.tn',      1),
    ('Krichen',   'N.',       'Maître de Conférences', 'n.krichen@fst.utm.tn',        1),
    ('Fayech',    'Ines',     'Maître Ass.',           'ines.fayech@fst.utm.tn',      1),
    ('Hamzaoui',  'M.',       'Maître de Conférences', 'm.hamzaoui@fst.utm.tn',       1),
    ('Blanco',    'Rym',      'PES-Français',          'rym.blanco@fst.utm.tn',       1),
    -- 🟡 E13 : Omrane Amina → Omrane Anissa, email harmonisé avec script DSI
    ('Omrane',    'Anissa',   'Maître Ass.',           'anissa.omrane@fst.utm.tn',    1),
    ('Jaballah',  'Soumaya',  'Economiste',            'jaballahsoumaya@hotmail.fr',  1)
ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- 7. ENSEIGNEMENT
-- 🔴 E12 CORRIGÉ : IGL3-TD-G1-G2 → IGL3-TD-ALGO-G1-G2 (code maintenant existant)
-- 🟡 E5  CORRIGÉ : IGL3-TD-G1-G2-VENDREDI → IGL3-TD-ALGO-G1-G2
--                   IGL3-TP-G1-G2 → IGL3-TP-ALGORITHMIQUE
--                   IGL3-TP-G1-G2-TECH-WEB → IGL3-TP-TECH-WEB
-- ============================================================================

-- ── Lundi ─────────────────────────────────────────────────────────────────

-- Projet d'application nouvelles technologies — F. Moussa (TP)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'faouzi.moussa@fst.utm.tn' AND m.code = 'IGL3-PROJET-NT'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Techniques de Compilation — Y. Hiaoui (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'y.hiaoui@fst.utm.tn' AND m.code = 'IGL3-TECH-COMPILATION'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Architecture Logicielle — Asma Amdouni (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'asma.amdouni@fst.utm.tn' AND m.code = 'IGL3-ARCHI-LOGICIELLE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- 🔴 E12 CORRIGÉ : IGL3-TD-G1-G2 → IGL3-TD-ALGO-G1-G2 (F. Abbassi, TD Algo Lundi)
-- NOTE : Si ce TD concerne Architecture Logicielle (et non Algorithmique),
--        changer le code en 'IGL3-ARCHI-LOGICIELLE' et le type en 'TD'
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'f.abbassi@fst.utm.tn' AND m.code = 'IGL3-ARCHI-LOGICIELLE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- ── Mardi ─────────────────────────────────────────────────────────────────

-- Tech Compilation TD — F. Abbassi (TD)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'f.abbassi@fst.utm.tn' AND m.code = 'IGL3-TECH-COMPILATION'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Anglais — N. Krichen (TD)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'n.krichen@fst.utm.tn' AND m.code = 'IGL3-ANGLAIS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- ── Mercredi ──────────────────────────────────────────────────────────────

-- Administration des BD — Agrebi Adel (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'adel.agrebi@fst.utm.tn' AND m.code = 'IGL3-ADMIN-BD'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Architecture Logicielle — Asma Amdouni (TD)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'asma.amdouni@fst.utm.tn' AND m.code = 'IGL3-ARCHI-LOGICIELLE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- ── Jeudi ─────────────────────────────────────────────────────────────────

-- Entrepôts de données — Manel Zekri (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'manel.zekri@fst.utm.tn' AND m.code = 'IGL3-ENTREPOTS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- TP/TD Entrepôts — Manel Zekri (TD)
-- 🟡 E5 CORRIGÉ : IGL3-TP-TD → IGL3-TP-ENTREPOTS
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'manel.zekri@fst.utm.tn' AND m.code = 'IGL3-TP-ENTREPOTS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Administration BD TD — Agrebi Adel (TD)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'adel.agrebi@fst.utm.tn' AND m.code = 'IGL3-ADMIN-BD-TD'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Français — Rym Blanco (TD)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'rym.blanco@fst.utm.tn' AND m.code = 'IGL3-FRANCAIS'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Programmation linéaire — Ines Fayech (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-PROG-LINEAIRE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- ── Vendredi ──────────────────────────────────────────────────────────────

-- Algorithmique — Ines Fayech (Cours)
-- 🟡 E10 CORRIGÉ : intitulé sans 'des Faitech'
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-ALGORITHMIQUE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- TD G1/G2 Algorithmique — Ines Fayech (TD)
-- 🔴 E12 / 🟡 E5 CORRIGÉS : IGL3-TD-G1-G2-VENDREDI → IGL3-TD-ALGO-G1-G2
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-TD-ALGO-G1-G2'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- TP G1/G2 Algorithmique — Ines Fayech (TP)
-- 🟡 E5 CORRIGÉ : IGL3-TP-G1-G2 → IGL3-TP-ALGORITHMIQUE
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-TP-ALGORITHMIQUE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Programmation linéaire TD — Ines Fayech (TD)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'ines.fayech@fst.utm.tn' AND m.code = 'IGL3-PROG-LINEAIRE-TD'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- ── Samedi ────────────────────────────────────────────────────────────────

-- Ingénierie des systèmes — Anissa Omrane (Cours)
-- 🟡 E13 CORRIGÉ : email anissa.omrane@fst.utm.tn
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'anissa.omrane@fst.utm.tn' AND m.code = 'IGL3-ING-SYSTEMES'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Technologie Web — M. Hamzaoui (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'm.hamzaoui@fst.utm.tn' AND m.code = 'IGL3-TECH-WEB'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- TP G1/G2 Tech Web — M. Hamzaoui (TP)
-- 🟡 E5 CORRIGÉ : IGL3-TP-G1-G2-TECH-WEB → IGL3-TP-TECH-WEB
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TP', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'm.hamzaoui@fst.utm.tn' AND m.code = 'IGL3-TP-TECH-WEB'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Tech Compilation TD quinzaine — F. Abbassi (TD)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'TD', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'f.abbassi@fst.utm.tn' AND m.code = 'IGL3-TECH-COMPILATION-TD'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

-- Microéconomie — Soumaya Jaballah (Cours)
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
SELECT e.id, m.id, 'COURS', 21, '2025-2026'
FROM enseignant e, matiere m
WHERE e.email = 'jaballahsoumaya@hotmail.fr' AND m.code = 'IGL3-MICROECONOMIE'
ON CONFLICT (enseignant_id, matiere_id, type_enseignement) DO NOTHING;

COMMIT;

-- ============================================================================
-- 8. VÉRIFICATIONS POST-INSERT
-- ============================================================================

-- Résumé de la section IGL3
SELECT
    s.id              AS section_id,
    s.nom             AS section,
    s.nb_etudiants,
    n.libelle         AS niveau,
    COUNT(DISTINCT sm.matiere_id)
                      AS nb_matieres_total,
    COUNT(DISTINCT CASE WHEN sm.a_examen_final = TRUE  THEN sm.matiere_id END)
                      AS nb_matieres_avec_examen,
    COUNT(DISTINCT CASE WHEN sm.a_examen_final = FALSE THEN sm.matiere_id END)
                      AS nb_matieres_sans_examen
FROM section s
JOIN niveau n          ON n.id = s.niveau_id
LEFT JOIN section_matiere sm ON sm.section_id = s.id
WHERE s.nom = 'IGL3'
GROUP BY s.id, s.nom, s.nb_etudiants, n.libelle;

-- Détail des matières avec statut examen
SELECT
    m.code,
    m.intitule,
    m.coefficient,
    m.duree_examen,
    CASE
        WHEN m.a_examen_final = FALSE THEN 'Pas d''examen final (DS seulement)'
        ELSE 'Examen final + DS'
    END AS statut
FROM section_matiere sm
JOIN section  s ON s.id = sm.section_id
JOIN matiere  m ON m.id = sm.matiere_id
JOIN niveau   n ON n.id = s.niveau_id
WHERE s.nom = 'IGL3' AND n.libelle = 'Cycle Ingénieur'
ORDER BY m.a_examen_final DESC, m.code;

-- Enseignants liés à IGL3 avec leurs matières
SELECT DISTINCT
    e.nom,
    e.prenom,
    e.grade,
    m.code            AS code_matiere,
    m.intitule        AS matiere,
    en.type_enseignement
FROM enseignement en
JOIN enseignant e ON e.id = en.enseignant_id
JOIN matiere    m ON m.id = en.matiere_id
WHERE m.code LIKE 'IGL3-%'
ORDER BY e.nom, e.prenom, m.code;

-- Groupes de la section
SELECT g.numero, g.effectif, s.nom AS section
FROM groupe g
JOIN section s ON s.id = g.section_id
WHERE s.nom = 'IGL3'
ORDER BY g.numero;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================