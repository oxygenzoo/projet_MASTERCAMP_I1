# Script Django pour lister les images sans la clé 'canny_mc' dans metadata
# Place ce fichier dans le dossier backend/api/ puis exécute-le avec 'python manage.py shell < backend/api/check_canny_mc.py'

from api.models import Image

count_total = 0
count_missing = 0
missing_ids = []

for img in Image.objects.all():
    count_total += 1
    meta = img.metadata or {}
    if 'canny_mc' not in meta:
        count_missing += 1
        missing_ids.append(img.id)
        print(f"Image ID {img.id} : canny_mc ABSENT")

print(f"\nTotal images : {count_total}")
print(f"Images sans canny_mc : {count_missing}")
if missing_ids:
    print(f"IDs sans canny_mc : {missing_ids}")
else:
    print("Toutes les images ont la clé canny_mc.")
