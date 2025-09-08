"""
Vues pour la gestion du profil utilisateur (photo de profil, etc.)
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from PIL import Image as PILImage
import os
from .models import User
from .serializers import UserSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    """
    Upload d'une photo de profil pour l'utilisateur connecté
    """
    try:
        if 'avatar' not in request.FILES:
            return Response({
                'error': 'Aucun fichier avatar fourni'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # Vérifier le type de fichier
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return Response({
                'error': 'Type de fichier non supporté. Utilisez JPG, PNG ou GIF.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier la taille (max 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response({
                'error': 'Fichier trop volumineux. Maximum 5MB.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        
        # Supprimer l'ancien avatar s'il existe
        if user.avatar and default_storage.exists(user.avatar.name):
            default_storage.delete(user.avatar.name)
        
        # Redimensionner l'image
        image = PILImage.open(avatar_file)
        
        # Convertir en RGB si nécessaire
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Redimensionner à 300x300 maximum en gardant les proportions
        image.thumbnail((300, 300), PILImage.Resampling.LANCZOS)
        
        # Sauvegarder l'image redimensionnée
        import io
        from django.core.files.base import ContentFile
        
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        # Générer un nom unique
        import uuid
        filename = f"avatar_{user.id}_{uuid.uuid4().hex[:8]}.jpg"
        
        # Sauvegarder le nouvel avatar
        user.avatar.save(
            filename,
            ContentFile(output.read()),
            save=True
        )
        
        # Retourner les données utilisateur mises à jour
        serializer = UserSerializer(user, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Photo de profil mise à jour avec succès',
            'user': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de l\'upload: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_avatar(request):
    """
    Supprime la photo de profil de l'utilisateur connecté
    """
    try:
        user = request.user
        
        if user.avatar and default_storage.exists(user.avatar.name):
            default_storage.delete(user.avatar.name)
            user.avatar.delete(save=True)
        
        serializer = UserSerializer(user, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Photo de profil supprimée avec succès',
            'user': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la suppression: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    # Suppression des logs utilisateurs pour éviter toute fuite de données
    """
    Met à jour les informations de profil de l'utilisateur
    """
    try:
        user = request.user
        data = request.data
        
        # Champs modifiables
        if 'username' in data:
            # Vérifier que le nom d'utilisateur n'est pas déjà pris
            if User.objects.exclude(id=user.id).filter(username=data['username']).exists():
                return Response({
                    'error': 'Ce nom d\'utilisateur est déjà pris'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.username = data['username']
        
        if 'email' in data:
            # Vérifier que l'email n'est pas déjà pris
            if User.objects.exclude(id=user.id).filter(email=data['email']).exists():
                return Response({
                    'error': 'Cette adresse email est déjà utilisée'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.email = data['email']
        
        if 'ville' in data:
            user.ville = data['ville']
            # La normalisation se fait automatiquement dans le save()
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        user.save()
        
        serializer = UserSerializer(user, context={'request': request})
        
        return Response({
            'success': True,
            'message': 'Profil mis à jour avec succès',
            'user': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': f'Erreur lors de la mise à jour: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
