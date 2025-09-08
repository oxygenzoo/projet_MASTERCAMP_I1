"""
Script pour appliquer les migrations de base de données
et configurer l'intégration ML
"""

import os
import sys
import subprocess
import django

# Ajouter le répertoire du projet au chemin Python
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastercamps.settings')
django.setup()

def run_migrations():
    """Exécute les migrations Django"""
    print("="*50)
    print("Exécution des migrations Django...")
    
    try:
        # Créer les fichiers de migration
        subprocess.run([sys.executable, "manage.py", "makemigrations", "api"], check=True)
        
        # Appliquer les migrations
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        
        print("✓ Migrations appliquées avec succès")
        print("="*50)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erreur lors des migrations: {e}")
        print("="*50)
        return False

def setup_ml_integration():
    """Configure l'intégration ML"""
    print("="*50)
    print("Configuration de l'intégration ML...")
    
    # Importer après configuration de Django
    from api.ml_integration import ml_service
    
    # Créer le répertoire des modèles s'il n'existe pas
    models_dir = os.path.join(project_root, 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"✓ Répertoire des modèles créé: {models_dir}")
    
    # Vérifier si le modèle ML est chargé
    if ml_service.model is not None:
        print("✓ Modèle ML existant chargé")
    else:
        print("ℹ Aucun modèle ML n'a été trouvé - il sera créé lors de l'entraînement")
    
    print("="*50)

def process_pending_images():
    """Traite les images en attente"""
    print("="*50)
    print("Traitement des images en attente...")
    
    # Importer après configuration de Django
    from api.ml_integration import ml_service
    from api.models import Image
    from django.db.models import Q
    
    # Compter les images en attente
    pending_count = Image.objects.filter(
        Q(classification_auto__isnull=True) | 
        Q(metadata__isnull=True)
    ).count()
    
    print(f"ℹ {pending_count} images en attente de traitement")
    
    if pending_count > 0:
        # Demander confirmation pour traiter les images
        choice = input("Voulez-vous traiter ces images maintenant? (o/n): ")
        
        if choice.lower() in ['o', 'oui', 'y', 'yes']:
            print("Traitement en cours...")
            
            # Limiter à 100 images pour cette exécution
            processed, errors = ml_service.process_pending_images(limit=100)
            
            print(f"✓ {processed} images traitées, {errors} erreurs")
        else:
            print("ℹ Traitement ignoré")
    
    print("="*50)

def main():
    """Point d'entrée principal"""
    print("\nINTÉGRATION ML - SCRIPT DE CONFIGURATION")
    print("="*50)
    
    # Exécuter les migrations
    migrations_ok = run_migrations()
    
    if migrations_ok:
        # Configurer l'intégration ML
        setup_ml_integration()
        
        # Traiter les images en attente
        process_pending_images()
        
        print("\nConfiguration terminée!")
        print(f"Vous pouvez maintenant accéder à l'API ML via:")
        print(f"  - http://localhost:8001/api/ml/analyze-image/")
        print(f"  - http://localhost:8001/api/ml/create-batch/")
        print(f"  - http://localhost:8001/api/ml/batch-list/")
        print("="*50)
    else:
        print("\n✗ Erreur: La configuration n'a pas pu être terminée à cause d'erreurs lors des migrations")

if __name__ == "__main__":
    main()
