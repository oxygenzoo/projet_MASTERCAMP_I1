"""
Gestionnaire d'export CSV pour les poubelles pleines
"""
import csv
import pandas as pd
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from .models import Image, User, Mairie
import os

class CSVExportManager:
    """
    Gestionnaire pour l'export des données de poubelles pleines
    """
    
    @classmethod
    def generer_csv_poubelles_pleines(cls, filtres=None):
        """
        Génère un CSV complet des poubelles pleines avec tous les détails
        
        Args:
            filtres: Dictionnaire de filtres optionnels
                - ville: Filtrer par ville
                - date_debut: Date de début (format: YYYY-MM-DD)
                - date_fin: Date de fin (format: YYYY-MM-DD)
                - utilisateur: Filtrer par utilisateur
                - quartier: Filtrer par quartier
                
        Returns:
            tuple: (DataFrame, nom_fichier)
        """
        # Query de base
        query = Image.objects.filter(classification_auto='pleine')
        
        # Appliquer les filtres
        if filtres:
            if filtres.get('ville'):
                query = query.filter(ville_normalized__icontains=filtres['ville'])
            
            if filtres.get('date_debut'):
                date_debut = datetime.strptime(filtres['date_debut'], '%Y-%m-%d').date()
                query = query.filter(date_upload__date__gte=date_debut)
            
            if filtres.get('date_fin'):
                date_fin = datetime.strptime(filtres['date_fin'], '%Y-%m-%d').date()
                query = query.filter(date_upload__date__lte=date_fin)
            
            if filtres.get('utilisateur'):
                query = query.filter(uploaded_by__username__icontains=filtres['utilisateur'])
            
            if filtres.get('quartier'):
                query = query.filter(quartier__icontains=filtres['quartier'])
        
        # Ordonner par date de création
        query = query.order_by('-date_upload')
        
        # Préparer les données
        data = []
        for image in query:
            # Informations de base
            row = {
                'ID': image.id,
                'Nom_Fichier': os.path.basename(image.image.name) if image.image else f'image_{image.id}',
                'Date_Detection': image.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                'Classification': image.classification_auto,
                'Confiance': getattr(image, 'confidence', 0.95),
                
                # Localisation
                'Ville': image.ville or 'Non spécifiée',
                'Ville_Normalisee': image.ville_normalized or 'Non spécifiée',
                'Quartier': image.quartier or 'Non spécifié',
                'Latitude': image.latitude,
                'Longitude': image.longitude,
                
                # Utilisateur
                'Utilisateur': image.uploaded_by.username if image.uploaded_by else 'Anonyme',
                'Email_Utilisateur': image.uploaded_by.email if image.uploaded_by else '',
                'Role_Utilisateur': image.uploaded_by.role if image.uploaded_by else '',
                
                # Détails techniques
                'Taille_Fichier': image.taille_fichier or 0,
                'Dimensions': image.dimensions or '',
                'Couleur_Moyenne': image.couleur_moyenne or '',
                'Contraste': image.contraste or 0,
                'Jour_Semaine': image.jour_semaine or '',
                
                # Métadonnées d'analyse
                'Methode_Analyse': 'MC',  # MasterCamps
                'Eclairage_Detecte': '',
                'Ouverture_Detectee': '',
                'Chevrons_Detectes': '',
                'Exposition': '',
            }
            
            # Ajouter les métadonnées d'analyse si disponibles
            if hasattr(image, 'metadata') and image.metadata:
                metadata = image.metadata
                
                # Critères MC
                mc_criteria = metadata.get('mc_criteria', {})
                row['Eclairage_Detecte'] = mc_criteria.get('eclairage', '')
                row['Ouverture_Detectee'] = 'Oui' if mc_criteria.get('ouverte', False) else 'Non'
                row['Chevrons_Detectes'] = 'Oui' if mc_criteria.get('chevrons', False) else 'Non'
                row['Exposition'] = mc_criteria.get('exposition', '')
                
                # Informations techniques détaillées
                technical = metadata.get('technical', {})
                if technical:
                    row['Format_Image'] = technical.get('format', '')
                    row['Mode_Couleur'] = technical.get('mode', '')
            
            # Informations sur la mairie
            try:
                mairie = Mairie.objects.filter(nom__iexact=image.ville_normalized).first()
                if mairie:
                    row['Email_Mairie'] = mairie.email
                    row['Seuil_Alerte_Mairie'] = mairie.seuil_alertes
                else:
                    row['Email_Mairie'] = ''
                    row['Seuil_Alerte_Mairie'] = ''
            except:
                row['Email_Mairie'] = ''
                row['Seuil_Alerte_Mairie'] = ''
            
            # Statut d'alerte
            if image.ville_normalized:
                # Compter combien de poubelles pleines dans cette ville ce jour-là
                jour_detection = image.date_upload.date()
                poubelles_meme_jour = Image.objects.filter(
                    ville_normalized=image.ville_normalized,
                    classification_auto='pleine',
                    date_upload__date=jour_detection
                ).count()
                
                row['Poubelles_Pleines_Meme_Jour'] = poubelles_meme_jour
                
                # Vérifier si cette image a potentiellement déclenché une alerte
                mairie_seuil = mairie.seuil_alertes if mairie else 10
                row['Alerte_Potentielle'] = 'Oui' if poubelles_meme_jour >= mairie_seuil else 'Non'
            else:
                row['Poubelles_Pleines_Meme_Jour'] = 0
                row['Alerte_Potentielle'] = 'Non'
            
            data.append(row)
        
        # Créer le DataFrame
        df = pd.DataFrame(data)
        
        # Générer le nom de fichier
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if filtres and filtres.get('ville'):
            nom_fichier = f"poubelles_pleines_{filtres['ville']}_{timestamp}.csv"
        else:
            nom_fichier = f"poubelles_pleines_global_{timestamp}.csv"
        
        return df, nom_fichier
    
    @classmethod
    def generer_csv_statistiques_ville(cls):
        """
        Génère un CSV avec les statistiques par ville
        """
        # Récupérer toutes les villes avec des poubelles pleines
        villes = Image.objects.filter(
            classification_auto='pleine',
            ville_normalized__isnull=False
        ).values_list('ville_normalized', flat=True).distinct()
        
        data = []
        for ville in villes:
            # Statistiques générales
            total_poubelles = Image.objects.filter(
                ville_normalized=ville,
                classification_auto='pleine'
            ).count()
            
            # Dernière semaine
            depuis_semaine = timezone.now() - timedelta(days=7)
            poubelles_semaine = Image.objects.filter(
                ville_normalized=ville,
                classification_auto='pleine',
                date_upload__gte=depuis_semaine
            ).count()
            
            # Dernier mois
            depuis_mois = timezone.now() - timedelta(days=30)
            poubelles_mois = Image.objects.filter(
                ville_normalized=ville,
                classification_auto='pleine',
                date_upload__gte=depuis_mois
            ).count()
            
            # Quartiers actifs
            quartiers = Image.objects.filter(
                ville_normalized=ville,
                classification_auto='pleine',
                quartier__isnull=False
            ).values_list('quartier', flat=True).distinct()
            
            # Utilisateurs actifs
            utilisateurs_actifs = Image.objects.filter(
                ville_normalized=ville,
                classification_auto='pleine',
                uploaded_by__isnull=False
            ).values_list('uploaded_by', flat=True).distinct().count()
            
            # Informations mairie
            mairie = Mairie.objects.filter(nom__iexact=ville).first()
            
            row = {
                'Ville': ville,
                'Total_Poubelles_Pleines': total_poubelles,
                'Poubelles_7_Jours': poubelles_semaine,
                'Poubelles_30_Jours': poubelles_mois,
                'Nombre_Quartiers': len(quartiers),
                'Quartiers_Liste': ', '.join(quartiers) if quartiers else '',
                'Utilisateurs_Actifs': utilisateurs_actifs,
                'Email_Mairie': mairie.email if mairie else '',
                'Seuil_Alerte': mairie.seuil_alertes if mairie else 10,
                'Moyenne_Par_Jour': round(poubelles_mois / 30, 2) if poubelles_mois > 0 else 0,
                'Derniere_Detection': Image.objects.filter(
                    ville_normalized=ville,
                    classification_auto='pleine'
                ).order_by('-date_upload').first().date_upload.strftime('%Y-%m-%d %H:%M:%S') if total_poubelles > 0 else 'Jamais'
            }
            
            data.append(row)
        
        # Trier par nombre total de poubelles pleines
        data.sort(key=lambda x: x['Total_Poubelles_Pleines'], reverse=True)
        
        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nom_fichier = f"statistiques_villes_{timestamp}.csv"
        
        return df, nom_fichier
    
    @classmethod
    def export_pour_mail_system(cls, ville=None, heures=24):
        """
        Export spécialement formaté pour le système mail.py
        Compatible avec le format attendu par les alertes
        """
        depuis = timezone.now() - timedelta(hours=heures)
        
        query = Image.objects.filter(
            classification_auto='pleine',
            date_upload__gte=depuis
        )
        
        if ville:
            query = query.filter(ville_normalized__iexact=ville)
        
        data = []
        for image in query:
            row = {
                'filename': os.path.basename(image.image.name) if image.image else f'image_{image.id}.jpg',
                'Prediction_Label': 'pleine',
                'Confidence': getattr(image, 'confidence', 0.95),
                'ville': image.ville_normalized or 'Non spécifiée',
                'quartier': image.quartier or 'Centre-ville',
                'latitude': image.latitude or 0,
                'longitude': image.longitude or 0,
                'date_detection': image.date_upload.strftime('%Y-%m-%d %H:%M:%S'),
                'utilisateur': image.uploaded_by.username if image.uploaded_by else 'Anonyme',
                'methode': 'MC'  # MasterCamps
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if ville:
            nom_fichier = f"predictions_optimized_{ville}_{timestamp}.csv"
        else:
            nom_fichier = f"predictions_optimized_global_{timestamp}.csv"
        
        return df, nom_fichier
