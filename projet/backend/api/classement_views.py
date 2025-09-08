"""
Vues pour le système de classement
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .classement import ClassementManager

@api_view(['GET'])
def classement_global(request):
    """
    Retourne le classement global des utilisateurs
    """
    try:
        limite = int(request.GET.get('limite', 50))
        limite = min(limite, 100)  # Maximum 100
        
        classement = ClassementManager.get_classement_global(limite)
        
        return Response({
            'success': True,
            'classement': classement,
            'total': len(classement)
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération du classement: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def classement_ville(request):
    """
    Retourne le classement pour une ville spécifique
    """
    try:
        ville = request.GET.get('ville')
        if not ville:
            return Response({
                'error': 'Paramètre ville requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        limite = int(request.GET.get('limite', 20))
        limite = min(limite, 50)  # Maximum 50 pour les villes
        
        classement = ClassementManager.get_classement_ville(ville, limite)
        
        return Response({
            'success': True,
            'ville': ville,
            'classement': classement,
            'total': len(classement)
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération du classement: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_stats(request):
    """
    Retourne les statistiques détaillées de l'utilisateur connecté
    """
    try:
        stats = ClassementManager.get_stats_utilisateur(request.user)
        
        return Response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mon_classement(request):
    """
    Retourne la position de l'utilisateur dans les classements
    """
    try:
        user = request.user
        
        # Classement global
        rang_global = ClassementManager.get_stats_utilisateur(user)['rang_global']
        
        # Classement ville
        rang_ville = None
        if user.ville_normalized:
            classement_ville = ClassementManager.get_classement_ville(user.ville_normalized, 1000)
            for item in classement_ville:
                if item['user_id'] == user.id:
                    rang_ville = item['rang']
                    break
        
        # Utilisateurs autour de moi dans le classement global
        from .models import User
        users_avant = list(User.objects.filter(
            role='user',
            points__gt=user.points
        ).order_by('points')[:3])
        
        users_apres = list(User.objects.filter(
            role='user',
            points__lt=user.points
        ).order_by('-points')[:3])
        
        return Response({
            'success': True,
            'mon_rang': {
                'global': rang_global,
                'ville': rang_ville
            },
            'mes_points': user.points,
            'contexte': {
                'users_avant': [{'username': u.username, 'points': u.points} for u in users_avant],
                'users_apres': [{'username': u.username, 'points': u.points} for u in users_apres]
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération du classement: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def competition_users(request):
    """
    Retourne le top des utilisateurs pour la compétition
    """
    try:
        from .models import User
        
        # Récupérer les utilisateurs triés par points
        users = User.objects.filter(role='user').order_by('-points')[:10]
        
        users_data = []
        for user in users:
            users_data.append({
                'username': user.username,
                'points': user.points,
                'avatar': user.avatar.url if user.avatar else '/default-avatar.png',
                'ville': user.ville
            })
        
        return Response({
            'success': True,
            'users': users_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des utilisateurs: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def competition_mairies(request):
    """
    Retourne le top des mairies pour la compétition
    """
    try:
        from .models import User, Mairie
        
        # Récupérer les mairies (User avec role='mairie') triées par points
        mairies = User.objects.filter(role='mairie').order_by('-points')[:5]
        
        mairies_data = []
        for mairie in mairies:
            # Utiliser les points réels stockés dans la base de données
            mairies_data.append({
                'ville': mairie.ville,
                'points': mairie.points,  # Points réels de la base
                'logo': mairie.avatar.url if mairie.avatar else '/default-logo.png',
                'email': mairie.email,
                'username': mairie.username
            })
        
        return Response({
            'success': True,
            'mairies': mairies_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des mairies: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
