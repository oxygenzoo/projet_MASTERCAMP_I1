from django.core.management.base import BaseCommand
from api.models import User, Image
from api.utils import normalize_name


class Command(BaseCommand):
    help = 'Normalise toutes les villes dans la base de données'

    def handle(self, *args, **options):
        """
        Normalise les champs ville pour assurer la cohérence
        """
        self.stdout.write("🔧 Normalisation des villes...")
        
        # Normaliser les utilisateurs
        users_updated = 0
        for user in User.objects.all():
            if user.ville and not user.ville_normalized:
                user.ville_normalized = normalize_name(user.ville)
                user.save()
                users_updated += 1
                self.stdout.write(f" User {user.email}: {user.ville} → {user.ville_normalized}")
        
        # Normaliser les images
        images_updated = 0
        for image in Image.objects.all():
            ville_updated = False
            quartier_updated = False
            
            if image.ville and not image.ville_normalized:
                image.ville_normalized = normalize_name(image.ville)
                ville_updated = True
                
            if image.quartier and not image.quartier_normalized:
                image.quartier_normalized = normalize_name(image.quartier)
                quartier_updated = True
                
            if ville_updated or quartier_updated:
                image.save()
                images_updated += 1
                self.stdout.write(f" Image {image.id}: ville={image.ville_normalized}, quartier={image.quartier_normalized}")
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(" RÉSULTATS DE LA NORMALISATION:")
        self.stdout.write(f"   • Utilisateurs mis à jour: {users_updated}")
        self.stdout.write(f"   • Images mises à jour: {images_updated}")
        self.stdout.write("="*60)
        
        # Vérification des correspondances
        self.stdout.write("\n VÉRIFICATION DES CORRESPONDANCES:")
        
        mairie_users = User.objects.filter(role='mairie')
        for user in mairie_users:
            if user.ville_normalized:
                matching_images = Image.objects.filter(ville_normalized=user.ville_normalized).count()
                self.stdout.write(f"  {user.ville} ({user.ville_normalized}): {matching_images} images")
        
        self.stdout.write(
            self.style.SUCCESS(" Normalisation terminée avec succès!")
        )
