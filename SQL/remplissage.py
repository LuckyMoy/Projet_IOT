import sqlite3
import random
from datetime import datetime, timedelta

# ouverture/initialisation de la base de donnée
conn = sqlite3.connect('logement.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# fonction d'insersion de mesures
def ajouter_mesures(capteur_id, nombre_mesures=10):
    for _ in range(nombre_mesures):
        valeur = round(random.uniform(15, 30), 2)  
        date = datetime.now() - timedelta(days=random.randint(0, 30))  # 30 mesures
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO Mesure (capteur_id, valeur, date) VALUES (?, ?, ?)", (capteur_id, valeur, date_str))

# fonction d'insersion de factures
def ajouter_factures(logement_adresse, nombre_factures=4):
    types_factures = ['Électricité', 'Eau', 'Gaz', 'Déchets']
    for _ in range(nombre_factures):
        type_facture = random.choice(types_factures)
        date = datetime.now() - timedelta(days=random.randint(0, 365))  # sur un an
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        montant = round(random.uniform(20, 200), 2)  # montant aléatoire entre 20 et 200 euros
        valeur_consomme = round(random.uniform(50, 500), 2) if type_facture != 'Déchets' else None  # Valeur consommée (null pour Déchets)
        c.execute("INSERT INTO Facture (logement_adresse, type, date, montant, valeur_consomme) VALUES (?, ?, ?, ?, ?)",
                  (logement_adresse, type_facture, date_str, montant, valeur_consomme))

# Ajouter des mesures pour chaque capteur existant
c.execute("SELECT id FROM CapteurActionneur")
capteurs = c.fetchall()
for capteur in capteurs:
    ajouter_mesures(capteur['id'])

# Ajouter des factures pour un logement spécifique
ajouter_factures('123 Rue du Four, Paris')

# fermeture
conn.commit()
conn.close()
