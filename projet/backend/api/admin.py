from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Mairie, Poubelle, Image, HistoriquePoints, ClassementMairies, ClassementUsers

# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'points', 'ville', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'ville', 'date_joined')
    search_fields = ('username', 'email', 'ville')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations WDP', {
            'fields': ('points', 'avatar', 'ville')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations WDP', {
            'fields': ('email', 'points', 'avatar', 'ville')
        }),
    )

@admin.register(Mairie)
class MairieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'nb_poubelles', 'points', 'seuil_alertes', 'date_creation')
    list_filter = ('date_creation', 'seuil_alertes')
    search_fields = ('nom', 'email')
    readonly_fields = ('date_creation',)
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'email', 'password', 'logo')
        }),
        ('Statistiques', {
            'fields': ('nb_poubelles', 'points', 'seuil_alertes')
        }),
        ('Métadonnées', {
            'fields': ('date_creation',)
        }),
    )

@admin.register(Poubelle)
class PoubelleAdmin(admin.ModelAdmin):
    list_display = ('id', 'etat', 'mairie', 'cree_par', 'rue', 'date_ajout', 'date_vidage')
    list_filter = ('etat', 'mairie', 'rue', 'date_ajout', 'date_vidage')
    search_fields = ('adresse', 'rue', 'mairie__nom', 'cree_par__username')
    readonly_fields = ('date_ajout',)
    
    fieldsets = (
        ('Localisation', {
            'fields': ('latitude', 'longitude', 'adresse', 'rue')
        }),
        ('État', {
            'fields': ('etat', 'photo')
        }),
        ('Relations', {
            'fields': ('cree_par', 'mairie')
        }),
        ('Dates', {
            'fields': ('date_ajout', 'date_vidage')
        }),
    )

@admin.register(HistoriquePoints)
class HistoriquePointsAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'type', 'poubelle', 'timestamp', 'description')
    list_filter = ('type', 'timestamp', 'user')
    search_fields = ('user__username', 'description', 'poubelle__id')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        ('Utilisateur et Points', {
            'fields': ('user', 'points', 'type')
        }),
        ('Détails', {
            'fields': ('poubelle', 'description')
        }),
        ('Métadonnées', {
            'fields': ('timestamp',)
        }),
    )

@admin.register(ClassementMairies)
class ClassementMairiesAdmin(admin.ModelAdmin):
    list_display = ('mairie', 'points', 'rang', 'date')
    list_filter = ('date', 'rang')
    search_fields = ('mairie__nom',)
    readonly_fields = ('date',)

@admin.register(ClassementUsers)
class ClassementUsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'rang', 'date')
    list_filter = ('date', 'rang')
    search_fields = ('user__username',)
    readonly_fields = ('date',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'thumbnail', 'date_creation', 'annotation', 'classification_auto', 'rue', 'user', 'poubelle')
    list_filter = ('annotation', 'classification_auto', 'jour_semaine', 'rue', 'date_creation')
    search_fields = ('annotation', 'adresse', 'rue', 'user__username')
    readonly_fields = ('image_preview', 'metadata', 'classification_auto', 'taille_fichier', 
                      'dimensions', 'couleur_moyenne', 'contraste')
    
    fieldsets = (
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Annotation', {
            'fields': ('annotation', 'classification_auto')
        }),
        ('Relations', {
            'fields': ('user', 'poubelle')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'taille_fichier', 'dimensions', 
                      'couleur_moyenne', 'contraste')
        }),
        ('Localisation', {
            'fields': ('latitude', 'longitude', 'adresse', 'rue')
        }),
        ('Données avancées', {
            'classes': ('collapse',),
            'fields': ('metadata', 'jour_semaine'),
        }),
    )
    
    def image_preview(self, obj):
        """Affiche une prévisualisation de l'image"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 300px; max-width: 100%;" />', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = 'Prévisualisation'
    
    def thumbnail(self, obj):
        """Affiche une miniature dans la liste"""
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "—"
    thumbnail.short_description = 'Image'
