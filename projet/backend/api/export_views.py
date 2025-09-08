"""
Vues pour l'export CSV des poubelles pleines
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .csv_export import CSVExportManager
import json

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_poubelles_pleines_csv(request):
    """
    Exporte les poubelles pleines en CSV avec filtres
    Accessible aux mairies (leur ville) et admins (toutes)
    """
    try:
        user = request.user
        
        # Préparer les filtres
        filtres = {}
        
        # Filtres disponibles pour tous
        if request.GET.get('date_debut'):
            filtres['date_debut'] = request.GET.get('date_debut')
        if request.GET.get('date_fin'):
            filtres['date_fin'] = request.GET.get('date_fin')
        if request.GET.get('quartier'):
            filtres['quartier'] = request.GET.get('quartier')
        
        # Contrôle d'accès
        if user.role == 'admin':
            # Admin peut tout voir
            if request.GET.get('ville'):
                filtres['ville'] = request.GET.get('ville')
            if request.GET.get('utilisateur'):
                filtres['utilisateur'] = request.GET.get('utilisateur')
        elif user.role == 'mairie':
            # Mairie ne voit que sa ville
            if user.ville_normalized:
                filtres['ville'] = user.ville_normalized
            else:
                return Response({
                    'error': 'Ville non configurée pour ce compte mairie'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Utilisateur normal ne peut pas exporter
            return Response({
                'error': 'Accès refusé. Compte mairie ou admin requis.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Générer le CSV
        df, nom_fichier = CSVExportManager.generer_csv_poubelles_pleines(filtres)
        
        if df.empty:
            return Response({
                'success': True,
                'message': 'Aucune poubelle pleine trouvée avec ces critères',
                'nombre_resultats': 0
            })
        
        # Créer la réponse HTTP avec le CSV
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
        
        # Ajouter le BOM pour Excel
        response.write('\ufeff')
        
        # Écrire le CSV
        df.to_csv(response, index=False, sep=';', encoding='utf-8')
        
        return response
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de l\'export: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_statistiques_villes_csv(request):
    """
    Exporte les statistiques par ville en CSV
    Accessible aux admins uniquement
    """
    try:
        if request.user.role != 'admin':
            return Response({
                'error': 'Accès restreint aux administrateurs'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Générer le CSV des statistiques
        df, nom_fichier = CSVExportManager.generer_csv_statistiques_ville()
        
        if df.empty:
            return Response({
                'success': True,
                'message': 'Aucune donnée disponible',
                'nombre_villes': 0
            })
        
        # Créer la réponse HTTP
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
        
        # Ajouter le BOM pour Excel
        response.write('\ufeff')
        
        # Écrire le CSV
        df.to_csv(response, index=False, sep=';', encoding='utf-8')
        
        return response
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de l\'export: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_export_csv(request):
    """
    Prévisualise les données qui seraient exportées
    Utile pour vérifier avant de télécharger
    """
    try:
        user = request.user
        
        # Mêmes filtres que l'export
        filtres = {}
        
        if request.GET.get('date_debut'):
            filtres['date_debut'] = request.GET.get('date_debut')
        if request.GET.get('date_fin'):
            filtres['date_fin'] = request.GET.get('date_fin')
        if request.GET.get('quartier'):
            filtres['quartier'] = request.GET.get('quartier')
        
        # Contrôle d'accès
        if user.role == 'admin':
            if request.GET.get('ville'):
                filtres['ville'] = request.GET.get('ville')
            if request.GET.get('utilisateur'):
                filtres['utilisateur'] = request.GET.get('utilisateur')
        elif user.role == 'mairie':
            if user.ville_normalized:
                filtres['ville'] = user.ville_normalized
            else:
                return Response({
                    'error': 'Ville non configurée pour ce compte mairie'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Accès refusé'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Générer un aperçu (maximum 10 lignes)
        df, nom_fichier = CSVExportManager.generer_csv_poubelles_pleines(filtres)
        
        # Limiter à 10 résultats pour l'aperçu
        preview_df = df.head(10)
        
        return Response({
            'success': True,
            'apercu': preview_df.to_dict('records'),
            'nombre_total': len(df),
            'nombre_colonnes': len(df.columns),
            'colonnes': list(df.columns),
            'nom_fichier': nom_fichier,
            'filtres_appliques': filtres
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la prévisualisation: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_export_disponible(request):
    """
    Retourne les statistiques sur les données disponibles pour export
    """
    try:
        user = request.user
        
        if user.role not in ['admin', 'mairie']:
            return Response({
                'error': 'Accès refusé'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from .models import Image
        from django.utils import timezone
        from datetime import timedelta
        
        # Filtre par rôle
        if user.role == 'mairie' and user.ville_normalized:
            base_query = Image.objects.filter(
                classification_auto='pleine',
                ville_normalized=user.ville_normalized
            )
        else:
            base_query = Image.objects.filter(classification_auto='pleine')
        
        # Statistiques temporelles
        maintenant = timezone.now()
        
        stats = {
            'total_poubelles_pleines': base_query.count(),
            'derniere_24h': base_query.filter(date_upload__gte=maintenant - timedelta(hours=24)).count(),
            'derniere_semaine': base_query.filter(date_upload__gte=maintenant - timedelta(days=7)).count(),
            'dernier_mois': base_query.filter(date_upload__gte=maintenant - timedelta(days=30)).count(),
            'plus_ancienne': base_query.order_by('date_upload').first().date_upload.isoformat() if base_query.exists() else None,
            'plus_recente': base_query.order_by('-date_upload').first().date_upload.isoformat() if base_query.exists() else None,
        }
        
        # Répartition par ville (pour admin)
        if user.role == 'admin':
            villes = base_query.values_list('ville_normalized', flat=True).distinct()
            stats['nombre_villes'] = len([v for v in villes if v])
            stats['villes_disponibles'] = list(villes)
        
        # Répartition par quartier
        quartiers = base_query.values_list('quartier', flat=True).distinct()
        stats['nombre_quartiers'] = len([q for q in quartiers if q])
        
        return Response({
            'success': True,
            'stats': stats,
            'role_utilisateur': user.role,
            'ville_filtree': user.ville_normalized if user.role == 'mairie' else None
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
