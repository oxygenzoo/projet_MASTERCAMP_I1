#!/usr/bin/env python
"""
Test des endpoints de classement
"""
import requests
import json

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("=== TEST DES ENDPOINTS DE CLASSEMENT ===")
    
    # Test endpoint competition_users
    print("\n1. Test endpoint competition_users:")
    try:
        response = requests.get(f"{base_url}/api/competition/users/")
        if response.status_code == 200:
            data = response.json()
            print(f"   Succès: {data['success']}")
            print(f"   Nombre d'utilisateurs: {len(data['users'])}")
            for i, user in enumerate(data['users'][:5], 1):
                print(f"   {i}. {user['username']}: {user['points']} points (ville: {user['ville']})")
        else:
            print(f"   Erreur: {response.status_code}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test endpoint competition_mairies
    print("\n2. Test endpoint competition_mairies:")
    try:
        response = requests.get(f"{base_url}/api/competition/mairies/")
        if response.status_code == 200:
            data = response.json()
            print(f"   Succès: {data['success']}")
            print(f"   Nombre de mairies: {len(data['mairies'])}")
            for i, mairie in enumerate(data['mairies'][:5], 1):
                print(f"   {i}. {mairie['ville']}: {mairie['points']} points (username: {mairie['username']})")
        else:
            print(f"   Erreur: {response.status_code}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    print("\n=== FIN DES TESTS ===")

if __name__ == "__main__":
    test_endpoints()
