#!/usr/bin/env python3
"""
Test des API de compétition
"""
import os
import sys
import django
import requests

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mastercamps.settings')
django.setup()

def test_competition_apis():
    """Test les API de compétition"""
    print("=== TEST API COMPÉTITION ===")
    
    base_url = 'http://localhost:8000'
    
    # Test API utilisateurs
    print("\n1. Test API utilisateurs")
    try:
        response = requests.get(f'{base_url}/api/competition/users/')
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"✓ API utilisateurs OK - {len(users)} utilisateurs récupérés")
            
            # Afficher les 3 premiers
            for i, user in enumerate(users[:3]):
                print(f"  {i+1}. {user['username']} - {user['points']} points ({user['ville']})")
                
            if len(users) > 10:
                print(f"⚠ ATTENTION: {len(users)} utilisateurs récupérés, mais on ne devrait en avoir que 10 max")
        else:
            print(f"✗ API utilisateurs ERREUR: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Erreur lors du test API utilisateurs: {e}")
    
    # Test API mairies
    print("\n2. Test API mairies")
    try:
        response = requests.get(f'{base_url}/api/competition/mairies/')
        if response.status_code == 200:
            data = response.json()
            mairies = data.get('mairies', [])
            print(f"✓ API mairies OK - {len(mairies)} mairies récupérées")
            
            # Afficher les 3 premières
            for i, mairie in enumerate(mairies[:3]):
                print(f"  {i+1}. {mairie['ville']} - {mairie['points']} points")
                
            if len(mairies) > 5:
                print(f"⚠ ATTENTION: {len(mairies)} mairies récupérées, mais on ne devrait en avoir que 5 max")
        else:
            print(f"✗ API mairies ERREUR: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"✗ Erreur lors du test API mairies: {e}")

if __name__ == "__main__":
    test_competition_apis()
