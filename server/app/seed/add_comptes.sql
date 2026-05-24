-- ============================================================
-- SCRIPT POUR AJOUTER LES COMPTES ENSEIGNANTS MANQUANTS
-- ============================================================

-- 1. Ajout des comptes pour tous les enseignants qui n'en ont pas
INSERT INTO compte_enseignant (enseignant_id, email, mot_de_passe, type_compte, actif)
SELECT 
    e.id,
    -- Format: prenom.nom@fst.utm.tn (tout en minuscules, espaces remplacés par des points si besoin)
    LOWER(REPLACE(e.prenom, ' ', '.')) || '.' || LOWER(REPLACE(e.nom, ' ', '.')) || '@fst.utm.tn',
    'password123', -- Mot de passe par défaut
    'ENSEIGNANT',
    TRUE
FROM enseignant e
WHERE NOT EXISTS (
    SELECT 1 FROM compte_enseignant c WHERE c.enseignant_id = e.id
);

-- ============================================================
-- NOTE: L'enseignant "Bench Teacher 1" aura l'email :
-- teacher.1.bench@fst.utm.tn ou similaire.
-- ============================================================
-- Vérification rapide :
-- SELECT * FROM compte_enseignant WHERE email LIKE '%bench%';
