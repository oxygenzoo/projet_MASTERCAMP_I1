"""
Système de classement et de points pour les utilisateurs
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta
from .models import User, Image

class ClassementManager:
    """
    Gestionnaire du système de classement
    """
    
    # Points accordés pour différentes actions
    POINTS_CONFIG = {
        'upload_image': 10,          # Points par image uploadée
        'image_pleine': 15,          # Bonus si image classée "pleine"
        'premiere_detection': 25,     # Bonus pour première détection dans un quartier
        'verification_admin': 5,      # Points si image vérifiée par admin
        'serie_consecutive': 20,      # Bonus pour 5 uploads dans la journée
        'weekly_bonus': 50,          # Bonus hebdomadaire pour les actifs
    }
    
    @classmethod
    def calculer_points_upload(cls, user, image):
        """
        Calcule les points à attribuer pour un upload d'image
        
        Args:
            user: Utilisateur qui a uploadé
            image: Instance de l'image uploadée
            
        Returns:
            dict: Détails des points attribués
        """
        points_detail = {
            'base': cls.POINTS_CONFIG['upload_image'],
            'bonus_pleine': 0,
            'bonus_premiere': 0,
            'bonus_serie': 0,
            'total': cls.POINTS_CONFIG['upload_image']
        }
        
        # Bonus si poubelle pleine détectée
        if image.classification_auto == 'pleine':
            points_detail['bonus_pleine'] = cls.POINTS_CONFIG['image_pleine']
            points_detail['total'] += points_detail['bonus_pleine']
        
        # Bonus première détection dans le quartier
        if image.quartier and image.ville_normalized:
            premiere_detection = not Image.objects.filter(
                ville_normalized=image.ville_normalized,
                quartier=image.quartier,
                uploaded_by=user,
                date_upload__lt=image.date_upload
            ).exists()
            
            if premiere_detection:
                points_detail['bonus_premiere'] = cls.POINTS_CONFIG['premiere_detection']
                points_detail['total'] += points_detail['bonus_premiere']
        
        # Bonus série consécutive (5 images dans la journée)
        aujourd_hui = timezone.now().date()
        uploads_aujourd_hui = Image.objects.filter(
            uploaded_by=user,
            date_upload__date=aujourd_hui
        ).count()
        
        if uploads_aujourd_hui >= 5 and uploads_aujourd_hui % 5 == 0:
            points_detail['bonus_serie'] = cls.POINTS_CONFIG['serie_consecutive']
            points_detail['total'] += points_detail['bonus_serie']
        
        return points_detail
    
    @classmethod
    def attribuer_points(cls, user, points_detail):
        """
        Attribue les points à l'utilisateur et enregistre l'historique
        """
        from .models import HistoriquePoints
        
        # Ajouter les points à l'utilisateur
        user.points += points_detail['total']
        user.save()
        
        # Enregistrer dans l'historique
        HistoriquePoints.objects.create(
            user=user,
            points=points_detail['total'],
            motif='upload_image',
            details=points_detail
        )
        
        return points_detail['total']
    
    @classmethod
    def get_classement_global(cls, limite=50):
        """
        Obtient le classement global des utilisateurs
        
        Args:
            limite: Nombre maximum d'utilisateurs à retourner
            
        Returns:
            list: Classement ordonné par points
        """
        users = User.objects.filter(
            role='user'  # Seulement les utilisateurs normaux
        ).order_by('-points', '-date_joined')[:limite]
        
        classement = []
        for rang, user in enumerate(users, 1):
            # Calculer les stats de l'utilisateur
            total_images = Image.objects.filter(uploaded_by=user).count()
            images_pleines = Image.objects.filter(
                uploaded_by=user, 
                classification_auto='pleine'
            ).count()
            
            # Activité récente (7 derniers jours)
            depuis_semaine = timezone.now() - timedelta(days=7)
            activite_recente = Image.objects.filter(
                uploaded_by=user,
                date_upload__gte=depuis_semaine
            ).count()
            
            classement.append({
                'rang': rang,
                'user_id': user.id,
                'username': user.username,
                'points': user.points,
                'ville': user.ville,
                'avatar_url': user.avatar.url if user.avatar else None,
                'stats': {
                    'total_images': total_images,
                    'images_pleines': images_pleines,
                    'activite_7j': activite_recente,
                    'membre_depuis': user.date_joined.strftime('%Y-%m-%d')
                }
            })
        
        return classement
    
    @classmethod
    def get_classement_ville(cls, ville, limite=20):
        """
        Obtient le classement pour une ville spécifique
        """
        if not ville:
            return []
        
        users = User.objects.filter(
            role='user',
            ville_normalized__iexact=ville
        ).order_by('-points', '-date_joined')[:limite]
        
        classement = []
        for rang, user in enumerate(users, 1):
            total_images = Image.objects.filter(
                uploaded_by=user,
                ville_normalized__iexact=ville
            ).count()
            
            classement.append({
                'rang': rang,
                'user_id': user.id,
                'username': user.username,
                'points': user.points,
                'total_images': total_images,
                'avatar_url': user.avatar.url if user.avatar else None
            })
        
        return classement
    
    @classmethod
    def get_stats_utilisateur(cls, user):
        """
        Obtient les statistiques détaillées d'un utilisateur
        """
        total_images = Image.objects.filter(uploaded_by=user).count()
        images_pleines = Image.objects.filter(
            uploaded_by=user, 
            classification_auto='pleine'
        ).count()
        
        # Classement global
        rang_global = User.objects.filter(
            role='user',
            points__gt=user.points
        ).count() + 1
        
        # Classement dans sa ville
        rang_ville = None
        if user.ville_normalized:
            rang_ville = User.objects.filter(
                role='user',
                ville_normalized=user.ville_normalized,
                points__gt=user.points
            ).count() + 1
        
        # Activité par mois
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        
        activite_mensuelle = Image.objects.filter(
            uploaded_by=user
        ).annotate(
            mois=TruncMonth('date_upload')
        ).values('mois').annotate(
            count=Count('id')
        ).order_by('mois')
        
        return {
            'points': user.points,
            'rang_global': rang_global,
            'rang_ville': rang_ville,
            'stats': {
                'total_images': total_images,
                'images_pleines': images_pleines,
                'taux_detection': round((images_pleines / total_images * 100) if total_images > 0 else 0, 1),
                'membre_depuis': user.date_joined,
                'ville': user.ville
            },
            'activite_mensuelle': list(activite_mensuelle)
        }

# Fonctions utilitaires pour les vues
def traiter_points_upload(user, image):
    """
    Traite l'attribution de points après un upload
    À appeler dans image_views.py
    """
    if user.role == 'user':  # Seuls les utilisateurs normaux gagnent des points
        points_detail = ClassementManager.calculer_points_upload(user, image)
        points_attribues = ClassementManager.attribuer_points(user, points_detail)
        
        return {
            'points_attribues': points_attribues,
            'detail': points_detail,
            'nouveau_total': user.points
        }
    
    return None
