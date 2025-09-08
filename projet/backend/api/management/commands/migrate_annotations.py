"""
Script pour migrer automatiquement les annotations des images :
- Si annotation est vide et classification_auto est 'pleine' ou 'vide', alors annotation = classification_auto
"""

from django.core.management.base import BaseCommand
from api.models import Image

class Command(BaseCommand):
    help = "Mise à jour automatique des annotations d'images selon la classification_auto"

    def handle(self, *args, **options):
        images = Image.objects.filter(annotation__isnull=True, classification_auto__in=['pleine', 'vide'])
        total = images.count()
        for img in images:
            img.annotation = img.classification_auto
            img.save(update_fields=['annotation'])
        self.stdout.write(self.style.SUCCESS(f"{total} images mises à jour (annotation auto)"))
