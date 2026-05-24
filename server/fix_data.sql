-- ============================================================================
-- Script de Correction des Données - Surveillance System
-- ============================================================================
-- Ce script corrige les problèmes de données qui causent les conflits
-- d'affectation automatique des surveillants.
-- ============================================================================

-- 1. Fixer section_departement_id NULL
-- ============================================================================
-- Problème: Toutes les planifications ont section_departement_id = NULL
-- Impact: L'algorithme ne peut pas matcher les enseignants par département
-- Solution: Définir le département pour toutes les planifications VALIDEE

UPDATE planification_examen 
SET section_departement_id = 1 
WHERE session_id = 1 
  AND statut = 'VALIDEE'
  AND section_departement_id IS NULL;

-- Vérifier le résultat
SELECT 
    id,
    type_epreuve,
    section_departement_id,
    statut,
    nb_surveillants_requis
FROM planification_examen 
WHERE session_id = 1 AND statut = 'VALIDEE'
ORDER BY id;

-- 2. Vérifier les charges horaires
-- ============================================================================
-- S'assurer que les enseignants ont un volume horaire défini

SELECT 
    e.id,
    e.nom,
    e.prenom,
    e.grade,
    d.nom as departement,
    COALESCE(ch.volume_horaire, 0) as volume_horaire,
    ch.annee_univ
FROM enseignant e
LEFT JOIN departement d ON e.departement_id = d.id
LEFT JOIN charge_horaire ch ON e.id = ch.enseignant_id 
    AND ch.annee_univ = '2025/2026'
ORDER BY d.nom, e.nom;

-- Si des enseignants n'ont pas de charge horaire, en créer:
-- (Décommenter et ajuster selon vos besoins)

/*
INSERT INTO charge_horaire (enseignant_id, annee_univ, volume_horaire)
SELECT 
    e.id,
    '2025/2026',
    40.0  -- 40 heures par défaut
FROM enseignant e
WHERE NOT EXISTS (
    SELECT 1 FROM charge_horaire ch 
    WHERE ch.enseignant_id = e.id 
    AND ch.annee_univ = '2025/2026'
);
*/

-- 3. Vérifier les disponibilités
-- ============================================================================
-- Lister les indisponibilités déclarées

SELECT 
    d.id,
    e.nom,
    e.prenom,
    d.date,
    d.heure_debut,
    d.heure_fin,
    d.type_dispo,
    d.motif
FROM disponibilite_enseignant d
JOIN enseignant e ON d.enseignant_id = e.id
WHERE d.date BETWEEN '2026-01-07' AND '2026-01-14'
ORDER BY d.date, d.heure_debut;

-- 4. Statistiques après correction
-- ============================================================================

SELECT 
    'Planifications VALIDEE' as metric,
    COUNT(*) as count
FROM planification_examen 
WHERE session_id = 1 AND statut = 'VALIDEE'

UNION ALL

SELECT 
    'Planifications avec département',
    COUNT(*) 
FROM planification_examen 
WHERE session_id = 1 
  AND statut = 'VALIDEE' 
  AND section_departement_id IS NOT NULL

UNION ALL

SELECT 
    'Enseignants avec charge horaire',
    COUNT(DISTINCT ch.enseignant_id)
FROM charge_horaire ch
WHERE ch.annee_univ = '2025/2026'
  AND ch.volume_horaire > 0

UNION ALL

SELECT 
    'Indisponibilités déclarées',
    COUNT(*)
FROM disponibilite_enseignant
WHERE date BETWEEN '2026-01-07' AND '2026-01-14';

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
-- Après avoir exécuté ce script, relancez l'affectation automatique
-- depuis l'interface web: http://localhost:3000/surveillance/affectation
-- ============================================================================
