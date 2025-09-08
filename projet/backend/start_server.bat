@echo off
echo  Demarrage du serveur MasterCamps...
echo.

cd /d "%~dp0"

if not exist "manage.py" (
    echo  Erreur: manage.py non trouvé. Assurez-vous d'être dans le répertoire backend.
    pause
    exit /b 1
)

echo  Activation de l'environnement virtuel...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo  Environnement virtuel activé
) else (
    echo   Environnement virtuel non trouvé, utilisation de Python système
)

echo  Installation/Vérification des dépendances...
python -m pip install --upgrade pip
python -m pip install -r ..\requirements.txt

echo  Vérification des migrations...
python manage.py migrate

echo.
echo  Démarrage du serveur Django...
echo  Interface d'upload disponible à: http://localhost:8000/upload
echo  API endpoint pour upload ZIP: http://localhost:8000/api/batch-upload-zip/
echo  Dashboard: http://localhost:8000/api/dashboard-stats/
echo.
echo  Pour arrêter le serveur, appuyez sur Ctrl+C
echo.

python manage.py runserver 8000

pause
