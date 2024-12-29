import os
import sqlite3, json
from SQL.utils import get_coordinates

def get_available_files(directory="www", base_path=""):
    """
    Renvoie une liste de fichiers disponibles dans le dossier donné et ses sous-dossiers.

    Les fichiers HTML sont retournés sans leur extension.
    Les autres fichiers sont retournés avec leur extension.
    Les fichiers dans les sous-dossiers incluent le chemin relatif.

    :param directory: Chemin du dossier à scanner (par défaut "www").
    :param base_path: Chemin relatif pour inclure les sous-dossiers dans le résultat.
    :return: Liste de noms de fichiers disponibles avec leurs chemins relatifs.
    """
    available_files = []

    # Vérifier si le dossier existe
    if os.path.exists(directory) and os.path.isdir(directory):
        # Parcourir les fichiers et sous-dossiers du répertoire
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)  # Chemin absolu
            relative_path = os.path.join(base_path, filename)  # Chemin relatif

            # Si c'est un dossier, explorer récursivement
            if os.path.isdir(filepath):
                available_files.extend(get_available_files(filepath, relative_path))
            elif os.path.isfile(filepath):
                # Si c'est un fichier HTML, retirer l'extension .html
                if filename.endswith(".html"):
                    available_files.append(os.path.splitext(relative_path)[0])
                else:
                    # Ajouter le fichier avec son chemin relatif et son extension
                    available_files.append(relative_path)
    else:
        print(f"Le dossier {directory} n'existe pas ou n'est pas accessible.")
    
    return available_files

def handle_logements(conn):
    """
    Gère la récupération des logements avec vérification des coordonnées manquantes.
    Si lat/lon est manquant pour un logement, elles sont calculées et ajoutées à la base.
    """
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Récupérez les informations des logements
    c.execute("SELECT adresse, lat, lon, nom, type FROM Logement")
    logements = [dict(row) for row in c.fetchall()]

    # Vérifiez et mettez à jour les coordonnées manquantes
    for logement in logements:
        if logement['lat'] is None or logement['lon'] is None:
            print(f"Coordonnées manquantes pour l'adresse : {logement['adresse']}")
            lat, lon = get_coordinates(logement['adresse'])
            if lat is not None and lon is not None:
                logement['lat'] = lat
                logement['lon'] = lon
                # Mettez à jour la base de données
                c.execute(
                    "UPDATE Logement SET lat = ?, lon = ? WHERE adresse = ?",
                    (lat, lon, logement['adresse'])
                )
                conn.commit()
            else:
                print(f"Impossible de récupérer les coordonnées pour {logement['adresse']}.")

    return logements