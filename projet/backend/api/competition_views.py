from django.http import JsonResponse
from django.db.models import Q
from api.models import User

def competition_users(request):
    """
    Récupère le top 5 des utilisateurs avec le plus de points
    """
    try:
        # Récupérer les utilisateurs triés par points (descendant)
        top_users = User.objects.filter(
            role='user'  # Seulement les utilisateurs normaux, pas les mairies
        ).exclude(
            points=0  # Exclure ceux qui n'ont pas de points
        ).order_by('-points')[:5]  # Top 5
        
        users_data = []
        for user in top_users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'points': user.points,
                'avatar': user.avatar.url if user.avatar else None,
                'ville': user.ville
            })
        
        return JsonResponse({
            'success': True,
            'users': users_data,
            'total_count': len(users_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'users': []
        })

def competition_mairies(request):
    """
    Récupère le top 5 des mairies avec le plus de points
    """
    try:
        # Récupérer les mairies triées par points (descendant)
        top_mairies = User.objects.filter(
            role='mairie'  # Seulement les mairies
        ).exclude(
            points=0  # Exclure celles qui n'ont pas de points
        ).order_by('-points')[:5]  # Top 5
        
        mairies_data = []
        for mairie in top_mairies:
            mairies_data.append({
                'id': mairie.id,
                'ville': mairie.ville or mairie.username,
                'points': mairie.points,
                'logo': mairie.avatar.url if mairie.avatar else None,
                'email': mairie.email
            })
        
        return JsonResponse({
            'success': True,
            'mairies': mairies_data,
            'total_count': len(mairies_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'mairies': []
        })
