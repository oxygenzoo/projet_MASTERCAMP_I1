#!/usr/bin/env python
"""
Script pour vérifier les données de classement dans la base
"""
import os
import sys
import django

# Configurer Django
sys.path.append('/mnt/c/Users/berda/Documents/test/Project_mastercamps/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastercamps.settings')
django.setup()

from api.models import User, Mairie, Image

print("=== VÉRIFICATION DES DONNÉES DE CLASSEMENT ===")

# Utilisateurs avec role='user'
print("\n1. UTILISATEURS (role='user'):")
users = User.objects.filter(role='user').order_by('-points')
print(f"Nombre d'utilisateurs: {users.count()}")
for user in users[:10]:
    print(f"  - {user.username} ({user.email}): {user.points} points, ville: {user.ville}")

# Utilisateurs avec role='mairie'
print("\n2. UTILISATEURS AVEC ROLE MAIRIE (role='mairie'):")
user_mairies = User.objects.filter(role='mairie').order_by('-points')
print(f"Nombre d'utilisateurs mairies: {user_mairies.count()}")
for mairie in user_mairies[:10]:
    print(f"  - {mairie.username} ({mairie.email}): {mairie.points} points, ville: {mairie.ville}")

# Entités Mairie
print("\n3. ENTITÉS MAIRIE (table Mairie):")
mairies = Mairie.objects.all().order_by('-points')
print(f"Nombre de mairies: {mairies.count()}")
for mairie in mairies[:10]:
    print(f"  - {mairie.nom} ({mairie.email}): {mairie.points} points")

# Analyser les images pour comprendre les points
print("\n4. ANALYSE DES IMAGES ET POINTS:")
images = Image.objects.all()
print(f"Nombre total d'images: {images.count()}")

# Compter les images par utilisateur
users_with_images = User.objects.filter(role='user', images_uploadees__isnull=False).distinct()
print(f"Utilisateurs avec images: {users_with_images.count()}")

# Calculer les points théoriques basés sur les images
print("\n5. CALCUL THÉORIQUE DES POINTS:")
for user in users[:5]:
    # Compter les images de ce user
    user_images = Image.objects.filter(user=user)
    pleines_annotation = user_images.filter(annotation='pleine').count()
    pleines_mc = user_images.filter(canny_mc='pleine').count()
    pleines_ml = user_images.filter(classification_auto='pleine').count()
    pleines_dl = user_images.filter(classification_dl='pleine').count()
    
    total_images = user_images.count()
    points_theoriques = total_images * 10  # 10 points par image uploadée
    
    print(f"  - {user.username}: {total_images} images, {pleines_annotation} pleines (annotation), {pleines_mc} pleines (MC), {pleines_ml} pleines (ML), {pleines_dl} pleines (DL)")
    print(f"    Points BDD: {user.points}, Points théoriques: {points_theoriques}")

print("\n=== FIN DE LA VÉRIFICATION ===")
