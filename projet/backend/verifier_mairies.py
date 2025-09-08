#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour vérifier les vraies mairies dans la base de données
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastercamps.settings')
django.setup()

from api.models import User

def verifier_mairies():
    """
    Vérifie quelles mairies existent réellement dans la base
    """
    print("=== VÉRIFICATION DES MAIRIES RÉELLES ===\n")
    
    # Récupérer toutes les mairies
    mairies = User.objects.filter(role='mairie')
    
    print(f"Nombre total de mairies trouvées: {mairies.count()}")
    
    if mairies.count() > 0:
        print("\nDétails des mairies:")
        for mairie in mairies:
            print(f"- ID: {mairie.id}")
            print(f"  Username: {mairie.username}")
            print(f"  Email: {mairie.email}")
            print(f"  Ville: {mairie.ville}")
            print(f"  Points: {mairie.points}")
            print(f"  Avatar: {mairie.avatar}")
            print()
    else:
        print("❌ Aucune mairie trouvée dans la base de données!")
        print("Il faut créer des comptes mairie d'abord.")
    
    # Vérifier aussi tous les utilisateurs normaux
    users = User.objects.filter(role='user').order_by('-points')[:10]
    print(f"\nTop 10 utilisateurs normaux:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.username} - {user.points} points")

if __name__ == "__main__":
    verifier_mairies()
