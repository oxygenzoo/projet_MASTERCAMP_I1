"""
Service d'intégration ML pour le backend Django
Permet d'utiliser les modèles ML entraînés pour classifier les images
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from django.core.files.storage import default_storage
from django.utils import timezone

# Ajout du chemin racine pour importer les modules du projet
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Import des modules ML
from MC_fusion import UnifiedWasteAnalyzer
try:
    # Import optionnel du RandomForestClassifier préentraîné
    import joblib
    from sklearn.ensemble import RandomForestClassifier
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Modèles
from .models import Image, Poubelle, User

# Paramètres
TARGET_FEATURES = 250  # Nombre optimal de features
MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'waste_classifier_model.joblib')
FEATURES_LIST_PATH = os.path.join(PROJECT_ROOT, 'models', 'selected_features.json')

# Instance globale de l'analyseur
waste_analyzer = UnifiedWasteAnalyzer(target_features=TARGET_FEATURES)

class MLService:
    """
    Service pour intégrer le modèle ML dans Django
    """
    
    def __init__(self):
        self.analyzer = waste_analyzer
        self.model = None
        self.selected_features = None
        self.load_model()
        
    def load_model(self):
        """Charge le modèle ML préentraîné s'il existe"""
        if not ML_AVAILABLE:
            return False
            
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                print(f"Modèle ML chargé depuis {MODEL_PATH}")
                
                # Charger la liste des features sélectionnées
                if os.path.exists(FEATURES_LIST_PATH):
                    with open(FEATURES_LIST_PATH, 'r') as f:
                        self.selected_features = json.load(f)
                    print(f"Liste de {len(self.selected_features)} features chargée")
                return True
            else:
                # Modèle ML non trouvé - mode silencieux sauf en debug
                if hasattr(settings, 'DEBUG') and settings.DEBUG:
                    print(f"Modèle ML non trouvé: {MODEL_PATH}")
                return False
        except Exception as e:
            # Mode silencieux pour les erreurs ML en développement
            if hasattr(settings, 'DEBUG') and settings.DEBUG:
                print(f"Erreur lors du chargement du modèle ML: {e}")
            return False
            
    def save_model(self, model, selected_features):
        """Sauvegarde le modèle ML entraîné"""
        if not ML_AVAILABLE:
            return False
            
        try:
            # Créer le répertoire models s'il n'existe pas
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            
            # Sauvegarder le modèle
            joblib.dump(model, MODEL_PATH)
            
            # Sauvegarder la liste des features
            with open(FEATURES_LIST_PATH, 'w') as f:
                json.dump(selected_features, f)
                
            print(f"Modèle ML sauvegardé dans {MODEL_PATH}")
            self.model = model
            self.selected_features = selected_features
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du modèle ML: {e}")
            return False
    
    def extract_features(self, image_instance):
        """
        Extrait les caractéristiques d'une image Django
        
        Args:
            image_instance: Instance du modèle Image de Django
            
        Returns:
            dict: Les caractéristiques extraites ou None en cas d'erreur
        """
        try:
            # Obtenir le chemin de l'image
            if hasattr(image_instance, 'image') and image_instance.image:
                image_path = image_instance.image.path
                
                if os.path.exists(image_path):
                    # Analyser l'image
                    features = self.analyzer.analyze_image(image_path)
                    
                    if features:
                        # Mettre à jour les métadonnées de l'image
                        image_instance.metadata = features
                        image_instance.save(update_fields=['metadata'])
                        return features
            
            return None
        except Exception as e:
            print(f"Erreur lors de l'extraction des caractéristiques: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def predict_image_class(self, features):
        """
        Prédit la classe d'une image à partir de ses caractéristiques
        
        Args:
            features: Dictionnaire ou DataFrame de caractéristiques
            
        Returns:
            tuple: (classe prédite, probabilité) ou (None, 0) si erreur
        """
        if not ML_AVAILABLE or self.model is None or self.selected_features is None:
            return None, 0
            
        try:
            # Convertir en DataFrame si nécessaire
            if isinstance(features, dict):
                features_df = pd.DataFrame([features])
            else:
                features_df = features
                
            # Sélectionner uniquement les features utilisées par le modèle
            available_features = [f for f in self.selected_features if f in features_df.columns]
            
            if len(available_features) < len(self.selected_features) * 0.8:
                print(f"Avertissement: seulement {len(available_features)}/{len(self.selected_features)} features disponibles")
            
            # Extraire les caractéristiques pour le modèle
            X = features_df[available_features]
            
            # Prédire la classe
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            confidence = np.max(probabilities)
            
            # Convertir en label texte
            class_label = 'pleine' if prediction == 1 else 'vide'
            
            return class_label, confidence
            
        except Exception as e:
            print(f"Erreur lors de la prédiction: {e}")
            import traceback
            traceback.print_exc()
            return None, 0
    
    def process_image(self, image_instance, save_result=True):
        """
        Traite complètement une image: extraction + classification
        
        Args:
            image_instance: Instance du modèle Image de Django
            save_result: Si True, sauvegarde le résultat dans le modèle
            
        Returns:
            dict: Résultats de l'analyse ou None si erreur
        """
        try:
            # Extraire les caractéristiques
            features = self.extract_features(image_instance)
            
            if not features:
                return None
                
            # Prédire la classe si le modèle est disponible
            if self.model is not None:
                class_label, confidence = self.predict_image_class(features)
                
                # Mettre à jour le modèle Image si demandé
                if save_result and class_label is not None:
                    image_instance.classification_auto = class_label
                    
                    # Calculer des métadonnées supplémentaires
                    if 'dimensions' in features:
                        image_instance.dimensions = features['dimensions']
                    if 'taille' in features:
                        image_instance.taille_fichier = features['taille']
                    if 'contraste' in features:
                        image_instance.contraste = features['contraste']
                    if 'couleur_moyenne' in features:
                        image_instance.couleur_moyenne = features['couleur_moyenne']
                        
                    # Jour de la semaine
                    if image_instance.date_creation:
                        image_instance.jour_semaine = image_instance.date_creation.strftime('%A')
                        
                    image_instance.save()
                    
                    # Mettre à jour la poubelle associée si elle existe
                    if image_instance.poubelle:
                        image_instance.poubelle.etat = class_label
                        image_instance.poubelle.save(update_fields=['etat'])
                
                # Ajouter les résultats de prédiction aux features
                features['classification_auto'] = class_label
                features['confidence'] = float(confidence)
                
            return features
            
        except Exception as e:
            print(f"Erreur lors du traitement de l'image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_pending_images(self, limit=100):
        """
        Traite toutes les images en attente de classification
        
        Args:
            limit: Nombre maximum d'images à traiter
            
        Returns:
            tuple: (nombre d'images traitées, nombre d'erreurs)
        """
        # Récupérer les images sans classification automatique
        pending_images = Image.objects.filter(
            Q(classification_auto__isnull=True) | 
            Q(metadata__isnull=True)
        ).order_by('-date_creation')[:limit]
        
        processed = 0
        errors = 0
        
        for image in pending_images:
            result = self.process_image(image, save_result=True)
            if result:
                processed += 1
            else:
                errors += 1
                
        return processed, errors
    
    def export_features_dataset(self, output_path=None):
        """
        Exporte un dataset avec toutes les caractéristiques des images
        et leurs classifications
        
        Args:
            output_path: Chemin où sauvegarder le CSV
            
        Returns:
            DataFrame ou None si erreur
        """
        try:
            # Récupérer toutes les images avec métadonnées et annotation
            images = Image.objects.filter(
                metadata__isnull=False
            ).order_by('-date_creation')
            
            if not images:
                return None
                
            # Créer un DataFrame vide
            all_data = []
            
            for image in images:
                if not image.metadata:
                    continue
                    
                # Extraire les caractéristiques
                features = image.metadata.copy()
                
                # Ajouter les annotations et classifications
                features['annotation'] = image.annotation
                features['classification_auto'] = image.classification_auto
                features['filename'] = os.path.basename(image.image.name) if image.image else ''
                features['id'] = image.id
                
                all_data.append(features)
            
            if not all_data:
                return None
                
            # Convertir en DataFrame
            df = pd.DataFrame(all_data)
            
            # Sauvegarder si un chemin est spécifié
            if output_path:
                df.to_csv(output_path, index=False)
                print(f"Dataset exporté vers {output_path}")
                
            return df
            
        except Exception as e:
            print(f"Erreur lors de l'export du dataset: {e}")
            import traceback
            traceback.print_exc()
            return None

# Créer une instance singleton du service ML
ml_service = MLService()
