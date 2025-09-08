"""
Vues pour la gestion des dashboards par rôle
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import Image, User
from .serializers import ImageSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_user(request):
    """
    Dashboard spécifique aux utilisateurs
    """
    user = request.user
    
    if user.role != 'user':
        return Response({
            'error': 'Accès refusé'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Statistiques utilisateur
    user_images = Image.objects.filter(user=user)
    
    stats = {
        'user_info': {
            'username': user.username,
            'email': user.email,
            'points': user.points,
            'ville': user.ville
        },
        'user_stats': {
            'total_uploads': user_images.count(),
            'images_pleines': user_images.filter(classification_auto='pleine').count(),
            'images_vides': user_images.filter(classification_auto='vide').count(),
        },
        'recent_uploads': ImageSerializer(
            user_images.order_by('-date_creation')[:5], 
            many=True, 
            context={'request': request}
        ).data
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_mairie(request):
    """
    Dashboard spécifique aux mairies avec coordonnées géographiques
    """
    user = request.user
    
    if user.role != 'mairie':
        return Response({
            'error': 'Accès refusé'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Importer les utilitaires géographiques
    try:
        from .geo_utils import obtenir_coordonnees_ville
    except ImportError as e:
        return Response({
            'error': 'Erreur de configuration géographique'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Statistiques pour la mairie
    all_images = Image.objects.all()
    
    # Filtrer par ville si spécifiée
    ville_mairie = user.ville
    coordonnees_ville = None
    
    if ville_mairie:
        try:
            from .utils import normalize_name
            ville_norm = normalize_name(ville_mairie)
            all_images = all_images.filter(ville_normalized=ville_norm)
            
            # Obtenir les coordonnées géographiques de la ville de la mairie
            coordonnees_ville = obtenir_coordonnees_ville(ville_mairie)
            
        except Exception as e:
            # Coordonnées par défaut (centre de la France)
            coordonnees_ville = {'lat': 46.603354, 'lng': 1.888334, 'nom': 'France'}
    else:
        # Pas de ville spécifiée, utiliser coordonnées par défaut
        coordonnees_ville = {'lat': 46.603354, 'lng': 1.888334, 'nom': 'France'}
    
    try:
        # Récupérer les zones avec poubelles pleines dans cette ville
        zones_critiques = all_images.filter(classification_auto='pleine').values('rue').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Récupérer les coordonnées des images pour la carte
        images_avec_coordonnees = all_images.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).values('id', 'latitude', 'longitude', 'rue', 'classification_auto', 'date_creation')[:100]
        
        # Obtenir les informations de la mairie depuis le modèle Mairie
        from .models import Mairie
        mairie_info = None
        try:
            if ville_mairie:
                mairie_obj = Mairie.objects.filter(nom__iexact=ville_mairie).first()
                if mairie_obj:
                    mairie_info = {
                        'nom': mairie_obj.nom,
                        'email': mairie_obj.email,
                        'seuil_alertes': mairie_obj.seuil_alertes,
                        'nb_poubelles': mairie_obj.nb_poubelles,
                        'points': mairie_obj.points
                    }
        except Exception as e:
            pass
        
        stats = {
            'mairie_info': {
                'username': user.username,
                'email': user.email,
                'ville': ville_mairie or 'Non spécifiée',
                'coordonnees': coordonnees_ville,
                'mairie_details': mairie_info
            },
            'geo_data': {
                'centre_carte': coordonnees_ville,
                'zoom_initial': 13,  # Zoom approprié pour une ville
                'images_carte': list(images_avec_coordonnees)
            },
            'global_stats': {
                'total_images': all_images.count(),
                'images_pleines': all_images.filter(classification_auto='pleine').count(),
                'images_vides': all_images.filter(classification_auto='vide').count(),
                'zones_critiques': list(zones_critiques)
            },
            'recent_reports': ImageSerializer(
                all_images.order_by('-date_creation')[:10], 
                many=True, 
                context={'request': request}
            ).data
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return Response({
            'error': f'Erreur serveur: {str(e)}',
            'ville': ville_mairie,
            'coordonnees_fallback': {'lat': 46.603354, 'lng': 1.888334, 'nom': 'France'}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_admin(request):
    """
    Dashboard spécifique aux administrateurs avec données géographiques
    """
    user = request.user
    
    if user.role != 'admin':
        return Response({
            'error': 'Accès refusé'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Importer les utilitaires géographiques
    from .geo_utils import obtenir_coordonnees_multiples_villes, calculer_centre_geographique
    
    # Statistiques globales pour l'admin
    all_images = Image.objects.all()
    all_users = User.objects.all()
    
    # Récupérer les villes avec des images
    villes_avec_images = all_images.filter(
        ville_normalized__isnull=False
    ).values_list('ville_normalized', flat=True).distinct()
    
    # Obtenir les coordonnées de toutes les villes
    coordonnees_villes = obtenir_coordonnees_multiples_villes(list(villes_avec_images))
    
    # Calculer le centre géographique
    centre_geo = calculer_centre_geographique(list(coordonnees_villes.values()))
    
    # Statistiques par ville
    stats_villes = []
    for ville in villes_avec_images:
        if ville:
            ville_images = all_images.filter(ville_normalized=ville)
            stats_villes.append({
                'ville': ville,
                'coordonnees': coordonnees_villes.get(ville),
                'total_images': ville_images.count(),
                'images_pleines': ville_images.filter(classification_auto='pleine').count(),
                'images_vides': ville_images.filter(classification_auto='vide').count(),
                'utilisateurs_actifs': ville_images.values('uploaded_by').distinct().count()
            })
    
    # Récupérer les images avec coordonnées pour la carte
    images_avec_coordonnees = all_images.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).values('id', 'latitude', 'longitude', 'ville_normalized', 'rue', 'classification_auto', 'date_creation')[:200]
    
    stats = {
        'admin_info': {
            'username': user.username,
            'email': user.email
        },
        'geo_data': {
            'centre_carte': centre_geo,
            'zoom_initial': 6,  # Zoom pour voir toute la France
            'coordonnees_villes': coordonnees_villes,
            'images_carte': list(images_avec_coordonnees)
        },
        'system_stats': {
            'total_users': all_users.count(),
            'total_mairies': all_users.filter(role='mairie').count(),
            'total_images': all_images.count(),
            'images_pleines': all_images.filter(classification_auto='pleine').count(),
            'images_vides': all_images.filter(classification_auto='vide').count(),
            'nombre_villes': len(stats_villes)
        },
        'stats_villes': stats_villes,
        'user_stats': {
            'most_active_users': [
                {
                    'username': u.username,
                    'uploads': Image.objects.filter(uploaded_by=u).count(),
                    'ville': u.ville
                }
                for u in all_users.filter(role='user').annotate(
                    upload_count=Count('uploaded_images')
                ).order_by('-upload_count')[:5]
            ]
        },
        'recent_activity': ImageSerializer(
            all_images.order_by('-date_creation')[:15], 
            many=True, 
            context={'request': request}
        ).data
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_user_data(request):
    """
    API spécifique pour récupérer les données du dashboard utilisateur
    """
    user = request.user
    
    # Compter les images uploadées par l'utilisateur
    user_images_count = Image.objects.filter(user=user).count()
    
    # Calculer le rang
    users_with_more_images = User.objects.annotate(
        image_count=Count('image')
    ).filter(image_count__gt=user_images_count).count()
    rank = users_with_more_images + 1
    
    # Calculer les points (10 points par image)
    points = user_images_count * 10
    
    response_data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar': '/account/plante.png',
            'rank': rank,
            'points': points,
            'role': getattr(user, 'role', 'user'),
            'ville': getattr(user, 'ville', ''),
        },
        'stats': {
            'images_uploaded': user_images_count,
        }
    }
    
    return Response(response_data, status=status.HTTP_200_OK)
