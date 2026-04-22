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
    id            SERIAL PRIMARY KEY,
    nom           VARCHAR(20) NOT NULL,
    nb_etudiants  INTEGER     NOT NULL DEFAULT 0,
    niveau_id     INTEGER     NOT NULL REFERENCES niveau(id)
);

-- ============================================================
-- 5. GROUPE
-- ============================================================
CREATE TABLE groupe (
    id          SERIAL PRIMARY KEY,
    numero      INTEGER NOT NULL,
    effectif    INTEGER NOT NULL DEFAULT 0,
    section_id  INTEGER NOT NULL REFERENCES section(id),
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
    a_examen_final  BOOLEAN NOT NULL DEFAULT TRUE,
    a_ds            BOOLEAN NOT NULL DEFAULT TRUE,
    duree_examen    INTEGER DEFAULT 120,
    duree_ds        INTEGER DEFAULT 60,
    UNIQUE (section_id, matiere_id)
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
    UNIQUE (enseignant_id, matiere_id, type_enseignement)
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
-- ✅ AJOUT : departement_id
--    Permet de savoir directement à quel département appartient
--    chaque examen planifié, sans avoir à remonter 4 jointures.
--    Valeur remplie au moment où l'admin choisit le département
--    dans l'interface avant de créer la planification.
-- ============================================================
CREATE TABLE planification_examen (
    id                      SERIAL PRIMARY KEY,
    session_id              INTEGER          NOT NULL REFERENCES session(id),
    departement_id          INTEGER          NOT NULL REFERENCES departement(id),  
    section_matiere_id      INTEGER          NOT NULL REFERENCES section_matiere(id),
    creneau_id              INTEGER          NOT NULL REFERENCES creneau(id),
    type_epreuve            type_epreuve     NOT NULL,
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
-- ✅ AJOUT : est_externe + motif_externe
--    est_externe  = FALSE → le prof appartient au même département que l'examen (cas normal)
--    est_externe  = TRUE  → le prof vient d'un autre département (cas de besoin / urgence)
--    motif_externe        → raison du recours à un prof externe (ex: "Manque de personnel")
-- ============================================================
CREATE TABLE surveillance (
    id                   SERIAL PRIMARY KEY,
    planification_id     INTEGER             NOT NULL REFERENCES planification_examen(id),
    enseignant_id        INTEGER             NOT NULL REFERENCES enseignant(id),
    est_externe          BOOLEAN             NOT NULL DEFAULT FALSE,
    motif_externe        VARCHAR(200),
    charge               NUMERIC(4,2)        DEFAULT 1.0,
    presence             BOOLEAN             DEFAULT FALSE,
    mode_affectation     mode_affectation    NOT NULL DEFAULT 'AUTOMATIQUE',
    statut_surveillance  statut_surveillance DEFAULT 'AFFECTE',
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (planification_id, enseignant_id)
);

-- ============================================================
-- INDEX
-- ============================================================
CREATE INDEX idx_niveau_dept       ON niveau(departement_id);
CREATE INDEX idx_section_niveau    ON section(niveau_id);
CREATE INDEX idx_groupe_section    ON groupe(section_id);
CREATE INDEX idx_ens_dept          ON enseignant(departement_id);
CREATE INDEX idx_enseignement_ens  ON enseignement(enseignant_id);
CREATE INDEX idx_enseignement_mat  ON enseignement(matiere_id);
CREATE INDEX idx_sm_section        ON section_matiere(section_id);
CREATE INDEX idx_sm_matiere        ON section_matiere(matiere_id);
CREATE INDEX idx_dispo_ens         ON disponibilite_enseignant(enseignant_id, date);
CREATE INDEX idx_planif_session    ON planification_examen(session_id);
CREATE INDEX idx_planif_dept       ON planification_examen(departement_id);   -- ✅ NOUVEAU
CREATE INDEX idx_planif_creneau    ON planification_examen(creneau_id);
CREATE INDEX idx_surv_planif       ON surveillance(planification_id);
CREATE INDEX idx_surv_ens          ON surveillance(enseignant_id);
CREATE INDEX idx_surv_externe      ON surveillance(est_externe);               -- ✅ NOUVEAU

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
-- 2. SESSION
-- ─────────────────────────────────────────────────────────────
INSERT INTO session (type_session, annee_universitaire, date_debut, date_fin, statut) VALUES
('PRINCIPALE', '2025/2026', '2026-01-07', '2026-01-15', 'VALIDEE');

-- ─────────────────────────────────────────────────────────────
-- 3. SALLES
-- ─────────────────────────────────────────────────────────────
INSERT INTO salle (code, designation, capacite, batiment) VALUES
('S22',              'Salle 22',                              25,  'Informatique'),
('AMPHI INFO',       'Amphithéâtre Informatique',            150,  'Principal'),
('AMPHI B',          'Amphithéâtre B',                       120,  'Principal'),
('AMPHI C',          'Amphithéâtre C',                       120,  'Principal'),
('S31',              'Salle 31',                              30,  'Principal'),
('S.BIB.INFO',       'Salle Bibliothèque Informatique',       40,  'Bibliothèque'),
('I 106',            'Salle I-106',                           30,  'Bâtiment I'),
('S.CONF.INF',       'Salle de Conférence Informatique',      50,  'Informatique'),
('Amphi Phys 2',     'Amphithéâtre Physique 2',              100,  'Physique'),
('AC2',              'Salle AC2',                             80,  'Annexe'),
('AC1',              'Salle AC1',                             80,  'Annexe'),
('I103',             'Salle I-103',                           30,  'Bâtiment I'),
('I104',             'Salle I-104',                           30,  'Bâtiment I'),
('I107',             'Salle I-107',                           30,  'Bâtiment I'),
('ME213',            'Salle ME-213',                          25,  'Mécanique'),
('ME216',            'Salle ME-216',                          25,  'Mécanique'),
('ME218',            'Salle ME-218',                          25,  'Mécanique'),
('ME219',            'Salle ME-219',                          25,  'Mécanique'),
('SLB1',             'Salle Labo 1',                          20,  'Laboratoires'),
('SLB2',             'Salle Labo 2',                          20,  'Laboratoires'),
('SLB3',             'Salle Labo 3',                          20,  'Laboratoires'),
('P15',              'Salle P-15',                            30,  'Physique'),
('SS2 INF',          'Salle Sous-Sol 2 Informatique',         30,  'Informatique'),
('Salle Conf Info',  'Salle de Conférence Info (alt)',        50,  'Informatique'),
('AM1',              'Salle AM1',                            100,  'Annexe'),
('AM2',              'Salle AM2',                            100,  'Annexe'),
('Amphi Info',       'Amphithéâtre Informatique (alt)',      150,  'Principal');

-- ─────────────────────────────────────────────────────────────
-- 4. CRENEAUX
-- ─────────────────────────────────────────────────────────────
INSERT INTO creneau (date, heure_debut, heure_fin, libelle) VALUES
('2026-01-07','08:30','10:30','Mer 07/01 – Matin'),
('2026-01-07','11:00','13:00','Mer 07/01 – Milieu'),
('2026-01-07','14:00','16:00','Mer 07/01 – Après-midi'),
('2026-01-08','08:30','10:30','Jeu 08/01 – Matin'),
('2026-01-08','11:00','13:00','Jeu 08/01 – Milieu'),
('2026-01-08','14:00','16:00','Jeu 08/01 – Après-midi'),
('2026-01-09','08:30','10:30','Ven 09/01 – Matin'),
('2026-01-09','11:00','13:00','Ven 09/01 – Milieu'),
('2026-01-09','14:00','16:00','Ven 09/01 – Après-midi'),
('2026-01-10','08:30','10:30','Sam 10/01 – Matin'),
('2026-01-10','11:00','13:00','Sam 10/01 – Milieu'),
('2026-01-12','08:30','10:30','Lun 12/01 – Matin'),
('2026-01-12','11:00','13:00','Lun 12/01 – Milieu'),
('2026-01-12','14:00','16:00','Lun 12/01 – Après-midi'),
('2026-01-13','08:30','10:30','Mar 13/01 – Matin'),
('2026-01-13','11:00','13:00','Mar 13/01 – Milieu'),
('2026-01-13','14:00','16:00','Mar 13/01 – Après-midi'),
('2026-01-14','08:30','10:30','Mer 14/01 – Matin'),
('2026-01-14','11:00','13:00','Mer 14/01 – Milieu'),
('2026-01-14','14:00','16:00','Mer 14/01 – Après-midi'),
('2026-01-15','08:30','10:30','Jeu 15/01 – Matin'),
('2026-01-15','11:00','13:00','Jeu 15/01 – Milieu'),
('2026-01-15','14:00','16:00','Jeu 15/01 – Après-midi');

-- ─────────────────────────────────────────────────────────────
-- 5. ENSEIGNANTS
-- ─────────────────────────────────────────────────────────────
INSERT INTO enseignant (nom, prenom, grade, email, telephone, departement_id) VALUES
('Abbes',            'Haythem',     'Maître de Conf.',   'haythem.abbes@fst.utm.tn',              '98475215', 1),
('Abbessi',          'Faten',       'PES-Info',           'faten.abbassi@fst.utm.tn',              '94765557', 1),
('Abed',             'Rahma',       'Maître Ass.',        'rahma.abed@fst.utm.tn',                 '94435732', 1),
('Abidi',            'Najib',       'PES-C2N',            'najib.labidi@fst.utm.tn',               '54419919', 1),
('Agrebi',           'Adel',        'Ass-Info',           'adel.agrebi@fst.utm.tn',                '52574610', 1),
('Alaya',            'Houda',       'Maître Ass.',        'houda.alaya@fst.utm.tn',                '97825671', 1),
('Amdouni',          'Asma',        'Maître Ass.',        'asma.amdouni@fst.utm.tn',               '54892821', 1),
('Amdouni',          'Naama',       'Maître Ass.',        'naama.amdouni@fst.utm.tn',              '29677289', 1),
('Ameur Abid',       'Chiheb',      'Maître Ass.',        'chiheb.abid@fst.utm.tn',                '22581598', 1),
('Aouadi',           'Hamed',       'Maître Ass.',        'hamed.aouadi@fst.utm.tn',               '98991791', 1),
('Azzabi',           'Fares',       'Expert-Info',        'azzabi.fa@gmail.com',                   '20060495', 1),
('Ben Azzouz',       'Yazid',       'Docteur-Gestion',    'yazidbenazouz@gmail.com',               '53565645', 1),
('Ben Dhiaf',        'Zouhour',     'Maître Ass.',        'zouhour.bendhiaf@fst.utm.tn',           '22532513', 1),
('Ben Hassine',      'Mohamed Ali', 'Maître Ass.',        'mohamedali.benhassine@fst.utm.tn',      '97422800', 1),
('Ben Moussa',       'Zied',        'PES-Info',           'zied.benmoussa@fst.utm.tn',             '58557402', 1),
('Ben Othman',       'Leila',       'Maître Ass.',        'leila.benothman@fst.utm.tn',            '98925135', 1),
('Bennani',          'Taha',        'Maître Ass.',        'taha.bennani@fst.utm.tn',               '21682982', 1),
('Blanco',           'Rym',         'PES-Français',       'rym.blanco@fst.utm.tn',                 '50753185', 1),
('Bouaita',          'Mourad',      'PES-Anglais',        'mourad.bouaita@fst.utm.tn',             '22519765', 1),
('Bouhadda',         'Hanene',      'Maître Ass.',        'hanen.bouhadda@fst.utm.tn',             '98636058', 1),
('Boussen',          'Sinda',       'Maître Ass.',        'sinda.boussen@fst.utm.tn',              '29310441', 1),
('Boussif',          'Nouh',        'Contractuel-Info',   'boussif.nouh@gmail.com',                '22660028', 1),
('Chabchoub',        'Sana',        'PES-C2N',            'sana.chabchoub@fst.utm.tn',             '22343376', 1),
('Chaouachi Allani', 'Imen',        'ING',                'imen.allani@gmail.com',                 '54889697', 1),
('Dammak',           'Nawel',       'PES-Anglais',        'nawel.krichene@fst.utm.tn',             '23663251', 1),
('Denden',           'Islem',       'Technologue',        'islem.denden@fst.utm.tn',               '98737000', 1),
('Doggaz',           'Narjes',      'Maître Ass.',        'narjes.doggaz@fst.utm.tn',              '24892812', 1),
('Dridi',            'Rim',         'Maître Ass.',        'rime.dridi@fst.utm.tn',                 '92237999', 1),
('Echaieb',          'Kamel',       'Maître Ass.',        'kamel.echaieb@fst.utm.tn',              '98377953', 1),
('El Kout',          'Ilhem',       'Contractuel-Info',   'ilhem.elkout@gmail.com',                '50149258', 1),
('Ellouze',          'Nourhene',    'Maître Ass.',        'nourhene.ellouze@fst.utm.tn',           '22797646', 1),
('Essid',            'Chaker',      'Maître Ass.',        'chaker.essid@fst.utm.tn',               '99970692', 1),
('Fayech',           'Ines',        'Maître Ass.',        'ines.fayech@fst.utm.tn',                '96957944', 1),
('Fourati',          'Hend',        'Maître Ass.',        'hend.fourati@fst.utm.tn',               '97980733', 1),
('Gargouri',         'Khalil',      'Technologue',        'khalil.gargouri@fst.utm.tn',            '52522455', 1),
('Gharbi',           'Asma',        'ASS-Droit Ethique',  'asma.gharbi16@gmail.com',               '94104439', 1),
('Gharbi',           'Hassen',      'MC-ENSI',            'hassen.gharbi@ensi-uma.tn',             '92897259', 1),
('Gharbi',           'Hella',       'PES-Anglais',        'hela.gharbi@fst.utm.tn',                '25988344', 1),
('Guesmi',           'Soumaya',     'Maître Ass.',        'soumaya.guesmi@fst.utm.tn',             '99853274', 1),
('Hajji',            'Imen',        'PES-Info',           'imen.hajji@fst.utm.tn',                 '97795658', 1),
('Hanana',           'Nourhene',    'ING',                'nourhene.hanana@etudiant-fst.utm.tn',   '93540919', 1),
('Hizem',            'Moez',        'Maître Ass.',        'moez.hizem@fst.utm.tn',                 '24740880', 1),
('Idi',              'Maroua',      'Contractuel-Info',   'marouaidi@gmail.com',                   '93687123', 1),
('Jaballah',         'Soumaya',     'Economiste',         'jaballahsoumaya@hotmail.fr',            '98511685', 1),
('Jandoubi',         'Amina',       'Contractuel-Info',   'jandoubi.amina@etudiant-fst.utm.tn',    '26166354', 1),
('Keraani',          'Dorsaf',      'PES-Anglais',        'dkeraani@yahoo.fr',                     '22894123', 1),
('Khaloui',          'Safa',        'Doctorant',          'khaloui.safa@etudiant-fst.utm.tn',      '21188588', 1),
('Kouki',            'Wahiba',      'PES-Anglais',        'wahiba.kouki@fst.utm.tn',               '96487844', 1),
('Krichi',           'Mohsen',      'Expert',             'krichim@gmail.com',                     '98597729', 1),
('Lassoued',         'Mohamed',     'Maître technologue', 'mohamed.lassoued@gmail.com',            '98438436', 1),
('Maalej',           'Rania',       'Maître Ass.',        'rania.maalej@fst.utm.tn',               '21106176', 1),
('Majd',             'Bellaj',      'Contractuel-Info',   'majd.bellaj@gmail.com',                 '93993741', 1),
('Majdi',            'Manel',       'Contractuel-Eco',    'menel.majdi08@gmail.com',               '28288448', 1),
('Maksoud',          'Hamdi',       'PES-C2N',            'hamdi.maksoud@fst.utm.tn',              '50812305', 1),
('Manita',           'Ghaith',      'Maître de Conf.',    'ghaith.manita@fst.utm.tn',              '55197776', 1),
('Masmoudi',         'Salma',       'Maître Ass.',        'salma.masmoudi@fst.utm.tn',             '93895345', 1),
('Mechraoui',        'Maryem',      'Doctorant',          'maryem.mechraoui@etudiant-fst.utm.tn',  '99959555', 1),
('Meddeb',           'Rahma',       'Maître Ass.',        'rahma.meddeb@fst.utm.tn',               '98424172', 1),
('Mehrez',           'Ichrak',      'Maître Ass.',        'ichrak.mehrez@fst.utm.tn',              '27765072', 1),
('Mekki',            'Asma',        'Maître Ass.',        'asma.mekki@fst.utm.tn',                 '44791837', 1),
('Mersni',           'Riheb',       'Expert-Info',        'rihabmersni@gmail.com',                 '22516789', 1),
('Moussa',           'Faouzi',      'Prof.',              'faouzi.moussa@fst.utm.tn',              '55909719', 1),
('Mrabet',           'Hichem',      'Maître Ass.',        'hichem.mrabet@fst.utm.tn',              '99010345', 1),
('Naouai',           'Mohamed',     'Maître Ass.',        'mohamed.naouai@fst.utm.tn',             '55614878', 1),
('Ochi',             'Wejda',       'Ass-Economie',       'wejda.ochi@fst.utm.tn',                 '98386353', 1),
('Omrane',           'Anissa',      'Maître Ass.',        'anissa.omrane@fst.utm.tn',              '98569736', 1),
('Riahi',            'Ines',        'Maître Ass.',        'ines.riahi@fst.utm.tn',                 '22649586', 1),
('Sghaier',          'Nizar',       'Expert-Info',        'nizar.sghaier@fst.utm.tn',              '99017988', 1),
('Souhir',           'Elouaer',     'PES-C2N',            'souhir.elouaer@fst.utm.tn',             '99719510', 1),
('Thabet',           'Chahnez',     'Contractuel-Math',   'thabetchahnez@yahoo.fr',                '52520468', 1),
('Younes',           'Sana',        'Maître Ass.',        'sana.younes@fst.utm.tn',                '94589390', 1),
('Zammeli',          'Saloua',      'Maître Ass.',        'saloua.zammeli@fst.utm.tn',             '95261481', 1),
('Zekri',            'Manel',       'Maître Ass.',        'manel.zekri@fst.utm.tn',                '98277018', 1),
('Zermani',          'Aymen',       'Maître Ass.',        'mohamedaymen.zermani@fst.utm.tn',       '24978202', 1),
('Zouaoui',          'Ramzi',       'Maître Ass.',        'ramzi.zouaoui@fst.utm.tn',              '98699375', 1),
('Zouaoui',          'Sana',        'PES-Info',           'sana.zouaoui@fst.utm.tn',               '96276502', 1);

-- ─────────────────────────────────────────────────────────────
-- 6. CHARGE_HORAIRE
-- ─────────────────────────────────────────────────────────────
INSERT INTO charge_horaire (enseignant_id, annee_univ, volume_horaire)
SELECT id, '2025/2026',
    CASE
        WHEN nom='Abbes'            AND prenom='Haythem'      THEN 192
        WHEN nom='Abbessi'          AND prenom='Faten'        THEN 96
        WHEN nom='Abed'             AND prenom='Rahma'        THEN 128
        WHEN nom='Abidi'            AND prenom='Najib'        THEN 112
        WHEN nom='Agrebi'           AND prenom='Adel'         THEN 96
        WHEN nom='Alaya'            AND prenom='Houda'        THEN 128
        WHEN nom='Amdouni'          AND prenom='Asma'         THEN 128
        WHEN nom='Amdouni'          AND prenom='Naama'        THEN 128
        WHEN nom='Ameur Abid'       AND prenom='Chiheb'       THEN 128
        WHEN nom='Aouadi'           AND prenom='Hamed'        THEN 112
        WHEN nom='Azzabi'           AND prenom='Fares'        THEN 192
        WHEN nom='Ben Azzouz'       AND prenom='Yazid'        THEN 192
        WHEN nom='Ben Dhiaf'        AND prenom='Zouhour'      THEN 128
        WHEN nom='Ben Hassine'      AND prenom='Mohamed Ali'  THEN 128
        WHEN nom='Ben Moussa'       AND prenom='Zied'         THEN 96
        WHEN nom='Ben Othman'       AND prenom='Leila'        THEN 128
        WHEN nom='Bennani'          AND prenom='Taha'         THEN 128
        WHEN nom='Blanco'           AND prenom='Rym'          THEN 96
        WHEN nom='Bouaita'          AND prenom='Mourad'       THEN 96
        WHEN nom='Bouhadda'         AND prenom='Hanene'       THEN 128
        WHEN nom='Boussen'          AND prenom='Sinda'        THEN 128
        WHEN nom='Boussif'          AND prenom='Nouh'         THEN 96
        WHEN nom='Chabchoub'        AND prenom='Sana'         THEN 112
        WHEN nom='Chaouachi Allani' AND prenom='Imen'         THEN 192
        WHEN nom='Dammak'           AND prenom='Nawel'        THEN 96
        WHEN nom='Denden'           AND prenom='Islem'        THEN 96
        WHEN nom='Doggaz'           AND prenom='Narjes'       THEN 128
        WHEN nom='Dridi'            AND prenom='Rim'          THEN 128
        WHEN nom='Echaieb'          AND prenom='Kamel'        THEN 160
        WHEN nom='El Kout'          AND prenom='Ilhem'        THEN 96
        WHEN nom='Ellouze'          AND prenom='Nourhene'     THEN 128
        WHEN nom='Essid'            AND prenom='Chaker'       THEN 128
        WHEN nom='Fayech'           AND prenom='Ines'         THEN 128
        WHEN nom='Fourati'          AND prenom='Hend'         THEN 128
        WHEN nom='Gargouri'         AND prenom='Khalil'       THEN 96
        WHEN nom='Gharbi'           AND prenom='Asma'         THEN 192
        WHEN nom='Gharbi'           AND prenom='Hassen'       THEN 220
        WHEN nom='Gharbi'           AND prenom='Hella'        THEN 192
        WHEN nom='Guesmi'           AND prenom='Soumaya'      THEN 128
        WHEN nom='Hajji'            AND prenom='Imen'         THEN 96
        WHEN nom='Hanana'           AND prenom='Nourhene'     THEN 220
        WHEN nom='Hizem'            AND prenom='Moez'         THEN 128
        WHEN nom='Idi'              AND prenom='Maroua'       THEN 96
        WHEN nom='Jaballah'         AND prenom='Soumaya'      THEN 220
        WHEN nom='Jandoubi'         AND prenom='Amina'        THEN 96
        WHEN nom='Keraani'          AND prenom='Dorsaf'       THEN 160
        WHEN nom='Khaloui'          AND prenom='Safa'         THEN 192
        WHEN nom='Kouki'            AND prenom='Wahiba'       THEN 192
        WHEN nom='Krichi'           AND prenom='Mohsen'       THEN 220
        WHEN nom='Lassoued'         AND prenom='Mohamed'      THEN 96
        WHEN nom='Maalej'           AND prenom='Rania'        THEN 128
        WHEN nom='Majd'             AND prenom='Bellaj'       THEN 96
        WHEN nom='Majdi'            AND prenom='Manel'        THEN 160
        WHEN nom='Maksoud'          AND prenom='Hamdi'        THEN 112
        WHEN nom='Manita'           AND prenom='Ghaith'       THEN 192
        WHEN nom='Masmoudi'         AND prenom='Salma'        THEN 128
        WHEN nom='Mechraoui'        AND prenom='Maryem'       THEN 192
        WHEN nom='Meddeb'           AND prenom='Rahma'        THEN 128
        WHEN nom='Mehrez'           AND prenom='Ichrak'       THEN 128
        WHEN nom='Mekki'            AND prenom='Asma'         THEN 128
        WHEN nom='Mersni'           AND prenom='Riheb'        THEN 192
        WHEN nom='Moussa'           AND prenom='Faouzi'       THEN 192
        WHEN nom='Mrabet'           AND prenom='Hichem'       THEN 128
        WHEN nom='Naouai'           AND prenom='Mohamed'      THEN 128
        WHEN nom='Ochi'             AND prenom='Wejda'        THEN 96
        WHEN nom='Omrane'           AND prenom='Anissa'       THEN 112
        WHEN nom='Riahi'            AND prenom='Ines'         THEN 128
        WHEN nom='Sghaier'          AND prenom='Nizar'        THEN 192
        WHEN nom='Souhir'           AND prenom='Elouaer'      THEN 112
        WHEN nom='Thabet'           AND prenom='Chahnez'      THEN 112
        WHEN nom='Younes'           AND prenom='Sana'         THEN 128
        WHEN nom='Zammeli'          AND prenom='Saloua'       THEN 128
        WHEN nom='Zekri'            AND prenom='Manel'        THEN 128
        WHEN nom='Zermani'          AND prenom='Aymen'        THEN 128
        WHEN nom='Zouaoui'          AND prenom='Ramzi'        THEN 128
        WHEN nom='Zouaoui'          AND prenom='Sana'         THEN 96
        ELSE 128
    END AS volume_horaire
FROM enseignant;

-- ─────────────────────────────────────────────────────────────
-- 7. NIVEAUX
-- ─────────────────────────────────────────────────────────────
INSERT INTO niveau (libelle, annee, type_formation, departement_id) VALUES
('MR',    2, 'INF/IOT', (SELECT id FROM departement WHERE code='DSI')),
('Prépa', 1, 'Intégré', (SELECT id FROM departement WHERE code='DSI')),
('L',     3, 'DSI',     (SELECT id FROM departement WHERE code='DSI'));

-- ─────────────────────────────────────────────────────────────
-- 8. SECTION
-- ─────────────────────────────────────────────────────────────
INSERT INTO section (nom, nb_etudiants, niveau_id) VALUES
('INF/IOT', 15, (SELECT id FROM niveau WHERE libelle='MR' AND type_formation='INF/IOT'));

-- ─────────────────────────────────────────────────────────────
-- 9. GROUPE
-- ─────────────────────────────────────────────────────────────
INSERT INTO groupe (numero, effectif, section_id) VALUES
(1, 15,
  (SELECT s.id
   FROM section s
   JOIN niveau  n ON s.niveau_id = n.id
   WHERE n.libelle='MR' AND n.type_formation='INF/IOT' AND s.nom='INF/IOT')
);

-- ─────────────────────────────────────────────────────────────
-- 10. MATIERES
-- ─────────────────────────────────────────────────────────────
INSERT INTO matiere (code, intitule, a_examen_final, a_ds, duree_examen, duree_ds) VALUES
('MR2-INF-322',  'Optimisation Combinatoire',                   TRUE, TRUE, 120, 60),
('MR2-INF-IOT',  'IDM pour les systèmes complexes Temps Réels', TRUE, TRUE, 120, 60),
('MR2-INF-312',  'Bases de données avancées',                   TRUE, TRUE, 120, 60),
('MR2-INF-331',  'Sécurité IOT',                                TRUE, TRUE, 120, 60),
('MR2-INF-351',  'Blockchain',                                  TRUE, TRUE, 120, 60),
('MR2-INF-FDD',  'Fouilles de Données',                         TRUE, TRUE, 120, 60),
('MR2-INF-352',  'Big Data',                                    TRUE, TRUE, 120, 60),
('MR2-INF-APL',  'Applications et plateforme IoT',              TRUE, TRUE, 120, 60),
('MR2-INF-CHP',  'Calcul de Haute Performance',                 TRUE, TRUE, 120, 60),
('MR2-INF-RIOT', 'Réseaux IoT',                                 TRUE, TRUE, 120, 60);

-- ─────────────────────────────────────────────────────────────
-- 11. SECTION_MATIERE
-- ─────────────────────────────────────────────────────────────
INSERT INTO section_matiere (section_id, matiere_id, a_examen_final, a_ds, duree_examen, duree_ds)
SELECT
    (SELECT s.id
     FROM section s
     JOIN niveau  n ON s.niveau_id = n.id
     WHERE n.libelle='MR' AND n.type_formation='INF/IOT' AND s.nom='INF/IOT'),
    m.id,
    TRUE, TRUE, 120, 60
FROM matiere m
WHERE m.code LIKE 'MR2-INF%';

-- ─────────────────────────────────────────────────────────────
-- 12. ENSEIGNEMENT
-- ─────────────────────────────────────────────────────────────
INSERT INTO enseignement (enseignant_id, matiere_id, type_enseignement, nb_heures, annee_sem)
VALUES
-- Optimisation Combinatoire
((SELECT id FROM enseignant WHERE nom='Manita'      AND prenom='Ghaith'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-322'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Amdouni'     AND prenom='Asma'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-322'), 'TD',    18, '2025/2026-S2'),

-- IDM Temps Réels
((SELECT id FROM enseignant WHERE nom='Zouaoui'     AND prenom='Sana'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-IOT'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Jandoubi'    AND prenom='Amina'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-IOT'), 'TD',    18, '2025/2026-S2'),

-- BD Avancées
((SELECT id FROM enseignant WHERE nom='Zouaoui'     AND prenom='Sana'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-312'), 'TD',    18, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Meddeb'      AND prenom='Rahma'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-312'), 'COURS', 21, '2025/2026-S2'),

-- Sécurité IOT
((SELECT id FROM enseignant WHERE nom='Hizem'       AND prenom='Moez'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-331'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Boussen'     AND prenom='Sinda'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-331'), 'TD',    18, '2025/2026-S2'),

-- Blockchain
((SELECT id FROM enseignant WHERE nom='Masmoudi'    AND prenom='Salma'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-351'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Gargouri'    AND prenom='Khalil'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-351'), 'TD',    18, '2025/2026-S2'),

-- Fouilles de Données
((SELECT id FROM enseignant WHERE nom='Ben Othman'  AND prenom='Leila'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-FDD'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Abbessi'     AND prenom='Faten'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-FDD'), 'TD',    18, '2025/2026-S2'),

-- Big Data
((SELECT id FROM enseignant WHERE nom='Ben Hassine' AND prenom='Mohamed Ali'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-352'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Hajji'       AND prenom='Imen'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-352'), 'TD',    18, '2025/2026-S2'),

-- Applications & Plateforme IoT
((SELECT id FROM enseignant WHERE nom='Boussen'     AND prenom='Sinda'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-APL'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Keraani'     AND prenom='Dorsaf'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-APL'), 'TD',    18, '2025/2026-S2'),

-- Calcul Haute Performance
((SELECT id FROM enseignant WHERE nom='Thabet'      AND prenom='Chahnez'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-CHP'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Riahi'       AND prenom='Ines'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-CHP'), 'TD',    18, '2025/2026-S2'),

-- Réseaux IoT
((SELECT id FROM enseignant WHERE nom='Essid'       AND prenom='Chaker'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-RIOT'), 'COURS', 21, '2025/2026-S2'),
((SELECT id FROM enseignant WHERE nom='Ameur Abid'  AND prenom='Chiheb'),
 (SELECT id FROM matiere    WHERE code='MR2-INF-RIOT'), 'TD',    18, '2025/2026-S2');

-- ─────────────────────────────────────────────────────────────
-- TABLES VOLONTAIREMENT NON REMPLIES
-- ─────────────────────────────────────────────────────────────
-- planification_examen      → à générer par l'algorithme
-- planif_salle              → à générer par l'algorithme
-- surveillance              → à générer par l'algorithme
-- disponibilite_enseignant  → à saisir par les enseignants

COMMIT;

-- ─────────────────────────────────────────────────────────────
-- VÉRIFICATIONS POST-INSERT
-- ─────────────────────────────────────────────────────────────
SELECT 'departement'                      AS table_name, COUNT(*) AS nb FROM departement              UNION ALL
SELECT 'niveau',                                          COUNT(*)        FROM niveau                   UNION ALL
SELECT 'section',                                         COUNT(*)        FROM section                  UNION ALL
SELECT 'groupe',                                          COUNT(*)        FROM groupe                   UNION ALL
SELECT 'salle',                                           COUNT(*)        FROM salle                    UNION ALL
SELECT 'creneau',                                         COUNT(*)        FROM creneau                  UNION ALL
SELECT 'session',                                         COUNT(*)        FROM session                  UNION ALL
SELECT 'enseignant',                                      COUNT(*)        FROM enseignant               UNION ALL
SELECT 'charge_horaire',                                  COUNT(*)        FROM charge_horaire           UNION ALL
SELECT 'matiere',                                         COUNT(*)        FROM matiere                  UNION ALL
SELECT 'section_matiere',                                 COUNT(*)        FROM section_matiere          UNION ALL
SELECT 'enseignement',                                    COUNT(*)        FROM enseignement             UNION ALL
SELECT 'disponibilite_enseignant (vide)',                 COUNT(*)        FROM disponibilite_enseignant UNION ALL
SELECT 'planification_examen (vide)',                     COUNT(*)        FROM planification_examen     UNION ALL
SELECT 'planif_salle (vide)',                             COUNT(*)        FROM planif_salle             UNION ALL
SELECT 'surveillance (vide)',                             COUNT(*)        FROM surveillance
ORDER BY table_name;