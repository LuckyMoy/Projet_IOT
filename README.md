# README - Projet IOT

## Description
Ce projet est réalisé dans le cadre du module IOT de Polytech Sorbonne (EI - Électronique et Informatique). Il vise à développer un serveur local pour l'interface de gestion et de visualisation des capteurs connectés.

## Prérequis

Avant de lancer le serveur, vous devez installer les dépendances nécessaires. Le projet repose sur **FastAPI**, un framework Python pour créer des APIs web rapides et performantes.

### Installation des dépendances

Assurez-vous d'avoir Python installé sur votre machine. Ensuite, vous pouvez installer les dépendances avec la commande suivante :

```bash
pip install fastapi
```

Vous devrez également installer **uvicorn** pour lancer le serveur local :

```bash
pip install uvicorn
```

## Lancer le serveur

Pour lancer le serveur local, utilisez la commande suivante :

```bash
fastapi run serveur_fast.py
```

Cela démarrera le serveur FastAPI en mode développement et vous pourrez accéder à l'interface via votre navigateur sur l'addresse **http://127.0.0.1:8000**.

## Réponse aux questions posées

### Partie 1.1
Les réponse aux questions 2 et 3 se trouvent dans **sql/logement.sql** directement. Les réponses au autres questions de la partie 1.1 se trouvent à la fin de ce même fichier en commentaires.

### Partie 1.2
La réponse aux questions d cette partie se trouvent dans le fichier **sql/remplissage.py** et **sql/remplissage_plus.py** qui est une version permettant de générer des données plus réalistes.

### Partie 2
La réponse à l'ensemble des execice de cette partie se trouve dans le fichier **/serveur_fast.py** qui a par la suite évolué pour donner suite au projet. **/serveur_rest.py** est une première version qui n'utilise pas *FastAPI*. 

Le fichier **sql/ex2-1.sh** est un script shell qui contient la liste des requettes curl pour remplir la base de donnée pour l'exercice 2.1. 

La source des programmes implémentés sur les cartes *ESP8266* pour l'exercice 2.4 se trouve dans le fichier **ino/capteur_temp/capteur_temp/ino**.

### Partie 3
La partie 3 correspond à l'ensemble du projet et plus précisément au fichier **/serveur_fast.py** et au répertoire **www/**.

## Auteur

Projet réalisé pour le module IOT de Polytech Sorbonne - Formation Électronique et Informatique par UL.