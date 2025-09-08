"""
Vue principale - Index et imports des autres vues
"""
from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
import sys
import os
from datetime import datetime, timedelta
from .models import Image, User
from .serializers import ImageSerializer, ImageUploadSerializer, ImageAnnotationSerializer

# Imports des autres fichiers de vues
from .user_views import get_user_data, save_user_profile
from .auth_views import register_user, login_user, logout_user, user_profile
from .dashboard_views import dashboard_user, dashboard_mairie, dashboard_admin, dashboard_user_data
from .image_views import ImageUploadView, ImageListView, ImageDetailView, ImageAnnotationView

# Importer les fonctions ML
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Extraction_caracteristiques import extract_features, classify_by_rules


def index(request):
    """Page d'accueil de l'API"""
    return JsonResponse({"message": "Bienvenue à l'API de MasterCamps pour l'optimisation des poubelles"})


@api_view(['GET'])
@permission_classes([AllowAny])
def test_user_data(request):
    """
    API de test pour vérifier si les données utilisateur sont accessibles
    """
    return Response({
        'username': 'Utilisateur Test',
        'email': 'test@example.com',
        'rank': 1,
        'points': 100,
        'message': 'API de test fonctionnelle'
    }, status=status.HTTP_200_OK)


def calculate_ml_metrics(queryset):
    """
    Calcule les métriques d'évaluation ML (accuracy, precision, recall, F1-score)
    """
    verified = queryset.filter(
        annotation__isnull=False,
        classification_auto__isnull=False
    )
    
    if not verified.exists():
        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'verified_count': 0,
            'confusion_matrix': {
                'true_positive': 0, 
                'false_positive': 0,
                'true_negative': 0,
                'false_negative': 0
            }
        }
    
    # Calculer les éléments de la matrice de confusion
    true_positive = verified.filter(classification_auto='pleine', annotation='pleine').count()
    false_positive = verified.filter(classification_auto='pleine', annotation='vide').count()
    true_negative = verified.filter(classification_auto='vide', annotation='vide').count()
    false_negative = verified.filter(classification_auto='vide', annotation='pleine').count()
    
    total = verified.count()
    accuracy = (true_positive + true_negative) / total if total > 0 else 0.0
    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0.0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'verified_count': total,
        'confusion_matrix': {
            'true_positive': true_positive,
            'false_positive': false_positive,
            'true_negative': true_negative,
            'false_negative': false_negative
        }
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Vue pour récupérer les statistiques du dashboard.
    Restaurée depuis l'ancien fichier views
    """
    from django.http import HttpResponse
    import csv
    
    # Déterminer le rôle et filtrer le queryset
    user = request.user
    user_role = getattr(user, 'role', 'user')
    
    if user_role == 'admin':
        queryset = Image.objects.all()
    elif user_role == 'mairie':
        user_ville_norm = getattr(user, 'ville_normalized', None)
        if not user_ville_norm:
            return Response(
                {"error": "Votre compte mairie n'est associé à aucune ville."},
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset = Image.objects.filter(ville_normalized=user_ville_norm)
    else:  # user_role == 'user'
        queryset = Image.objects.filter(user=user)
    
    # Compter le nombre total d'images
    total_images = queryset.count()
    
    # Si aucune image n'est trouvée
    if total_images == 0:
        return Response({
            'total_images': 0,
            'annotation_counts': [],
            'auto_classification': [],
            'classification_accuracy': 0,
        })
    
    # Annotations manuelles
    annotation_counts = list(queryset.values('annotation')
                            .annotate(count=Count('annotation'))
                            .order_by('annotation'))
    
    # Classification automatique
    auto_classification = list(queryset.values('classification_auto')
                              .annotate(count=Count('classification_auto'))
                              .order_by('classification_auto'))
    
    # Calculer les métriques ML
    ml_metrics = calculate_ml_metrics(queryset)
    accuracy = ml_metrics['accuracy']
    
    return Response({
        'total_images': total_images,
        'annotation_counts': annotation_counts,
        'auto_classification': auto_classification,
        'classification_accuracy': accuracy,
        'ml_metrics': ml_metrics,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_images_csv(request):
    """
    Vue pour exporter les données d'images au format CSV
    Restaurée depuis l'ancien fichier views
    """
    from django.http import HttpResponse
    import csv
    
    # Déterminer le rôle et filtrer le queryset
    user = request.user
    user_role = getattr(user, 'role', 'user')
    
    if user_role == 'admin':
        queryset = Image.objects.all().order_by('-date_creation')
    elif user_role == 'mairie':
        user_ville_norm = getattr(user, 'ville_normalized', None)
        if not user_ville_norm:
            return Response(
                {"error": "Votre compte mairie n'est associé à aucune ville."},
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset = Image.objects.filter(ville_normalized=user_ville_norm).order_by('-date_creation')
    else:  # user_role == 'user'
        queryset = Image.objects.filter(user=user).order_by('-date_creation')
    
    # Créer la réponse HTTP avec le fichier CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="images_export.csv"'
    
    writer = csv.writer(response)
    # En-têtes du CSV
    writer.writerow([
        'ID', 'Date création', 'Annotation', 'Classification auto', 
        'Latitude', 'Longitude', 'Adresse', 'Rue', 
        'Taille fichier', 'Dimensions', 'Couleur moyenne', 'Contraste', 
        'Jour semaine'
    ])
    
    # Données
    for image in queryset:
        writer.writerow([
            image.id,
            image.date_creation,
            image.annotation,
            image.classification_auto,
            image.latitude,
            image.longitude,
            image.adresse,
            image.rue,
            image.taille_fichier,
            image.dimensions,
            image.couleur_moyenne,
            image.contraste,
            image.jour_semaine
        ])
    
    return response


@api_view(['GET'])
def rue_analysis(request):
    """
    Vue pour analyser les données par rue
    """
    rue_stats = []
    # Récupérer toutes les rues distinctes
    rues = Image.objects.exclude(rue__isnull=True)\
                        .values_list('rue', flat=True)\
                        .distinct()
    for rue in rues:
        # Filtrer les images par rue
        qs = Image.objects.filter(rue=rue)
        # Compter le nombre d'images
        total = qs.count()
        # Compter par annotation
        pleines = qs.filter(annotation='pleine').count()
        vides = qs.filter(annotation='vide').count()
        # Calculer le taux de poubelles pleines
        taux_pleines = (pleines / total) if total > 0 else 0
        # Ajouter aux statistiques
        rue_stats.append({
            'rue': rue,
            'total_images': total,
            'poubelles_pleines': pleines,
            'poubelles_vides': vides,
            'taux_pleines': taux_pleines,
        })
    return Response({
        'rue_stats': rue_stats,
        'total_rues': len(rue_stats)
    })


@api_view(['GET'])
def recent_uploads(request):
    """
    Vue pour les uploads récents
    Restaurée depuis l'ancien fichier views
    """
    recent_images = Image.objects.all().order_by('-date_creation')[:5]
    serializer = ImageSerializer(recent_images, many=True, context={'request': request})
    
    return Response(serializer.data)
