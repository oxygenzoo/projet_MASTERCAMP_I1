from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Image
# Import des fonctions d'aide
from .admin_helpers import (
    get_mairie_stats, 
    tester_alerte_mairie, 
    modifier_seuil_mairie, 
    get_historique_alertes
)

@staff_member_required
def dashboard_admin(request):
    """
    Vue du tableau de bord administrateur pour analyser les besoins
    """
    # Statistiques générales
    total_images = Image.objects.count()
    images_pleines = Image.objects.filter(
        Q(annotation='pleine') | Q(classification_auto='pleine')
    ).count()
    images_vides = Image.objects.filter(
        Q(annotation='vide') | Q(classification_auto='vide')
    ).count()
    
    # Analyses récentes (dernières 24h)
    hier = timezone.now() - timedelta(days=1)
    analyses_recentes = Image.objects.filter(date_creation__gte=hier)
    
    # Poubelles nécessitant une intervention (pleines)
    poubelles_pleines = analyses_recentes.filter(
        Q(annotation='pleine') | Q(classification_auto='pleine')
    ).values('quartier', 'adresse').annotate(
        nombre=Count('id')
    ).order_by('-nombre')
    
    # Statistiques par quartier
    stats_quartiers = Image.objects.values('quartier').annotate(
        total=Count('id'),
        pleines=Count('id', filter=Q(Q(annotation='pleine') | Q(classification_auto='pleine'))),
        vides=Count('id', filter=Q(Q(annotation='vide') | Q(classification_auto='vide')))
    ).order_by('-pleines')
    
    # Images nécessitant une vérification (divergence entre IA et annotation)
    images_divergentes = Image.objects.filter(
        annotation__isnull=False,
        classification_auto__isnull=False
    ).exclude(annotation=F('classification_auto'))
    
    # Alertes simplifiées basées sur les quartiers
    alertes_quartiers = []
    for stat in stats_quartiers:
        if stat['pleines'] > 5:  # Seuil d'alerte simple
            alertes_quartiers.append({
                'quartier': stat['quartier'],
                'nombre_pleines': stat['pleines'],
                'seuil': 5,
                'urgence': 'critique' if stat['pleines'] > 10 else 'normale'
            })
    
    context = {
        'total_images': total_images,
        'images_pleines': images_pleines,
        'images_vides': images_vides,
        'taux_remplissage': round((images_pleines / total_images * 100) if total_images > 0 else 0, 1),
        'analyses_recentes': analyses_recentes.count(),
        'poubelles_pleines': poubelles_pleines,
        'stats_quartiers': stats_quartiers,
        'images_divergentes': images_divergentes,
        'alertes_quartiers': alertes_quartiers,
    }
    
    return render(request, 'admin/dashboard_admin.html', context)

@staff_member_required
def analyse_details(request, image_id):
    """
    Vue détaillée d'une analyse spécifique
    """
    image = get_object_or_404(Image, id=image_id)
    
    # Métadonnées d'analyse
    metadata = image.metadata or {}
    
    # Vérifier la cohérence entre annotation et classification
    coherence = None
    if image.annotation and image.classification_auto:
        coherence = image.annotation == image.classification_auto
    
    context = {
        'image': image,
        'metadata': metadata,
        'coherence': coherence,
        'necessite_verification': image.annotation != image.classification_auto if image.annotation and image.classification_auto else False
    }
    
    return render(request, 'admin/analyse_details.html', context)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mairie_stats_view(request):
    """
    Vue pour obtenir les statistiques des mairies et leurs seuils
    Accessible aux administrateurs uniquement
    """
    if request.user.role != 'admin':
        return Response(
            {"error": "Accès refusé. Administrateur requis."}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        stats = get_mairie_stats()
        return Response({
            "success": True,
            "data": stats,
            "total_mairies": len(stats)
        })
    except Exception as e:
        return Response(
            {"error": f"Erreur lors de la récupération des stats: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def modifier_seuil_view(request):
    """
    Vue pour modifier le seuil d'alerte d'une mairie
    Accessible aux administrateurs uniquement
    """
    if request.user.role != 'admin':
        return Response(
            {"error": "Accès refusé. Administrateur requis."}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    mairie_id = request.data.get('mairie_id')
    nouveau_seuil = request.data.get('nouveau_seuil')
    
    if not mairie_id or not nouveau_seuil:
        return Response(
            {"error": "mairie_id et nouveau_seuil sont requis"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        nouveau_seuil = int(nouveau_seuil)
        resultat = modifier_seuil_mairie(mairie_id, nouveau_seuil)
        
        if resultat['success']:
            return Response(resultat)
        else:
            return Response(resultat, status=status.HTTP_400_BAD_REQUEST)
            
    except ValueError:
        return Response(
            {"error": "Le seuil doit être un nombre entier"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"error": f"Erreur lors de la modification: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tester_alerte_view(request):
    """
    Vue pour tester le système d'alerte d'une mairie
    Accessible aux administrateurs uniquement
    """
    if request.user.role != 'admin':
        return Response(
            {"error": "Accès refusé. Administrateur requis."}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    mairie_id = request.data.get('mairie_id')
    
    if not mairie_id:
        return Response(
            {"error": "mairie_id est requis"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        resultat = tester_alerte_mairie(mairie_id)
        
        if resultat['success']:
            return Response(resultat)
        else:
            return Response(resultat, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response(
            {"error": f"Erreur lors du test: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historique_alertes_view(request):
    """
    Vue pour obtenir l'historique des alertes
    Accessible aux administrateurs uniquement
    """
    if request.user.role != 'admin':
        return Response(
            {"error": "Accès refusé. Administrateur requis."}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        jours = int(request.GET.get('jours', 7))
        historique = get_historique_alertes(jours)
        
        return Response({
            "success": True,
            "data": historique,
            "periode_jours": jours
        })
    except Exception as e:
        return Response(
            {"error": f"Erreur lors de la récupération de l'historique: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
