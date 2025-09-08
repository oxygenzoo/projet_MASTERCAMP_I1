from rest_framework import serializers
from .models import Image, BatchAnalysis, User

class ImageSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle Image exposant tous les champs
    """
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = [
            'id', 'image', 'image_url', 'date_creation', 'annotation',
            'latitude', 'longitude', 'adresse', 'metadata',
            'classification_auto', 'classification_dl', 'confidence_dl',
            'canny_top_count', 'canny_bottom_count', 'canny_ratio', 'canny_mc',
            'taille_fichier', 'dimensions',
            'couleur_moyenne', 'contraste', 'rue', 'ville', 'jour_semaine'
        ]
        read_only_fields = [
            'date_creation', 'metadata', 'classification_auto', 'classification_dl',
            'confidence_dl', 'canny_top_count', 'canny_bottom_count', 'canny_ratio', 'canny_mc',
            'taille_fichier', 'dimensions', 'couleur_moyenne', 
            'contraste', 'jour_semaine'
        ]
    
    def get_image_url(self, obj):
        """Retourne l'URL complète de l'image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class ImageUploadSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'upload d'une nouvelle image
    """
    file = serializers.ImageField(required=False, write_only=True)
    
    class Meta:
        model = Image
        fields = ['image', 'file', 'latitude', 'longitude', 'adresse', 'rue', 'ville']
        extra_kwargs = {
            'image': {'required': False}
        }
    
    def validate(self, data):
        """Valide et traite les champs d'image"""
        # Si 'file' est fourni mais pas 'image', utiliser 'file' comme 'image'
        if 'file' in data and 'image' not in data:
            data['image'] = data.pop('file')
        elif 'file' in data:
            # Si les deux sont fournis, utiliser 'image' et supprimer 'file'
            data.pop('file')
        
        # S'assurer qu'une image est fournie
        if 'image' not in data:
            raise serializers.ValidationError("Une image est requise (champ 'image' ou 'file')")
            
        return data

class ImageAnnotationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'annotation d'une image existante
    """
    class Meta:
        model = Image
        fields = ['annotation']
        
    def validate_annotation(self, value):
        """Valide que l'annotation est soit 'pleine' soit 'vide'"""
        if value not in ['pleine', 'vide']:
            raise serializers.ValidationError("L'annotation doit être 'pleine' ou 'vide'")
        return value

class UserSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle User avec photo de profil
    """
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'points', 'ville', 
                 'first_name', 'last_name', 'avatar', 'avatar_url', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'avatar_url']
    
    def get_avatar_url(self, obj):
        """Retourne l'URL complète de l'avatar"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

class BatchAnalysisSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle BatchAnalysis
    """
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = BatchAnalysis
        fields = ['id', 'name', 'status', 'created_by', 'created_at', 
                 'completed_at', 'total_images', 'processed_images',
                 'success_count', 'error_count', 'csv_result', 'results_json']
