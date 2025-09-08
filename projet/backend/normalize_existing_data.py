"""
Script pour normaliser les données existantes (ville et quartier)
"""
import os
import django
import sys

# Configurer l'environnement Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastercamps.settings')
django.setup()

# Importer les modèles après la configuration
from api.models import Image, User
from api.utils import normalize_name

def normalize_user_data():
    """Normalise les villes pour tous les utilisateurs existants"""
    print("Normalisation des villes pour les utilisateurs...")
    users_updated = 0
    users = User.objects.filter(ville__isnull=False)
    
    for user in users:
        if user.ville and not user.ville_normalized:
            user.ville_normalized = normalize_name(user.ville)
            user.save(update_fields=['ville_normalized'])
            users_updated += 1
    
    print(f"{users_updated} utilisateurs mis à jour avec des villes normalisées")

def normalize_image_data():
    """Normalise les villes et quartiers pour toutes les images existantes"""
    print("Normalisation des données d'images...")
    images_updated = 0
    images = Image.objects.all()
    
    for image in images:
        updated = False
        if image.ville and not image.ville_normalized:
            image.ville_normalized = normalize_name(image.ville)
            updated = True
        
        if image.quartier and not image.quartier_normalized:
            image.quartier_normalized = normalize_name(image.quartier)
            updated = True
        
        if updated:
            image.save(update_fields=['ville_normalized', 'quartier_normalized'])
            images_updated += 1
    
    print(f"{images_updated} images mises à jour avec des données normalisées")

if __name__ == "__main__":
    print("Début de la normalisation des données existantes...")
    normalize_user_data()
    normalize_image_data()
    print("Normalisation terminée!")
