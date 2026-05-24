-- ============================================================================
-- Script de Création des Tables d'Authentification
-- ============================================================================
-- Ce script crée les tables nécessaires pour l'authentification JWT
-- et la gestion des comptes enseignants
-- ============================================================================

-- 1. Table compte_enseignant
-- ============================================================================
-- Stocke les informations d'authentification des enseignants

CREATE TABLE IF NOT EXISTS compte_enseignant (
    id SERIAL PRIMARY KEY,
    enseignant_id INTEGER NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Contrainte de clé étrangère vers enseignant
    CONSTRAINT fk_compte_enseignant 
        FOREIGN KEY (enseignant_id) 
        REFERENCES enseignant(id) 
        ON DELETE CASCADE
);

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_compte_enseignant_username ON compte_enseignant(username);
CREATE INDEX IF NOT EXISTS idx_compte_enseignant_email ON compte_enseignant(email);
CREATE INDEX IF NOT EXISTS idx_compte_enseignant_enseignant_id ON compte_enseignant(enseignant_id);
CREATE INDEX IF NOT EXISTS idx_compte_enseignant_is_active ON compte_enseignant(is_active);

-- Commentaires
COMMENT ON TABLE compte_enseignant IS 'Comptes d''authentification des enseignants';
COMMENT ON COLUMN compte_enseignant.enseignant_id IS 'Référence vers la table enseignant';
COMMENT ON COLUMN compte_enseignant.username IS 'Nom d''utilisateur unique pour la connexion';
COMMENT ON COLUMN compte_enseignant.email IS 'Email unique de l''enseignant';
COMMENT ON COLUMN compte_enseignant.hashed_password IS 'Mot de passe hashé avec bcrypt';
COMMENT ON COLUMN compte_enseignant.is_active IS 'Compte actif ou désactivé';
COMMENT ON COLUMN compte_enseignant.is_admin IS 'Droits administrateur';
COMMENT ON COLUMN compte_enseignant.last_login IS 'Date et heure de la dernière connexion';

-- ============================================================================
-- 2. Table refresh_token (optionnel - pour JWT refresh tokens)
-- ============================================================================

CREATE TABLE IF NOT EXISTS refresh_token (
    id SERIAL PRIMARY KEY,
    compte_enseignant_id INTEGER NOT NULL,
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    
    CONSTRAINT fk_refresh_token_compte 
        FOREIGN KEY (compte_enseignant_id) 
        REFERENCES compte_enseignant(id) 
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_refresh_token_compte_id ON refresh_token(compte_enseignant_id);
CREATE INDEX IF NOT EXISTS idx_refresh_token_token ON refresh_token(token);
CREATE INDEX IF NOT EXISTS idx_refresh_token_expires_at ON refresh_token(expires_at);

COMMENT ON TABLE refresh_token IS 'Tokens de rafraîchissement JWT';
COMMENT ON COLUMN refresh_token.token IS 'Token de rafraîchissement unique';
COMMENT ON COLUMN refresh_token.expires_at IS 'Date d''expiration du token';
COMMENT ON COLUMN refresh_token.revoked IS 'Token révoqué (déconnexion)';

-- ============================================================================
-- 3. Table audit_log (optionnel - pour tracer les connexions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    compte_enseignant_id INTEGER,
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_audit_log_compte 
        FOREIGN KEY (compte_enseignant_id) 
        REFERENCES compte_enseignant(id) 
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_log_compte_id ON audit_log(compte_enseignant_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action ON audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

COMMENT ON TABLE audit_log IS 'Journal d''audit des actions d''authentification';
COMMENT ON COLUMN audit_log.action IS 'Type d''action: LOGIN, LOGOUT, FAILED_LOGIN, etc.';
COMMENT ON COLUMN audit_log.ip_address IS 'Adresse IP de l''utilisateur';
COMMENT ON COLUMN audit_log.user_agent IS 'User agent du navigateur';

-- ============================================================================
-- 4. Fonction pour mettre à jour updated_at automatiquement
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour compte_enseignant
DROP TRIGGER IF EXISTS update_compte_enseignant_updated_at ON compte_enseignant;
CREATE TRIGGER update_compte_enseignant_updated_at
    BEFORE UPDATE ON compte_enseignant
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 5. Données de test (optionnel)
-- ============================================================================
-- Créer des comptes de test pour les enseignants existants
-- Mot de passe par défaut: "password123" (hashé avec bcrypt)
-- IMPORTANT: Changer ces mots de passe en production!

-- Hash bcrypt pour "password123": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6

INSERT INTO compte_enseignant (enseignant_id, username, email, hashed_password, is_active, is_admin)
SELECT 
    e.id,
    LOWER(REPLACE(e.nom || '.' || e.prenom, ' ', '')),
    LOWER(REPLACE(e.nom || '.' || e.prenom, ' ', '')) || '@university.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6',
    TRUE,
    FALSE
FROM enseignant e
WHERE NOT EXISTS (
    SELECT 1 FROM compte_enseignant ce WHERE ce.enseignant_id = e.id
)
LIMIT 10;  -- Créer seulement pour les 10 premiers enseignants (ajuster selon besoin)

-- Créer un compte admin
INSERT INTO compte_enseignant (enseignant_id, username, email, hashed_password, is_active, is_admin)
SELECT 
    e.id,
    'admin',
    'admin@university.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6',
    TRUE,
    TRUE
FROM enseignant e
WHERE e.id = 1
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- 6. Vérification des tables créées
-- ============================================================================

SELECT 
    'compte_enseignant' as table_name,
    COUNT(*) as row_count
FROM compte_enseignant

UNION ALL

SELECT 
    'refresh_token',
    COUNT(*)
FROM refresh_token

UNION ALL

SELECT 
    'audit_log',
    COUNT(*)
FROM audit_log;

-- ============================================================================
-- 7. Afficher les comptes créés
-- ============================================================================

SELECT 
    ce.id,
    ce.username,
    ce.email,
    e.nom,
    e.prenom,
    e.grade,
    d.nom as departement,
    ce.is_active,
    ce.is_admin,
    ce.created_at
FROM compte_enseignant ce
JOIN enseignant e ON ce.enseignant_id = e.id
LEFT JOIN departement d ON e.departement_id = d.id
ORDER BY ce.id;

-- ============================================================================
-- 8. Requêtes utiles pour la gestion des comptes
-- ============================================================================

-- Activer/Désactiver un compte
-- UPDATE compte_enseignant SET is_active = FALSE WHERE username = 'nom.prenom';

-- Réinitialiser le mot de passe (password123)
-- UPDATE compte_enseignant 
-- SET hashed_password = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/qvQu6'
-- WHERE username = 'nom.prenom';

-- Promouvoir un utilisateur en admin
-- UPDATE compte_enseignant SET is_admin = TRUE WHERE username = 'nom.prenom';

-- Voir les dernières connexions
-- SELECT 
--     ce.username,
--     e.nom,
--     e.prenom,
--     ce.last_login,
--     ce.is_active
-- FROM compte_enseignant ce
-- JOIN enseignant e ON ce.enseignant_id = e.id
-- ORDER BY ce.last_login DESC NULLS LAST
-- LIMIT 20;

-- Voir l'historique d'audit
-- SELECT 
--     al.created_at,
--     ce.username,
--     al.action,
--     al.success,
--     al.ip_address
-- FROM audit_log al
-- LEFT JOIN compte_enseignant ce ON al.compte_enseignant_id = ce.id
-- ORDER BY al.created_at DESC
-- LIMIT 50;

-- ============================================================================
-- FIN DU SCRIPT
-- ============================================================================
-- Les tables d'authentification sont maintenant créées et prêtes à l'emploi.
-- 
-- Comptes de test créés avec:
--   Username: nom.prenom (en minuscules, sans espaces)
--   Password: password123
--   Admin: username=admin, password=admin123
--
-- IMPORTANT: Changez ces mots de passe en production!
-- ============================================================================
