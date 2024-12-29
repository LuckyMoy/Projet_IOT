import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv("./api.env")

# Récupérer la clé API
API_KEY = os.getenv('API_KEY')
BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"

def generate_factures_chart(data):
    """Génère une page HTML contenant un camembert Google Charts."""
    # Préparer les données pour le graphique
    chart_data = ""
    dict_data = {}
    for facture in data:
        type_facture = facture[2]  # Colonne `type` dans la table Facture
        montant = facture[4]      # Colonne `montant`
        if not type_facture in dict_data:
            dict_data[type_facture] = 0
        dict_data[type_facture] += montant

    for type_facture in dict_data:
        chart_data += f"['{type_facture}', {dict_data[type_facture]}],"

    # print(chart_data)

    # HTML valide avec Google Charts
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <!-- Charger l'API AJAX de Google Charts -->
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <script type="text/javascript">

        // Charger l'API de visualisation et le package corechart.
        google.charts.load('current', {{'packages':['corechart']}});

        // Définir un callback pour dessiner le graphique après le chargement de l'API
        google.charts.setOnLoadCallback(drawChart);

        // Fonction callback pour créer et afficher le graphique
        function drawChart() {{
            // Créer une table de données pour le graphique
            var data = google.visualization.arrayToDataTable([
                ['Type de Facture', 'Montant'],
                {chart_data}
            ]);

            // Options pour personnaliser le graphique
            var options = {{
                title: 'Repartition des Montants par Type de Facture',
                width: 900,
                height: 500
            }};

            // Instancier le graphique et le dessiner dans le div chart_div
            var chart = new google.visualization.PieChart(document.getElementById('chart_div'));
            chart.draw(data, options);
        }}
        </script>
    </head>
    <body>
        <h1>Repartition des Factures</h1>
        <!-- Div qui contiendra le graphique -->
        <div id="chart_div" style="width: 900px; height: 500px;"></div>
    </body>
    </html>
    """
    return html

def get_weather_forecast(city):
    """Effectue une requête à l'API OpenWeatherMap pour obtenir les prévisions météo."""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # Température en degrés Celsius
        "cnt": 20,           # Nombre de prévisions (5 jours)
        "lang": 'fr'
    }
    try:
        response = requests.get(BASE_WEATHER_URL, params=params)
        response.raise_for_status()
        return response.json()  # Renvoie les données météo au format JSON
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête météo : {e}")
        return None

def generate_weather_page(city, weather_data):
    """Génère une page HTML affichant les prévisions météo."""
    forecast_html = ""
    for item in weather_data["list"]:
        date = item["dt_txt"]
        temperature = item["main"]["temp"]
        description = item["weather"][0]["description"]
        forecast_html += f"<li>{date}: {temperature} C, {description}</li>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Previsions meteo pour {city}</title>
    </head>
    <body>
        <h1>Previsions meteo pour {city} (5 jours)</h1>
        <ul>
            {forecast_html}
        </ul>
    </body>
    </html>
    """
    return html
