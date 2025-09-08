import requests
from django.core.management.base import BaseCommand
from api.models import Image

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "WDP-migration-script/1.0"

# Pour usage local, limiter le nombre de requêtes (Nominatim impose un rate limit)
def geocode_address(adresse, ville):
    params = {
        'q': f"{adresse}, {ville}",
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': USER_AGENT}
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"Erreur géocodage {adresse}, {ville}: {e}")
    return None, None

class Command(BaseCommand):
    help = "Ajoute les coordonnées GPS aux images de Sarcelles sans latitude/longitude"

    def handle(self, *args, **options):
        images = Image.objects.filter(ville__iexact="SARCELLES").filter(latitude__isnull=True)
        print(f"{images.count()} images à migrer pour Sarcelles...")
        for img in images:
            adresse = img.adresse or img.rue or "Sarcelles"
            lat, lon = geocode_address(adresse, "Sarcelles")
            if lat and lon:
                img.latitude = lat
                img.longitude = lon
                img.save()
                print(f"[OK] {img.id} : {adresse} => {lat}, {lon}")
            else:
                print(f"[FAIL] {img.id} : {adresse} => PAS DE COORDONNÉES")
        print("Migration terminée.")
