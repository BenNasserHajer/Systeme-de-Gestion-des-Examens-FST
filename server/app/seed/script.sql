    -- -- BEGIN;

    -- -- -- ============================================================
    -- -- -- NETTOYAGE (ré-exécution propre)
    -- -- -- ============================================================
    -- -- DROP TABLE IF EXISTS surveillance              CASCADE;
    -- -- DROP TABLE IF EXISTS planif_salle              CASCADE;
    -- -- DROP TABLE IF EXISTS planification_examen     CASCADE;
    -- -- DROP TABLE IF EXISTS disponibilite_enseignant CASCADE;
    -- -- DROP TABLE IF EXISTS enseignement             CASCADE;
    -- -- DROP TABLE IF EXISTS section_matiere          CASCADE;
    -- -- DROP TABLE IF EXISTS matiere                  CASCADE;
    -- -- DROP TABLE IF EXISTS charge_horaire           CASCADE;
    -- -- DROP TABLE IF EXISTS enseignant               CASCADE;
    -- -- DROP TABLE IF EXISTS session                  CASCADE;
    -- -- DROP TABLE IF EXISTS creneau                  CASCADE;
    -- -- DROP TABLE IF EXISTS salle                    CASCADE;
    -- -- DROP TABLE IF EXISTS groupe                   CASCADE;
    -- -- DROP TABLE IF EXISTS section                  CASCADE;
    -- -- DROP TABLE IF EXISTS niveau                   CASCADE;
    -- -- DROP TABLE IF EXISTS departement              CASCADE;

    -- -- DROP TYPE IF EXISTS jour_semaine;
    -- -- DROP TYPE IF EXISTS type_disponibilite;
    -- -- DROP TYPE IF EXISTS statut_planif;
    -- -- DROP TYPE IF EXISTS mode_affectation;
    -- -- DROP TYPE IF EXISTS type_enseignement;
    -- -- DROP TYPE IF EXISTS type_epreuve;
    -- -- DROP TYPE IF EXISTS type_session;
    -- -- DROP TYPE IF EXISTS statut_surveillance;

    -- -- -- ============================================================
    -- -- -- EXTENSIONS
    -- -- -- ============================================================
    -- -- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- -- -- ============================================================
    -- -- -- 1. ÉNUMÉRATIONS
    -- -- -- ============================================================
    -- -- CREATE TYPE type_session        AS ENUM ('PRINCIPALE','RATTRAPAGE');
    -- -- CREATE TYPE type_epreuve        AS ENUM ('EXAMEN_FINAL','DS');
    -- -- CREATE TYPE type_enseignement   AS ENUM ('COURS','TD','TP');
    -- -- CREATE TYPE mode_affectation    AS ENUM ('AUTOMATIQUE','MANUELLE');
    -- -- CREATE TYPE statut_planif       AS ENUM ('BROUILLON','VALIDEE','PUBLIEE');
    -- -- CREATE TYPE type_disponibilite  AS ENUM ('DISPONIBLE','INDISPONIBLE','COURS_PREVU','MISSION','CONGE');
    -- -- CREATE TYPE jour_semaine        AS ENUM ('LUNDI','MARDI','MERCREDI','JEUDI','VENDREDI','SAMEDI');
    -- -- CREATE TYPE statut_surveillance AS ENUM ('AFFECTE','CONFIRME');

    -- -- -- ============================================================
    -- -- -- 2. DEPARTEMENT
    -- -- -- ============================================================
    -- -- CREATE TABLE departement (
    -- --     id    SERIAL PRIMARY KEY,
    -- --     nom   VARCHAR(100) NOT NULL,
    -- --     code  VARCHAR(20)  NOT NULL UNIQUE
    -- -- );

    -- -- -- ============================================================
    -- -- -- 3. NIVEAU
    -- -- -- ============================================================
    -- -- CREATE TABLE niveau (
    -- --     id              SERIAL PRIMARY KEY,
    -- --     libelle         VARCHAR(50)  NOT NULL,
    -- --     annee           INTEGER      NOT NULL,
    -- --     type_formation  VARCHAR(50)  NOT NULL,
    -- --     departement_id  INTEGER      NOT NULL REFERENCES departement(id)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 4. SECTION
    -- -- -- ============================================================
    -- -- CREATE TABLE section (
    -- --     id            SERIAL PRIMARY KEY,
    -- --     nom           VARCHAR(20) NOT NULL,
    -- --     nb_etudiants  INTEGER     NOT NULL DEFAULT 0,
    -- --     niveau_id     INTEGER     NOT NULL REFERENCES niveau(id)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 5. GROUPE
    -- -- -- ============================================================
    -- -- CREATE TABLE groupe (
    -- --     id          SERIAL PRIMARY KEY,
    -- --     numero      INTEGER NOT NULL,
    -- --     effectif    INTEGER NOT NULL DEFAULT 0,
    -- --     section_id  INTEGER NOT NULL REFERENCES section(id),
    -- --     UNIQUE (section_id, numero)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 6. SALLE
    -- -- -- ============================================================
    -- -- CREATE TABLE salle (
    -- --     id           SERIAL PRIMARY KEY,
    -- --     code         VARCHAR(30)  NOT NULL UNIQUE,
    -- --     designation  VARCHAR(100),
    -- --     capacite     INTEGER      NOT NULL,
    -- --     batiment     VARCHAR(50)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 7. CRENEAU
    -- -- -- ============================================================
    -- -- CREATE TABLE creneau (
    -- --     id           SERIAL PRIMARY KEY,
    -- --     date         DATE NOT NULL,
    -- --     heure_debut  TIME NOT NULL,
    -- --     heure_fin    TIME NOT NULL,
    -- --     libelle      VARCHAR(50),
    -- --     UNIQUE (date, heure_debut)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 8. SESSION
    -- -- -- ============================================================
    -- -- CREATE TABLE session (
    -- --     id                   SERIAL PRIMARY KEY,
    -- --     type_session         type_session  NOT NULL,
    -- --     annee_universitaire  VARCHAR(10)   NOT NULL,
    -- --     date_debut           DATE          NOT NULL,
    -- --     date_fin             DATE          NOT NULL,
    -- --     statut               statut_planif NOT NULL DEFAULT 'BROUILLON'
    -- -- );

    -- -- -- ============================================================
    -- -- -- 9. ENSEIGNANT
    -- -- -- ============================================================
    -- -- CREATE TABLE enseignant (
    -- --     id              SERIAL PRIMARY KEY,
    -- --     nom             VARCHAR(60)  NOT NULL,
    -- --     prenom          VARCHAR(60)  NOT NULL,
    -- --     grade           VARCHAR(50),
    -- --     email           VARCHAR(100) UNIQUE,
    -- --     telephone       VARCHAR(20),
    -- --     departement_id  INTEGER REFERENCES departement(id)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 10. CHARGE_HORAIRE
    -- -- -- ============================================================
    -- -- CREATE TABLE charge_horaire (
    -- --     id              SERIAL PRIMARY KEY,
    -- --     enseignant_id   INTEGER       NOT NULL REFERENCES enseignant(id),
    -- --     annee_univ      VARCHAR(10)   NOT NULL,
    -- --     volume_horaire  NUMERIC(6,2)  NOT NULL DEFAULT 0,
    -- --     UNIQUE (enseignant_id, annee_univ)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 11. MATIERE
    -- -- -- ============================================================
    -- -- CREATE TABLE matiere (
    -- --     id              SERIAL PRIMARY KEY,
    -- --     code            VARCHAR(20)  NOT NULL UNIQUE,
    -- --     intitule        VARCHAR(150) NOT NULL,
    -- --     coefficient     NUMERIC(4,2) DEFAULT 1,
    -- --     credit          INTEGER      DEFAULT 1,
    -- --     a_examen_final  BOOLEAN      NOT NULL DEFAULT TRUE,
    -- --     a_ds            BOOLEAN      NOT NULL DEFAULT TRUE,
    -- --     duree_examen    INTEGER      DEFAULT 120,
    -- --     duree_ds        INTEGER      DEFAULT 60
    -- -- );

    -- -- -- ============================================================
    -- -- -- 12. SECTION_MATIERE
    -- -- -- Utilise annee_sem VARCHAR(20)
    -- -- -- ============================================================
    -- -- CREATE TABLE section_matiere (
    -- --     id              SERIAL PRIMARY KEY,
    -- --     section_id      INTEGER NOT NULL REFERENCES section(id),
    -- --     matiere_id      INTEGER NOT NULL REFERENCES matiere(id),
    -- --     annee_sem       VARCHAR(20) NOT NULL,
    -- --     a_examen_final  BOOLEAN NOT NULL DEFAULT TRUE,
    -- --     a_ds            BOOLEAN NOT NULL DEFAULT TRUE,
    -- --     duree_examen    INTEGER DEFAULT 120,
    -- --     duree_ds        INTEGER DEFAULT 60,
    -- --     UNIQUE (section_id, matiere_id, annee_sem)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 13. ENSEIGNEMENT
    -- -- -- ============================================================
    -- -- CREATE TABLE enseignement (
    -- --     id                  SERIAL PRIMARY KEY,
    -- --     enseignant_id       INTEGER           NOT NULL REFERENCES enseignant(id),
    -- --     matiere_id          INTEGER           NOT NULL REFERENCES matiere(id),
    -- --     type_enseignement   type_enseignement NOT NULL,
    -- --     nb_heures           NUMERIC(5,2)      NOT NULL DEFAULT 0,
    -- --     annee_sem           VARCHAR(20),
    -- --     UNIQUE (enseignant_id, matiere_id, type_enseignement, annee_sem)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 14. DISPONIBILITE_ENSEIGNANT
    -- -- -- ============================================================
    -- -- CREATE TABLE disponibilite_enseignant (
    -- --     id             SERIAL PRIMARY KEY,
    -- --     enseignant_id  INTEGER            NOT NULL REFERENCES enseignant(id),
    -- --     date           DATE               NOT NULL,
    -- --     heure_debut    TIME               NOT NULL,
    -- --     heure_fin      TIME               NOT NULL,
    -- --     type_dispo     type_disponibilite NOT NULL DEFAULT 'INDISPONIBLE',
    -- --     motif          VARCHAR(200),
    -- --     confirme       BOOLEAN            NOT NULL DEFAULT TRUE
    -- -- );

    -- -- -- ============================================================
    -- -- -- 15. PLANIFICATION_EXAMEN
    -- -- -- Utilise semestre INTEGER
    -- -- -- ============================================================
    -- -- CREATE TABLE planification_examen (
    -- --     id                      SERIAL PRIMARY KEY,
    -- --     session_id              INTEGER          NOT NULL REFERENCES session(id),
    -- --     departement_id          INTEGER          NOT NULL REFERENCES departement(id),  
    -- --     section_matiere_id      INTEGER          NOT NULL REFERENCES section_matiere(id),
    -- --     creneau_id              INTEGER          NOT NULL REFERENCES creneau(id),
    -- --     type_epreuve            type_epreuve     NOT NULL,
    -- --     semestre                INTEGER          NOT NULL CHECK (semestre IN (1,2)),
    -- --     duree                   INTEGER          NOT NULL DEFAULT 120,
    -- --     mode_affectation        mode_affectation NOT NULL DEFAULT 'AUTOMATIQUE',
    -- --     statut                  statut_planif    NOT NULL DEFAULT 'BROUILLON',
    -- --     nb_groupes              INTEGER          DEFAULT 1,
    -- --     nb_surveillants_requis  INTEGER          DEFAULT 2,
    -- --     UNIQUE (session_id, section_matiere_id, creneau_id, type_epreuve)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 16. PLANIF_SALLE
    -- -- -- ============================================================
    -- -- CREATE TABLE planif_salle (
    -- --     planification_id  INTEGER NOT NULL REFERENCES planification_examen(id),
    -- --     salle_id          INTEGER NOT NULL REFERENCES salle(id),
    -- --     groupe_id         INTEGER REFERENCES groupe(id),
    -- --     PRIMARY KEY (planification_id, salle_id)
    -- -- );

    -- -- -- ============================================================
    -- -- -- 17. SURVEILLANCE
    -- -- -- ============================================================
    -- -- CREATE TABLE surveillance (
    -- --     id                   SERIAL PRIMARY KEY,
    -- --     planification_id     INTEGER             NOT NULL REFERENCES planification_examen(id) ON DELETE CASCADE,
    -- --     enseignant_id        INTEGER             NOT NULL REFERENCES enseignant(id) ON DELETE CASCADE,
    -- --     groupe_id            INTEGER             REFERENCES groupe(id) ON DELETE SET NULL,
    -- --     salle_id             INTEGER             REFERENCES salle(id)  ON DELETE SET NULL,
    -- --     est_externe          BOOLEAN             NOT NULL DEFAULT FALSE,
    -- --     motif_externe        VARCHAR(200),
    -- --     charge               NUMERIC(4,2)        DEFAULT 1.0,
    -- --     presence             BOOLEAN             DEFAULT FALSE,
    -- --     mode_affectation     mode_affectation    NOT NULL DEFAULT 'AUTOMATIQUE',
    -- --     statut_surveillance  statut_surveillance DEFAULT 'AFFECTE',
    -- --     created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- --     updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- --     CONSTRAINT uq_surv_planif_ens_groupe UNIQUE (planification_id, enseignant_id, groupe_id)
    -- -- );

    -- -- -- ============================================================
    -- -- -- INDEX
    -- -- -- ============================================================
    -- -- CREATE INDEX idx_niveau_dept       ON niveau(departement_id);
    -- -- CREATE INDEX idx_section_niveau    ON section(niveau_id);
    -- -- CREATE INDEX idx_groupe_section    ON groupe(section_id);
    -- -- CREATE INDEX idx_ens_dept          ON enseignant(departement_id);
    -- -- CREATE INDEX idx_enseignement_ens  ON enseignement(enseignant_id);
    -- -- CREATE INDEX idx_enseignement_mat  ON enseignement(matiere_id);
    -- -- CREATE INDEX idx_sm_section        ON section_matiere(section_id);
    -- -- CREATE INDEX idx_sm_matiere        ON section_matiere(matiere_id);
    -- -- CREATE INDEX idx_dispo_ens         ON disponibilite_enseignant(enseignant_id, date);
    -- -- CREATE INDEX idx_planif_session    ON planification_examen(session_id);
    -- -- CREATE INDEX idx_planif_dept       ON planification_examen(departement_id);
-- -- CREATE INDEX idx_planif_creneau    ON planification_examen(creneau_id);
-- -- CREATE INDEX idx_surv_planif       ON surveillance(planification_id);
-- -- CREATE INDEX idx_surv_ens          ON surveillance(enseignant_id);
-- -- CREATE INDEX idx_surv_groupe       ON surveillance(groupe_id);
-- -- CREATE INDEX idx_surv_salle        ON surveillance(salle_id);
-- -- CREATE INDEX idx_surv_externe      ON surveillance(est_externe);

-- -- --

-- -- -- ============================================================
-- -- -- ============================================================
-- -- --                      REMPLISSAGE (DML)
-- -- -- ============================================================
-- -- -- ============================================================

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 1. DEPARTEMENT
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO departement (nom, code) VALUES
-- -- ('Département des Sciences de l''Informatique', 'DSI');

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 2. SESSION
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut) VALUES
-- -- ('PRINCIPALE', '2025/2026', '2026-01-07', '2026-01-15', 'VALIDEE');

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 3. SALLES
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO salle (code, designation, capacite, batiment) VALUES
-- -- ('S22',              'Salle 22',                              25,  'Informatique'),
-- -- ('AMPHI INFO',       'Amphithéâtre Informatique',            150,  'Principal'),
-- -- ('AMPHI B',          'Amphithéâtre B',                       120,  'Principal'),
-- -- ('AMPHI C',          'Amphithéâtre C',                       120,  'Principal'),
-- -- ('S31',              'Salle 31',                              30,  'Principal'),
-- -- ('S.BIB.INFO',       'Salle Bibliothèque Informatique',       40,  'Bibliothèque'),
-- -- ('I 106',            'Salle I-106',                           30,  'Bâtiment I'),
-- -- ('S.CONF.INF',       'Salle de Conférence Informatique',      50,  'Informatique'),
-- -- ('Amphi Phys 2',     'Amphithéâtre Physique 2',              100,  'Physique'),
-- -- ('AC2',              'Salle AC2',                             80,  'Annexe'),
-- -- ('AC1',              'Salle AC1',                             80,  'Annexe');

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 4. CRENEAUX
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO creneau (date, heure_debut, heure_fin, libelle) VALUES
-- -- ('2026-01-07','08:30','10:30','Mer 07/01 – Matin'),
-- -- ('2026-01-07','11:00','13:00','Mer 07/01 – Milieu'),
-- -- ('2026-01-07','14:00','16:00','Mer 07/01 – Après-midi'),
-- -- ('2026-01-08','08:30','10:30','Jeu 08/01 – Matin'),
-- -- ('2026-01-08','11:00','13:00','Jeu 08/01 – Milieu'),
-- -- ('2026-01-08','14:00','16:00','Jeu 08/01 – Après-midi'),
-- -- ('2026-01-09','08:30','10:30','Ven 09/01 – Matin'),
-- -- ('2026-01-09','11:00','13:00','Ven 09/01 – Milieu'),
-- -- ('2026-01-09','14:00','16:00','Ven 09/01 – Après-midi');

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 5. ENSEIGNANTS (version réduite pour l'exemple)
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO enseignant (nom, prenom, grade, email, telephone, departement_id) VALUES
-- -- ('Manita',           'Ghaith',      'Maître de Conf.',   'ghaith.manita@fst.utm.tn',      '55197776', 1),
-- -- ('Zouaoui',          'Sana',        'PES-Info',          'sana.zouaoui@fst.utm.tn',       '96276502', 1),
-- -- ('Meddeb',           'Rahma',       'Maître Ass.',       'rahma.meddeb@fst.utm.tn',        '98424172', 1),
-- -- ('Hizem',            'Moez',        'Maître Ass.',       'moez.hizem@fst.utm.tn',         '24740880', 1),
-- -- ('Ben Othman',       'Leila',       'Maître Ass.',       'leila.benothman@fst.utm.tn',    '98925135', 1),
-- -- ('Amdouni',          'Asma',        'Maître Ass.',       'asma.amdouni@fst.utm.tn',       '54892821', 1),
-- -- ('Boussen',          'Sinda',       'Maître Ass.',       'sinda.boussen@fst.utm.tn',      '29310441', 1),
-- -- ('Masmoudi',         'Salma',       'Maître Ass.',       'salma.masmoudi@fst.utm.tn',     '93895345', 1);

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 6. CHARGE_HORAIRE
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO charge_horaire (enseignant_id, annee_univ, volume_horaire)
-- -- SELECT id, '2025/2026', 192 FROM enseignant;

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 7. NIVEAUX
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO niveau (libelle, annee, type_formation, departement_id) VALUES
-- -- ('MR',    2, 'INF/IOT', (SELECT id FROM departement WHERE code='DSI'));

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 8. SECTION
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO section (nom, nb_etudiants, niveau_id) VALUES
-- -- ('INF/IOT', 15, (SELECT id FROM niveau WHERE libelle='MR' AND type_formation='INF/IOT'));

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 9. GROUPE
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO groupe (numero, effectif, section_id) VALUES
-- -- (1, 15, (SELECT s.id FROM section s JOIN niveau n ON s.niveau_id = n.id WHERE n.libelle='MR' AND n.type_formation='INF/IOT' AND s.nom='INF/IOT'));

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 10. MATIERES (version réduite à 4 matières)
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO matiere (code, intitule, a_examen_final, a_ds, duree_examen, duree_ds) VALUES
-- -- ('MR2-INF-322',  'Optimisation Combinatoire',                   TRUE, TRUE, 120, 60),
-- -- ('MR2-INF-IOT',  'IDM pour les systèmes complexes Temps Réels', TRUE, TRUE, 120, 60),
-- -- ('MR2-INF-312',  'Bases de données avancées',                   TRUE, TRUE, 120, 60),
-- -- ('MR2-INF-331',  'Sécurité IOT',                                TRUE, TRUE, 120, 60);

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 11. SECTION_MATIERE (avec annee_sem)
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO section_matiere (section_id, matiere_id, annee_sem, a_examen_final, a_ds, duree_examen, duree_ds)
-- -- SELECT
-- --     (SELECT s.id FROM section s JOIN niveau n ON s.niveau_id = n.id WHERE n.libelle='MR' AND n.type_formation='INF/IOT' AND s.nom='INF/IOT'),
-- --     m.id,
-- --     CASE 
-- --         WHEN m.code IN ('MR2-INF-322', 'MR2-INF-312') THEN '2025/2026-S1'
-- --         ELSE '2025/2026-S2'
-- --     END AS annee_sem,
-- --     TRUE, TRUE, 120, 60
-- -- FROM matiere m
-- -- WHERE m.code IN ('MR2-INF-322', 'MR2-INF-IOT', 'MR2-INF-312', 'MR2-INF-331');

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 12. ENSEIGNEMENT (avec annee_sem)
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
-- -- VALUES
-- -- -- Semestre 1
-- -- ((SELECT id FROM enseignant WHERE nom='Manita' AND prenom='Ghaith'),
-- --  (SELECT id FROM matiere WHERE code='MR2-INF-322'), 'COURS', 21, '2025/2026-S1'),
-- -- ((SELECT id FROM enseignant WHERE nom='Amdouni' AND prenom='Asma'),
-- --  (SELECT id FROM matiere WHERE code='MR2-INF-322'), 'TD', 18, '2025/2026-S1'),
-- -- ((SELECT id FROM enseignant WHERE nom='Zouaoui' AND prenom='Sana'),
-- --  (SELECT id FROM matiere WHERE code='MR2-INF-312'), 'COURS', 21, '2025/2026-S1'),
-- -- ((SELECT id FROM enseignant WHERE nom='Meddeb' AND prenom='Rahma'),
-- --  (SELECT id FROM matiere WHERE code='MR2-INF-312'), 'TD', 18, '2025/2026-S1'),

-- -- -- Semestre 2
-- -- ((SELECT id FROM enseignant WHERE nom='Zouaoui' AND prenom='Sana'),
-- --  (SELECT id FROM matiere WHERE code='MR2-INF-IOT'), 'COURS', 21, '2025/2026-S2'),
-- -- ((SELECT id FROM enseignant WHERE nom='Hizem' AND prenom='Moez'),
-- --  (SELECT id FROM matiere WHERE code='MR2-INF-331'), 'COURS', 21, '2025/2026-S2'),
-- -- ((SELECT id FROM enseignant WHERE nom='Boussen' AND prenom='Sinda'),
-- --  (SELECT id FROM matiere WHERE code='MR2-INF-331'), 'TD', 18, '2025/2026-S2');

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 13. PLANIFICATION_EXAMEN (avec semestre) - uniquement VALIDEE
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO planification_examen (session_id, departement_id, section_matiere_id, creneau_id, type_epreuve, semestre, duree, mode_affectation, statut, nb_groupes, nb_surveillants_requis)
-- -- VALUES
-- -- -- Semestre 1 - Optimisation Combinatoire (EXAMEN_FINAL)
-- -- (1, 1, 
-- --  (SELECT id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id WHERE m.code = 'MR2-INF-322' AND sm.annee_sem = '2025/2026-S1'),
-- --  (SELECT id FROM creneau WHERE date = '2026-01-07' AND heure_debut = '08:30'), 
-- --  'EXAMEN_FINAL', 1, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- -- -- Semestre 1 - Optimisation Combinatoire (DS)
-- -- (1, 1,
-- --  (SELECT id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id WHERE m.code = 'MR2-INF-322' AND sm.annee_sem = '2025/2026-S1'),
-- --  (SELECT id FROM creneau WHERE date = '2026-01-08' AND heure_debut = '08:30'),
-- --  'DS', 1, 60, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- -- -- Semestre 1 - BD Avancées (EXAMEN_FINAL)
-- -- (1, 1,
-- --  (SELECT id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id WHERE m.code = 'MR2-INF-312' AND sm.annee_sem = '2025/2026-S1'),
-- --  (SELECT id FROM creneau WHERE date = '2026-01-07' AND heure_debut = '11:00'),
-- --  'EXAMEN_FINAL', 1, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- -- -- Semestre 2 - IDM Temps Réels (EXAMEN_FINAL)
-- -- (1, 1,
-- --  (SELECT id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id WHERE m.code = 'MR2-INF-IOT' AND sm.annee_sem = '2025/2026-S2'),
-- --  (SELECT id FROM creneau WHERE date = '2026-01-09' AND heure_debut = '08:30'),
-- --  'EXAMEN_FINAL', 2, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- -- -- Semestre 2 - Sécurité IOT (EXAMEN_FINAL)
-- -- (1, 1,
-- --  (SELECT id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id WHERE m.code = 'MR2-INF-331' AND sm.annee_sem = '2025/2026-S2'),
-- --  (SELECT id FROM creneau WHERE date = '2026-01-09' AND heure_debut = '14:00'),
-- --  'EXAMEN_FINAL', 2, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2);

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 14. PLANIF_SALLE
-- -- -- ─────────────────────────────────────────────────────────────
-- -- INSERT INTO planif_salle (planification_id, salle_id, groupe_id)
-- -- SELECT 
-- --     p.id,
-- --     s.id,
-- --     (SELECT id FROM groupe WHERE section_id = (SELECT section_id FROM section_matiere WHERE id = p.section_matiere_id) AND numero = 1)
-- -- FROM planification_examen p
-- -- CROSS JOIN (
-- --     SELECT id FROM salle WHERE code IN ('S22', 'AMPHI INFO')
-- --     LIMIT 1
-- -- ) s
-- -- WHERE p.statut = 'VALIDEE';

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 15. SURVEILLANCE (réaliste avec professeurs du même département)
-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- 15. SURVEILLANCE
-- -- -- ─────────────────────────────────────────────────────────────

-- -- -- Pour Optimisation Combinatoire (Exam Final)
-- -- INSERT INTO surveillance (planification_id, enseignant_id, groupe_id, salle_id, est_externe, charge, mode_affectation, statut_surveillance)
-- -- SELECT
-- --     p.id,
-- --     e.id,
-- --     (SELECT g.id FROM groupe g WHERE g.section_id = (SELECT sm.section_id FROM section_matiere sm WHERE sm.id = p.section_matiere_id) AND g.numero = 1),
-- --     (SELECT sa.id FROM salle sa WHERE sa.code = 'S22'),
-- --     FALSE, 1.0, 'AUTOMATIQUE', 'AFFECTE'
-- -- FROM planification_examen p
-- -- CROSS JOIN (
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Manita'
-- --     UNION ALL
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Amdouni'
-- -- ) e
-- -- WHERE p.id = (
-- --     SELECT pe.id FROM planification_examen pe
-- --     WHERE pe.type_epreuve = 'EXAMEN_FINAL' AND pe.semestre = 1
-- --     AND pe.section_matiere_id IN (
-- --         SELECT sm.id FROM section_matiere sm
-- --         JOIN matiere m ON sm.matiere_id = m.id
-- --         WHERE m.code = 'MR2-INF-322'
-- --     ) LIMIT 1
-- -- );

-- -- -- Pour Optimisation Combinatoire (DS)
-- -- INSERT INTO surveillance (planification_id, enseignant_id, groupe_id, salle_id, est_externe, charge, mode_affectation, statut_surveillance)
-- -- SELECT
-- --     p.id,
-- --     e.id,
-- --     (SELECT g.id FROM groupe g WHERE g.section_id = (SELECT sm.section_id FROM section_matiere sm WHERE sm.id = p.section_matiere_id) AND g.numero = 1),
-- --     (SELECT sa.id FROM salle sa WHERE sa.code = 'S22'),
-- --     FALSE, 1.0, 'AUTOMATIQUE', 'AFFECTE'
-- -- FROM planification_examen p
-- -- CROSS JOIN (
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Manita'
-- --     UNION ALL
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Amdouni'
-- -- ) e
-- -- WHERE p.id = (
-- --     SELECT pe.id FROM planification_examen pe
-- --     WHERE pe.type_epreuve = 'DS' AND pe.semestre = 1
-- --     AND pe.section_matiere_id IN (
-- --         SELECT sm.id FROM section_matiere sm
-- --         JOIN matiere m ON sm.matiere_id = m.id
-- --         WHERE m.code = 'MR2-INF-322'
-- --     ) LIMIT 1
-- -- );

-- -- -- Pour BD Avancées (Exam Final)
-- -- INSERT INTO surveillance (planification_id, enseignant_id, groupe_id, salle_id, est_externe, charge, mode_affectation, statut_surveillance)
-- -- SELECT
-- --     p.id,
-- --     e.id,
-- --     (SELECT g.id FROM groupe g WHERE g.section_id = (SELECT sm.section_id FROM section_matiere sm WHERE sm.id = p.section_matiere_id) AND g.numero = 1),
-- --     (SELECT sa.id FROM salle sa WHERE sa.code = 'S22'),
-- --     FALSE, 1.0, 'AUTOMATIQUE', 'AFFECTE'
-- -- FROM planification_examen p
-- -- CROSS JOIN (
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Zouaoui'
-- --     UNION ALL
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Meddeb'
-- -- ) e
-- -- WHERE p.id = (
-- --     SELECT pe.id FROM planification_examen pe
-- --     WHERE pe.type_epreuve = 'EXAMEN_FINAL' AND pe.semestre = 1
-- --     AND pe.section_matiere_id IN (
-- --         SELECT sm.id FROM section_matiere sm
-- --         JOIN matiere m ON sm.matiere_id = m.id
-- --         WHERE m.code = 'MR2-INF-312'
-- --     ) LIMIT 1
-- -- );

-- -- -- Pour IDM Temps Réels (Exam Final)
-- -- INSERT INTO surveillance (planification_id, enseignant_id, groupe_id, salle_id, est_externe, charge, mode_affectation, statut_surveillance)
-- -- SELECT
-- --     p.id,
-- --     e.id,
-- --     (SELECT g.id FROM groupe g WHERE g.section_id = (SELECT sm.section_id FROM section_matiere sm WHERE sm.id = p.section_matiere_id) AND g.numero = 1),
-- --     (SELECT sa.id FROM salle sa WHERE sa.code = 'S22'),
-- --     FALSE, 1.0, 'AUTOMATIQUE', 'AFFECTE'
-- -- FROM planification_examen p
-- -- CROSS JOIN (
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Zouaoui'
-- --     UNION ALL
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Boussen'
-- -- ) e
-- -- WHERE p.id = (
-- --     SELECT pe.id FROM planification_examen pe
-- --     WHERE pe.type_epreuve = 'EXAMEN_FINAL' AND pe.semestre = 2
-- --     AND pe.section_matiere_id IN (
-- --         SELECT sm.id FROM section_matiere sm
-- --         JOIN matiere m ON sm.matiere_id = m.id
-- --         WHERE m.code = 'MR2-INF-IOT'
-- --     ) LIMIT 1
-- -- );

-- -- -- Pour Sécurité IOT (Exam Final)
-- -- INSERT INTO surveillance (planification_id, enseignant_id, groupe_id, salle_id, est_externe, charge, mode_affectation, statut_surveillance)
-- -- SELECT
-- --     p.id,
-- --     e.id,
-- --     (SELECT g.id FROM groupe g WHERE g.section_id = (SELECT sm.section_id FROM section_matiere sm WHERE sm.id = p.section_matiere_id) AND g.numero = 1),
-- --     (SELECT sa.id FROM salle sa WHERE sa.code = 'S22'),
-- --     FALSE, 1.0, 'AUTOMATIQUE', 'AFFECTE'
-- -- FROM planification_examen p
-- -- CROSS JOIN (
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Hizem'
-- --     UNION ALL
-- --     SELECT ens.id FROM enseignant ens WHERE ens.nom = 'Boussen'
-- -- ) e
-- -- WHERE p.id = (
-- --     SELECT pe.id FROM planification_examen pe
-- --     WHERE pe.type_epreuve = 'EXAMEN_FINAL' AND pe.semestre = 2
-- --     AND pe.section_matiere_id IN (
-- --         SELECT sm.id FROM section_matiere sm
-- --         JOIN matiere m ON sm.matiere_id = m.id
-- --         WHERE m.code = 'MR2-INF-331'
-- --     ) LIMIT 1
-- -- );

-- -- COMMIT;

-- -- -- ─────────────────────────────────────────────────────────────
-- -- -- VÉRIFICATIONS POST-INSERT
-- -- -- ─────────────────────────────────────────────────────────────
-- -- SELECT 'departement'                      AS table_name, COUNT(*) AS nb FROM departement              UNION ALL
-- -- SELECT 'niveau',                                          COUNT(*)        FROM niveau                   UNION ALL
-- -- SELECT 'section',                                         COUNT(*)        FROM section                  UNION ALL
-- -- SELECT 'groupe',                                          COUNT(*)        FROM groupe                   UNION ALL
-- -- SELECT 'salle',                                           COUNT(*)        FROM salle                    UNION ALL
-- -- SELECT 'creneau',                                         COUNT(*)        FROM creneau                  UNION ALL
-- -- SELECT 'session',                                         COUNT(*)        FROM session                  UNION ALL
-- -- SELECT 'enseignant',                                      COUNT(*)        FROM enseignant               UNION ALL
-- -- SELECT 'charge_horaire',                                  COUNT(*)        FROM charge_horaire           UNION ALL
-- -- SELECT 'matiere',                                         COUNT(*)        FROM matiere                  UNION ALL
-- -- SELECT 'section_matiere',                                 COUNT(*)        FROM section_matiere          UNION ALL
-- -- SELECT 'enseignement',                                    COUNT(*)        FROM enseignement             UNION ALL
-- -- SELECT 'disponibilite_enseignant',                        COUNT(*)        FROM disponibilite_enseignant UNION ALL
-- -- SELECT 'planification_examen',                            COUNT(*)        FROM planification_examen     UNION ALL
-- -- SELECT 'planif_salle',                                    COUNT(*)        FROM planif_salle             UNION ALL
-- -- SELECT 'surveillance',                                    COUNT(*)        FROM surveillance
-- -- ORDER BY table_name;


-- BEGIN;

-- -- ============================================================
-- -- NETTOYAGE (ré-exécution propre)
-- -- ============================================================
-- DROP TABLE IF EXISTS surveillance              CASCADE;
-- DROP TABLE IF EXISTS planif_salle              CASCADE;
-- DROP TABLE IF EXISTS planification_examen     CASCADE;
-- DROP TABLE IF EXISTS disponibilite_enseignant CASCADE;
-- DROP TABLE IF EXISTS enseignement             CASCADE;
-- DROP TABLE IF EXISTS section_matiere          CASCADE;
-- DROP TABLE IF EXISTS matiere                  CASCADE;
-- DROP TABLE IF EXISTS charge_horaire           CASCADE;
-- DROP TABLE IF EXISTS enseignant               CASCADE;
-- DROP TABLE IF EXISTS session                  CASCADE;
-- DROP TABLE IF EXISTS creneau                  CASCADE;
-- DROP TABLE IF EXISTS salle                    CASCADE;
-- DROP TABLE IF EXISTS groupe                   CASCADE;
-- DROP TABLE IF EXISTS section                  CASCADE;
-- DROP TABLE IF EXISTS niveau                   CASCADE;
-- DROP TABLE IF EXISTS departement              CASCADE;

-- DROP TYPE IF EXISTS jour_semaine;
-- DROP TYPE IF EXISTS type_disponibilite;
-- DROP TYPE IF EXISTS statut_planif;
-- DROP TYPE IF EXISTS mode_affectation;
-- DROP TYPE IF EXISTS type_enseignement;
-- DROP TYPE IF EXISTS type_epreuve;
-- DROP TYPE IF EXISTS type_session;
-- DROP TYPE IF EXISTS statut_surveillance;

-- -- ============================================================
-- -- EXTENSIONS
-- -- ============================================================
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -- ============================================================
-- -- 1. ÉNUMÉRATIONS
-- -- ============================================================
-- CREATE TYPE type_session        AS ENUM ('PRINCIPALE','RATTRAPAGE');
-- CREATE TYPE type_epreuve        AS ENUM ('EXAMEN_FINAL','DS');
-- CREATE TYPE type_enseignement   AS ENUM ('COURS','TD','TP');
-- CREATE TYPE mode_affectation    AS ENUM ('AUTOMATIQUE','MANUELLE');
-- CREATE TYPE statut_planif       AS ENUM ('BROUILLON','VALIDEE','PUBLIEE');
-- CREATE TYPE type_disponibilite  AS ENUM ('DISPONIBLE','INDISPONIBLE','COURS_PREVU','MISSION','CONGE');
-- CREATE TYPE jour_semaine        AS ENUM ('LUNDI','MARDI','MERCREDI','JEUDI','VENDREDI','SAMEDI');
-- CREATE TYPE statut_surveillance AS ENUM ('AFFECTE','CONFIRME');

-- -- ============================================================
-- -- 2. DEPARTEMENT
-- -- ============================================================
-- CREATE TABLE departement (
--     id    SERIAL PRIMARY KEY,
--     nom   VARCHAR(100) NOT NULL,
--     code  VARCHAR(20)  NOT NULL UNIQUE
-- );

-- -- ============================================================
-- -- 3. NIVEAU
-- -- ============================================================
-- CREATE TABLE niveau (
--     id              SERIAL PRIMARY KEY,
--     libelle         VARCHAR(50)  NOT NULL,
--     type_formation  VARCHAR(50)  NOT NULL,
--     departement_id  INTEGER      NOT NULL REFERENCES departement(id)
-- );

-- -- ============================================================
-- -- 4. SECTION
-- -- ============================================================
-- CREATE TABLE section (
--     id         SERIAL PRIMARY KEY,
--     nom        VARCHAR(20) NOT NULL,
--     niveau_id  INTEGER     NOT NULL REFERENCES niveau(id)
-- );

-- -- ============================================================
-- -- 5. GROUPE
-- -- ============================================================
-- CREATE TABLE groupe (
--     id            SERIAL PRIMARY KEY,
--     numero        INTEGER     NOT NULL,
--     effectif      INTEGER     NOT NULL DEFAULT 0,
--     nb_etudiants  INTEGER     NOT NULL DEFAULT 0,
--     annee         VARCHAR(10) NOT NULL,
--     section_id    INTEGER     NOT NULL REFERENCES section(id),
--     UNIQUE (section_id, numero)
-- );

-- -- ============================================================
-- -- 6. SALLE
-- -- ============================================================
-- CREATE TABLE salle (
--     id           SERIAL PRIMARY KEY,
--     code         VARCHAR(30)  NOT NULL UNIQUE,
--     designation  VARCHAR(100),
--     capacite     INTEGER      NOT NULL,
--     batiment     VARCHAR(50)
-- );

-- -- ============================================================
-- -- 7. CRENEAU
-- -- ============================================================
-- CREATE TABLE creneau (
--     id           SERIAL PRIMARY KEY,
--     date         DATE NOT NULL,
--     heure_debut  TIME NOT NULL,
--     heure_fin    TIME NOT NULL,
--     libelle      VARCHAR(50),
--     UNIQUE (date, heure_debut)
-- );

-- -- ============================================================
-- -- 8. SESSION
-- -- ============================================================
-- CREATE TABLE session (
--     id                   SERIAL PRIMARY KEY,
--     type_session         type_session  NOT NULL,
--     annee_universitaire  VARCHAR(10)   NOT NULL,
--     date_debut           DATE          NOT NULL,
--     date_fin             DATE          NOT NULL,
--     statut               statut_planif NOT NULL DEFAULT 'BROUILLON'
-- );

-- -- ============================================================
-- -- 9. ENSEIGNANT
-- -- ============================================================
-- CREATE TABLE enseignant (
--     id              SERIAL PRIMARY KEY,
--     nom             VARCHAR(60)  NOT NULL,
--     prenom          VARCHAR(60)  NOT NULL,
--     grade           VARCHAR(50),
--     email           VARCHAR(100) UNIQUE,
--     telephone       VARCHAR(20),
--     departement_id  INTEGER REFERENCES departement(id)
-- );

-- -- ============================================================
-- -- 10. CHARGE_HORAIRE
-- -- ============================================================
-- CREATE TABLE charge_horaire (
--     id              SERIAL PRIMARY KEY,
--     enseignant_id   INTEGER       NOT NULL REFERENCES enseignant(id),
--     annee_univ      VARCHAR(10)   NOT NULL,
--     volume_horaire  NUMERIC(6,2)  NOT NULL DEFAULT 0,
--     UNIQUE (enseignant_id, annee_univ)
-- );

-- -- ============================================================
-- -- 11. MATIERE
-- -- ============================================================
-- CREATE TABLE matiere (
--     id              SERIAL PRIMARY KEY,
--     code            VARCHAR(20)  NOT NULL UNIQUE,
--     intitule        VARCHAR(150) NOT NULL,
--     coefficient     NUMERIC(4,2) DEFAULT 1,
--     credit          INTEGER      DEFAULT 1,
--     a_examen_final  BOOLEAN      NOT NULL DEFAULT TRUE,
--     a_ds            BOOLEAN      NOT NULL DEFAULT TRUE,
--     duree_examen    INTEGER      DEFAULT 120,
--     duree_ds        INTEGER      DEFAULT 60
-- );

-- -- ============================================================
-- -- 12. SECTION_MATIERE
-- -- ============================================================
-- CREATE TABLE section_matiere (
--     id              SERIAL PRIMARY KEY,
--     section_id      INTEGER NOT NULL REFERENCES section(id),
--     matiere_id      INTEGER NOT NULL REFERENCES matiere(id),
--     annee_sem       VARCHAR(20) NOT NULL,
--     a_examen_final  BOOLEAN NOT NULL DEFAULT TRUE,
--     a_ds            BOOLEAN NOT NULL DEFAULT TRUE,
--     duree_examen    INTEGER DEFAULT 120,
--     duree_ds        INTEGER DEFAULT 60,
--     UNIQUE (section_id, matiere_id, annee_sem)
-- );

-- -- ============================================================
-- -- 13. ENSEIGNEMENT
-- -- ============================================================
-- CREATE TABLE enseignement (
--     id                  SERIAL PRIMARY KEY,
--     enseignant_id       INTEGER           NOT NULL REFERENCES enseignant(id),
--     matiere_id          INTEGER           NOT NULL REFERENCES matiere(id),
--     type_enseignement   type_enseignement NOT NULL,
--     nb_heures           NUMERIC(5,2)      NOT NULL DEFAULT 0,
--     annee_sem           VARCHAR(20),
--     UNIQUE (enseignant_id, matiere_id, type_enseignement, annee_sem)
-- );

-- -- ============================================================
-- -- 14. DISPONIBILITE_ENSEIGNANT
-- -- ============================================================
-- CREATE TABLE disponibilite_enseignant (
--     id             SERIAL PRIMARY KEY,
--     enseignant_id  INTEGER            NOT NULL REFERENCES enseignant(id),
--     date           DATE               NOT NULL,
--     heure_debut    TIME               NOT NULL,
--     heure_fin      TIME               NOT NULL,
--     type_dispo     type_disponibilite NOT NULL DEFAULT 'INDISPONIBLE',
--     motif          VARCHAR(200),
--     confirme       BOOLEAN            NOT NULL DEFAULT TRUE
-- );

-- -- ============================================================
-- -- 15. PLANIFICATION_EXAMEN
-- -- ============================================================
-- CREATE TABLE planification_examen (
--     id                      SERIAL PRIMARY KEY,
--     session_id              INTEGER          NOT NULL REFERENCES session(id),
--     departement_id          INTEGER          NOT NULL REFERENCES departement(id),
--     section_matiere_id      INTEGER          NOT NULL REFERENCES section_matiere(id),
--     creneau_id              INTEGER          NOT NULL REFERENCES creneau(id),
--     type_epreuve            type_epreuve     NOT NULL,
--     semestre                INTEGER          NOT NULL CHECK (semestre IN (1,2)),
--     duree                   INTEGER          NOT NULL DEFAULT 120,
--     mode_affectation        mode_affectation NOT NULL DEFAULT 'AUTOMATIQUE',
--     statut                  statut_planif    NOT NULL DEFAULT 'BROUILLON',
--     nb_groupes              INTEGER          DEFAULT 1,
--     nb_surveillants_requis  INTEGER          DEFAULT 2,
--     UNIQUE (session_id, section_matiere_id, creneau_id, type_epreuve)
-- );

-- -- ============================================================
-- -- 16. PLANIF_SALLE
-- -- ============================================================
-- CREATE TABLE planif_salle (
--     planification_id  INTEGER NOT NULL REFERENCES planification_examen(id),
--     salle_id          INTEGER NOT NULL REFERENCES salle(id),
--     groupe_id         INTEGER REFERENCES groupe(id),
--     PRIMARY KEY (planification_id, salle_id)
-- );

-- -- ============================================================
-- -- 17. SURVEILLANCE
-- -- ============================================================
-- CREATE TABLE surveillance (
--     id                   SERIAL PRIMARY KEY,
--     planification_id     INTEGER             NOT NULL REFERENCES planification_examen(id) ON DELETE CASCADE,
--     enseignant_id        INTEGER             NOT NULL REFERENCES enseignant(id) ON DELETE CASCADE,
--     groupe_id            INTEGER             REFERENCES groupe(id) ON DELETE SET NULL,
--     salle_id             INTEGER             REFERENCES salle(id)  ON DELETE SET NULL,
--     est_externe          BOOLEAN             NOT NULL DEFAULT FALSE,
--     motif_externe        VARCHAR(200),
--     charge               NUMERIC(4,2)        DEFAULT 1.0,
--     presence             BOOLEAN             DEFAULT FALSE,
--     mode_affectation     mode_affectation    NOT NULL DEFAULT 'AUTOMATIQUE',
--     statut_surveillance  statut_surveillance DEFAULT 'AFFECTE',
--     created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     CONSTRAINT uq_surv_planif_ens_groupe UNIQUE (planification_id, enseignant_id, groupe_id)
-- );

-- -- ============================================================
-- -- INDEX
-- -- ============================================================
-- CREATE INDEX idx_niveau_dept       ON niveau(departement_id);
-- CREATE INDEX idx_section_niveau    ON section(niveau_id);
-- CREATE INDEX idx_groupe_section    ON groupe(section_id);
-- CREATE INDEX idx_groupe_annee      ON groupe(annee);
-- CREATE INDEX idx_ens_dept          ON enseignant(departement_id);
-- CREATE INDEX idx_enseignement_ens  ON enseignement(enseignant_id);
-- CREATE INDEX idx_enseignement_mat  ON enseignement(matiere_id);
-- CREATE INDEX idx_sm_section        ON section_matiere(section_id);
-- CREATE INDEX idx_sm_matiere        ON section_matiere(matiere_id);
-- CREATE INDEX idx_dispo_ens         ON disponibilite_enseignant(enseignant_id, date);
-- CREATE INDEX idx_planif_session    ON planification_examen(session_id);
-- CREATE INDEX idx_planif_dept       ON planification_examen(departement_id);
-- CREATE INDEX idx_planif_creneau    ON planification_examen(creneau_id);
-- CREATE INDEX idx_surv_planif       ON surveillance(planification_id);
-- CREATE INDEX idx_surv_ens          ON surveillance(enseignant_id);
-- CREATE INDEX idx_surv_groupe       ON surveillance(groupe_id);
-- CREATE INDEX idx_surv_salle        ON surveillance(salle_id);
-- CREATE INDEX idx_surv_externe      ON surveillance(est_externe);


-- -- ============================================================
-- -- ============================================================
-- --                      REMPLISSAGE (DML)
-- -- ============================================================
-- -- ============================================================

-- -- ─────────────────────────────────────────────────────────────
-- -- 1. DEPARTEMENT
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO departement (nom, code) VALUES
-- ('Département des Sciences de l''Informatique', 'DSI');

-- -- ─────────────────────────────────────────────────────────────
-- -- 2. NIVEAU
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO niveau (libelle, type_formation, departement_id) VALUES
-- ('Cycle Ingénieur', 'Informatique', 1);

-- -- ─────────────────────────────────────────────────────────────
-- -- 3. SECTION  (IGL3 et IGL4)
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO section (nom, niveau_id) VALUES
-- ('IGL3', 1),
-- ('IGL4', 1);

-- -- ─────────────────────────────────────────────────────────────
-- -- 4. GROUPE  (1 groupe par section, année 2025/2026)
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO groupe (numero, effectif, nb_etudiants, annee, section_id) VALUES
-- (1, 35, 35, '2025/2026', (SELECT id FROM section WHERE nom = 'IGL3')),
-- (2, 30, 30, '2025/2026', (SELECT id FROM section WHERE nom = 'IGL4'));

-- -- ─────────────────────────────────────────────────────────────
-- -- 5. SALLE
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO salle (code, designation, capacite, batiment) VALUES
-- ('AMPHI A',  'Amphithéâtre A',   120, 'Principal'),
-- ('S101',     'Salle 101',         40, 'Bâtiment I'),
-- ('S102',     'Salle 102',         40, 'Bâtiment I');

-- -- ─────────────────────────────────────────────────────────────
-- -- 6. CRENEAU
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO creneau (date, heure_debut, heure_fin, libelle) VALUES
-- ('2026-01-07', '08:30', '10:30', 'Mer 07/01 – Matin'),
-- ('2026-01-07', '11:00', '13:00', 'Mer 07/01 – Milieu'),
-- ('2026-01-08', '08:30', '10:30', 'Jeu 08/01 – Matin'),
-- ('2026-01-08', '11:00', '13:00', 'Jeu 08/01 – Milieu');

-- -- ─────────────────────────────────────────────────────────────
-- -- 7. SESSION
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut) VALUES
-- ('PRINCIPALE', '2025/2026', '2026-01-07', '2026-01-15', 'VALIDEE');

-- -- ─────────────────────────────────────────────────────────────
-- -- 8. ENSEIGNANT  (4 profs)
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO enseignant (nom, prenom, grade, email, telephone, departement_id) VALUES
-- ('Manita',   'Ghaith', 'Maître de Conf.', 'ghaith.manita@fst.utm.tn',   '55197776', 1),
-- ('Zouaoui',  'Sana',   'PES-Info',        'sana.zouaoui@fst.utm.tn',    '96276502', 1),
-- ('Meddeb',   'Rahma',  'Maître Ass.',     'rahma.meddeb@fst.utm.tn',    '98424172', 1),
-- ('Hizem',    'Moez',   'Maître Ass.',     'moez.hizem@fst.utm.tn',      '24740880', 1);

-- -- ─────────────────────────────────────────────────────────────
-- -- 9. CHARGE_HORAIRE
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO charge_horaire (enseignant_id, annee_univ, volume_horaire)
-- SELECT id, '2025/2026', 192 FROM enseignant;

-- -- ─────────────────────────────────────────────────────────────
-- -- 10. MATIERE  (4 matières : 2 par semestre)
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds) VALUES
-- ('IGL3-INF-101', 'Algorithmique Avancée',       2, 3, TRUE, TRUE, 120, 60),
-- ('IGL3-INF-102', 'Réseaux et Protocoles',        2, 3, TRUE, TRUE, 120, 60),
-- ('IGL4-INF-201', 'Intelligence Artificielle',    2, 3, TRUE, TRUE, 120, 60),
-- ('IGL4-INF-202', 'Génie Logiciel',               2, 3, TRUE, TRUE, 120, 60);

-- -- ─────────────────────────────────────────────────────────────
-- -- 11. SECTION_MATIERE
-- --     IGL3 → 2 matières S1 | IGL4 → 2 matières S2
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO section_matiere (section_id, matiere_id, annee_sem, a_examen_final, a_ds, duree_examen, duree_ds) VALUES
-- -- IGL3 – Semestre 1
-- ((SELECT id FROM section WHERE nom='IGL3'),
--  (SELECT id FROM matiere WHERE code='IGL3-INF-101'), '2025/2026-S1', TRUE, TRUE, 120, 60),
-- ((SELECT id FROM section WHERE nom='IGL3'),
--  (SELECT id FROM matiere WHERE code='IGL3-INF-102'), '2025/2026-S1', TRUE, TRUE, 120, 60),
-- -- IGL4 – Semestre 2
-- ((SELECT id FROM section WHERE nom='IGL4'),
--  (SELECT id FROM matiere WHERE code='IGL4-INF-201'), '2025/2026-S2', TRUE, TRUE, 120, 60),
-- ((SELECT id FROM section WHERE nom='IGL4'),
--  (SELECT id FROM matiere WHERE code='IGL4-INF-202'), '2025/2026-S2', TRUE, TRUE, 120, 60);

-- -- ─────────────────────────────────────────────────────────────
-- -- 12. ENSEIGNEMENT
-- --     Manita  → Algorithmique (COURS S1)
-- --     Zouaoui → Réseaux       (COURS S1)
-- --     Meddeb  → IA            (COURS S2)
-- --     Hizem   → Génie Log.    (COURS S2)
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem) VALUES
-- ((SELECT id FROM enseignant WHERE nom='Manita'),
--  (SELECT id FROM matiere WHERE code='IGL3-INF-101'), 'COURS', 21, '2025/2026-S1'),
-- ((SELECT id FROM enseignant WHERE nom='Zouaoui'),
--  (SELECT id FROM matiere WHERE code='IGL3-INF-102'), 'COURS', 21, '2025/2026-S1'),
-- ((SELECT id FROM enseignant WHERE nom='Meddeb'),
--  (SELECT id FROM matiere WHERE code='IGL4-INF-201'), 'COURS', 21, '2025/2026-S2'),
-- ((SELECT id FROM enseignant WHERE nom='Hizem'),
--  (SELECT id FROM matiere WHERE code='IGL4-INF-202'), 'COURS', 21, '2025/2026-S2');

-- -- ─────────────────────────────────────────────────────────────
-- -- 13. DISPONIBILITE_ENSEIGNANT  (4 enregistrements)
-- --     Manita   → indisponible le 07/01 matin
-- --     Zouaoui  → mission      le 07/01 milieu
-- --     Meddeb   → congé        le 08/01 matin
-- --     Hizem    → cours prévu  le 08/01 milieu
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO disponibilite_enseignant (enseignant_id, date, heure_debut, heure_fin, type_dispo, motif, confirme) VALUES
-- ((SELECT id FROM enseignant WHERE nom='Manita'),
--  '2026-01-07', '08:30', '10:30', 'INDISPONIBLE',  'Indisponibilité personnelle',     TRUE),
-- ((SELECT id FROM enseignant WHERE nom='Zouaoui'),
--  '2026-01-07', '11:00', '13:00', 'MISSION',        'Mission à l''extérieur',          TRUE),
-- ((SELECT id FROM enseignant WHERE nom='Meddeb'),
--  '2026-01-08', '08:30', '10:30', 'CONGE',           'Congé maladie',                   TRUE),
-- ((SELECT id FROM enseignant WHERE nom='Hizem'),
--  '2026-01-08', '11:00', '13:00', 'COURS_PREVU',    'Cours de rattrapage planifié',    TRUE);

-- -- ─────────────────────────────────────────────────────────────
-- -- 14. PLANIFICATION_EXAMEN
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO planification_examen
--     (session_id, departement_id, section_matiere_id, creneau_id,
--      type_epreuve, semestre, duree, mode_affectation, statut, nb_groupes, nb_surveillants_requis)
-- VALUES
-- -- IGL3 / Algorithmique S1 – Examen Final
-- (1, 1,
--  (SELECT sm.id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id
--   WHERE m.code = 'IGL3-INF-101' AND sm.annee_sem = '2025/2026-S1'),
--  (SELECT id FROM creneau WHERE date = '2026-01-07' AND heure_debut = '08:30'),
--  'EXAMEN_FINAL', 1, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- -- IGL3 / Réseaux S1 – Examen Final
-- (1, 1,
--  (SELECT sm.id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id
--   WHERE m.code = 'IGL3-INF-102' AND sm.annee_sem = '2025/2026-S1'),
--  (SELECT id FROM creneau WHERE date = '2026-01-07' AND heure_debut = '11:00'),
--  'EXAMEN_FINAL', 1, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- -- IGL4 / IA S2 – Examen Final
-- (1, 1,
--  (SELECT sm.id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id
--   WHERE m.code = 'IGL4-INF-201' AND sm.annee_sem = '2025/2026-S2'),
--  (SELECT id FROM creneau WHERE date = '2026-01-08' AND heure_debut = '08:30'),
--  'EXAMEN_FINAL', 2, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- -- IGL4 / Génie Logiciel S2 – Examen Final
-- (1, 1,
--  (SELECT sm.id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id
--   WHERE m.code = 'IGL4-INF-202' AND sm.annee_sem = '2025/2026-S2'),
--  (SELECT id FROM creneau WHERE date = '2026-01-08' AND heure_debut = '11:00'),
--  'EXAMEN_FINAL', 2, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2);

-- -- ─────────────────────────────────────────────────────────────
-- -- 15. PLANIF_SALLE
-- -- ─────────────────────────────────────────────────────────────
-- INSERT INTO planif_salle (planification_id, salle_id, groupe_id)
-- VALUES
-- -- IGL3 / Algorithmique → AMPHI A / groupe 1 IGL3
-- (1, (SELECT id FROM salle WHERE code='AMPHI A'),
--     (SELECT g.id FROM groupe g JOIN section s ON g.section_id = s.id WHERE s.nom='IGL3' AND g.numero=1)),

-- -- IGL3 / Réseaux → S101 / groupe 1 IGL3
-- (2, (SELECT id FROM salle WHERE code='S101'),
--     (SELECT g.id FROM groupe g JOIN section s ON g.section_id = s.id WHERE s.nom='IGL3' AND g.numero=1)),

-- -- IGL4 / IA → AMPHI A / groupe 2 IGL4
-- (3, (SELECT id FROM salle WHERE code='AMPHI A'),
--     (SELECT g.id FROM groupe g JOIN section s ON g.section_id = s.id WHERE s.nom='IGL4' AND g.numero=2)),

-- -- IGL4 / Génie Logiciel → S102 / groupe 2 IGL4
-- (4, (SELECT id FROM salle WHERE code='S102'),
--     (SELECT g.id FROM groupe g JOIN section s ON g.section_id = s.id WHERE s.nom='IGL4' AND g.numero=2));

-- -- ─────────────────────────────────────────────────────────────
-- -- 16. SURVEILLANCE  → vide intentionnellement
-- --     (sera remplie par l'algorithme d'affectation automatique)
-- -- ─────────────────────────────────────────────────────────────


-- COMMIT;

-- -- ─────────────────────────────────────────────────────────────
-- -- VÉRIFICATIONS POST-INSERT
-- -- ─────────────────────────────────────────────────────────────
-- SELECT 'departement'             AS table_name, COUNT(*) AS nb FROM departement              UNION ALL
-- SELECT 'niveau',                                COUNT(*)        FROM niveau                   UNION ALL
-- SELECT 'section',                               COUNT(*)        FROM section                  UNION ALL
-- SELECT 'groupe',                                COUNT(*)        FROM groupe                   UNION ALL
-- SELECT 'salle',                                 COUNT(*)        FROM salle                    UNION ALL
-- SELECT 'creneau',                               COUNT(*)        FROM creneau                  UNION ALL
-- SELECT 'session',                               COUNT(*)        FROM session                  UNION ALL
-- SELECT 'enseignant',                            COUNT(*)        FROM enseignant               UNION ALL
-- SELECT 'charge_horaire',                        COUNT(*)        FROM charge_horaire           UNION ALL
-- SELECT 'matiere',                               COUNT(*)        FROM matiere                  UNION ALL
-- SELECT 'section_matiere',                       COUNT(*)        FROM section_matiere          UNION ALL
-- SELECT 'enseignement',                          COUNT(*)        FROM enseignement             UNION ALL
-- SELECT 'disponibilite_enseignant',              COUNT(*)        FROM disponibilite_enseignant UNION ALL
-- SELECT 'planification_examen',                  COUNT(*)        FROM planification_examen     UNION ALL
-- SELECT 'planif_salle',                          COUNT(*)        FROM planif_salle             UNION ALL
-- SELECT 'surveillance',                          COUNT(*)        FROM surveillance
-- ORDER BY table_name;



BEGIN;

-- ============================================================
-- NETTOYAGE (ré-exécution propre)
-- ============================================================
DROP TABLE IF EXISTS surveillance              CASCADE;
DROP TABLE IF EXISTS planif_salle              CASCADE;
DROP TABLE IF EXISTS planification_examen     CASCADE;
DROP TABLE IF EXISTS disponibilite_enseignant CASCADE;
DROP TABLE IF EXISTS enseignement             CASCADE;
DROP TABLE IF EXISTS section_matiere          CASCADE;
DROP TABLE IF EXISTS matiere                  CASCADE;
DROP TABLE IF EXISTS charge_horaire           CASCADE;
DROP TABLE IF EXISTS enseignant               CASCADE;
DROP TABLE IF EXISTS session                  CASCADE;
DROP TABLE IF EXISTS creneau                  CASCADE;
DROP TABLE IF EXISTS salle                    CASCADE;
DROP TABLE IF EXISTS groupe                   CASCADE;
DROP TABLE IF EXISTS section                  CASCADE;
DROP TABLE IF EXISTS niveau                   CASCADE;
DROP TABLE IF EXISTS departement              CASCADE;

DROP TYPE IF EXISTS jour_semaine;
DROP TYPE IF EXISTS type_disponibilite;
DROP TYPE IF EXISTS statut_planif;
DROP TYPE IF EXISTS mode_affectation;
DROP TYPE IF EXISTS type_enseignement;
DROP TYPE IF EXISTS type_epreuve;
DROP TYPE IF EXISTS type_session;
DROP TYPE IF EXISTS statut_surveillance;

-- ============================================================
-- EXTENSIONS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. ÉNUMÉRATIONS
-- ============================================================
CREATE TYPE type_session        AS ENUM ('PRINCIPALE','RATTRAPAGE');
CREATE TYPE type_epreuve        AS ENUM ('EXAMEN_FINAL','DS');
CREATE TYPE type_enseignement   AS ENUM ('COURS','TD','TP');
CREATE TYPE mode_affectation    AS ENUM ('AUTOMATIQUE','MANUELLE');
CREATE TYPE statut_planif       AS ENUM ('BROUILLON','VALIDEE','PUBLIEE');
CREATE TYPE type_disponibilite  AS ENUM ('DISPONIBLE','INDISPONIBLE','COURS_PREVU','MISSION','CONGE');
CREATE TYPE jour_semaine        AS ENUM ('LUNDI','MARDI','MERCREDI','JEUDI','VENDREDI','SAMEDI');
CREATE TYPE statut_surveillance AS ENUM ('AFFECTE','CONFIRME');

-- ============================================================
-- 2. DEPARTEMENT
-- ============================================================
CREATE TABLE departement (
    id    SERIAL PRIMARY KEY,
    nom   VARCHAR(100) NOT NULL,
    code  VARCHAR(20)  NOT NULL UNIQUE
);

-- ============================================================
-- 3. NIVEAU
-- ============================================================
CREATE TABLE niveau (
    id              SERIAL PRIMARY KEY,
    libelle         VARCHAR(50)  NOT NULL,
    type_formation  VARCHAR(50)  NOT NULL,
    departement_id  INTEGER      NOT NULL REFERENCES departement(id)
);

-- ============================================================
-- 4. SECTION
-- ============================================================
CREATE TABLE section (
    id         SERIAL PRIMARY KEY,
    nom        VARCHAR(20) NOT NULL,
    niveau_id  INTEGER     NOT NULL REFERENCES niveau(id)
);

-- ============================================================
-- 5. GROUPE
-- ============================================================
CREATE TABLE groupe (
    id            SERIAL PRIMARY KEY,
    numero        INTEGER     NOT NULL,
    effectif      INTEGER     NOT NULL DEFAULT 0,
    nb_etudiants  INTEGER     NOT NULL DEFAULT 0,
    annee         VARCHAR(10) NOT NULL,
    section_id    INTEGER     NOT NULL REFERENCES section(id),
    UNIQUE (section_id, numero)
);

-- ============================================================
-- 6. SALLE
-- ============================================================
CREATE TABLE salle (
    id           SERIAL PRIMARY KEY,
    code         VARCHAR(30)  NOT NULL UNIQUE,
    designation  VARCHAR(100),
    capacite     INTEGER      NOT NULL,
    batiment     VARCHAR(50)
);

-- ============================================================
-- 7. CRENEAU
-- ============================================================
CREATE TABLE creneau (
    id           SERIAL PRIMARY KEY,
    date         DATE NOT NULL,
    heure_debut  TIME NOT NULL,
    heure_fin    TIME NOT NULL,
    libelle      VARCHAR(50),
    UNIQUE (date, heure_debut)
);

-- ============================================================
-- 8. SESSION
-- ============================================================
CREATE TABLE session (
    id                   SERIAL PRIMARY KEY,
    type_session         type_session  NOT NULL,
    annee_universitaire  VARCHAR(10)   NOT NULL,
    date_debut           DATE          NOT NULL,
    date_fin             DATE          NOT NULL,
    statut               statut_planif NOT NULL DEFAULT 'BROUILLON'
);

-- ============================================================
-- 9. ENSEIGNANT
-- ============================================================
CREATE TABLE enseignant (
    id              SERIAL PRIMARY KEY,
    nom             VARCHAR(60)  NOT NULL,
    prenom          VARCHAR(60)  NOT NULL,
    grade           VARCHAR(50),
    email           VARCHAR(100) UNIQUE,
    telephone       VARCHAR(20),
    departement_id  INTEGER REFERENCES departement(id)
);

-- ============================================================
-- 9b. COMPTE_ENSEIGNANT (Auth)       
-- ============================================================
CREATE TABLE compte_enseignant (
    id              SERIAL PRIMARY KEY,
    enseignant_id   INTEGER      NOT NULL UNIQUE REFERENCES enseignant(id) ON DELETE CASCADE,
    email           VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe    VARCHAR(255) NOT NULL,
    type_compte     VARCHAR(30)  NOT NULL DEFAULT 'ENSEIGNANT',
    actif           BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_compte_enseignant_email ON compte_enseignant(email);
CREATE INDEX idx_compte_enseignant_ens   ON compte_enseignant(enseignant_id);

-- ============================================================
-- 10. CHARGE_HORAIRE
-- ============================================================
CREATE TABLE charge_horaire (
    id              SERIAL PRIMARY KEY,
    enseignant_id   INTEGER       NOT NULL REFERENCES enseignant(id),
    annee_univ      VARCHAR(10)   NOT NULL,
    volume_horaire  NUMERIC(6,2)  NOT NULL DEFAULT 0,
    UNIQUE (enseignant_id, annee_univ)
);

-- ============================================================
-- 11. MATIERE
-- ============================================================
CREATE TABLE matiere (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(20)  NOT NULL UNIQUE,
    intitule        VARCHAR(150) NOT NULL,
    coefficient     NUMERIC(4,2) DEFAULT 1,
    credit          INTEGER      DEFAULT 1,
    a_examen_final  BOOLEAN      NOT NULL DEFAULT TRUE,
    a_ds            BOOLEAN      NOT NULL DEFAULT TRUE,
    duree_examen    INTEGER      DEFAULT 120,
    duree_ds        INTEGER      DEFAULT 60
);

-- ============================================================
-- 12. SECTION_MATIERE
-- ============================================================
CREATE TABLE section_matiere (
    id              SERIAL PRIMARY KEY,
    section_id      INTEGER NOT NULL REFERENCES section(id),
    matiere_id      INTEGER NOT NULL REFERENCES matiere(id),
    annee_sem       VARCHAR(20) NOT NULL,
    a_examen_final  BOOLEAN NOT NULL DEFAULT TRUE,
    a_ds            BOOLEAN NOT NULL DEFAULT TRUE,
    duree_examen    INTEGER DEFAULT 120,
    duree_ds        INTEGER DEFAULT 60,
    UNIQUE (section_id, matiere_id, annee_sem)
);

-- ============================================================
-- 13. ENSEIGNEMENT
-- ============================================================
CREATE TABLE enseignement (
    id                  SERIAL PRIMARY KEY,
    enseignant_id       INTEGER           NOT NULL REFERENCES enseignant(id),
    matiere_id          INTEGER           NOT NULL REFERENCES matiere(id),
    type_enseignement   type_enseignement NOT NULL,
    nb_heures           NUMERIC(5,2)      NOT NULL DEFAULT 0,
    annee_sem           VARCHAR(20),
    UNIQUE (enseignant_id, matiere_id, type_enseignement, annee_sem)
);

-- ============================================================
-- 14. DISPONIBILITE_ENSEIGNANT
-- ============================================================
CREATE TABLE disponibilite_enseignant (
    id             SERIAL PRIMARY KEY,
    enseignant_id  INTEGER            NOT NULL REFERENCES enseignant(id),
    date           DATE               NOT NULL,
    heure_debut    TIME               NOT NULL,
    heure_fin      TIME               NOT NULL,
    type_dispo     type_disponibilite NOT NULL DEFAULT 'INDISPONIBLE',
    motif          VARCHAR(200),
    confirme       BOOLEAN            NOT NULL DEFAULT TRUE
);

-- ============================================================
-- 15. PLANIFICATION_EXAMEN
-- ============================================================
CREATE TABLE planification_examen (
    id                      SERIAL PRIMARY KEY,
    session_id              INTEGER          NOT NULL REFERENCES session(id),
    departement_id          INTEGER          NOT NULL REFERENCES departement(id),
    section_matiere_id      INTEGER          NOT NULL REFERENCES section_matiere(id),
    creneau_id              INTEGER          NOT NULL REFERENCES creneau(id),
    type_epreuve            type_epreuve     NOT NULL,
    semestre                INTEGER          NOT NULL CHECK (semestre IN (1,2)),
    duree                   INTEGER          NOT NULL DEFAULT 120,
    mode_affectation        mode_affectation NOT NULL DEFAULT 'AUTOMATIQUE',
    statut                  statut_planif    NOT NULL DEFAULT 'BROUILLON',
    nb_groupes              INTEGER          DEFAULT 1,
    nb_surveillants_requis  INTEGER          DEFAULT 2,
    UNIQUE (session_id, section_matiere_id, creneau_id, type_epreuve)
);

-- ============================================================
-- 16. PLANIF_SALLE
-- ============================================================
CREATE TABLE planif_salle (
    planification_id  INTEGER NOT NULL REFERENCES planification_examen(id),
    salle_id          INTEGER NOT NULL REFERENCES salle(id),
    groupe_id         INTEGER REFERENCES groupe(id),
    PRIMARY KEY (planification_id, salle_id)
);

-- ============================================================
-- 17. SURVEILLANCE
-- ============================================================
CREATE TABLE surveillance (
    id                   SERIAL PRIMARY KEY,
    planification_id     INTEGER             NOT NULL REFERENCES planification_examen(id) ON DELETE CASCADE,
    enseignant_id        INTEGER             NOT NULL REFERENCES enseignant(id) ON DELETE CASCADE,
    groupe_id            INTEGER             REFERENCES groupe(id) ON DELETE SET NULL,
    salle_id             INTEGER             REFERENCES salle(id)  ON DELETE SET NULL,
    est_externe          BOOLEAN             NOT NULL DEFAULT FALSE,
    motif_externe        VARCHAR(200),
    charge               NUMERIC(4,2)        DEFAULT 1.0,
    presence             BOOLEAN             DEFAULT FALSE,
    mode_affectation     mode_affectation    NOT NULL DEFAULT 'AUTOMATIQUE',
    statut_surveillance  statut_surveillance DEFAULT 'AFFECTE',
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_surv_planif_ens_groupe UNIQUE (planification_id, enseignant_id, groupe_id)
);

-- ============================================================
-- INDEX
-- ============================================================
CREATE INDEX idx_niveau_dept       ON niveau(departement_id);
CREATE INDEX idx_section_niveau    ON section(niveau_id);
CREATE INDEX idx_groupe_section    ON groupe(section_id);
CREATE INDEX idx_groupe_annee      ON groupe(annee);
CREATE INDEX idx_ens_dept          ON enseignant(departement_id);
CREATE INDEX idx_enseignement_ens  ON enseignement(enseignant_id);
CREATE INDEX idx_enseignement_mat  ON enseignement(matiere_id);
CREATE INDEX idx_sm_section        ON section_matiere(section_id);
CREATE INDEX idx_sm_matiere        ON section_matiere(matiere_id);
CREATE INDEX idx_dispo_ens         ON disponibilite_enseignant(enseignant_id, date);
CREATE INDEX idx_planif_session    ON planification_examen(session_id);
CREATE INDEX idx_planif_dept       ON planification_examen(departement_id);
CREATE INDEX idx_planif_creneau    ON planification_examen(creneau_id);
CREATE INDEX idx_surv_planif       ON surveillance(planification_id);
CREATE INDEX idx_surv_ens          ON surveillance(enseignant_id);
CREATE INDEX idx_surv_groupe       ON surveillance(groupe_id);
CREATE INDEX idx_surv_salle        ON surveillance(salle_id);
CREATE INDEX idx_surv_externe      ON surveillance(est_externe);


-- ============================================================
-- ============================================================
--                      REMPLISSAGE (DML)
-- ============================================================
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- 1. DEPARTEMENT
-- ─────────────────────────────────────────────────────────────
INSERT INTO departement (nom, code) VALUES
('Département des Sciences de l''Informatique', 'DSI');

-- ─────────────────────────────────────────────────────────────
-- 2. NIVEAU
-- ─────────────────────────────────────────────────────────────
INSERT INTO niveau (libelle, type_formation, departement_id) VALUES
('Cycle Ingénieur', 'Informatique', 1);

-- ─────────────────────────────────────────────────────────────
-- 3. SECTION  (IGL3 et IGL4)
-- ─────────────────────────────────────────────────────────────
INSERT INTO section (nom, niveau_id) VALUES
('IGL3', 1),
('IGL4', 1);

-- ─────────────────────────────────────────────────────────────
-- 4. GROUPE  (1 groupe par section, année 2025/2026)
-- ─────────────────────────────────────────────────────────────
INSERT INTO groupe (numero, effectif, nb_etudiants, annee, section_id) VALUES
(1, 35, 35, '2025/2026', (SELECT id FROM section WHERE nom = 'IGL3')),
(2, 30, 30, '2025/2026', (SELECT id FROM section WHERE nom = 'IGL4'));

-- ─────────────────────────────────────────────────────────────
-- 5. SALLE
-- ─────────────────────────────────────────────────────────────
INSERT INTO salle (code, designation, capacite, batiment) VALUES
('AMPHI A',  'Amphithéâtre A',   120, 'Principal'),
('S101',     'Salle 101',         40, 'Bâtiment I'),
('S102',     'Salle 102',         40, 'Bâtiment I');

-- ─────────────────────────────────────────────────────────────
-- 6. CRENEAU
-- ─────────────────────────────────────────────────────────────
INSERT INTO creneau (date, heure_debut, heure_fin, libelle) VALUES
('2026-01-07', '08:30', '10:30', 'Mer 07/01 – Matin'),
('2026-01-07', '11:00', '13:00', 'Mer 07/01 – Milieu'),
('2026-01-08', '08:30', '10:30', 'Jeu 08/01 – Matin'),
('2026-01-08', '11:00', '13:00', 'Jeu 08/01 – Milieu');

-- ─────────────────────────────────────────────────────────────
-- 7. SESSION
-- ─────────────────────────────────────────────────────────────
INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut) VALUES
('PRINCIPALE', '2025/2026', '2026-01-07', '2026-01-15', 'VALIDEE');

-- ─────────────────────────────────────────────────────────────
-- 8. ENSEIGNANT  (4 profs)
-- ─────────────────────────────────────────────────────────────
INSERT INTO enseignant (nom, prenom, grade, email, telephone, departement_id) VALUES
('Manita',   'Ghaith', 'Maître de Conf.', 'ghaith.manita@fst.utm.tn',   '55197776', 1),
('Zouaoui',  'Sana',   'PES-Info',        'sana.zouaoui@fst.utm.tn',    '96276502', 1),
('Meddeb',   'Rahma',  'Maître Ass.',     'rahma.meddeb@fst.utm.tn',    '98424172', 1),
('Hizem',    'Moez',   'Maître Ass.',     'moez.hizem@fst.utm.tn',      '24740880', 1);

-- ─────────────────────────────────────────────────────────────
-- 8b. COMPTE_ENSEIGNANT (Auth)       
-- ─────────────────────────────────────────────────────────────
INSERT INTO compte_enseignant (enseignant_id, email, mot_de_passe, type_compte) VALUES
((SELECT id FROM enseignant WHERE nom='Manita'  AND prenom='Ghaith'),
 'ghaith.manita@fst.utm.tn',  'Manita123',   'ENSEIGNANT'),
((SELECT id FROM enseignant WHERE nom='Zouaoui' AND prenom='Sana'),
 'sana.zouaoui@fst.utm.tn',   'Zouaoui123',  'ENSEIGNANT'),
((SELECT id FROM enseignant WHERE nom='Meddeb'  AND prenom='Rahma'),
 'rahma.meddeb@fst.utm.tn',   'Meddeb123',   'ENSEIGNANT'),
((SELECT id FROM enseignant WHERE nom='Hizem'   AND prenom='Moez'),
 'moez.hizem@fst.utm.tn',     'Hizem123',    'ENSEIGNANT');

-- ─────────────────────────────────────────────────────────────
-- 9. CHARGE_HORAIRE
-- ─────────────────────────────────────────────────────────────
INSERT INTO charge_horaire (enseignant_id, annee_univ, volume_horaire)
SELECT id, '2025/2026', 192 FROM enseignant;

-- ─────────────────────────────────────────────────────────────
-- 10. MATIERE  (4 matières : 2 par semestre)
-- ─────────────────────────────────────────────────────────────
INSERT INTO matiere (code, intitule, coefficient, credit, a_examen_final, a_ds, duree_examen, duree_ds) VALUES
('IGL3-INF-101', 'Algorithmique Avancée',       2, 3, TRUE, TRUE, 120, 60),
('IGL3-INF-102', 'Réseaux et Protocoles',        2, 3, TRUE, TRUE, 120, 60),
('IGL4-INF-201', 'Intelligence Artificielle',    2, 3, TRUE, TRUE, 120, 60),
('IGL4-INF-202', 'Génie Logiciel',               2, 3, TRUE, TRUE, 120, 60);

-- ─────────────────────────────────────────────────────────────
-- 11. SECTION_MATIERE
--     IGL3 → 2 matières S1 | IGL4 → 2 matières S2
-- ─────────────────────────────────────────────────────────────
INSERT INTO section_matiere (section_id, matiere_id, annee_sem, a_examen_final, a_ds, duree_examen, duree_ds) VALUES
-- IGL3 – Semestre 1
((SELECT id FROM section WHERE nom='IGL3'),
 (SELECT id FROM matiere WHERE code='IGL3-INF-101'), '2025/2026-S1', TRUE, TRUE, 120, 60),
((SELECT id FROM section WHERE nom='IGL3'),
 (SELECT id FROM matiere WHERE code='IGL3-INF-102'), '2025/2026-S1', TRUE, TRUE, 120, 60),
-- IGL4 – Semestre 2
((SELECT id FROM section WHERE nom='IGL4'),
 (SELECT id FROM matiere WHERE code='IGL4-INF-201'), '2025/2026-S2', TRUE, TRUE, 120, 60),
((SELECT id FROM section WHERE nom='IGL4'),
 (SELECT id FROM matiere WHERE code='IGL4-INF-202'), '2025/2026-S2', TRUE, TRUE, 120, 60);

-- ─────────────────────────────────────────────────────────────
-- 12. ENSEIGNEMENT
--     Manita  → Algorithmique (COURS S1)
--     Zouaoui → Réseaux       (COURS S1)
--     Meddeb  → IA            (COURS S2)
--     Hizem   → Génie Log.    (COURS S2)
-- ─────────────────────────────────────────────────────────────
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem) VALUES
((SELECT id FROM enseignant WHERE nom='Manita'),
 (SELECT id FROM matiere WHERE code='IGL3-INF-101'), 'COURS', 21, '2025/2026-S1'),
((SELECT id FROM enseignant WHERE nom='Zouaoui'),
 (SELECT id FROM matiere WHERE code='IGL3-INF-102'), 'COURS', 21, '2025/2026-S1'),
((SELECT id FROM enseignant WHERE nom='Meddeb'),
 (SELECT id FROM matiere WHERE code='IGL4-INF-201'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Hizem'),
 (SELECT id FROM matiere WHERE code='IGL4-INF-202'), 'COURS', 21, '2025/2026-S2');

-- ─────────────────────────────────────────────────────────────
-- 13. DISPONIBILITE_ENSEIGNANT  (4 enregistrements)
--     Manita   → indisponible le 07/01 matin
--     Zouaoui  → mission      le 07/01 milieu
--     Meddeb   → congé        le 08/01 matin
--     Hizem    → cours prévu  le 08/01 milieu
-- ─────────────────────────────────────────────────────────────
INSERT INTO disponibilite_enseignant (enseignant_id, date, heure_debut, heure_fin, type_dispo, motif, confirme) VALUES
((SELECT id FROM enseignant WHERE nom='Manita'),
 '2026-01-07', '08:30', '10:30', 'INDISPONIBLE',  'Indisponibilité personnelle',     TRUE),
((SELECT id FROM enseignant WHERE nom='Zouaoui'),
 '2026-01-07', '11:00', '13:00', 'MISSION',        'Mission à l''extérieur',          TRUE),
((SELECT id FROM enseignant WHERE nom='Meddeb'),
 '2026-01-08', '08:30', '10:30', 'CONGE',           'Congé maladie',                   TRUE),
((SELECT id FROM enseignant WHERE nom='Hizem'),
 '2026-01-08', '11:00', '13:00', 'COURS_PREVU',    'Cours de rattrapage planifié',    TRUE);

-- ─────────────────────────────────────────────────────────────
-- 14. PLANIFICATION_EXAMEN
-- ─────────────────────────────────────────────────────────────
INSERT INTO planification_examen
    (session_id, departement_id, section_matiere_id, creneau_id,
     type_epreuve, semestre, duree, mode_affectation, statut, nb_groupes, nb_surveillants_requis)
VALUES
-- IGL3 / Algorithmique S1 – Examen Final
(1, 1,
 (SELECT sm.id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id
  WHERE m.code = 'IGL3-INF-101' AND sm.annee_sem = '2025/2026-S1'),
 (SELECT id FROM creneau WHERE date = '2026-01-07' AND heure_debut = '08:30'),
 'EXAMEN_FINAL', 1, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- IGL3 / Réseaux S1 – Examen Final
(1, 1,
 (SELECT sm.id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id
  WHERE m.code = 'IGL3-INF-102' AND sm.annee_sem = '2025/2026-S1'),
 (SELECT id FROM creneau WHERE date = '2026-01-07' AND heure_debut = '11:00'),
 'EXAMEN_FINAL', 1, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- IGL4 / IA S2 – Examen Final
(1, 1,
 (SELECT sm.id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id
  WHERE m.code = 'IGL4-INF-201' AND sm.annee_sem = '2025/2026-S2'),
 (SELECT id FROM creneau WHERE date = '2026-01-08' AND heure_debut = '08:30'),
 'EXAMEN_FINAL', 2, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2),

-- IGL4 / Génie Logiciel S2 – Examen Final
(1, 1,
 (SELECT sm.id FROM section_matiere sm JOIN matiere m ON sm.matiere_id = m.id
  WHERE m.code = 'IGL4-INF-202' AND sm.annee_sem = '2025/2026-S2'),
 (SELECT id FROM creneau WHERE date = '2026-01-08' AND heure_debut = '11:00'),
 'EXAMEN_FINAL', 2, 120, 'AUTOMATIQUE', 'VALIDEE', 1, 2);

-- ─────────────────────────────────────────────────────────────
-- 15. PLANIF_SALLE
-- ─────────────────────────────────────────────────────────────
INSERT INTO planif_salle (planification_id, salle_id, groupe_id)
VALUES
-- IGL3 / Algorithmique → AMPHI A / groupe 1 IGL3
(1, (SELECT id FROM salle WHERE code='AMPHI A'),
    (SELECT g.id FROM groupe g JOIN section s ON g.section_id = s.id WHERE s.nom='IGL3' AND g.numero=1)),

-- IGL3 / Réseaux → S101 / groupe 1 IGL3
(2, (SELECT id FROM salle WHERE code='S101'),
    (SELECT g.id FROM groupe g JOIN section s ON g.section_id = s.id WHERE s.nom='IGL3' AND g.numero=1)),

-- IGL4 / IA → AMPHI A / groupe 2 IGL4
(3, (SELECT id FROM salle WHERE code='AMPHI A'),
    (SELECT g.id FROM groupe g JOIN section s ON g.section_id = s.id WHERE s.nom='IGL4' AND g.numero=2)),

-- IGL4 / Génie Logiciel → S102 / groupe 2 IGL4
(4, (SELECT id FROM salle WHERE code='S102'),
    (SELECT g.id FROM groupe g JOIN section s ON g.section_id = s.id WHERE s.nom='IGL4' AND g.numero=2));

-- ─────────────────────────────────────────────────────────────
-- 16. SURVEILLANCE  → vide intentionnellement
--     (sera remplie par l'algorithme d'affectation automatique)
-- ─────────────────────────────────────────────────────────────


COMMIT;

-- ─────────────────────────────────────────────────────────────
-- VÉRIFICATIONS POST-INSERT
-- ─────────────────────────────────────────────────────────────
SELECT 'departement'             AS table_name, COUNT(*) AS nb FROM departement              UNION ALL
SELECT 'niveau',                                COUNT(*)        FROM niveau                   UNION ALL
SELECT 'section',                               COUNT(*)        FROM section                  UNION ALL
SELECT 'groupe',                                COUNT(*)        FROM groupe                   UNION ALL
SELECT 'salle',                                 COUNT(*)        FROM salle                    UNION ALL
SELECT 'creneau',                               COUNT(*)        FROM creneau                  UNION ALL
SELECT 'session',                               COUNT(*)        FROM session                  UNION ALL
SELECT 'enseignant',                            COUNT(*)        FROM enseignant               UNION ALL
SELECT 'charge_horaire',                        COUNT(*)        FROM charge_horaire           UNION ALL
SELECT 'matiere',                               COUNT(*)        FROM matiere                  UNION ALL
SELECT 'section_matiere',                       COUNT(*)        FROM section_matiere          UNION ALL
SELECT 'enseignement',                          COUNT(*)        FROM enseignement             UNION ALL
SELECT 'disponibilite_enseignant',              COUNT(*)        FROM disponibilite_enseignant UNION ALL
SELECT 'planification_examen',                  COUNT(*)        FROM planification_examen     UNION ALL
SELECT 'planif_salle',                          COUNT(*)        FROM planif_salle             UNION ALL
SELECT 'surveillance',                          COUNT(*)        FROM surveillance
ORDER BY table_name;
