import requests

def get_coordinates(address):
    """
    Récupère les coordonnées géographiques (latitude, longitude) d'une adresse donnée
    en utilisant l'API Nominatim (OpenStreetMap).
    
    :param address: Adresse pour laquelle récupérer les coordonnées.
    :return: Tuple (latitude, longitude) ou None si l'adresse n'est pas trouvée.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,         # Adresse à rechercher
        'format': 'json',     # Format de la réponse
        'addressdetails': 1   # Inclure les détails de l'adresse dans la réponse
    }
    headers = {
        'User-Agent': 'GeoApp (your-email@example.com)'  # Requis par Nominatim
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Vérifie que la requête a réussi
        data = response.json()

        if data:
            # Récupère la latitude et la longitude de la première réponse
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
        else:
            print("Adresse introuvable.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return None
