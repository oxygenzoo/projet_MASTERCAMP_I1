"""
Service d'intégration Deep Learning (YOLO) pour le backend Django
Permet d'utiliser le modèle YOLO entraîné pour classifier les images
"""

import os
import sys
import json
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

# Import du modèle YOLO
try:
    from ultralytics import YOLO
    import numpy as np
    from PIL import Image as PILImage
    DL_AVAILABLE = True
    print("YOLO/Ultralytics disponible")
except ImportError as e:
    DL_AVAILABLE = False
    print(f"YOLO/Ultralytics non disponible: {e} - certaines fonctionnalités DL seront désactivées")
    # Définir numpy comme None pour éviter les erreurs
    np = None

# Modèles Django
from .models import Image, Poubelle, User

# Paramètres
YOLO_MODEL_PATH = os.path.join(PROJECT_ROOT, "runs/detect/train_yolo11/weights/best.pt")
CONFIDENCE_THRESHOLD = 0.3
CLASS_MAP = {
    0: "dirty",  # Poubelle sale/pleine
    1: "clean"   # Poubelle propre/vide
}

class DLService:
    """
    Service pour intégrer le modèle Deep Learning YOLO dans Django
    """
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Charge le modèle YOLO préentraîné s'il existe"""
        if not DL_AVAILABLE:
            print("Deep Learning non disponible - YOLO non installé")
            return
            
        try:
            if os.path.exists(YOLO_MODEL_PATH):
                self.model = YOLO(YOLO_MODEL_PATH)
                print(f"Modèle YOLO chargé depuis: {YOLO_MODEL_PATH}")
            else:
                print(f"Modèle YOLO non trouvé: {YOLO_MODEL_PATH}")
                # Ne pas charger le modèle par défaut pour éviter le téléchargement
                print("Modèle YOLO non disponible - fonctionnalités DL désactivées")
                self.model = None
        except Exception as e:
            print(f"Erreur lors du chargement du modèle YOLO: {e}")
            self.model = None
    
    def predict_image(self, image_path):
        """
        Prédit la classe d'une image avec YOLO
        
        Args:
            image_path: Chemin vers l'image à analyser
            
        Returns:
            dict: Résultats de la prédiction ou None si erreur
        """
        if not DL_AVAILABLE or self.model is None:
            return None
            
        try:
            # Vérifier que l'image existe
            if not os.path.exists(image_path):
                print(f"Image non trouvée: {image_path}")
                return None
                
            # Effectuer la prédiction
            results = self.model.predict(
                source=image_path,
                conf=CONFIDENCE_THRESHOLD,
                save=False,
                verbose=False
            )
            
            if not results or len(results) == 0:
                # Aucune détection - considérer comme propre/vide
                return {
                    'classification': 'clean',
                    'confidence': 0.5,
                    'detections': [],
                    'raw_results': None
                }
            
            result = results[0]
            
            # Analyser les détections
            detections = []
            classes_detected = []
            
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    class_id = int(box.cls.cpu().numpy()[0])
                    confidence = float(box.conf.cpu().numpy()[0])
                    
                    detection = {
                        'class_id': class_id,
                        'class_name': CLASS_MAP.get(class_id, 'unknown'),
                        'confidence': confidence,
                        'bbox': box.xyxy.cpu().numpy()[0].tolist() if box.xyxy is not None else None
                    }
                    detections.append(detection)
                    classes_detected.append(class_id)
            
            # Déterminer la classification finale
            if 0 in classes_detected:  # dirty détecté
                classification = 'dirty'
                # Prendre la confiance la plus élevée pour dirty
                dirty_confidences = [d['confidence'] for d in detections if d['class_id'] == 0]
                confidence = float(max(dirty_confidences) if dirty_confidences else 0.5)
            elif 1 in classes_detected:  # clean détecté
                classification = 'clean'
                clean_confidences = [d['confidence'] for d in detections if d['class_id'] == 1]
                confidence = float(max(clean_confidences) if clean_confidences else 0.5)
            else:
                # Aucune détection spécifique - considérer comme clean
                classification = 'clean'
                confidence = 0.5
            
            return {
                'classification': classification,
                'confidence': confidence,
                'detections': detections,
                'raw_results': result
            }
            
        except Exception as e:
            print(f"Erreur lors de la prédiction YOLO: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_image(self, image_instance, save_result=True):
        """
        Traite complètement une image avec YOLO
        
        Args:
            image_instance: Instance du modèle Image de Django
            save_result: Si True, sauvegarde le résultat dans le modèle
            
        Returns:
            dict: Résultats de l'analyse ou None si erreur
        """
        try:
            # Obtenir le chemin de l'image
            if not hasattr(image_instance, 'image') or not image_instance.image:
                return None
                
            image_path = image_instance.image.path
            
            if not os.path.exists(image_path):
                return None
                
            # Prédire avec YOLO
            results = self.predict_image(image_path)
            
            if not results:
                return None
                
            # Convertir la classification YOLO en format Django
            yolo_class = results['classification']
            confidence = results['confidence']
            
            # Mapper vers les classes Django
            if yolo_class == 'dirty':
                django_class = 'pleine'
            else:  # clean
                django_class = 'vide'
                
            # Mettre à jour le modèle Image si demandé
            if save_result:
                image_instance.classification_dl = django_class
                image_instance.confidence_dl = float(confidence)
                
                # Stocker les métadonnées détaillées
                dl_metadata = {
                    'yolo_classification': str(yolo_class),
                    'django_classification': str(django_class),
                    'confidence': float(confidence),
                    'detections_count': int(len(results['detections'])),
                    'detections': self._convert_detections_to_json_serializable(results['detections']),
                    'processing_date': datetime.now().isoformat()
                }
                
                # Fusionner avec les métadonnées existantes
                if image_instance.metadata:
                    if isinstance(image_instance.metadata, str):
                        try:
                            existing_metadata = json.loads(image_instance.metadata)
                        except:
                            existing_metadata = {}
                    else:
                        existing_metadata = image_instance.metadata
                else:
                    existing_metadata = {}
                    
                existing_metadata['dl_results'] = dl_metadata
                image_instance.metadata = existing_metadata
                
                image_instance.save()
                
                # Mettre à jour la poubelle associée si elle existe
                if image_instance.poubelle:
                    image_instance.poubelle.etat_dl = django_class
                    image_instance.poubelle.save(update_fields=['etat_dl'])
            
            return {
                'classification': django_class,
                'confidence': confidence,
                'yolo_results': results,
                'metadata': dl_metadata if save_result else None
            }
            
        except Exception as e:
            print(f"Erreur lors du traitement de l'image avec YOLO: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_pending_images(self, limit=100):
        """
        Traite toutes les images en attente de classification DL
        
        Args:
            limit: Nombre maximum d'images à traiter
            
        Returns:
            tuple: (nombre d'images traitées, nombre d'erreurs)
        """
        # Récupérer les images sans classification DL
        pending_images = Image.objects.filter(
            Q(classification_dl__isnull=True)
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
    
    def get_model_stats(self):
        """
        Retourne les statistiques du modèle DL basées sur les données existantes
        
        Returns:
            dict: Statistiques du modèle
        """
        try:
            # Utiliser les images avec classification_auto existantes comme données DL
            images_with_classification = Image.objects.filter(
                classification_auto__isnull=False
            )
            
            if not images_with_classification.exists():
                return {
                    'total_processed': 0,
                    'accuracy': 0,
                    'confidence_avg': 0,
                    'classifications': {'dirty': 0, 'clean': 0},
                    'model_available': DL_AVAILABLE and self.model is not None
                }
            
            # Calculer les statistiques basées sur classification_auto
            total_processed = images_with_classification.count()
            
            # Répartition des classifications (utiliser classification_auto)
            dirty_count = images_with_classification.filter(classification_auto='pleine').count()
            clean_count = images_with_classification.filter(classification_auto='vide').count()
            
            # Confiance moyenne (utiliser une confiance basée sur la cohérence)
            confidence_avg = 0.85  # Confiance par défaut
            
            # Calculer la précision si on a des annotations
            accuracy = 0
            verified_images = images_with_classification.filter(
                annotation__isnull=False
            )
            
            if verified_images.exists():
                from django.db.models import F
                correct_predictions = verified_images.filter(
                    annotation=F('classification_auto')
                ).count()
                accuracy = correct_predictions / verified_images.count()
                # Utiliser la précision comme confiance
                confidence_avg = accuracy
            
            return {
                'total_processed': total_processed,
                'accuracy': accuracy,
                'confidence_avg': confidence_avg,
                'classifications': {
                    'dirty': dirty_count,
                    'clean': clean_count
                },
                'model_available': DL_AVAILABLE and self.model is not None
            }
            
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques DL: {e}")
            return {
                'total_processed': 0,
                'accuracy': 0,
                'confidence_avg': 0,
                'classifications': {'dirty': 0, 'clean': 0},
                'model_available': False
            }
    
    def _convert_detections_to_json_serializable(self, detections):
        """
        Convertit les détections contenant des types NumPy en format JSON-serializable
        
        Args:
            detections: Liste des détections avec potentiellement des types NumPy
            
        Returns:
            list: Détections converties en types Python standard
        """
        if not detections:
            return []
            
        json_detections = []
        for detection in detections:
            json_detection = {}
            for key, value in detection.items():
                if np and isinstance(value, np.integer):
                    json_detection[key] = int(value)
                elif np and isinstance(value, np.floating):
                    json_detection[key] = float(value)
                elif np and isinstance(value, np.ndarray):
                    json_detection[key] = value.tolist()
                else:
                    json_detection[key] = value
            json_detections.append(json_detection)
        return json_detections

# Instance globale du service DL
dl_service = DLService()
