# Script Django pour enrichir les images sans la clé 'canny_mc' dans metadata

import sys
import os
# Ajout du chemin racine du projet pour l'import du module MC_canny_classifier
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../')))
# Ajout du dossier backend au sys.path pour permettre l'import de api.models
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)
# Initialisation Django si nécessaire
import django
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mastercamps.settings'
django.setup()
from api.models import Image
from MC_canny_classifier import classify_canny

count_total = 0
count_enriched = 0
missing_ids = []

for img in Image.objects.all():
    count_total += 1
    meta = img.metadata or {}
    if 'canny_mc' not in meta:
        try:
            image_path = img.image.path if hasattr(img.image, 'path') else None
            if image_path:
                canny_ratio, canny_label, (canny_top, canny_bottom) = classify_canny(image_path)
                # Conversion explicite en int natif pour la compatibilité JSON
                canny_result = {
                    'canny_ratio': float(canny_ratio),
                    'canny_label': canny_label,  # Peut être une chaîne ('vide', 'pleine', etc.)
                    'canny_top_count': int(canny_top),
                    'canny_bottom_count': int(canny_bottom)
                }
                meta['canny_mc'] = canny_result
                img.metadata = meta
                img.save()
                count_enriched += 1
                print(f"Image ID {img.id} enrichie avec canny_mc.")
            else:
                print(f"Image ID {img.id} : chemin image introuvable.")
        except Exception as e:
            print(f"Erreur pour l'image ID {img.id} : {e}")
            missing_ids.append(img.id)

print(f"\nTotal images traitées : {count_total}")
print(f"Images enrichies : {count_enriched}")
if missing_ids:
    print(f"IDs en erreur : {missing_ids}")
else:
    print("Toutes les images sans canny_mc ont été enrichies.")
