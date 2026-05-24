-- ============================================================================
-- Création du Compte Admin
-- ============================================================================

-- Supprimer le compte admin s'il existe déjà
DELETE FROM compte_enseignant WHERE email = 'admin@university.edu';

-- Créer le compte admin
-- Hash bcrypt pour "admin123": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6
INSERT INTO compte_enseignant (
    enseignant_id,
    email,
    mot_de_passe,
    type_compte,
    actif
)
SELECT 
    e.id,
    'admin@university.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6',
    'ADMIN',
    TRUE
FROM enseignant e
WHERE e.id = 1
ON CONFLICT (email) DO UPDATE
SET 
    mot_de_passe = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6',
    type_compte = 'ADMIN',
    actif = TRUE;

-- Vérifier le compte créé
SELECT 
    ce.id,
    ce.email,
    e.nom,
    e.prenom,
    ce.type_compte,
    ce.actif,
    ce.created_at
FROM compte_enseignant ce
JOIN enseignant e ON ce.enseignant_id = e.id
WHERE ce.email = 'admin@university.edu';

-- Afficher les informations de connexion
SELECT 
    '✅ Compte admin créé avec succès!' as message,
    'admin@university.edu' as email,
    'admin123' as mot_de_passe;
