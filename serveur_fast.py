from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import json
from SQL.serv_utils import generate_factures_chart, generate_weather_page, get_weather_forecast
from www.utils import handle_logements

app = FastAPI()

DATABASE = "SQL/logement.db"
WWW_DIR = Path("www")


# BaseModel pour les réponses structurées de la bdd
class Logement(BaseModel):
    adresse: str
    lat: float | None
    lon: float | None
    tel: str
    IP: str

# Modèle Pydantic pour valider le JSON envoyé par l'esp
class CapteurData(BaseModel):
    id_capteur: int
    ref_comm: str
    value: float


# Utility function to interact with the SQLite database 
# Source GPT
def get_db_connection():
    """
    Crée et retourne une connexion SQLite avec un row_factory pour des dictionnaires.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """
    Servir la page d'accueil.
    """
    home_path = WWW_DIR / "home.html"
    if not home_path.exists():
        raise HTTPException(status_code=404, detail="Page d'accueil introuvable.")
    return FileResponse(home_path)


@app.get("/api/logements", response_class=JSONResponse)
async def get_logements():
    """
    Récupérer la liste des logements.
    """
    conn = get_db_connection()
    logements = handle_logements(get_db_connection())
    conn.close()
    return [dict(logement) for logement in logements]


@app.get("/factures-chart", response_class=HTMLResponse)
async def factures_chart():
    """
    Générer un graphique des factures.
    """
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM Facture").fetchall()
    conn.close()

    if not data:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible pour les factures.")

    return generate_factures_chart(data)


@app.get("/weather", response_class=HTMLResponse)
async def weather(city: str = Query(default="Paris")):
    """
    Afficher la météo pour une ville.
    """
    weather_data = get_weather_forecast(city)
    if not weather_data:
        raise HTTPException(status_code=500, detail="Impossible de récupérer les données météo.")
    return generate_weather_page(city, weather_data)

@app.get("/api/logements", response_class=JSONResponse)
async def get_capteurs():
    """
    Récupérer la liste des logements .
    """
    conn = get_db_connection()
    try:
        
        query_pieces = """
        SELECT adresse, tel, IP, date_insertion, lat, lon, nom, type
        FROM Logement
        """
        logements = conn.execute(query_pieces).fetchall()
        # Vérification si des pièces ont été trouvées
        if not logements:
            raise HTTPException(status_code=404, detail="Aucun logement trouvé")
        
        return logements

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

@app.get("/api/capteurs", response_class=JSONResponse)
async def get_capteurs(
    adresse: str | None = Query(None, description="Adresse du logement"),
    piece_nom: str | None = Query(None, description="Nom de la pièce (optionnel)")
):
    """
    Récupérer les capteurs d'un logement en fonction de l'adresse. Si une pièce est spécifiée,
    retourne uniquement les capteurs de cette pièce, sinon concatène les capteurs de toutes les pièces.
    """
    conn = get_db_connection()
    try:
        if adresse and piece_nom:
            query_pieces = """
            SELECT id, nom
            FROM Piece
            WHERE logement_adresse = ? AND nom = ?
            """
            pieces = conn.execute(query_pieces, (adresse, piece_nom)).fetchall()
        elif adresse:
            query_pieces = """
            SELECT id, nom
            FROM Piece
            WHERE logement_adresse = ?
            """
            pieces = conn.execute(query_pieces, (adresse,)).fetchall()
        else:
            query_pieces = """
            SELECT id, nom
            FROM Piece
            """
            pieces = conn.execute(query_pieces).fetchall()
        # Vérification si des pièces ont été trouvées
        if not pieces:
            raise HTTPException(status_code=404, detail="Aucune pièce trouvée pour cette adresse ou cette pièce.")

        # récupérer les capteurs associés à ces pièces
        capteurs = []
        query_capteurs = """
        SELECT 
            C.id AS id,
            C.type AS type,
            C.ref_comm AS ref_comm,
            C.port AS port,
            C.date_insertion AS date_insertion,
            C.derniere_mesure AS derniere_mesure,
            P.nom AS piece_nom,
            P.id AS piece_id
        FROM CapteurActionneur C
        JOIN Piece P ON C.piece_id = P.id
        WHERE C.piece_id = ?
        """
        for piece in pieces:
            capteurs_piece = conn.execute(query_capteurs, (piece["id"],)).fetchall()
            capteurs.extend([dict(capteur) for capteur in capteurs_piece])

        # vérif la dernière mesure pour chaque capteur et y ajouter le champ 'active'
        query_last_measure = """
        SELECT date
        FROM Mesure
        WHERE capteur_id = ?
        ORDER BY date DESC
        LIMIT 1
        """

        for capteur in capteurs:
            if capteur["derniere_mesure"] == None:
                last_measure = conn.execute(query_last_measure, (capteur["id"],)).fetchone()["date"]
                conn.execute(
                    "UPDATE CapteurActionneur SET derniere_mesure = ? WHERE id = ?",
                    (last_measure, capteur["id"],)
                )
                conn.commit()
            else:
                last_measure = capteur["derniere_mesure"]
            if last_measure:
                last_measure_time = datetime.strptime(last_measure, "%Y-%m-%d %H:%M:%S")
                one_hour_ago = datetime.now() - timedelta(hours=2)
                capteur["active"] = last_measure_time >= one_hour_ago
            else:
                capteur["active"] = False

        # verif si des capteurs ont été trouvés
        if not capteurs:
            raise HTTPException(status_code=404, detail="Aucun capteur trouvé pour les pièces spécifiées.")
        return capteurs

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

@app.get("/api/mesures/{capteur_id}", response_class=JSONResponse)
async def get_mesures(
    capteur_id: int,
    period: str = Query("1"),  # Par défaut, 1 jour
    reference_date: str = Query(datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))  # Par défaut, l'heure actuelle
):
    """
    Récupère les mesures pour un capteur spécifique, filtrées par une période définie et une plage horaire.
    """
    conn = get_db_connection()

    try:
        # Calculer la plage de dates : date_start et date_end
        reference_datetime = datetime.strptime(reference_date, "%Y-%m-%dT%H:%M:%S")
        if period == "1h":
            date_start = reference_datetime - timedelta(hours=1)
        elif period == "3h":
            date_start = reference_datetime - timedelta(hours=3)
        elif period == "12h":
            date_start = reference_datetime - timedelta(hours=12)
        elif period.isdigit():  # Périodes en jours
            date_start = reference_datetime - timedelta(days=int(period))
        elif period == "all":
            date_start = None
        else:
            raise HTTPException(status_code=400, detail="Période invalide.")
        date_end = reference_datetime

        # Construire la requête SQL avec bornes
        if date_start:
            query = """
                SELECT date AS d, valeur AS v
                FROM Mesure
                WHERE capteur_id = ? AND datetime(date) BETWEEN ? AND ?
                ORDER BY date ASC
            """
            params = (capteur_id, date_start.strftime("%Y-%m-%d %H:%M:%S"), date_end.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            query = """
                SELECT date AS d, valeur AS v
                FROM Mesure
                WHERE capteur_id = ?
                ORDER BY date ASC
            """
            params = (capteur_id,)

        # Exécuter la requête
        mesures = conn.execute(query, params).fetchall()

        # Si aucune mesure n'est trouvée, retourner une erreur 404
        if not mesures:
            raise HTTPException(status_code=404, detail="Aucune mesure trouvée pour ce capteur dans la plage spécifiée.")

        return [dict(mesure) for mesure in mesures]
    except sqlite3.Error as e:
        print("Erreur DB :", e)
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()




@app.post("/add-logement", response_class=JSONResponse)
async def add_logement(logement: Logement):
    """
    Ajouter un logement dans la base de données.
    """
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO Logement (adresse, lat, lon, tel, IP) VALUES (?, ?, ?, ?, ?)",
            (logement.adresse, logement.lat, logement.lon, logement.tel, logement.IP),
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'insertion : {str(e)}")
    conn.close()
    return {"message": "Logement ajouté avec succès"}


@app.get("/api/weather-json", response_class=JSONResponse)
async def get_weather_json(city: str = Query(default="Paris")):
    """
    Retourner la météo sous forme JSON.
    """
    weather_data = get_weather_forecast(city)
    if not weather_data:
        raise HTTPException(status_code=500, detail="Impossible de récupérer les données météo.")
    return weather_data

@app.post("/api/capteur", response_class=JSONResponse)
async def post_capteur_mesure(data: CapteurData):
    """
    Ajoute une mesure envoyée par un capteur à la base de données.
    """
    print("recu d'un capteur:", data)
    conn = get_db_connection()
    try:
        # Vérifiez que le capteur existe dans la base
        capteur = conn.execute(
            "SELECT id FROM CapteurActionneur WHERE id = ? AND ref_comm = ?",
            (data.id_capteur, data.ref_comm)
        ).fetchone()

        if not capteur:
            raise HTTPException(status_code=404, detail="Capteur non trouvé.")

        # Insérer les mesures dans la table
        conn.execute(
            "INSERT INTO Mesure (capteur_id, valeur, date) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (data.id_capteur, data.value)
        )
        conn.execute(
            "UPDATE CapteurActionneur SET derniere_mesure = CURRENT_TIMESTAMP WHERE id = ?",
            (capteur["id"],)
        )
        conn.commit()

        conn.commit()
        return {"message": "Mesure ajoutée avec succès", "id_capteur": data.id_capteur}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")
    finally:
        conn.close()

@app.get("/{file_path:path}")
async def serve_static(file_path: str):
    """
    Servir les fichiers statiques depuis le dossier www
    """
    if not '.' in file_path:
        file_path += '.html'
    file = WWW_DIR / file_path
    if file.exists() and file.is_file():
        return FileResponse(file)
    raise HTTPException(status_code=404, detail=f"Fichier {file_path} introuvable.")