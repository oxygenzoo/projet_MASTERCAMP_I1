"""
Utilitaire pour exporter le modèle ML entraîné vers le format utilisable par l'API Django
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# Assurez-vous que les bibliothèques ML sont installées
try:
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    print("Erreur: sklearn n'est pas installé. Installez-le avec 'pip install scikit-learn'")
    sys.exit(1)

def export_ml_model(model, selected_features, output_dir=None):
    """
    Exporte un modèle ML et ses features pour utilisation avec l'API Django
    
    Args:
        model: Le modèle scikit-learn entraîné
        selected_features: Liste des noms de features utilisées par le modèle
        output_dir: Répertoire de sortie (par défaut: ./models/)
        
    Returns:
        tuple: (model_path, features_path)
    """
    # Définir le répertoire de sortie
    if output_dir is None:
        # Obtenir le répertoire racine du projet
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(project_root, 'models')
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Chemins des fichiers
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = os.path.join(output_dir, 'waste_classifier_model.joblib')
    features_path = os.path.join(output_dir, 'selected_features.json')
    
    # Sauvegarder une copie avec timestamp pour historique
    model_history_path = os.path.join(output_dir, f'waste_classifier_{timestamp}.joblib')
    
    # Sauvegarder le modèle
    joblib.dump(model, model_path)
    joblib.dump(model, model_history_path)
    
    # Sauvegarder la liste des features
    with open(features_path, 'w') as f:
        json.dump(selected_features, f)
    
    print(f"✓ Modèle exporté vers: {model_path}")
    print(f"✓ Features exportées vers: {features_path}")
    print(f"✓ Copie d'archive créée: {model_history_path}")
    
    return model_path, features_path

# Point d'entrée pour utilisation directe
if __name__ == "__main__":
    print("\nEXPORT DU MODÈLE ML POUR DJANGO API")
    print("="*50)
    
    # Vérifier les fichiers d'analyse ML
    feature_analysis_files = [f for f in os.listdir('.') if f.startswith('feature_analysis_optimized_')]
    
    if not feature_analysis_files:
        print("✗ Erreur: Aucun fichier d'analyse de features trouvé.")
        print("  Exécutez d'abord ML.py pour entraîner un modèle.")
        sys.exit(1)
    
    # Trouver le fichier d'analyse le plus récent
    latest_feature_file = max(feature_analysis_files, key=os.path.getctime)
    print(f"ℹ Fichier d'analyse trouvé: {latest_feature_file}")
    
    # Charger les modèles sauvegardés
    try:
        # Rechercher le modèle de performance
        model_summary_file = "model_performance_summary.csv"
        if not os.path.exists(model_summary_file):
            print(f"✗ Fichier {model_summary_file} non trouvé.")
            sys.exit(1)
            
        # Charger les features importantes
        feature_df = pd.read_csv(latest_feature_file)
        selected_features = feature_df['feature'].tolist()
        
        if len(selected_features) == 0:
            print("✗ Erreur: Aucune feature trouvée dans le fichier d'analyse.")
            sys.exit(1)
            
        print(f"ℹ {len(selected_features)} features sélectionnées.")
        
        # Demander confirmation
        print("\nVoulez-vous exporter le modèle ML pour l'API Django?")
        choice = input("Cela remplacera le modèle existant (o/n): ")
        
        if choice.lower() in ['o', 'oui', 'y', 'yes']:
            # Réentraîner un modèle simple à partir des données
            print("\nEn train de préparer le modèle pour l'export...")
            
            # Charger les données d'entraînement
            train_clean = pd.read_csv("train_clean.csv")
            train_dirty = pd.read_csv("train_dirty.csv")
            
            # Préparer les données
            train_clean['target'] = 0  # vide
            train_dirty['target'] = 1  # pleine
            
            # Fusionner
            df_train = pd.concat([train_clean, train_dirty], ignore_index=True)
            
            # Sélectionner les features importantes uniquement
            available_features = [f for f in selected_features if f in df_train.columns]
            X_train = df_train[available_features]
            y_train = df_train['target']
            
            # Créer et entraîner un modèle RandomForest simplifié
            model = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                class_weight='balanced'
            )
            
            print("Entraînement du modèle...")
            model.fit(X_train, y_train)
            
            # Exporter le modèle
            print("\nExport du modèle...")
            export_ml_model(model, available_features)
            
            print("\n✓ Modèle exporté avec succès pour l'API Django!")
            print("  Vous pouvez maintenant exécuter setup_ml_integration.py")
            print("  pour configurer l'intégration Django.")
            
        else:
            print("Export annulé.")
        
    except Exception as e:
        print(f"✗ Erreur lors de l'export du modèle: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
