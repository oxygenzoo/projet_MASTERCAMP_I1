@echo off
echo ===========================================
echo   DEMARRAGE DU PROJET MASTERCAMPS WDP
echo ===========================================

echo.
echo Verification des dependances...

REM Verifier si Python est installe
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

REM Verifier si Node.js est installe
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Node.js n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

echo Python et Node.js detectes.

echo.
echo ===========================================
echo   INSTALLATION DES DEPENDANCES
echo ===========================================

echo.
echo Installation des dependances Python (Backend)...
cd backend
pip install django djangorestframework django-cors-headers Pillow
pip install ultralytics
pip install -r ..\requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Echec de l'installation des dependances Python
    pause
    exit /b 1
)

echo.
echo Verification et creation des modeles ML...
if not exist "..\models\waste_classifier_model.joblib" (
    echo Creation du modele scikit-learn...
    python -c "import joblib; from sklearn.ensemble import RandomForestClassifier; import os; os.makedirs('../models', exist_ok=True); model = RandomForestClassifier(); joblib.dump(model, '../models/waste_classifier_model.joblib'); print('Modele scikit-learn cree')"
)

if not exist "..\runs\detect\train_yolo11\weights\best.pt" (
    echo Creation du modele YOLO...
    python -c "from ultralytics import YOLO; import os; os.makedirs('../runs/detect/train_yolo11/weights', exist_ok=True); model = YOLO('yolo11n.pt'); model.save('../runs/detect/train_yolo11/weights/best.pt'); print('Modele YOLO cree')"
)

echo.
echo Installation des dependances Node.js (Frontend)...
cd ..\Front\poubelle-project
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Echec de l'installation des dependances Node.js
    pause
    exit /b 1
)

echo.
echo ===========================================
echo   DEMARRAGE DES SERVEURS
echo ===========================================

echo.
echo Demarrage du serveur Django (Backend) sur le port 8000...
cd ..\..\backend
start "Django Backend" cmd /c "python manage.py runserver 8000"

echo.
echo Demarrage du serveur ML API sur le port 8001...
cd ..
start "ML API Server" cmd /c "cd backend && python manage.py runserver 8001"

echo.
echo Attente de 3 secondes pour le demarrage des backends...
timeout /t 3 /nobreak >nul

echo.
echo Demarrage du serveur Vite (Frontend)...
cd Front\poubelle-project
start "Vite Frontend" cmd /c "npm run dev"

echo.
echo ===========================================
echo   SERVEURS DEMARES
echo ===========================================
echo.
echo Backend Django      : http://localhost:8000
echo API ML              : http://localhost:8001
echo Frontend Vue        : http://localhost:5173 (ou 5174 si 5173 est occupé)
echo.
echo API Endpoints principaux:
echo - Upload interface  : http://localhost:8000/api/upload/
echo - Upload ZIP batch  : http://localhost:8000/api/batch-upload-zip/
echo - Dashboard stats   : http://localhost:8000/api/dashboard-stats/  [!] NOTEZ LE TIRET (-)
echo.
echo API ML endpoints:
echo - Analyse d'image   : http://localhost:8001/api/ml/analyze-image/
echo - Création de batch : http://localhost:8001/api/ml/create-batch/
echo - Liste des batches : http://localhost:8001/api/ml/batch-list/
echo.
echo Traitement par lot:
echo - Via Python script : python run_batch_analysis.py
echo - Via API REST      : POST http://localhost:8001/api/ml/create-batch/
echo.
echo Les serveurs sont en cours d'execution.
echo Fermez cette fenetre pour arreter le projet.
echo.
echo ===========================================
echo   GUIDE D'UTILISATION RAPIDE
echo ===========================================
echo.
echo 1. ENVOI D'IMAGES:
echo    - Interface Web: http://localhost:5173
echo    - API Upload: http://localhost:8000/api/upload/
echo.
echo 2. TRAITEMENT PAR LOT:
echo    - Utilisez l'interface web pour télécharger plusieurs images
echo    - OU exécutez: python run_batch_analysis.py (interface graphique)
echo    - OU API: POST http://localhost:8001/api/ml/create-batch/
echo.
echo 3. VISUALISATION:
echo    - Dashboard: http://localhost:5173/dashboard
echo    - API Stats: http://localhost:8000/api/dashboard-stats/
echo.
echo ===========================================

REM Garder la fenetre ouverte
pause
