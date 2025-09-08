"""
Connecteur entre le backend Django et le système d'alerte mail.py
Se déclenche automatiquement quand des poubelles pleines sont détectées
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

# Import des modèles Django
from .models import Image, User, Mairie

# Ajouter le répertoire racine au path pour importer mail.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Import du module mail existant
try:
    import mail
    MAIL_AVAILABLE = True
except ImportError:
    MAIL_AVAILABLE = False
    print("[WARNING] Module mail.py non disponible")

class MailConnector:
    """
    Connecteur pour intégrer le système d'alerte mail.py au backend Django
    """
    
    def __init__(self):
        self.seuil_poubelles = 10  # Seuil par défaut comme dans le mail.py
        self.mode_analyse = 'Django'  # Mode spécifique pour Django
        
    def generer_csv_depuis_django(self, ville=None, derniere_heure=24):
        """
        Génère un CSV des poubelles pleines depuis la base Django
        Compatible avec le format attendu par mail.py
        Utilise le nouveau système CSV amélioré
        
        Args:
            ville: Filtrer par ville (optionnel)
            derniere_heure: Période en heures à analyser
            
        Returns:
            tuple: (DataFrame, nom_fichier_csv)
        """
        from .csv_export import CSVExportManager
        
        # Utiliser le système d'export amélioré
        return CSVExportManager.export_pour_mail_system(ville, derniere_heure)
        
    def sauvegarder_csv_temporaire(self, df, nom_fichier):
        """
        Sauvegarde le DataFrame en CSV temporaire pour mail.py
        """
        # Créer le répertoire temp s'il n'existe pas
        temp_dir = os.path.join(PROJECT_ROOT, 'temp_mail')
        os.makedirs(temp_dir, exist_ok=True)
        
        chemin_fichier = os.path.join(temp_dir, nom_fichier)
        
        # Sauvegarder avec le format attendu par mail.py
        df.to_csv(chemin_fichier, sep=';', index=False)
        
        return chemin_fichier
        
    def nettoyer_fichiers_temporaires(self, chemin_fichier):
        """
        Nettoie les fichiers temporaires créés
        """
        try:
            if os.path.exists(chemin_fichier):
                os.remove(chemin_fichier)
            
            # Nettoyer aussi les fichiers d'alerte générés par mail.py
            for fichier in ['alertes_ML.csv', 'alertes_DL.csv', 'alertes_Django.csv']:
                if os.path.exists(fichier):
                    os.remove(fichier)
                    
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
            
    def obtenir_emails_destinataires(self, ville=None):
        """
        Obtient les emails des destinataires selon la ville
        
        Args:
            ville: Ville concernée (optionnel)
            
        Returns:
            list: Liste des emails
        """
        emails = []
        
        if ville:
            # Emails des comptes mairie pour cette ville
            mairies = User.objects.filter(
                role='mairie',
                ville_normalized=ville,
                email__isnull=False
            ).exclude(email='')
            
            emails.extend([user.email for user in mairies])
        
        # Toujours ajouter les administrateurs
        admins = User.objects.filter(
            role='admin',
            email__isnull=False
        ).exclude(email='')
        
        emails.extend([user.email for user in admins])
        
        return list(set(emails))  # Supprimer les doublons
        
    def declencher_alerte_ville(self, ville):
        """
        Déclenche une vérification d'alerte pour une ville spécifique
        
        Args:
            ville: Nom de la ville normalisé
            
        Returns:
            bool: True si alerte envoyée, False sinon
        """
        if not MAIL_AVAILABLE:
            print(f"[WARNING] Module mail.py non disponible pour {ville}")
            return False
            
        try:
            print(f"[INFO] Vérification des alertes pour la ville: {ville}")
            
            # Obtenir le seuil personnalisé pour cette ville
            seuil_ville = self.obtenir_seuil_mairie(ville)
            
            # Générer le CSV depuis Django
            df_poubelles, nom_fichier = self.generer_csv_depuis_django(ville=ville)
            nb_poubelles = len(df_poubelles)
            
            print(f"[INFO] {nb_poubelles} poubelles pleines détectées à {ville} (seuil: {seuil_ville})")
            
            if nb_poubelles >= seuil_ville:
                # Sauvegarder temporairement le CSV
                chemin_csv = self.sauvegarder_csv_temporaire(df_poubelles, nom_fichier)
                
                # Changer vers le répertoire du projet pour mail.py
                repertoire_original = os.getcwd()
                os.chdir(PROJECT_ROOT)
                
                try:
                    # Obtenir les emails destinataires
                    emails = self.obtenir_emails_destinataires(ville)
                    
                    if emails:
                        # Utiliser la fonction du mail.py pour chaque destinataire
                        for email in emails:
                            print(f"[INFO] Envoi d'alerte à {email} pour {ville}")
                            
                            # Utiliser le seuil personnalisé de la ville
                            mail.verifier_et_envoyer_alerte(
                                mail=email,
                                seuil=seuil_ville,
                                mode='ML'  # Utiliser le mode ML qui cherche les CSV predictions_*
                            )
                        
                        print(f"[SUCCESS] Alerte envoyée pour {ville} à {len(emails)} destinataires")
                        return True
                    else:
                        print(f"[WARNING] Aucun email destinataire trouvé pour {ville}")
                        return False
                        
                finally:
                    # Restaurer le répertoire original
                    os.chdir(repertoire_original)
                    # Nettoyer les fichiers temporaires
                    self.nettoyer_fichiers_temporaires(chemin_csv)
                    
            else:
                print(f"[INFO] Seuil non atteint pour {ville} ({nb_poubelles}/{seuil_ville})")
                return False
                
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'alerte pour {ville}: {e}")
            return False
            
    def declencher_alerte_globale(self):
        """
        Déclenche une vérification d'alerte globale (toutes villes confondues)
        
        Returns:
            bool: True si alerte envoyée, False sinon
        """
        if not MAIL_AVAILABLE:
            print("[WARNING] Module mail.py non disponible pour alerte globale")
            return False
            
        try:
            print("[INFO] Vérification de l'alerte globale")
            
            # Générer le CSV global
            df_poubelles, nom_fichier = self.generer_csv_depuis_django()
            nb_poubelles = len(df_poubelles)
            
            print(f"[INFO] {nb_poubelles} poubelles pleines détectées globalement")
            
            if nb_poubelles >= self.seuil_poubelles:
                # Sauvegarder temporairement le CSV
                chemin_csv = self.sauvegarder_csv_temporaire(df_poubelles, nom_fichier)
                
                # Changer vers le répertoire du projet pour mail.py
                repertoire_original = os.getcwd()
                os.chdir(PROJECT_ROOT)
                
                try:
                    # Obtenir les emails des administrateurs
                    emails = self.obtenir_emails_destinataires()
                    
                    if emails:
                        # Utiliser la fonction du mail.py pour chaque administrateur
                        for email in emails:
                            print(f"[INFO] Envoi d'alerte globale à {email}")
                            
                            mail.verifier_et_envoyer_alerte(
                                mail=email,
                                seuil=self.seuil_poubelles,
                                mode='ML'
                            )
                        
                        print(f"[SUCCESS] Alerte globale envoyée à {len(emails)} administrateurs")
                        return True
                    else:
                        print("[WARNING] Aucun email administrateur trouvé")
                        return False
                        
                finally:
                    # Restaurer le répertoire original
                    os.chdir(repertoire_original)
                    # Nettoyer les fichiers temporaires
                    self.nettoyer_fichiers_temporaires(chemin_csv)
                    
            else:
                print(f"[INFO] Seuil global non atteint ({nb_poubelles}/{self.seuil_poubelles})")
                return False
                
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'alerte globale: {e}")
            return False
            
    def verifier_alertes_automatiques(self, ville_recente=None):
        """
        Vérifie automatiquement s'il faut déclencher des alertes
        Appelé après chaque upload d'image classifiée comme 'pleine'
        
        Args:
            ville_recente: Ville de la dernière image uploadée (pour optimiser)
            
        Returns:
            dict: Résultats des vérifications
        """
        resultats = {
            'alerte_ville': False,
            'alerte_globale': False,
            'ville_concernee': ville_recente,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"[INFO] Déclenchement vérification automatique des alertes")
        
        # 1. Vérifier l'alerte spécifique à la ville
        if ville_recente:
            resultats['alerte_ville'] = self.declencher_alerte_ville(ville_recente)
        
        # 2. Vérifier l'alerte globale
        resultats['alerte_globale'] = self.declencher_alerte_globale()
        
        return resultats

    def obtenir_seuil_mairie(self, ville):
        """
        Obtient le seuil personnalisé configuré par la mairie pour cette ville
        
        Args:
            ville: Nom de la ville normalisé
            
        Returns:
            int: Seuil personnalisé ou seuil par défaut (10)
        """
        try:
            # Chercher l'entrée Mairie correspondante
            mairie = Mairie.objects.filter(nom__iexact=ville).first()
            if mairie and mairie.seuil_alertes:
                print(f"[INFO] Seuil personnalisé pour {ville}: {mairie.seuil_alertes}")
                return mairie.seuil_alertes
            else:
                print(f"[INFO] Seuil par défaut pour {ville}: {self.seuil_poubelles}")
                return self.seuil_poubelles
        except Exception as e:
            print(f"[ERROR] Erreur récupération seuil pour {ville}: {e}")
            return self.seuil_poubelles

# Instance globale du connecteur
mail_connector = MailConnector()

def get_mail_connector():
    """Retourne l'instance du connecteur mail"""
    return mail_connector

def verifier_alerte_apres_upload(image_instance):
    """
    Fonction appelée automatiquement après l'upload et classification d'une image
    
    Args:
        image_instance: Instance de l'image qui vient d'être classifiée
    """
    if image_instance.classification_auto == 'pleine':
        ville = getattr(image_instance, 'ville_normalized', None)
        connector = get_mail_connector()
        resultats = connector.verifier_alertes_automatiques(ville_recente=ville)
        
        print(f"[AUTO-ALERT] Résultats: {resultats}")
        return resultats
    
    return None
