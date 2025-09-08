"""
Tests pour l'application API du projet Wild Dump Prevention
"""
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
import os
import tempfile
import sys
from PIL import Image as PILImage
import io
import numpy as np
from .models import Image

# Importer les fonctions depuis Extraction_caracteristiques.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Extraction_caracteristiques import extract_features, classify_by_rules

class ImageModelTests(TestCase):
    """Tests pour le modèle Image"""
    
    def setUp(self):
        """Création d'une image de test"""
        # Créer une image temporaire pour les tests
        image_file = self.create_test_image()
        
        # Créer une instance du modèle Image
        self.image = Image.objects.create(
            image=SimpleUploadedFile('test_image.jpg', image_file.read(),
                                   content_type='image/jpeg'),
            latitude=48.856614,
            longitude=2.3522219,
            adresse='123 Test Street',
            rue='TestRue'
        )
        
    def create_test_image(self):
        """Crée une image de test"""
        # Créer une image simple pour les tests
        file = io.BytesIO()
        image = PILImage.new('RGB', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'jpeg')
        file.name = 'test.jpg'
        file.seek(0)
        return file
        
    def test_image_creation(self):
        """Teste la création d'une image"""
        self.assertTrue(isinstance(self.image, Image))
        self.assertTrue(self.image.image.name.endswith('.jpg'))
        
    def test_image_str_representation(self):
        """Teste la représentation en chaîne d'une image"""
        self.assertTrue(str(self.image).startswith('Image'))
        
    def test_image_has_annotation(self):
        """Teste la méthode has_annotation"""
        self.assertFalse(self.image.has_annotation())
        
        # Ajouter une annotation
        self.image.annotation = 'pleine'
        self.image.save()
        
        self.assertTrue(self.image.has_annotation())
        
    def test_image_is_auto_classified(self):
        """Teste la méthode is_auto_classified"""
        self.assertFalse(self.image.is_auto_classified())
        
        # Ajouter une classification automatique
        self.image.classification_auto = 'pleine'
        self.image.save()
        
        self.assertTrue(self.image.is_auto_classified())


class ImageAPITests(APITestCase):
    """Tests pour les endpoints API"""
    
    def setUp(self):
        """Configuration des tests API"""
        self.upload_url = reverse('image-upload')
        self.image_list_url = reverse('image-list')
        self.dashboard_url = reverse('dashboard-stats')
        
        # Créer une image de test
        self.image_file = self.create_test_image()
        
    def create_test_image(self):
        """Crée une image de test"""
        file = io.BytesIO()
        image = PILImage.new('RGB', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'jpeg')
        file.name = 'test.jpg'
        file.seek(0)
        return file
        
    def test_upload_image(self):
        """Teste l'upload d'une image"""
        # Récupérer l'image de test
        self.image_file.seek(0)
        
        # Données pour la requête
        data = {
            'image': self.image_file,
            'latitude': 48.856614,
            'longitude': 2.3522219,
            'rue': 'TestRue'
        }
        
        # Envoyer la requête
        response = self.client.post(self.upload_url, data, format='multipart')
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('image_url', response.data)
        self.assertEqual(response.data['rue'], 'TestRue')
        
        # Vérifier que l'image a été créée en base
        self.assertEqual(Image.objects.count(), 1)
        
    def test_list_images(self):
        """Teste la liste des images"""
        # Créer quelques images test
        self.upload_test_images(3)
        
        # Récupérer la liste des images
        response = self.client.get(self.image_list_url)
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
    def test_annotate_image(self):
        """Teste l'annotation d'une image"""
        # Créer une image
        self.image_file.seek(0)
        response = self.client.post(
            self.upload_url,
            {'image': self.image_file},
            format='multipart'
        )
        image_id = response.data['id']
        
        # URL pour l'annotation
        annotate_url = reverse('image-annotate', args=[image_id])
        
        # Annoter l'image
        response = self.client.patch(
            annotate_url,
            {'annotation': 'pleine'},
            format='json'
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['annotation'], 'pleine')
        
        # Vérifier en base
        updated_image = Image.objects.get(id=image_id)
        self.assertEqual(updated_image.annotation, 'pleine')
        
    def test_dashboard_stats(self):
        """Teste les statistiques du dashboard"""
        # Créer des images avec différentes annotations et classifications
        self.upload_test_images(5)
        
        # Mettre à jour quelques images pour tester les statistiques
        images = Image.objects.all()
        images[0].annotation = 'pleine'
        images[0].classification_auto = 'pleine'
        images[0].save()
        
        images[1].annotation = 'vide'
        images[1].classification_auto = 'vide'
        images[1].save()
        
        # Récupérer les statistiques
        response = self.client.get(self.dashboard_url)
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_images', response.data)
        self.assertEqual(response.data['total_images'], 5)
        self.assertIn('annotation_counts', response.data)
        self.assertIn('auto_classification', response.data)
        
    def upload_test_images(self, count):
        """Utilitaire pour uploader plusieurs images de test"""
        for i in range(count):
            image_file = self.create_test_image()
            self.client.post(
                self.upload_url,
                {'image': image_file, 'quartier': f'Quartier{i}'},
                format='multipart'
            )


class ImageProcessingTests(TestCase):
    """Tests pour le module de traitement d'image"""
    
    def setUp(self):
        """Configuration des tests de traitement d'image"""
        self.image_file = self.create_test_image()
        
    def create_test_image(self):
        """Crée une image de test"""
        file = io.BytesIO()
        image = PILImage.new('RGB', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'jpeg')
        file.name = 'test.jpg'
        file.seek(0)
        return file
        
    def test_extract_features(self):
        """Teste l'extraction de caractéristiques"""
        # Réinitialiser le pointeur du fichier
        self.image_file.seek(0)
        
        # Extraire les caractéristiques
        features = extract_features(self.image_file)
        
        # Vérifier la structure des caractéristiques
        self.assertIn('technical', features)
        self.assertIn('temporal', features)
        self.assertIn('file_size', features['technical'])
        self.assertIn('dimensions', features['technical'])
        self.assertIn('avg_color', features['technical'])
        self.assertIn('contrast', features['technical'])
        self.assertIn('day_of_week', features['temporal'])
        
    def test_classify_by_rules(self):
        """Teste la classification par règles"""
        # Créer des caractéristiques fictives pour tester les règles
        features_dark = {
            'technical': {
                'brightness': 0.3,
                'contrast': 150
            }
        }
        
        features_bright = {
            'technical': {
                'brightness': 0.8,
                'contrast': 80
            }
        }
        
        # Tester la classification
        self.assertEqual(classify_by_rules(features_dark), 'pleine')
        self.assertEqual(classify_by_rules(features_bright), 'vide')
