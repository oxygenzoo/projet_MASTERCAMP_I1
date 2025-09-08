# -*- coding: utf-8 -*-
"""
API d'analyse d'image de déchets - Intégration avec MC_fusion
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

import os
import json
import sys
import traceback
from datetime import datetime

# Import du module MC_fusion (ajuster le chemin si nécessaire)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from MC_fusion import UnifiedWasteAnalyzer

# Créer une instance unique de l'analyseur pour optimiser les performances
waste_analyzer = UnifiedWasteAnalyzer(target_features=200)

@api_view(['POST'])
@csrf_exempt
@parser_classes([MultiPartParser, FormParser])
def analyze_waste_image(request):
    """
    Point d'entrée API pour l'analyse d'une image de déchets
    
    POST /api/analyze-waste/
    
    Paramètres:
    - image: Fichier image à analyser
    - options (optionnel): Options d'analyse au format JSON
    
    Retourne:
    - Un objet JSON avec toutes les caractéristiques extraites
    """
    try:
        # Vérification du fichier image
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'Aucune image fournie'}, status=400)
        
        image_file = request.FILES['image']
        
        # Options d'analyse (optionnelles)
        options = {}
        if 'options' in request.POST:
            try:
                options = json.loads(request.POST['options'])
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Format JSON des options invalide'}, status=400)
        
        # Analyse de l'image
        features = waste_analyzer.analyze_django_image(image_file)
        
        if features is None:
            return JsonResponse({'error': 'Échec de l\'analyse de l\'image'}, status=500)
        
        # Ajouter des métadonnées
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'feature_count': len(features) - 3,  # Moins les métadonnées
        }
        
        return JsonResponse(result)
    
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': f'Erreur serveur: {str(e)}'}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def batch_analyze_images(request):
    """
    Point d'entrée API pour l'analyse d'un lot d'images
    
    POST /api/analyze-batch/
    
    Paramètres:
    - images[]: Liste de fichiers images à analyser
    - options (optionnel): Options d'analyse au format JSON
    
    Retourne:
    - Un objet JSON avec les caractéristiques extraites pour chaque image
    """
    try:
        # Vérification des fichiers images
        if 'images[]' not in request.FILES:
            return JsonResponse({'error': 'Aucune image fournie'}, status=400)
        
        image_files = request.FILES.getlist('images[]')
        
        if not image_files:
            return JsonResponse({'error': 'Liste d\'images vide'}, status=400)
        
        # Analyse des images
        results = []
        for image_file in image_files:
            features = waste_analyzer.analyze_django_image(image_file)
            if features:
                results.append({
                    'filename': image_file.name,
                    'features': features
                })
        
        # Ajouter des métadonnées
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'total_images': len(image_files),
            'processed_images': len(results),
            'results': results
        }
        
        return JsonResponse(response)
    
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': f'Erreur serveur: {str(e)}'}, status=500)
