#!/usr/bin/env python3
"""
Script pour démarrer le serveur Django et ouvrir l'interface d'upload
"""
import os
import sys
import webbrowser
import time
import subprocess
from pathlib import Path

def main():
    print(" Démarrage du serveur MasterCamps...")
    
    # Vérifier que nous sommes dans le bon répertoire
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    if not Path('manage.py').exists():
        print(" Erreur: manage.py non trouvé. Assurez-vous d'être dans le répertoire backend.")
        return
    
    # Déterminer l'exécutable Python
    python_exe = sys.executable
    venv_python = backend_dir / 'venv' / 'Scripts' / 'python.exe'
    
    if venv_python.exists():
        python_exe = str(venv_python)
        print(" Utilisation de l'environnement virtuel")
    else:
        print("  Environnement virtuel non trouvé, utilisation de Python système")
    
    print(" Installation/Vérification des dépendances...")
    try:
        subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([python_exe, '-m', 'pip', 'install', '-r', '../requirements.txt'], check=True)
        print(" Dépendances installées/vérifiées")
    except subprocess.CalledProcessError:
        print("  Erreur lors de l'installation des dépendances, mais on continue...")
    
    print(" Vérification des migrations...")
    try:
        # Appliquer les migrations
        subprocess.run([python_exe, 'manage.py', 'migrate'], check=True)
        print(" Migrations appliquées avec succès")
    except subprocess.CalledProcessError:
        print("  Erreur lors des migrations, mais on continue...")
    
    print(" Démarrage du serveur Django...")
    print(" Interface d'upload disponible à: http://localhost:8000/upload")
    print(" API endpoint pour upload ZIP: http://localhost:8000/api/batch-upload-zip/")
    print(" Dashboard: http://localhost:8000/api/dashboard-stats/")
    print("\n Pour arrêter le serveur, appuyez sur Ctrl+C")
    
    # Démarrer le serveur Django
    try:
        subprocess.run([python_exe, 'manage.py', 'runserver', '8000'])
    except KeyboardInterrupt:
        print("\n Serveur arrêté. Au revoir!")

if __name__ == "__main__":
    main()
