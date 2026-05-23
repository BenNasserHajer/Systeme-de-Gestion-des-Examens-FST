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
    annee           INTEGER      NOT NULL,
    type_formation  VARCHAR(50)  NOT NULL,
    departement_id  INTEGER      NOT NULL REFERENCES departement(id)
);

-- ============================================================
-- 4. SECTION
-- ============================================================
CREATE TABLE section (
    id         SERIAL PRIMARY KEY,
    nom        VARCHAR(20) NOT NULL,       -- nb_etudiants supprimé → migré vers groupe
    niveau_id  INTEGER     NOT NULL REFERENCES niveau(id)
);

-- ============================================================
-- 5. GROUPE
-- ============================================================
CREATE TABLE groupe (
    id            SERIAL PRIMARY KEY,
    numero        INTEGER     NOT NULL,
    effectif      INTEGER     NOT NULL DEFAULT 0,
    nb_etudiants  INTEGER     NOT NULL DEFAULT 0,  -- ← migré depuis section
    annee         VARCHAR(10) NOT NULL,             -- ← nouveau champ ex: "2025/2026"
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
    batiment     VARCHAR(50),
    id_departement INTEGER REFERENCES departement(id)
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
CREATE INDEX idx_groupe_annee      ON groupe(annee);              -- ← nouvel index
CREATE INDEX idx_salle_departement ON salle(id_departement);
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

COMMIT;
