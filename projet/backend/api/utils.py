"""
Fonctions utilitaires pour l'API
"""

def normalize_name(name):
    """
    Normalise un nom (ville ou rue) :
    - Convertit en minuscules
    - Supprime les espaces supplémentaires
    - Supprime les accents (à implémenter si nécessaire)
    
    Args:
        name (str): Nom à normaliser
    Returns:
        str: Nom normalisé
    """
    if not name:
        return ""
    
    # Mettre en minuscules
    name = name.lower()
    
    # Supprimer les espaces en début/fin et réduire les espaces multiples
    name = " ".join(name.split())
    
    # TODO: Si nécessaire, ajouter la suppression des accents ici
    
    return name
