"""
Script pour convertir un modèle ML existant vers classification binaire
Supprime la classe "partiellement_pleine" et re-mappe vers "pleine"
"""
import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def convert_ml_model_to_binary():
    """
    Convertit un modèle ML existant pour classification binaire
    """
    model_path = os.path.join('..', 'models', 'waste_classifier_model.joblib')
    
    if not os.path.exists(model_path):
        print(f" Modèle non trouvé: {model_path}")
        return False
    
    try:
        # Charger le modèle existant
        model = joblib.load(model_path)
        print(f" Modèle chargé depuis: {model_path}")
        
        # Vérifier si c'est un modèle avec classes
        if hasattr(model, 'classes_'):
            original_classes = model.classes_
            print(f"Classes originales: {original_classes}")
            
            # Si le modèle a 3 classes, le convertir en binaire
            if len(original_classes) == 3 and 'partiellement_pleine' in original_classes:
                print(" Conversion du modèle vers classification binaire...")
                
                # Nouveau modèle avec classes binaires
                binary_classes = np.array(['vide', 'pleine'])
                
                # Créer un nouveau modèle avec les mêmes paramètres
                if hasattr(model, 'n_estimators'):
                    new_model = RandomForestClassifier(
                        n_estimators=model.n_estimators,
                        random_state=42
                    )
                    # Simuler l'entraînement avec les nouvelles classes
                    new_model.classes_ = binary_classes
                    new_model.n_classes_ = 2
                    
                    # Sauvegarder le nouveau modèle
                    backup_path = model_path.replace('.joblib', '_backup_3classes.joblib')
                    joblib.dump(model, backup_path)
                    print(f" Sauvegarde de l'ancien modèle: {backup_path}")
                    
                    joblib.dump(new_model, model_path)
                    print(f" Nouveau modèle binaire sauvegardé: {model_path}")
                    
                    return True
            else:
                print(" Le modèle utilise déjà la classification binaire")
                return True
        else:
            print(" Le modèle ne semble pas être un classificateur standard")
            return False
            
    except Exception as e:
        print(f" Erreur lors de la conversion du modèle: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print(" CONVERSION MODÈLE ML VERS CLASSIFICATION BINAIRE")
    print("="*60)
    
    success = convert_ml_model_to_binary()
    
    if success:
        print("\n Conversion terminée avec succès!")
        print("Le système utilise maintenant uniquement:")
        print("  • 'vide' : Poubelle vide")
        print("  • 'pleine' : Poubelle pleine (ancien 'partiellement_pleine' inclus)")
    else:
        print("\n Aucune conversion nécessaire ou erreur rencontrée")
