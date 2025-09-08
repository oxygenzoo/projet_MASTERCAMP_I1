#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simple pour récupérer les meilleurs utilisateurs et mairies depuis la base de données
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

def get_best_users_and_mairies():
    """
    Récupère directement les meilleurs utilisateurs et mairies depuis la base de données
    """
    print("=== RÉCUPÉRATION DES MEILLEURS SCORES ===\n")
    
    # Récupérer les 5 meilleurs utilisateurs normaux (role='user')
    print("Top 5 utilisateurs:")
    best_users = User.objects.filter(role='user').order_by('-points')[:5]
    
    for i, user in enumerate(best_users, 1):
        print(f"{i}. {user.username} - {user.points} points")
    
    print(f"\nNombre total d'utilisateurs: {User.objects.filter(role='user').count()}")
    
    # Récupérer les 5 meilleures mairies (role='mairie')  
    print("\nTop 5 mairies:")
    best_mairies = User.objects.filter(role='mairie').order_by('-points')[:5]
    
    for i, mairie in enumerate(best_mairies, 1):
        ville = mairie.ville or mairie.username
        print(f"{i}. Mairie de {ville} - {mairie.points} points")
    
    print(f"\nNombre total de mairies: {User.objects.filter(role='mairie').count()}")
    
    return best_users, best_mairies

if __name__ == "__main__":
    get_best_users_and_mairies()
