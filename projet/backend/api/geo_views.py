"""
Vues pour la gestion géographique et cartographique
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import Image, Mairie

@api_view(['GET'])
def obtenir_coordonnees_ville_api(request):
    """
    API pour obtenir les coordonnées d'une ville
    """
    ville = request.GET.get('ville')
    
    if not ville:
        return Response({
            'error': 'Paramètre "ville" requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .geo_utils import obtenir_coordonnees_ville
        coordonnees = obtenir_coordonnees_ville(ville)
        
        return Response({
            'success': True,
            'ville': ville,
            'coordonnees': coordonnees
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des coordonnées: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def coordonnees_carte_mairie(request):
    """
    API spécialisée pour le dashboard des mairies
    Retourne les coordonnées optimisées pour l'affichage de la carte
    """
    user = request.user
    
    if user.role != 'mairie':
        return Response({
            'error': 'Accès réservé aux comptes mairie'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        ville_mairie = user.ville
        
        if not ville_mairie:
            return Response({
                'error': 'Aucune ville configurée pour ce compte mairie'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtenir les coordonnées de la ville
        from .geo_utils import obtenir_coordonnees_ville
        coordonnees = obtenir_coordonnees_ville(ville_mairie)
        
        # Récupérer les images avec coordonnées GPS de cette ville
        from .utils import normalize_name
        ville_norm = normalize_name(ville_mairie)
        
        images_avec_gps = Image.objects.filter(
            ville_normalized=ville_norm,
            latitude__isnull=False,
            longitude__isnull=False
        ).values(
            'id', 'latitude', 'longitude', 'quartier', 
            'classification_auto', 'date_upload'
        )[:100]  # Limiter pour les performances
        
        # Statistiques par zone
        zones_stats = {}
        for image in images_avec_gps:
            quartier = image['quartier'] or 'Centre-ville'
            if quartier not in zones_stats:
                zones_stats[quartier] = {
                    'total': 0,
                    'pleines': 0,
                    'vides': 0,
                    'coordonnees': []
                }
            
            zones_stats[quartier]['total'] += 1
            if image['classification_auto'] == 'pleine':
                zones_stats[quartier]['pleines'] += 1
            else:
                zones_stats[quartier]['vides'] += 1
            
            zones_stats[quartier]['coordonnees'].append({
                'lat': float(image['latitude']),
                'lng': float(image['longitude']),
                'classification': image['classification_auto'],
                'date': image['date_upload'].isoformat() if image['date_upload'] else None
            })
        
        return Response({
            'success': True,
            'ville': ville_mairie,
            'coordonnees_centre': coordonnees,
            'images_carte': list(images_avec_gps),
            'zones_statistiques': zones_stats,
            'nombre_points': len(images_avec_gps)
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des données cartographiques: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def coordonnees_multiples_villes(request):
    """
    Obtient les coordonnées de plusieurs villes
    
    Paramètres GET:
    - villes: liste des villes séparées par des virgules
    ou récupère automatiquement toutes les villes avec des images
    """
    try:
        villes_param = request.GET.get('villes')
        
        if villes_param:
            # Villes spécifiées dans les paramètres
            villes_list = [v.strip() for v in villes_param.split(',')]
        else:
            # Récupérer toutes les villes avec des images
            villes_list = Image.objects.filter(
                ville_normalized__isnull=False
            ).values_list('ville_normalized', flat=True).distinct()
        
        from .geo_utils import obtenir_coordonnees_ville
        coordonnees = {}
        for ville in villes_list:
            try:
                coords = obtenir_coordonnees_ville(ville)
                coordonnees[ville] = coords
            except:
                coordonnees[ville] = None
        
        return Response({
            'success': True,
            'coordonnees_villes': coordonnees,
            'nombre_villes': len(coordonnees)
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des coordonnées: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def images_avec_coordonnees(request):
    """
    Récupère les images avec leurs coordonnées pour affichage sur carte
    
    Paramètres GET:
    - ville: filtrer par ville (optionnel)
    - limite: nombre maximum d'images (défaut: 100)
    - classification: filtrer par classification (pleine/vide)
    """
    try:
        # Paramètres de filtrage
        ville = request.GET.get('ville')
        limite = int(request.GET.get('limite', 100))
        classification = request.GET.get('classification')
        
        # Limiter le nombre maximum pour éviter la surcharge
        limite = min(limite, 500)
        
        # Query de base
        query = Image.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        # Appliquer les filtres
        if ville:
            query = query.filter(ville_normalized__icontains=ville)
        
        if classification in ['pleine', 'vide']:
            query = query.filter(classification_auto=classification)
        
        # Contrôle d'accès
        user = request.user
        if user.role == 'mairie' and user.ville_normalized:
            # Les mairies ne voient que leur ville
            query = query.filter(ville_normalized=user.ville_normalized)
        
        # Récupérer les données
        images_data = query.order_by('-date_upload').values(
            'id', 'latitude', 'longitude', 'ville_normalized', 'quartier', 
            'classification_auto', 'date_upload', 'uploaded_by__username'
        )[:limite]
        
        # Formater les données pour la carte
        markers = []
        for image in images_data:
            markers.append({
                'id': image['id'],
                'lat': float(image['latitude']),
                'lng': float(image['longitude']),
                'ville': image['ville_normalized'],
                'quartier': image['quartier'] or 'Non spécifié',
                'classification': image['classification_auto'],
                'date': image['date_upload'].isoformat(),
                'utilisateur': image['uploaded_by__username'] or 'Anonyme',
                'couleur': 'red' if image['classification_auto'] == 'pleine' else 'green'
            })
        
        return Response({
            'success': True,
            'markers': markers,
            'nombre_total': len(markers),
            'filtres': {
                'ville': ville,
                'classification': classification,
                'limite': limite
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des images: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def centre_carte_utilisateur(request):
    """
    Calcule le centre de carte optimal pour l'utilisateur connecté
    """
    try:
        user = request.user
        from .geo_utils import obtenir_coordonnees_ville
        
        if user.role == 'mairie' and user.ville:
            # Pour les mairies, centrer sur leur ville
            coordonnees = obtenir_coordonnees_ville(user.ville)
            zoom = 13
        elif user.role == 'user' and user.ville:
            # Pour les utilisateurs, centrer sur leur ville
            coordonnees = obtenir_coordonnees_ville(user.ville)
            zoom = 12
        else:
            # Pour les admins ou utilisateurs sans ville, centrer sur la France
            coordonnees = {'lat': 46.603354, 'lng': 1.888334}  # Centre de la France
            zoom = 6
        
        return Response({
            'success': True,
            'centre': coordonnees,
            'zoom_recommande': zoom,
            'utilisateur': {
                'role': user.role,
                'ville': user.ville
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors du calcul du centre: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
