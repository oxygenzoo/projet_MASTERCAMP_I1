@echo off
echo "==================================================================="
echo "           Configuration et lancement de l'API ML intégrée"
echo "==================================================================="

echo.
echo "Étape 1: Installation des dépendances..."
pip install -r ..\requirements.txt

echo.
echo "Étape 2: Configuration de l'intégration ML..."
python setup_ml_integration.py

echo.
echo "Étape 3: Démarrage du serveur Django (API ML)..."
python manage.py runserver 0.0.0.0:8001

echo.
echo "Le serveur est arrêté."
