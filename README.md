projet_MASTERCAMP_I1
Contexte
Projet de fin d’études réalisé dans le cadre du programme MasterCamps – EFREI Paris. Objectif : développer une application web de gestion urbaine intégrant IA et vision par ordinateur pour améliorer la collecte et le suivi des déchets.

Langages et frameworks : Python (Django, DRF), JavaScript (Vue.js)

Technologies IA : OpenCV, Scikit-learn

Base de données : SQLite

Durée : projet finalisé, prêt à l’emploi

Sujet
L’application permet :

aux citoyens de signaler l’état des poubelles via photos,

aux mairies de suivre en temps réel les signalements,

aux administrateurs d’analyser des statistiques globales.

Une classification automatique (pleine/vide) est réalisée à l’upload grâce à un module d’intelligence artificielle.

Objectifs
Optimiser les tournées de collecte pour les services municipaux

Fournir des statistiques détaillées aux administrations

Favoriser la participation citoyenne via un système de points

Améliorer la propreté urbaine grâce à une gestion intelligente des déchets

Structure du projet
Project_mastercamps/ ├── backend/ # API Django REST │ ├── api/ # Modèles, vues, sérialiseurs │ └── manage.py ├── Front/poubelle-project/ # Frontend Vue.js │ ├── src/components/ # Composants │ ├── src/views/ # Pages │ └── src/services/ # Appels API ├── models/ # Modèles ML ├── ML.py # Module d’IA ├── MC_fusion.py # Analyseur unifié └── requirements.txt # Dépendances Python

Installation
Prérequis

Python 3.8+

Node.js 16+

Git

Étapes rapides (Windows)

1. Cloner le projet
git clone [URL_DU_DEPOT] cd Project_mastercamps

2. Installation automatique
start_project.bat

Lancement manuel

Backend Django

cd backend pip install -r ../requirements.txt python manage.py migrate python manage.py runserver 8000

Frontend Vue.js

cd Front/poubelle-project npm install npm run dev

Types d’utilisateurs
Citoyen : upload d’images, statistiques personnelles, points de participation

Mairie : tableau de bord, suivi des poubelles sur carte, export CSV

Administrateur : gestion utilisateurs, statistiques globales, monitoring

Visualisation
Frontend (Vue.js) : http://localhost:5173

Backend (API Django) : http://localhost:8000

Interface Admin : http://localhost:8000/admin

Tests
Backend
cd backend python manage.py test api

Frontend
cd Front/poubelle-project npm run test

Compétences mobilisées
Développement Fullstack (Django + Vue.js)

IA & Vision par ordinateur (OpenCV, Scikit-learn)

Conception d’API REST

Gestion de bases de données

Déploiement et sécurité applicative

Auteurs
Projet développé par une équipe d’étudiants du programme MasterCamps – EFREI Paris.
