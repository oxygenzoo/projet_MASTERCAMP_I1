"""
Vues pour la gestion des utilisateurs et authentification
"""
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Count
from .models import Image, User


def sync_mairie_accounts():
    """
    Fonction utilitaire pour synchroniser les comptes mairie avec les villes
    """
    from .models import Mairie
    
    # Récupérer tous les utilisateurs mairie
    mairie_users = User.objects.filter(role='mairie')
    
    for user in mairie_users:
        if not user.ville:
            try:
                # Chercher la mairie correspondante
                mairie = Mairie.objects.get(email=user.email)
                user.ville = mairie.nom
                user.save()
                print(f"[SYNC] Utilisateur {user.email} associé à la ville {mairie.nom}")
            except Mairie.DoesNotExist:
                print(f"[WARNING] Aucune mairie trouvée pour l'email {user.email}")


@api_view(['POST'])
@permission_classes([AllowAny])
def create_mairie_account(request):
    """
    Créer un compte utilisateur pour une mairie existante
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'error': 'Email et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si la mairie existe
        from .models import Mairie
        try:
            mairie = Mairie.objects.get(email=email)
        except Mairie.DoesNotExist:
            return Response({
                'error': 'Aucune mairie trouvée avec cet email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Créer le compte utilisateur
        user = User.objects.create_user(
            username=f"mairie_{mairie.nom.lower().replace(' ', '_')}",
            email=email,
            password=password,
            role='mairie',
            ville=mairie.nom
        )
        
        # Créer le token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Compte mairie créé avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'ville': user.ville
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la création: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    """
    API pour récupérer les données utilisateur (nom, email, rang, points)
    Format exact attendu par le frontend
    """
    user = request.user
    # Suppression des logs utilisateurs pour éviter toute fuite de données
    
    # Calculer le nombre d'images uploadées
    user_images_count = Image.objects.filter(user=user).count()
    
    # Calculer le rang
    users_with_more_images = User.objects.annotate(
        image_count=Count('image')
    ).filter(image_count__gt=user_images_count).count()
    rank = users_with_more_images + 1
    
    # Calculer les points (10 points par image)
    points = user_images_count * 10
    
    response_data = {
        'username': user.username,
        'email': user.email,
        'rank': rank,
        'points': points,
    }
    
    # Suppression des logs utilisateurs pour éviter toute fuite de données
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_user_profile(request):
    """
    API pour sauvegarder le profil utilisateur
    """
    try:
        user = request.user
        data = request.data
        
        print(f"[DEBUG] Sauvegarde profil pour: {user.username}")
        print(f"[DEBUG] Données reçues: {data}")
        
        if 'username' in data and data['username']:
            user.username = data['username']
        if 'email' in data and data['email']:
            user.email = data['email']
            
        user.save()
        
        return Response({
            'success': True,
            'message': 'Profil sauvegardé avec succès'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"[ERREUR] Sauvegarde profil: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    """
    API pour récupérer les données utilisateur (nom, email, rang, points)
    Format attendu par le frontend DashboardUser.vue
    """
    user = request.user
    print(f"[DEBUG] Récupération données pour: {user.username}")
    
    # Calculer le nombre d'images uploadées par l'utilisateur
    user_images_count = Image.objects.filter(user=user).count()
    
    # Calculer le rang basé sur le nombre d'images
    users_with_more_images = User.objects.annotate(
        image_count=Count('image')
    ).filter(image_count__gt=user_images_count).count()
    rank = users_with_more_images + 1
    
    # Calculer les points (10 points par image uploadée)
    points = user_images_count * 10
    
    response_data = {
        'username': user.username,
        'email': user.email,
        'rank': rank,
        'points': points,
        'avatar': '/account/plante.png'  # Avatar par défaut
    }
    
    print(f"[DEBUG] Données utilisateur renvoyées: {response_data}")
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_user_profile(request):
    """
    API pour sauvegarder les modifications du profil utilisateur
    """
    try:
        user = request.user
        data = request.data
        
        print(f"[DEBUG] Sauvegarde profil pour: {user.username}")
        print(f"[DEBUG] Données reçues: {data}")
        
        # Mettre à jour les champs modifiables
        if 'username' in data and data['username']:
            user.username = data['username']
        if 'email' in data and data['email']:
            user.email = data['email']
            
        user.save()
        
        return Response({
            'success': True,
            'message': 'Profil sauvegardé avec succès'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"[ERREUR] Sauvegarde profil: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_user_data(request):
    """
    API spécifique pour le dashboard utilisateur
    Retourne toutes les données nécessaires pour afficher le dashboard
    """
    user = request.user
    print(f"[DEBUG] Récupération données dashboard pour: {user.username}")
    
    # Statistiques utilisateur
    user_images_count = Image.objects.filter(user=user).count()
    
    # Calculer le rang
    users_with_more_images = User.objects.annotate(
        image_count=Count('image')
    ).filter(image_count__gt=user_images_count).count()
    rank = users_with_more_images + 1
    
    # Points
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
            'total_users': User.objects.count()
        }
    }
    
    print(f"[DEBUG] Données dashboard renvoyées: {response_data}")
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def load_user_data(request):
    """
    API unifié pour charger toutes les données utilisateur nécessaires au frontend
    Compatible avec DashboardUser.vue loadUserData()
    """
    user = request.user
    print(f"[DEBUG] loadUserData pour: {user.username}")
    
    # Calculer le nombre d'images uploadées
    user_images_count = Image.objects.filter(user=user).count()
    
    # Calculer le rang
    users_with_more_images = User.objects.annotate(
        image_count=Count('image')
    ).filter(image_count__gt=user_images_count).count()
    rank = users_with_more_images + 1
    
    # Calculer les points (10 points par image)
    points = user_images_count * 10
    
    response_data = {
        'username': user.username,
        'email': user.email,
        'rank': rank,
        'points': points,
        'avatar': '/account/plante.png',  # Avatar par défaut
        'role': getattr(user, 'role', 'user'),
        'ville': getattr(user, 'ville', ''),
        'images_count': user_images_count
    }
    
    print(f"[DEBUG] loadUserData renvoyées: {response_data}")
    return Response(response_data, status=status.HTTP_200_OK)
