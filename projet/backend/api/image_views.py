"""
Vues pour la gestion des images
"""
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import generics, status, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime, timedelta
import sys
import os
import zipfile
import tempfile
from PIL import Image as PILImage
from .models import Image, User
from .serializers import ImageSerializer, ImageUploadSerializer, ImageAnnotationSerializer

# Importer les fonctions ML
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Extraction_caracteristiques import extract_features, classify_by_rules
# Import du classifieur Canny MC
import sys as _sys
import os as _os
_sys.path.append(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))
from MC_canny_classifier import classify_canny

# Importer le connecteur mail
from .mail_connector import verifier_alerte_apres_upload

# Importer le système de classement
from .classement import traiter_points_upload


class ImageUploadView(generics.CreateAPIView):
    """
    Vue pour uploader une image.
    Compatible avec le frontend (accepte 'file' et 'image')
    """
    serializer_class = ImageUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Suppression des logs utilisateurs pour éviter toute fuite de données
        try:
            data = request.data.copy()
            
            # Gestion du champ 'file' vs 'image' pour compatibilité frontend
            if 'file' in request.FILES and 'image' not in request.FILES:
                data['image'] = request.FILES['file']
            
            # Récupérer les champs supplémentaires du frontend
            eclairage = data.get('eclairage', '')
            chevrons = data.get('chevrons', '')
            ouverte = data.get('ouverte', '')
            
            # Vérifications obligatoires
            if 'rue' not in data or not data['rue']:
                return Response(
                    {"detail": "La rue est obligatoire."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if 'ville' not in data or not data['ville']:
                return Response(
                    {"detail": "La ville est obligatoire."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            upload_serializer = self.serializer_class(data=data)
            if upload_serializer.is_valid():
                # Sauvegarder l'image
                image_instance = upload_serializer.save()
                image_instance.user = request.user
                
                # Stocker les métadonnées du frontend
                metadata = getattr(image_instance, 'metadata', {}) or {}
                metadata.update({
                    'frontend_data': {
                        'eclairage': eclairage,
                        'chevrons': chevrons,
                        'ouverte': ouverte
                    }
                })
                image_instance.metadata = metadata
                image_instance.save()
                
                # Extraire les caractéristiques et classifier
                try:
                    image_field = 'image' if 'image' in request.data else 'file'
                    if hasattr(request.data[image_field], 'seek'):
                        request.data[image_field].seek(0)
                    
                    features = extract_features(request.data[image_field])
                    image_path = image_instance.image.path if hasattr(image_instance.image, 'path') else None
                    
                    # Préparer les critères spécifiques pour l'analyse MC
                    mc_criteria = {
                        'eclairage': eclairage.lower() if eclairage else 'normal',
                        'ouverte': ouverte.lower() == 'true' if ouverte else False,
                        'chevrons': chevrons.lower() == 'true' if chevrons else False,
                        'exposition': 'pleine' if eclairage and 'soleil' in eclairage.lower() else 'normale'
                    }
                    
                    # Classification MC adaptée avec les critères spécifiques
                    classification = classify_by_rules(features, image_path, mc_criteria)

                    # --- AJOUT CLASSIFICATION CANNY MC ---
                    canny_result = None
                    if image_path:
                        canny_ratio, canny_label, (canny_top, canny_bottom) = classify_canny(image_path)
                        canny_result = {
                            'canny_ratio': float(canny_ratio),
                            'canny_label': str(canny_label),
                            'canny_top_count': int(canny_top),
                            'canny_bottom_count': int(canny_bottom)
                        }
                        image_instance.metadata['canny_mc'] = canny_result
                        
                        # Mise à jour des nouveaux champs directs
                        image_instance.canny_top_count = int(canny_top)
                        image_instance.canny_bottom_count = int(canny_bottom)
                        image_instance.canny_ratio = float(canny_ratio)
                        image_instance.canny_mc = str(canny_label)
                    # --- FIN AJOUT ---

                    # Mettre à jour l'instance avec l'analyse MC
                    image_instance.metadata.update(features)
                    image_instance.metadata['mc_criteria'] = mc_criteria
                    image_instance.metadata['analysis_method'] = 'mc'
                    
                    # Convertir toutes les métadonnées en format JSON-serializable
                    image_instance.metadata = make_json_serializable(image_instance.metadata)

                    image_instance.classification_auto = classification
                    image_instance.taille_fichier = features['technical']['file_size']
                    image_instance.dimensions = features['technical']['dimensions']
                    image_instance.couleur_moyenne = features['technical']['avg_color']
                    image_instance.contraste = features['technical']['contrast']
                    image_instance.jour_semaine = features['temporal']['day_of_week']

                    # Annotation automatique si possible
                    auto_annot = None
                    if classification in ['pleine', 'vide']:
                        auto_annot = classification
                    # Deep learning (YOLO)
                    try:
                        from .dl_integration import dl_service
                        dl_result = dl_service.process_image(image_instance, save_result=True)
                        if not auto_annot and dl_result and dl_result.get('classification') in ['pleine', 'vide']:
                            auto_annot = dl_result['classification']
                    except Exception:
                        pass
                    if auto_annot:
                        image_instance.annotation = auto_annot
                    image_instance.save()
                    
                    # Suppression des logs de classification
                    
                    # Déclencher automatiquement la vérification des alertes mail
                    try:
                        alerte_result = verifier_alerte_apres_upload(image_instance)
                    except Exception as e:
                        pass
                    
                    # Attribution des points pour l'utilisateur
                    points_result = None
                    try:
                        points_result = traiter_points_upload(request.user, image_instance)
                    except Exception as e:
                        pass
                except Exception as e:
                    pass
                
                response_serializer = ImageSerializer(image_instance, context={'request': request})
                response_data = response_serializer.data
                
                # Ajouter les informations de points si disponibles
                if points_result:
                    response_data['points_attribues'] = points_result
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            pass
            return Response(
                {"error": f"Erreur lors de l'upload: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImageListView(generics.ListAPIView):
    """
    Vue pour lister les images avec filtres par rôle
    """
    serializer_class = ImageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['rue', 'adresse']
    ordering_fields = ['date_creation', 'rue', 'id']
    ordering = ['-date_creation']
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        user_role = getattr(user, 'role', 'user')
        
        if user_role == 'admin':
            queryset = Image.objects.all()
        elif user_role == 'mairie':
            user_ville = getattr(user, 'ville_normalized', None)
            if not user_ville:
                queryset = Image.objects.none()
            else:
                queryset = Image.objects.filter(ville_normalized=user_ville)
        else:  # user
            queryset = Image.objects.filter(user=user)
        
        # Appliquer les filtres de requête
        annotation = self.request.query_params.get('annotation', None)
        if annotation is not None:
            queryset = queryset.filter(annotation=annotation)
            
        classification = self.request.query_params.get('classification', None)
        if classification is not None:
            queryset = queryset.filter(classification_auto=classification)
            
        rue = self.request.query_params.get('rue', None)
        if rue is not None and user_role != 'mairie':
            queryset = queryset.filter(rue__icontains=rue)
            
        ville = self.request.query_params.get('ville', None)
        if ville is not None:
            from .utils import normalize_name
            ville_norm = normalize_name(ville)
            queryset = queryset.filter(ville_normalized=ville_norm)
            
        return queryset


class ImageDetailView(generics.RetrieveAPIView):
    """
    Vue pour afficher les détails d'une image
    """
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        user_role = getattr(user, 'role', 'user')
        
        if user_role == 'admin':
            return Image.objects.all()
        elif user_role == 'mairie':
            user_ville_norm = getattr(user, 'ville_normalized', None)
            if not user_ville_norm:
                return Image.objects.none()
            return Image.objects.filter(ville_normalized=user_ville_norm)
        else:  # user
            return Image.objects.filter(user=user)


import json
try:
    import numpy as np
except ImportError:
    np = None

def make_json_serializable(obj):
    """
    Convertit récursivement un objet pour qu'il soit JSON-serializable
    """
    if isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif np and isinstance(obj, np.integer):
        return int(obj)
    elif np and isinstance(obj, np.floating):
        return float(obj)
    elif np and isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


class ImageAnnotationView(generics.UpdateAPIView):
    """
    Vue pour mettre à jour l'annotation d'une image
    """
    serializer_class = ImageAnnotationSerializer
    http_method_names = ['patch']
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        user_role = getattr(user, 'role', 'user')
        
        if user_role == 'admin':
            return Image.objects.all()
        elif user_role == 'mairie':
            user_ville = getattr(user, 'ville_normalized', None)
            if not user_ville:
                return Image.objects.none()
            return Image.objects.filter(ville_normalized=user_ville)
        else:  # user
            return Image.objects.filter(user=user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_upload_zip(request):
    """
    Endpoint pour uploader un batch d'images dans un fichier ZIP
    Compatible avec le frontend qui utilise /batch-upload-zip/
    """
    try:
        if 'zip_file' not in request.FILES:
            return Response({"detail": "Aucun fichier ZIP fourni."}, status=status.HTTP_400_BAD_REQUEST)
        
        zip_file = request.FILES['zip_file']
        rue = request.data.get('rue', '')
        ville = request.data.get('ville', '')
        
        if not rue or not ville:
            return Response({"detail": "Rue et ville sont obligatoires."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que c'est un fichier ZIP valide
        if not zipfile.is_zipfile(zip_file):
            return Response({"detail": "Le fichier fourni n'est pas un fichier ZIP valide."}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_images = []
        errors = []
        
        # Extraire et traiter les images du ZIP
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    continue  # Ignorer les fichiers non-image
                
                try:
                    # Extraire le fichier image
                    image_data = zip_ref.read(filename)
                    
                    # Créer une instance d'image directement
                    image_instance = Image(
                        user=request.user,
                        rue=rue,
                        ville=ville,
                        adresse=f"Batch upload - {filename}",
                    )
                    
                    # Sauvegarder le fichier image
                    from django.core.files.base import ContentFile
                    image_instance.image.save(
                        filename,
                        ContentFile(image_data),
                        save=False
                    )
                    
                    # Extraire les features ML si possible
                    try:
                        # Utiliser l'extraction ML
                        features = extract_features(image_instance.image.path)
                        classification = classify_by_rules(features)
                        
                        # Mettre à jour les champs ML
                        image_instance.ml_features = features
                        image_instance.classification = classification
                        image_instance.confidence_score = features.get('confidence', 0.0)
                    except Exception as ml_error:
                        print(f"[WARNING] Erreur ML pour {filename}: {ml_error}")
                        # Continuer sans les features ML
                    
                    image_instance.save()
                    uploaded_images.append({
                        'id': image_instance.id,
                        'filename': filename,
                        'classification': getattr(image_instance, 'classification', None)
                    })
                    
                except Exception as e:
                    errors.append(f"Erreur avec {filename}: {str(e)}")
        
        return Response({
            "detail": f"Batch traité avec succès. {len(uploaded_images)} images uploadées.",
            "uploaded_images": uploaded_images,
            "errors": errors
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def annotate_image(request, image_id):
    """
    Endpoint pour annoter une image
    Compatible avec le frontend qui utilise /annotate/<id>/
    """
    try:
        image = get_object_or_404(Image, id=image_id)
        
        # Vérifier les permissions
        user = request.user
        user_role = getattr(user, 'role', 'user')
        
        if user_role == 'user' and image.user != user:
            return Response(
                {"detail": "Vous ne pouvez annoter que vos propres images."},
                status=status.HTTP_403_FORBIDDEN
            )
        elif user_role == 'mairie':
            user_ville = getattr(user, 'ville_normalized', None)
            if not user_ville or image.ville_normalized != user_ville:
                return Response(
                    {"detail": "Vous ne pouvez annoter que les images de votre ville."},
                    status=status.HTTP_403_FORBIDDEN
                )
        # Admin peut tout annoter
        
        annotation = request.data.get('annotation')
        if annotation not in ['pleine', 'vide']:
            return Response(
                {"detail": "L'annotation doit être 'pleine' ou 'vide'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if annotation == 'vide' and user_role == 'mairie':
            image.delete()
            return Response({
                "detail": "Image supprimée car marquée comme vide par la mairie.",
                "image_id": image_id,
                "annotation": annotation
            }, status=status.HTTP_200_OK)
        else:
            image.annotation = annotation
            image.save()
            return Response({
                "detail": "Image annotée avec succès.",
                "image_id": image.id,
                "annotation": image.annotation
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
