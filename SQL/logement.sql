-- Question 2: Suppression des tables existantes
-- On commence par supprimer les tables pour eviter les conflits lors de la creation.
DROP TABLE IF EXISTS Mesure;
DROP TABLE IF EXISTS CapteurActionneur;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS Facture;
DROP TABLE IF EXISTS Logement;

-- Question 3: Creation des tables avec des commentaires explicatifs

-- Table Logement : represente un logement, identifie par son adresse, son telephone, son IP et une date d'insertion.
CREATE TABLE Logement (
    adresse TEXT PRIMARY KEY,        -- Identifiant unique pour chaque logement (adresse)
    tel TEXT NOT NULL,               -- Numero de telephone du logement
    IP TEXT NOT NULL,                -- Adresse IP du logement
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date d'insertion dans la base
    lat TEXT DEFAULT NULL,
    lon TEXTDEFAULT NULL,
    nom TEXT DEFAULT NULL,
    type TEXT DEFAULT NULL
);

-- Table Piece : represente une pièce dans un logement, localisee par ses coordonnees 3D dans une matrice.
CREATE TABLE Piece (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique de la pièce
    logement_adresse TEXT NOT NULL,        -- Adresse du logement auquel appartient la pièce
    nom TEXT,
    x INTEGER,                             -- Coordonnee x de la pièce
    y INTEGER,                             -- Coordonnee y de la pièce
    z INTEGER,                             -- Coordonnee z de la pièce
    FOREIGN KEY (logement_adresse) REFERENCES Logement(adresse) ON DELETE CASCADE
);

-- Table CapteurActionneur : represente un capteur ou un actionneur situe dans une pièce.
CREATE TABLE CapteurActionneur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                   -- Identifiant unique du capteur/actionneur
    type TEXT NOT NULL,                                     -- Type de capteur/actionneur (temperature, electricite, etc.)
    ref_comm TEXT NOT NULL,                                 -- Reference commerciale du capteur/actionneur
    piece_id INTEGER NOT NULL,                              -- Reference à la pièce où se situe le capteur/actionneur
    port TEXT NOT NULL,                                     -- Port de communication avec le serveur
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- Date d'insertion dans la base
    derniere_mesure TIMESTAMP DEFAULT NULL,     -- Date d'insertion dans la base
    FOREIGN KEY (piece_id) REFERENCES Piece(id) ON DELETE CASCADE
);

-- Table Mesure : represente une mesure prise par un capteur/actionneur à un moment donne.
CREATE TABLE Mesure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                   -- Identifiant unique de la mesure
    capteur_id INTEGER NOT NULL,                            -- Reference au capteur/actionneur ayant pris la mesure
    valeur REAL NOT NULL,                                   -- Valeur de la mesure (temperature, consommation, etc.)
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date d'insertion de la mesure
    FOREIGN KEY (capteur_id) REFERENCES CapteurActionneur(id) ON DELETE CASCADE
);

-- Table Facture : represente une facture liee à un logement avec le type de ressource consommee.
CREATE TABLE Facture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique de la facture
    logement_adresse TEXT NOT NULL,        -- Adresse du logement auquel est rattachee la facture
    type TEXT NOT NULL,                    -- Type de facture (eau, electricite, dechets, etc.)
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date de la facture
    montant REAL NOT NULL,                 -- Montant de la facture
    valeur_consomme REAL,                  -- Valeur consommee (quantite d'eau, d'electricite, etc.)
    FOREIGN KEY (logement_adresse) REFERENCES Logement(adresse) ON DELETE CASCADE
);

-- Question 4: Insertion d'un logement et de 4 pièces

-- Insertion d'un logement
-- INSERT INTO Logement (adresse, tel, IP) 
-- VALUES ('123 Rue du Four, Paris', '0102030405', '192.168.1.10');

-- -- Insertion de 4 pièces pour le logement avec l'adresse '123 Rue du Four, Paris'
-- INSERT INTO Piece (logement_adresse, x, y, z) VALUES ('123 Rue du Four, Paris', 0, 0, 0);
-- INSERT INTO Piece (logement_adresse, x, y, z) VALUES ('123 Rue du Four, Paris', 1, 0, 0);
-- INSERT INTO Piece (logement_adresse, x, y, z) VALUES ('123 Rue du Four, Paris', 0, 1, 0);
-- INSERT INTO Piece (logement_adresse, x, y, z) VALUES ('123 Rue du Four, Paris', 1, 1, 0);

-- -- Question 5: Creation de types de capteurs/actionneurs

-- -- Insertion de types de capteurs/actionneurs
-- INSERT INTO CapteurActionneur (type, ref_comm, piece_id, port) VALUES ('Temperature', 'TEMP-1234', 1, 'COM1');
-- INSERT INTO CapteurActionneur (type, ref_comm, piece_id, port) VALUES ('Luminosite', 'LUMI-5678', 2, 'COM2');
-- INSERT INTO CapteurActionneur (type, ref_comm, piece_id, port) VALUES ('Consommation Electrique', 'ELEC-9101', 3, 'COM3');
-- INSERT INTO CapteurActionneur (type, ref_comm, piece_id, port) VALUES ('Niveau d Eau', 'EAU-1121', 4, 'COM4');

-- -- Question 6: Creation de capteurs/actionneurs specifiques

-- -- Insertion de capteurs/actionneurs dans des pièces specifiques
-- -- Capteur de temperature dans la pièce 1
-- INSERT INTO CapteurActionneur (type, ref_comm, piece_id, port) VALUES ('Temperature', 'TEMP-1234', 1, 'COM1');

-- -- Capteur de luminosite dans la pièce 2
-- INSERT INTO CapteurActionneur (type, ref_comm, piece_id, port) VALUES ('Luminosite', 'LUMI-5678', 2, 'COM2');

-- -- Question 7: Creation de mesures pour chaque capteur/actionneur

-- -- Insertion de mesures pour le capteur de temperature (capteur ID 1)
-- INSERT INTO Mesure (capteur_id, valeur, date) VALUES (1, 22.5, CURRENT_TIMESTAMP);
-- INSERT INTO Mesure (capteur_id, valeur, date) VALUES (1, 23.0, CURRENT_TIMESTAMP);

-- -- Insertion de mesures pour le capteur de luminosite (capteur ID 2)
-- INSERT INTO Mesure (capteur_id, valeur, date) VALUES (2, 300, CURRENT_TIMESTAMP);
-- INSERT INTO Mesure (capteur_id, valeur, date) VALUES (2, 320, CURRENT_TIMESTAMP);

-- -- Question 8: Creation de factures

-- -- Insertion de factures pour le logement avec l'adresse '123 Rue du Four, Paris'
-- INSERT INTO Facture (logement_adresse, type, date, montant, valeur_consomme) VALUES ('123 Rue du Four, Paris', 'Electricite', CURRENT_TIMESTAMP, 120.50, 350);
-- INSERT INTO Facture (logement_adresse, type, date, montant, valeur_consomme) VALUES ('123 Rue du Four, Paris', 'Eau', CURRENT_TIMESTAMP, 30.00, 20);
-- INSERT INTO Facture (logement_adresse, type, date, montant, valeur_consomme) VALUES ('123 Rue du Four, Paris', 'Dechets', CURRENT_TIMESTAMP, 15.00, NULL);
-- INSERT INTO Facture (logement_adresse, type, date, montant, valeur_consomme) VALUES ('123 Rue du Four, Paris', 'Gaz', CURRENT_TIMESTAMP, 45.75, 100);

