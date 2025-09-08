# -*- coding: utf-8 -*-
"""
MC_canny_classifier.py - Classification d'images par analyse de contours (Canny)
Script indépendant pour la méthode conditionnelle MC (analyse de contours)
- Applique Canny sur chaque image d'un dossier
- Calcule le ratio de contours haut/bas
- Classe l'image (pleine/vide) selon un seuil
- Exporte les résultats dans un fichier Excel/CSV
"""

import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime
import argparse

def classify_canny(image_path, ratio_threshold=1.0):
    image = cv2.imread(image_path)
    if image is None:
        return None, None, None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    h = edges.shape[0]
    # Découper en deux zones (haut/bas)
    top = edges[:h//2, :]
    bottom = edges[h//2:, :]
    top_count = np.sum(top > 0)
    bottom_count = np.sum(bottom > 0)
    ratio = (top_count + 1) / (bottom_count + 1)
    # Classification simple
    # AJUSTEMENT SEUIL : ratio > 1.0 => pleine, sinon vide (seuil abaissé pour améliorer la détection)
    if ratio > 1.0:
        label = 'pleine'
    else:
        label = 'vide'
    return ratio, label, (top_count, bottom_count)

def process_folder(folder, output_csv=None, ratio_threshold=1.5):
    image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in image_exts]
    results = []
    for fname in files:
        path = os.path.join(folder, fname)
        ratio, label, (top, bottom) = classify_canny(path, ratio_threshold)
        results.append({
            'filename': fname,
            'canny_top_count': top,
            'canny_bottom_count': bottom,
            'canny_ratio': ratio,
            'canny_class': label
        })
    df = pd.DataFrame(results)
    if output_csv is not None:
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"Résultats sauvegardés dans {output_csv}")
    return df
