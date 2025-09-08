from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Table User
class User(AbstractUser):
    """
    Modèle utilisateur étendu pour le projet WDP
    """
    ROLE_CHOICES = [
        ('user', 'Utilisateur'),
        ('mairie', 'Mairie'),
        ('admin', 'Administrateur'),
    ]
    
    email = models.EmailField(unique=True)
    points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    ville_normalized = models.CharField(max_length=100, blank=True, null=True,
                                      help_text="Version normalisée de la ville pour les recherches")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Utiliser email comme identifiant de connexion
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        
    def save(self, *args, **kwargs):
        """Override save pour normaliser le champ ville"""
        from .utils import normalize_name
        
        # Normaliser la ville avant sauvegarde
        if self.ville:
            self.ville_normalized = normalize_name(self.ville)
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} ({self.email})"

# Table Mairie
class Mairie(models.Model):
    """
    Modèle représentant une mairie/ville
    """
    nom = models.CharField(max_length=100, unique=True, help_text="Nom de la ville")
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Sera hashé
    logo = models.ImageField(upload_to='mairies_logos/', blank=True, null=True)
    nb_poubelles = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    seuil_alertes = models.IntegerField(default=10, validators=[MinValueValidator(1)], 
                                      help_text="Seuil pour déclencher les alertes")
    points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mairie"
        verbose_name_plural = "Mairies"
        
    def __str__(self):
        return self.nom

# Table Poubelle
class Poubelle(models.Model):
    """
    Modèle représentant une poubelle avec sa localisation et son état
    """
    ETAT_CHOICES = [
        ('pleine', 'Pleine'),
        ('vide', 'Vide'),
    ]
    
    latitude = models.FloatField()
    longitude = models.FloatField()
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES)
    etat_dl = models.CharField(max_length=20, choices=ETAT_CHOICES, blank=True, null=True,
                              help_text="État déterminé par Deep Learning")
    photo = models.ImageField(upload_to='poubelles/')
    cree_par = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poubelles_creees')
    mairie = models.ForeignKey(Mairie, on_delete=models.CASCADE, related_name='poubelles')
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_vidage = models.DateTimeField(blank=True, null=True)
    
    # Champs additionnels
    adresse = models.CharField(max_length=255, blank=True, null=True)
    rue = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = "Poubelle"
        verbose_name_plural = "Poubelles"
        ordering = ['-date_ajout']
        
    def __str__(self):
        return f"Poubelle {self.id} - {self.etat} ({self.mairie.nom})"

# Table HistoriquePoints
class HistoriquePoints(models.Model):
    """
    Historique des points gagnés par les utilisateurs
    """
    TYPE_CHOICES = [
        ('pleine', 'Poubelle pleine (+10 points)'),
        ('vide', 'Poubelle vide (+5 points)'),
        ('bonus', 'Bonus spécial'),
        ('malus', 'Malus/correction'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historique_points')
    points = models.IntegerField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    poubelle = models.ForeignKey(Poubelle, on_delete=models.CASCADE, blank=True, null=True, 
                               related_name='historique_points')
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Historique des points"
        verbose_name_plural = "Historique des points"
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.username} - {self.points} pts ({self.type})"

# Table ClassementMairies
class ClassementMairies(models.Model):
    """
    Classement des mairies par points
    """
    mairie = models.ForeignKey(Mairie, on_delete=models.CASCADE, related_name='classements')
    points = models.IntegerField(validators=[MinValueValidator(0)])
    date = models.DateField(auto_now_add=True)
    rang = models.IntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Classement des mairies"
        verbose_name_plural = "Classements des mairies"
        ordering = ['-points', 'date']
        unique_together = ['mairie', 'date']  # Une seule entrée par mairie par jour
        
    def __str__(self):
        return f"{self.mairie.nom} - {self.points} pts (Rang: {self.rang})"

# Table ClassementUsers
class ClassementUsers(models.Model):
    """
    Classement des utilisateurs par points
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classements')
    points = models.IntegerField(validators=[MinValueValidator(0)])
    date = models.DateField(auto_now_add=True)
    rang = models.IntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Classement des utilisateurs"
        verbose_name_plural = "Classements des utilisateurs"
        ordering = ['-points', 'date']
        unique_together = ['user', 'date']  # Une seule entrée par utilisateur par jour
        
    def __str__(self):
        return f"{self.user.username} - {self.points} pts (Rang: {self.rang})"

# Modèle Image existant (conservé pour compatibilité)
class Image(models.Model):
    """
    Modèle représentant une image de poubelle avec métadonnées pour le projet WDP
    """
    # Champs de base
    image = models.ImageField(upload_to='uploads/')
    date_creation = models.DateTimeField(auto_now_add=True)
    annotation = models.CharField(max_length=10, choices=[('pleine', 'Pleine'), ('vide', 'Vide')], blank=True, null=True)
    
    # Champs de localisation
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    rue = models.CharField(max_length=100, blank=True, null=True)
    
    # Métadonnées de l'image
    metadata = models.JSONField(blank=True, null=True, 
                              help_text="Stocke les caractéristiques extraites de l'image")
    
    # Analyse et classification
    classification_auto = models.CharField(max_length=10, choices=[('pleine', 'Pleine'), ('vide', 'Vide')], blank=True, null=True, 
                                       help_text="Classification automatique basée sur les règles")
    classification_dl = models.CharField(max_length=10, choices=[('pleine', 'Pleine'), ('vide', 'Vide')], blank=True, null=True,
                                        help_text="Classification Deep Learning avec YOLO")
    confidence_dl = models.FloatField(blank=True, null=True, 
                                     help_text="Niveau de confiance de la classification DL (0-1)")
    
    # Champs MC (Canny Classifier)
    canny_top_count = models.IntegerField(blank=True, null=True, 
                                        help_text="Nombre de contours détectés dans la partie haute")
    canny_bottom_count = models.IntegerField(blank=True, null=True, 
                                           help_text="Nombre de contours détectés dans la partie basse")
    canny_ratio = models.FloatField(blank=True, null=True, 
                                  help_text="Ratio top/bottom pour la classification MC")
    canny_mc = models.CharField(max_length=10, choices=[('pleine', 'Pleine'), ('vide', 'Vide')], blank=True, null=True,
                              help_text="Classification MC (Canny)")
    
    taille_fichier = models.IntegerField(blank=True, null=True, help_text="Taille du fichier en octets")
    dimensions = models.CharField(max_length=50, blank=True, null=True, help_text="Dimensions de l'image (ex: 800x600)")
    couleur_moyenne = models.CharField(max_length=20, blank=True, null=True, help_text="Couleur moyenne de l'image (RGB)")
    contraste = models.FloatField(blank=True, null=True, help_text="Valeur du contraste de l'image")
    
    # Métadonnées contextuelles pour l'analyse des risques
    rue_normalized = models.CharField(max_length=100, blank=True, null=True, 
                                        help_text="Version normalisée de la rue pour les recherches")
    ville = models.CharField(max_length=100, blank=True, null=True)
    ville_normalized = models.CharField(max_length=100, blank=True, null=True,
                                     help_text="Version normalisée de la ville pour les recherches")
    jour_semaine = models.CharField(max_length=10, blank=True, null=True)
    
    # Liens vers les nouveaux modèles
    poubelle = models.ForeignKey(Poubelle, on_delete=models.SET_NULL, blank=True, null=True, 
                               related_name='images')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, 
                           related_name='images_uploadees')
    
    class Meta:
        verbose_name = "Image de poubelle"
        verbose_name_plural = "Images de poubelles"
        ordering = ['-date_creation']
    
    def __str__(self):
        status = self.annotation or "non annotée"
        return f"Image {self.id} - {status} ({self.date_creation.strftime('%Y-%m-%d')})"
        
    def set_location(self, lat, lon):
        """Définit la localisation à partir des coordonnées latitude/longitude"""
        self.latitude = lat
        self.longitude = lon
        self.save()
        
    def has_annotation(self):
        """Vérifie si l'image a été annotée manuellement"""
        return self.annotation is not None
        
    def is_auto_classified(self):
        """Vérifie si l'image a été classifiée automatiquement"""
        return self.classification_auto is not None
    
    def save(self, *args, **kwargs):
        """Override save pour normaliser les champs ville et rue"""
        from .utils import normalize_name
        # Normaliser la ville et la rue avant sauvegarde
        if self.ville:
            self.ville_normalized = normalize_name(self.ville)
        if self.rue:
            self.rue_normalized = normalize_name(self.rue)
        super().save(*args, **kwargs)
    
    def get_image_status(self):
        """
        Retourne le statut complet de l'image en combinant annotation
        et classification automatique
        """
        if self.annotation:
            # Priorité à l'annotation manuelle
            status = f"Annotation: {self.annotation}"
        elif self.classification_auto:
            # Utiliser la classification auto si pas d'annotation
            status = f"Classification auto: {self.classification_auto}"
        else:
            # Ni l'un ni l'autre
            status = "Non classifiée"
            
        return status
    
    def consistency_check(self):
        """
        Vérifie la cohérence entre l'annotation manuelle
        et la classification automatique
        """
        if not self.annotation or not self.classification_auto:
            return None
            
        return self.annotation == self.classification_auto

# Nouveau modèle pour les analyses par lot
class BatchAnalysis(models.Model):
    """
    Modèle pour stocker les résultats des analyses par lot
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours de traitement'),
        ('completed', 'Terminée'),
        ('failed', 'Échouée'),
    ]
    
    name = models.CharField(max_length=100, help_text="Nom de l'analyse par lot")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='batch_analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Résultats
    total_images = models.IntegerField(default=0)
    processed_images = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    
    # Résultats détaillés (optionnel)
    results_json = models.JSONField(null=True, blank=True)
    
    # Fichiers de résultats
    csv_result = models.FileField(upload_to='batch_results/', null=True, blank=True)
    
    class Meta:
        verbose_name = "Analyse par lot"
        verbose_name_plural = "Analyses par lot"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Lot #{self.id} - {self.name} ({self.status})"
    
    def mark_complete(self):
        """Marque l'analyse comme terminée"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def mark_failed(self):
        """Marque l'analyse comme échouée"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def update_progress(self, processed, success, error):
        """Met à jour la progression de l'analyse"""
        self.processed_images = processed
        self.success_count = success
        self.error_count = error
        self.save(update_fields=['processed_images', 'success_count', 'error_count'])
