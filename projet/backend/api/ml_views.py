"""
Vues API pour l'intégration ML
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings
from django.core.exceptions import PermissionDenied

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

import os
import sys
import json
import traceback
from datetime import datetime
import threading

# Imports des modules ML
from .ml_integration import ml_service
from .batch_processing import process_batch, export_dataset
from .models import Image, BatchAnalysis, Poubelle
from .serializers import ImageSerializer, BatchAnalysisSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def analyze_single_image(request):
    """
    Point d'entrée API pour l'analyse d'une seule image
    
    POST /api/ml/analyze-image/
    
    Paramètres:
    - image: Fichier image à analyser
    - options (optionnel): Options d'analyse au format JSON
    
    Retourne:
    - Un objet JSON avec les caractéristiques et la classification
    """
    try:
        # Vérifier si l'image est fournie
        if 'image' not in request.FILES:
            return Response({'error': 'Aucune image fournie'}, status=status.HTTP_400_BAD_REQUEST)
            
        image_file = request.FILES['image']
        
        # Créer une instance Image
        image = Image(
            image=image_file,
            user=request.user,
        )
        
        # Ajouter des métadonnées supplémentaires si disponibles
        if 'latitude' in request.data and 'longitude' in request.data:
            try:
                image.latitude = float(request.data['latitude'])
                image.longitude = float(request.data['longitude'])
            except (ValueError, TypeError):
                pass
                
        if 'adresse' in request.data:
            image.adresse = request.data['adresse']
            
        if 'quartier' in request.data:
            image.quartier = request.data['quartier']
            
        # Sauvegarder l'image
        image.save()
        
        # Analyser l'image avec le service ML
        features = ml_service.process_image(image, save_result=True)
        
        if not features:
            return Response({
                'error': 'Échec de l\'analyse de l\'image',
                'image_id': image.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Construire la réponse
        response = {
            'success': True,
            'image_id': image.id,
            'classification': image.classification_auto,
            'confidence': features.get('confidence', 0),
            'features_count': len(features) - 3  # Moins les métadonnées
        }
        
        # Ajouter l'URL de l'image
        if image.image:
            response['image_url'] = request.build_absolute_uri(image.image.url)
        
        return Response(response)
        
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'Erreur serveur: {str(e)}'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_batch_analysis(request):
    """
    Crée une nouvelle tâche d'analyse par lot
    
    POST /api/ml/create-batch/
    
    Paramètres:
    - name: Nom de l'analyse par lot
    
    Retourne:
    - Un objet BatchAnalysis créé
    """
    try:
        # Vérifier les permissions (admin ou mairie)
        if not (request.user.is_staff or request.user.role == 'mairie'):
            return Response({'error': 'Permissions insuffisantes'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Valider les données
        name = request.data.get('name', f"Analyse {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Créer le BatchAnalysis
        batch = BatchAnalysis.objects.create(
            name=name,
            created_by=request.user,
            status='pending'
        )
        
        # Démarrer le traitement dans un thread séparé
        thread = threading.Thread(target=process_batch, args=(batch.id,))
        thread.daemon = True
        thread.start()
        
        # Retourner la réponse
        serializer = BatchAnalysisSerializer(batch)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'Erreur serveur: {str(e)}'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_batch_status(request, batch_id):
    """
    Récupère le statut d'une analyse par lot
    
    GET /api/ml/batch-status/<batch_id>/
    
    Retourne:
    - Un objet BatchAnalysis
    """
    try:
        # Récupérer le BatchAnalysis
        batch = get_object_or_404(BatchAnalysis, id=batch_id)
        
        # Vérifier les permissions
        if not (request.user.is_staff or request.user.role == 'mairie' or 
                (batch.created_by and batch.created_by == request.user)):
            return Response({'error': 'Permissions insuffisantes'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Sérialiser et retourner
        serializer = BatchAnalysisSerializer(batch)
        return Response(serializer.data)
        
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'Erreur serveur: {str(e)}'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_batch_analyses(request):
    """
    Liste toutes les analyses par lot
    
    GET /api/ml/batch-list/
    
    Paramètres (optionnels):
    - status: Filtrer par statut
    
    Retourne:
    - Liste d'objets BatchAnalysis
    """
    try:
        # Filtrer selon le rôle de l'utilisateur
        if request.user.is_staff:
            # Les admins voient tout
            batches = BatchAnalysis.objects.all()
        elif request.user.role == 'mairie':
            # Les mairies voient toutes les analyses
            batches = BatchAnalysis.objects.all()
        else:
            # Les utilisateurs normaux voient seulement leurs analyses
            batches = BatchAnalysis.objects.filter(created_by=request.user)
        
        # Filtrer par statut si spécifié
        status_filter = request.query_params.get('status')
        if status_filter:
            batches = batches.filter(status=status_filter)
            
        # Paginer et sérialiser
        serializer = BatchAnalysisSerializer(batches, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'Erreur serveur: {str(e)}'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_ml_dataset(request):
    """
    Exporte un dataset complet pour entraînement ML
    
    GET /api/ml/export-dataset/
    
    Paramètres (optionnels):
    - include_annotations: Si True, inclut seulement les images annotées
    
    Retourne:
    - URL du fichier CSV généré
    """
    try:
        # Vérifier les permissions (admin ou mairie)
        if not (request.user.is_staff or request.user.role == 'mairie'):
            return Response({'error': 'Permissions insuffisantes'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Paramètres
        include_annotations = request.query_params.get('include_annotations', 'true').lower() == 'true'
        
        # Générer le dataset
        output_path = export_dataset(include_annotations=include_annotations)
        
        if not output_path:
            return Response({'error': 'Aucune donnée à exporter'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Générer l'URL du fichier
        file_url = request.build_absolute_uri(
            settings.MEDIA_URL + 'exports/' + os.path.basename(output_path)
        )
        
        return Response({
            'success': True,
            'file_url': file_url,
            'filename': os.path.basename(output_path),
            'export_date': datetime.now().isoformat()
        })
        
    except Exception as e:
        traceback.print_exc()
        return Response({'error': f'Erreur serveur: {str(e)}'}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
