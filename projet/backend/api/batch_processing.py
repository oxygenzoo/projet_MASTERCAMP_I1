"""
Module de traitement par lot des images avec ML
"""

import os
import sys
import pandas as pd
import logging
import traceback
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db.models import Q

# Configuration du logging
logger = logging.getLogger(__name__)

# Imports des modèles
from .models import Image, BatchAnalysis, Poubelle
from .ml_integration import ml_service

def process_batch(batch_id):
    """
    Traite un lot d'images par batch_id
    
    Args:
        batch_id: ID du BatchAnalysis
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Récupérer l'objet BatchAnalysis
        batch = BatchAnalysis.objects.get(id=batch_id)
        
        # Mettre à jour le statut
        batch.status = 'processing'
        batch.save(update_fields=['status'])
        
        # Récupérer toutes les images non traitées (sans classification_auto ou sans métadonnées)
        images = Image.objects.filter(
            Q(classification_auto__isnull=True) | 
            Q(metadata__isnull=True)
        ).order_by('-date_creation')
        
        # Mettre à jour le nombre total d'images
        batch.total_images = images.count()
        batch.save(update_fields=['total_images'])
        
        # Initialiser les compteurs
        processed = 0
        success = 0
        error = 0
        
        # Stocker les résultats détaillés
        results_list = []
        
        # Traiter chaque image
        for image in images:
            try:
                # Traiter l'image avec le service ML
                features = ml_service.process_image(image, save_result=True)
                
                if features:
                    success += 1
                    results_list.append({
                        'image_id': image.id,
                        'filename': os.path.basename(image.image.name),
                        'status': 'success',
                        'classification': image.classification_auto,
                        'confidence': features.get('confidence', 0)
                    })
                else:
                    error += 1
                    results_list.append({
                        'image_id': image.id,
                        'filename': os.path.basename(image.image.name),
                        'status': 'error',
                        'error': 'Échec du traitement'
                    })
                    
            except Exception as e:
                error += 1
                logger.error(f"Erreur lors du traitement de l'image {image.id}: {e}")
                results_list.append({
                    'image_id': image.id,
                    'filename': os.path.basename(image.image.name) if image.image else 'unknown',
                    'status': 'error',
                    'error': str(e)
                })
            
            # Mettre à jour les compteurs
            processed += 1
            
            # Mettre à jour la progression toutes les 10 images
            if processed % 10 == 0:
                batch.update_progress(processed, success, error)
        
        # Générer un CSV des résultats
        if results_list:
            df = pd.DataFrame(results_list)
            
            # Créer un fichier CSV en mémoire
            csv_content = df.to_csv(index=False)
            
            # Sauvegarder le CSV dans le modèle
            csv_filename = f"batch_results_{batch_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            batch.csv_result.save(csv_filename, ContentFile(csv_content.encode('utf-8')))
            
        # Mettre à jour les résultats détaillés
        batch.results_json = {
            'images': results_list[:100],  # Limiter à 100 résultats pour éviter des problèmes de taille
            'summary': {
                'total': batch.total_images,
                'processed': processed,
                'success': success,
                'error': error,
                'completion_rate': f"{(success/batch.total_images)*100:.2f}%" if batch.total_images > 0 else "0%"
            }
        }
        
        # Marquer comme terminé
        batch.mark_complete()
        batch.update_progress(processed, success, error)
        
        return True
        
    except BatchAnalysis.DoesNotExist:
        logger.error(f"BatchAnalysis avec ID {batch_id} non trouvé")
        return False
    except Exception as e:
        logger.error(f"Erreur lors du traitement du lot {batch_id}: {e}")
        traceback.print_exc()
        
        # Marquer comme échoué si l'objet existe
        try:
            batch = BatchAnalysis.objects.get(id=batch_id)
            batch.mark_failed()
        except Exception:
            pass
            
        return False

def export_dataset(output_path=None, include_annotations=True):
    """
    Exporte toutes les images et leurs caractéristiques en CSV
    
    Args:
        output_path: Chemin où sauvegarder le CSV (optionnel)
        include_annotations: Si True, inclut seulement les images annotées
        
    Returns:
        str: Chemin du fichier CSV ou None si erreur
    """
    try:
        # Filtrer les images selon les critères
        query = Q(metadata__isnull=False)
        
        if include_annotations:
            query &= Q(annotation__isnull=False)
            
        # Récupérer les images
        images = Image.objects.filter(query).order_by('-date_creation')
        
        if not images:
            logger.warning("Aucune image trouvée pour l'export")
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
            logger.warning("Aucune donnée extraite pour l'export")
            return None
            
        # Convertir en DataFrame
        df = pd.DataFrame(all_data)
        
        # Créer un nom de fichier par défaut si non spécifié
        if not output_path:
            media_root = settings.MEDIA_ROOT
            export_dir = os.path.join(media_root, 'exports')
            os.makedirs(export_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(export_dir, f"waste_dataset_{timestamp}.csv")
        
        # Sauvegarder le CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Dataset exporté vers {output_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export du dataset: {e}")
        traceback.print_exc()
        return None
