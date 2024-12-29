curl -X POST "http://localhost:8888/Mesure/?capteur_id=1&valeur=22.5&date=2024-11-01%2010:30:00"
curl -X POST "http://localhost:8888/Mesure/?capteur_id=1&valeur=23.8&date=2024-11-10%2014:45:00"
curl -X POST "http://localhost:8888/Mesure/?capteur_id=2&valeur=300.0&date=2024-11-05%2009:00:00"
curl -X POST "http://localhost:8888/Mesure/?capteur_id=2&valeur=320.5&date=2024-11-15%2012:15:00"

curl -X POST "http://localhost:8888/Facture/?logement_adresse=123%20Rue%20du%20Four,%20Paris&type=Electricite&date=2024-10-01%2012:00:00&montant=150.75&valeur_consomme=400"
curl -X POST "http://localhost:8888/Facture/?logement_adresse=123%20Rue%20du%20Four,%20Paris&type=Eau&date=2024-10-15%2015:00:00&montant=45.50&valeur_consomme=50"
curl -X POST "http://localhost:8888/Facture/?logement_adresse=123%20Rue%20du%20Four,%20Paris&type=Dechets&date=2024-10-20%2010:00:00&montant=30.00&valeur_consomme="
curl -X POST "http://localhost:8888/Facture/?logement_adresse=123%20Rue%20du%20Four,%20Paris&type=Gaz&date=2024-10-25%2018:00:00&montant=100.25&valeur_consomme=150"

curl -X POST "http://localhost:8888/Logement/?adresse=4%20Place%20Jussieu&tel=0100000000&IP=127.0.0.1"
