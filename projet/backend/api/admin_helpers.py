"""
Fonctions d'aide pour l'administration du système d'alerte
"""

from .models import Mairie, User, Image
from .mail_connector import get_mail_connector
from django.utils import timezone
from datetime import timedelta

def get_mairie_stats():
    """
    Obtient les statistiques de toutes les mairies
    
    Returns:
        list: Liste des mairies avec leurs stats
    """
    stats = []
    for mairie in Mairie.objects.all():
        # Compter les poubelles pleines récentes (24h)
        depuis = timezone.now() - timedelta(hours=24)
        poubelles_pleines = Image.objects.filter(
            ville_normalized__iexact=mairie.nom,
            classification_auto='pleine',
            date_upload__gte=depuis
        ).count()
        
        stats.append({
            'id': mairie.id,
            'nom': mairie.nom,
            'email': mairie.email,
            'seuil_alertes': mairie.seuil_alertes,
            'poubelles_pleines_24h': poubelles_pleines,
            'seuil_atteint': poubelles_pleines >= mairie.seuil_alertes,
            'nb_poubelles': mairie.nb_poubelles,
            'points': mairie.points
        })
    
    return stats

def tester_alerte_mairie(mairie_id):
    """
    Teste le système d'alerte pour une mairie spécifique
    
    Args:
        mairie_id: ID de la mairie à tester
        
    Returns:
        dict: Résultat du test
    """
    try:
        mairie = Mairie.objects.get(id=mairie_id)
        connector = get_mail_connector()
        
        resultat = connector.declencher_alerte_ville(mairie.nom)
        
        return {
            'success': True,
            'mairie': mairie.nom,
            'alerte_envoyee': resultat,
            'seuil': mairie.seuil_alertes,
            'message': f"Test d'alerte effectué pour {mairie.nom}"
        }
        
    except Mairie.DoesNotExist:
        return {
            'success': False,
            'error': 'Mairie non trouvée'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def modifier_seuil_mairie(mairie_id, nouveau_seuil):
    """
    Modifie le seuil d'alerte d'une mairie
    
    Args:
        mairie_id: ID de la mairie
        nouveau_seuil: Nouveau seuil (entier > 0)
        
    Returns:
        dict: Résultat de la modification
    """
    try:
        if nouveau_seuil < 1:
            return {
                'success': False,
                'error': 'Le seuil doit être supérieur à 0'
            }
            
        mairie = Mairie.objects.get(id=mairie_id)
        ancien_seuil = mairie.seuil_alertes
        
        mairie.seuil_alertes = nouveau_seuil
        mairie.save()
        
        return {
            'success': True,
            'mairie': mairie.nom,
            'ancien_seuil': ancien_seuil,
            'nouveau_seuil': nouveau_seuil,
            'message': f"Seuil modifié de {ancien_seuil} à {nouveau_seuil} pour {mairie.nom}"
        }
        
    except Mairie.DoesNotExist:
        return {
            'success': False,
            'error': 'Mairie non trouvée'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_historique_alertes(jours=7):
    """
    Obtient l'historique des images qui ont déclenché des alertes
    
    Args:
        jours: Nombre de jours à analyser
        
    Returns:
        dict: Historique par ville
    """
    depuis = timezone.now() - timedelta(days=jours)
    
    images_pleines = Image.objects.filter(
        classification_auto='pleine',
        date_upload__gte=depuis
    ).order_by('-date_upload')
    
    historique = {}
    for image in images_pleines:
        ville = image.ville_normalized or 'Non spécifiée'
        
        if ville not in historique:
            historique[ville] = {
                'total_images': 0,
                'derniere_alerte': None,
                'images': []
            }
        
        historique[ville]['total_images'] += 1
        historique[ville]['images'].append({
            'id': image.id,
            'date': image.date_upload,
            'utilisateur': image.uploaded_by.username if image.uploaded_by else 'Anonyme',
            'quartier': image.quartier
        })
        
        if not historique[ville]['derniere_alerte'] or image.date_upload > historique[ville]['derniere_alerte']:
            historique[ville]['derniere_alerte'] = image.date_upload
    
    return historique
