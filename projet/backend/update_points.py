#!/usr/bin/env python
"""
Script pour calculer et mettre à jour les points des utilisateurs et mairies
"""
import os
import sys
import django

# Configurer Django
sys.path.append('/mnt/c/Users/berda/Documents/test/Project_mastercamps/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastercamps.settings')
django.setup()

from api.models import User, Mairie, Image, HistoriquePoints
from django.db.models import Count, Q

def calculer_points_utilisateur(user):
    """Calcule les points d'un utilisateur basé sur ses images"""
    # Récupérer toutes les images de l'utilisateur
    images = Image.objects.filter(user=user)
    
    points_total = 0
    
    # Points pour chaque image uploadée (10 points)
    points_upload = images.count() * 10
    points_total += points_upload
    
    # Points bonus pour les poubelles pleines détectées (5 points supplémentaires)
    # Utiliser n'importe quelle méthode de détection (annotation, MC, ML, DL)
    images_pleines = images.filter(
        Q(annotation='pleine') | 
        Q(canny_mc='pleine') | 
        Q(classification_auto='pleine') | 
        Q(classification_dl='pleine')
    ).distinct()
    
    points_pleines = images_pleines.count() * 5
    points_total += points_pleines
    
    return points_total, points_upload, points_pleines

def calculer_points_mairie(mairie_user):
    """Calcule les points d'une mairie basé sur les images de sa ville"""
    # Récupérer toutes les images de la ville de cette mairie
    images = Image.objects.filter(ville_normalized=mairie_user.ville_normalized)
    
    points_total = 0
    
    # Points pour chaque image dans la ville (5 points)
    points_images = images.count() * 5
    points_total += points_images
    
    # Points bonus pour les poubelles pleines (3 points supplémentaires)
    images_pleines = images.filter(
        Q(annotation='pleine') | 
        Q(canny_mc='pleine') | 
        Q(classification_auto='pleine') | 
        Q(classification_dl='pleine')
    ).distinct()
    
    points_pleines = images_pleines.count() * 3
    points_total += points_pleines
    
    return points_total, points_images, points_pleines

def main():
    print("=== CALCUL ET MISE À JOUR DES POINTS ===")
    
    # Mettre à jour les points des utilisateurs
    print("\n1. MISE À JOUR DES POINTS UTILISATEURS:")
    users = User.objects.filter(role='user')
    
    for user in users:
        points_total, points_upload, points_pleines = calculer_points_utilisateur(user)
        ancien_points = user.points
        
        # Mettre à jour les points
        user.points = points_total
        user.save()
        
        if points_total > 0:
            print(f"  - {user.username}: {ancien_points} → {points_total} points")
            print(f"    (Upload: {points_upload}, Pleines: {points_pleines})")
            
            # Créer un historique des points si nécessaire
            if ancien_points != points_total:
                HistoriquePoints.objects.create(
                    user=user,
                    points=points_total - ancien_points,
                    type='bonus',
                    description=f"Recalcul automatique des points"
                )
    
    # Mettre à jour les points des mairies
    print("\n2. MISE À JOUR DES POINTS MAIRIES:")
    mairies = User.objects.filter(role='mairie')
    
    for mairie in mairies:
        if mairie.ville_normalized:
            points_total, points_images, points_pleines = calculer_points_mairie(mairie)
            ancien_points = mairie.points
            
            # Mettre à jour les points
            mairie.points = points_total
            mairie.save()
            
            if points_total > 0:
                print(f"  - {mairie.username} ({mairie.ville}): {ancien_points} → {points_total} points")
                print(f"    (Images: {points_images}, Pleines: {points_pleines})")
    
    # Afficher le top des utilisateurs
    print("\n3. TOP 5 UTILISATEURS APRÈS MISE À JOUR:")
    top_users = User.objects.filter(role='user').order_by('-points')[:5]
    for i, user in enumerate(top_users, 1):
        print(f"  {i}. {user.username}: {user.points} points")
    
    # Afficher le top des mairies
    print("\n4. TOP 5 MAIRIES APRÈS MISE À JOUR:")
    top_mairies = User.objects.filter(role='mairie').order_by('-points')[:5]
    for i, mairie in enumerate(top_mairies, 1):
        print(f"  {i}. {mairie.ville}: {mairie.points} points")
    
    print("\n=== MISE À JOUR TERMINÉE ===")

if __name__ == "__main__":
    main()
