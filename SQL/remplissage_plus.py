import sqlite3
import random
from datetime import datetime, timedelta

# Connexion à la base de données
db_path = 'logement.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()


def insert_logements():
    """
    Insère 3 logements avec des adresses réelles et des informations de base.
    """
    logements = [
        ("12 Avenue de Paris, Versailles", "0102030406", "192.168.1.11", "Maison", "home"),
        ("4 Place Jussieu, Paris", "0102030407", "192.168.1.12", "Polytech", "public"),
        ("1 Rue Thomas Edison, Evry", "0102030408", "192.168.1.13", "Usine", "company"),
    ]
    for adresse, tel, ip, nom, type in logements:
        c.execute("INSERT INTO Logement (adresse, tel, IP, nom, type) VALUES (?, ?, ?, ?, ?)", (adresse, tel, ip, nom, type))


def insert_pieces():
    """
    Insère des pièces pour chaque logement avec des noms réalistes.
    """
    logements = c.execute("SELECT adresse FROM Logement").fetchall()
    pieces = [
        ["Salon", "Cuisine", "Chambre 1", "Salle de bain"],
        ["Salon", "Cuisine", "Chambre", "Bureau"],
        ["Atelier", "Entrepôt", "Bureau", "Salle de réunion"]
    ]

    for idx, logement in enumerate(logements):
        logement_adresse = logement[0]
        for piece_idx, piece in enumerate(pieces[idx]):
            c.execute(
                "INSERT INTO Piece (logement_adresse, nom, x, y, z) VALUES (?, ?, ?, ?, ?)",
                (logement_adresse, piece, piece_idx % 2, piece_idx // 2, 0)
            )


def insert_capteurs():
    """
    Insère des capteurs variés pour chaque pièce de chaque logement.
    """
    capteur_types = ["Luminosité", "Température", "Eau"]
    pieces = c.execute("SELECT id FROM Piece").fetchall()

    for piece_id in pieces:
        num_capteurs = random.randint(1, 3)  # Chaque pièce a entre 1 et 3 capteurs
        capteurs = random.sample(capteur_types, num_capteurs)
        for capteur_type in capteurs:
            c.execute(
                "INSERT INTO CapteurActionneur (type, ref_comm, piece_id, port) VALUES (?, ?, ?, ?)",
                (capteur_type, f"{capteur_type[:4].upper()}-{random.randint(1000, 9999)}", piece_id[0], f"COM{random.randint(1, 10)}")
            )


def insert_mesures():
    """
    Insère une mesure par minute pour chaque capteur sur une période d'un mois.
    Les mesures suivent des modèles réalistes et incluent des variations aléatoires.
    """
    capteurs = c.execute("SELECT id, type, piece_id FROM CapteurActionneur").fetchall()
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    for capteur_id, capteur_type, piece_id in capteurs:
        current_date = start_date

        # Récupérer des informations contextuelles sur le logement
        logement_adresse = c.execute(
            "SELECT logement_adresse FROM Piece WHERE id = ?", (piece_id,)
        ).fetchone()[0]
        is_usine = "Industrielle" in logement_adresse

        while current_date <= end_date:
            # Générer une mesure réaliste en fonction du type de capteur
            if capteur_type == "Luminosité":
                # Simuler une luminosité variable avec un cycle jour/nuit
                hour = current_date.hour
                if 6 <= hour <= 18:  # Journée
                    valeur = random.uniform(500, 1000)  # Journée ensoleillée
                    if random.random() < 0.3:  # 30% de chances de nuages
                        valeur *= random.uniform(0.5, 0.8)
                else:  # Nuit
                    valeur = random.uniform(0, 10)  # Luminosité faible
            elif capteur_type == "Température":
                # Simuler une température avec un cycle jour/nuit
                hour = current_date.hour
                if 6 <= hour <= 18:  # Journée
                    valeur = random.uniform(20, 25) if not is_usine else random.uniform(18, 30)
                else:  # Nuit
                    valeur = random.uniform(15, 20) if not is_usine else random.uniform(10, 18)
                # Ajouter une variation aléatoire
                valeur += random.uniform(-1, 1)
            elif capteur_type == "Eau":
                # Simuler une consommation d'eau (périodes d'activité et d'inactivité)
                hour = current_date.hour
                if is_usine:
                    valeur = random.uniform(50, 100)  # Consommation constante élevée
                else:
                    if 6 <= hour <= 8 or 18 <= hour <= 21:  # Périodes d'activité
                        valeur = random.uniform(10, 50)
                    else:  # Périodes calmes
                        valeur = random.uniform(0, 5)
            else:
                valeur = random.uniform(0, 100)  # Valeur par défaut

            # Insérer la mesure dans la base de données
            c.execute(
                "INSERT INTO Mesure (capteur_id, valeur, date) VALUES (?, ?, ?)",
                (capteur_id, round(valeur, 2), current_date.strftime('%Y-%m-%d %H:%M:%S'))
            )

            # Avancer d'une minute
            current_date += timedelta(minutes=1)

        print(f"Mesures insérées pour le capteur {capteur_id} ({capteur_type}).")


def main():
    insert_logements()
    insert_pieces()
    insert_capteurs()
    insert_mesures()
    conn.commit()
    print("Base de données remplie avec succès !")


if __name__ == "__main__":
    main()
    conn.close()
