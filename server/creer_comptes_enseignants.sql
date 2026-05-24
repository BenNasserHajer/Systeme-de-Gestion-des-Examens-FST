-- ============================================================================
-- Script pour créer des comptes enseignants
-- ============================================================================

-- IMPORTANT: Ce script crée des comptes avec des mots de passe en CLAIR
-- En production, utilisez bcrypt pour hasher les mots de passe!

-- ============================================================================
-- Option 1: Créer un compte pour UN enseignant spécifique
-- ============================================================================

-- Exemple: Créer un compte pour l'enseignant avec id=1
-- Remplacer les valeurs selon vos besoins

INSERT INTO compte_enseignant (
    enseignant_id,
    email,
    mot_de_passe,
    type_compte,
    actif
) VALUES (
    1,                              -- ID de l'enseignant (voir avec voir_enseignants.sql)
    'enseignant1@fst.utm.tn',      -- Email de connexion
    'password123',                  -- Mot de passe en CLAIR (⚠️ à changer!)
    'ENSEIGNANT',                   -- Type de compte
    true                            -- Compte actif
)
ON CONFLICT (enseignant_id) DO NOTHING;  -- Ne rien faire si le compte existe déjà


-- ============================================================================
-- Option 2: Créer des comptes pour PLUSIEURS enseignants
-- ============================================================================

-- Exemple: Créer des comptes pour les 5 premiers enseignants
-- Ajustez les IDs et emails selon vos données

INSERT INTO compte_enseignant (enseignant_id, email, mot_de_passe, type_compte, actif)
VALUES 
    (1, 'enseignant1@fst.utm.tn', 'password123', 'ENSEIGNANT', true),
    (2, 'enseignant2@fst.utm.tn', 'password123', 'ENSEIGNANT', true),
    (3, 'enseignant3@fst.utm.tn', 'password123', 'ENSEIGNANT', true),
    (4, 'enseignant4@fst.utm.tn', 'password123', 'ENSEIGNANT', true),
    (5, 'enseignant5@fst.utm.tn', 'password123', 'ENSEIGNANT', true)
ON CONFLICT (enseignant_id) DO NOTHING;


-- ============================================================================
-- Option 3: Créer des comptes pour TOUS les enseignants automatiquement
-- ============================================================================

-- Cette requête génère automatiquement des emails basés sur nom.prenom@fst.utm.tn
-- et utilise 'password123' comme mot de passe par défaut

INSERT INTO compte_enseignant (enseignant_id, email, mot_de_passe, type_compte, actif)
SELECT 
    e.id,
    LOWER(REPLACE(e.prenom, ' ', '.') || '.' || REPLACE(e.nom, ' ', '.')) || '@fst.utm.tn' as email,
    'password123' as mot_de_passe,
    'ENSEIGNANT' as type_compte,
    true as actif
FROM enseignant e
WHERE NOT EXISTS (
    SELECT 1 FROM compte_enseignant ce WHERE ce.enseignant_id = e.id
)
ON CONFLICT (email) DO NOTHING;


-- ============================================================================
-- Option 4: Créer des comptes en utilisant l'email existant de l'enseignant
-- ============================================================================

-- Si les enseignants ont déjà un email dans la table enseignant,
-- utilisez-le pour créer le compte

INSERT INTO compte_enseignant (enseignant_id, email, mot_de_passe, type_compte, actif)
SELECT 
    e.id,
    e.email,
    'password123' as mot_de_passe,
    'ENSEIGNANT' as type_compte,
    true as actif
FROM enseignant e
WHERE e.email IS NOT NULL 
  AND e.email != ''
  AND NOT EXISTS (
    SELECT 1 FROM compte_enseignant ce WHERE ce.enseignant_id = e.id
)
ON CONFLICT (email) DO NOTHING;


-- ============================================================================
-- Vérification après création
-- ============================================================================

-- Voir tous les comptes créés
SELECT 
    ce.id,
    e.nom,
    e.prenom,
    ce.email,
    ce.type_compte,
    ce.actif,
    ce.created_at
FROM compte_enseignant ce
INNER JOIN enseignant e ON ce.enseignant_id = e.id
ORDER BY ce.created_at DESC;


-- ============================================================================
-- Exemples de modification
-- ============================================================================

-- Changer le mot de passe d'un compte
UPDATE compte_enseignant 
SET mot_de_passe = 'nouveau_password', 
    updated_at = NOW()
WHERE email = 'enseignant1@fst.utm.tn';

-- Désactiver un compte
UPDATE compte_enseignant 
SET actif = false, 
    updated_at = NOW()
WHERE email = 'enseignant1@fst.utm.tn';

-- Réactiver un compte
UPDATE compte_enseignant 
SET actif = true, 
    updated_at = NOW()
WHERE email = 'enseignant1@fst.utm.tn';

-- Supprimer un compte
DELETE FROM compte_enseignant 
WHERE email = 'enseignant1@fst.utm.tn';


-- ============================================================================
-- NOTES IMPORTANTES
-- ============================================================================

/*
1. SÉCURITÉ:
   - Les mots de passe sont stockés en CLAIR (pas sécurisé!)
   - En production, utilisez bcrypt pour hasher les mots de passe
   - Voir le script Python: creer_comptes_enseignants.py

2. CONTRAINTES:
   - Un enseignant ne peut avoir qu'UN SEUL compte (enseignant_id UNIQUE)
   - Chaque email doit être unique (email UNIQUE)
   - L'enseignant_id doit exister dans la table enseignant (FOREIGN KEY)

3. EMAILS:
   - Format recommandé: prenom.nom@fst.utm.tn
   - Évitez les espaces et caractères spéciaux
   - Utilisez LOWER() pour normaliser

4. MOTS DE PASSE PAR DÉFAUT:
   - 'password123' est utilisé comme exemple
   - Demandez aux enseignants de changer leur mot de passe après la première connexion
   - Implémentez une fonctionnalité "Mot de passe oublié"

5. TYPES DE COMPTE:
   - 'ENSEIGNANT': Compte enseignant standard
   - 'ADMIN': Compte administrateur (à éviter, utilisez le compte admin hardcodé)

6. STATUT ACTIF:
   - true: Le compte peut se connecter
   - false: Le compte est désactivé (ne peut pas se connecter)
*/
