"""
Module d'extraction de caractéristiques d'images pour Wild Dump Prevention (WDP)
Intègre les fonctionnalités d'extraction avancées et d'analyse pour la classification des poubelles.
Version simplifiée - utilise les fonctionnalités de base uniquement.
"""
from PIL import Image
import numpy as np
import cv2
import os
import json
from datetime import datetime
import io
import pandas as pd

# Le module d'analyse avancée a été supprimé, on utilise uniquement l'analyse de base
ADVANCED_ANALYSIS_AVAILABLE = False

# Fonctions de remplacement pour maintenir la compatibilité
def AdvancedWasteAnalyzer():
    pass

def analyze_image_with_advanced_method(image_path):
    return None

def extract_features(image_file):
    """
    Extrait les caractéristiques d'une image
    
    Args:
        image_file: Fichier image uploadé via Django, fichier local ou objet BytesIO
        
    Returns:
        dict: Dictionnaire contenant les caractéristiques de l'image
    """
    # Sauvegarder la position du curseur si c'est un fichier en mémoire
    try:
        original_position = image_file.tell()
        image_file.seek(0)
        img = Image.open(image_file)
    except AttributeError:
        # Si c'est un chemin de fichier au lieu d'un objet fichier
        img = Image.open(image_file)
        original_position = None
    
    # Taille du fichier
    try:
        # Pour les fichiers uploadés via Django (UploadedFile)
        file_size = image_file.size
    except AttributeError:
        # Pour les objets BytesIO ou les chemins de fichiers
        try:
            if original_position is not None:
                image_file.seek(0, os.SEEK_END)
                file_size = image_file.tell()
                image_file.seek(0)
            else:
                file_size = os.path.getsize(image_file)
        except:
            file_size = 0
    
    # Dimensions
    width, height = img.size
    
    # Convertir en RGB si nécessaire (pour le calcul de couleur)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convertir en numpy array pour les calculs
    img_array = np.array(img)

    # Couleur moyenne (RGB)
    avg_red = np.mean(img_array[:,:,0])
    avg_green = np.mean(img_array[:,:,1])
    avg_blue = np.mean(img_array[:,:,2])
    avg_color = f"rgb({int(avg_red)},{int(avg_green)},{int(avg_blue)})"
    
    # Dominance de couleurs
    color_dominance = "rouge" if avg_red > avg_green and avg_red > avg_blue else "vert" if avg_green > avg_red and avg_green > avg_blue else "bleu"
    
    # Luminosité moyenne
    brightness = (0.299 * avg_red + 0.587 * avg_green + 0.114 * avg_blue) / 255
    
    # Contraste (différence max-min)
    red_contrast = np.max(img_array[:,:,0]) - np.min(img_array[:,:,0])
    green_contrast = np.max(img_array[:,:,1]) - np.min(img_array[:,:,1])
    blue_contrast = np.max(img_array[:,:,2]) - np.min(img_array[:,:,2])
    contrast = (red_contrast + green_contrast + blue_contrast) / 3
    
    # Conversion en niveaux de gris pour OpenCV
    if img.mode == "RGB":
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    elif img.mode == "L":
        gray = np.array(img)
    else:
        gray = None
    
    # Détection des contours (fonctionnalité avancée)
    edge_count = 0
    contour_pixels = 0
    if gray is not None:
        edges = cv2.Canny(gray, 100, 200)
        contour_pixels = int(np.sum(edges > 0))
        
        # Trouver les contours réels pour analyser leur nombre et complexité
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        edge_count = len(contours)
    
    # Calcul de la texture (variance locale)
    texture_variance = 0
    if gray is not None:
        # Calculer la variance comme mesure de texture
        texture_variance = np.var(gray)
    
    # Histogramme (simplifié)
    hist_r, _ = np.histogram(img_array[:,:,0], bins=10, range=(0, 256))
    hist_g, _ = np.histogram(img_array[:,:,1], bins=10, range=(0, 256))
    hist_b, _ = np.histogram(img_array[:,:,2], bins=10, range=(0, 256))
    
    # Détection de zones claires et sombres
    dark_threshold = 50
    bright_threshold = 200
    dark_ratio = np.mean(gray < dark_threshold) if gray is not None else 0
    bright_ratio = np.mean(gray > bright_threshold) if gray is not None else 0
    
    # Jour de la semaine
    day_of_week = datetime.now().strftime("%A")
    
    # Créer un dictionnaire de caractéristiques
    features = {
        'technical': {
            'file_size': file_size,
            'dimensions': f"{width}x{height}",
            'aspect_ratio': width / height if height != 0 else 0,
            'avg_color': avg_color,
            'color_dominance': color_dominance,
            'brightness': float(brightness),
            'contrast': float(contrast),
            'contour_pixels': contour_pixels,  # Détection de contours avancée
            'edge_count': edge_count,         # Nombre de contours distincts
            'texture_variance': float(texture_variance),  # Mesure de texture
            'dark_ratio': float(dark_ratio),   # Proportion de zones sombres
            'bright_ratio': float(bright_ratio),  # Proportion de zones claires
            'r_mean': float(avg_red),      # Composantes RGB individuelles
            'g_mean': float(avg_green),
            'b_mean': float(avg_blue),
            'histogram': {
                'red': hist_r.tolist(),
                'green': hist_g.tolist(),
                'blue': hist_b.tolist(),
            }
        },
        'temporal': {
            'day_of_week': day_of_week,
            'timestamp': datetime.now().isoformat(),
            'hour': datetime.now().hour,     # Heure du jour
            'is_weekend': datetime.now().weekday() >= 5  # Si c'est le weekend
        }
    }
    
    # Restaurer la position du curseur si applicable
    if original_position is not None:
        image_file.seek(original_position)
    
    return features

def classify_by_rules(features, image_path=None, mc_criteria=None):
    """
    Classifie une image en fonction des caractéristiques extraites et des critères MC
    
    Args:
        features (dict): Dictionnaire de caractéristiques extraites par extract_features()
        image_path (str, optional): Chemin vers l'image pour l'analyse avancée
        mc_criteria (dict, optional): Critères spécifiques MC (éclairage, ouverte, chevrons, exposition)
        
    Returns:
        str: 'pleine' ou 'vide' (suppression de 'partiellement_pleine')
    """
    
    # Essayer d'utiliser l'analyse avancée si disponible et si on a le chemin de l'image
    if ADVANCED_ANALYSIS_AVAILABLE and image_path and os.path.exists(image_path):
        try:
            advanced_result = analyze_image_with_advanced_method(image_path)
            if advanced_result:
                # Ajouter les résultats de l'analyse avancée aux features
                features['advanced_analysis'] = advanced_result
                # Adapter le résultat avec les critères MC
                return adapt_classification_with_mc_criteria(advanced_result['classification'], mc_criteria)
        except Exception as e:
            print(f" Erreur dans l'analyse avancée, utilisation de l'analyse de base: {e}")
    
    # Analyse de base améliorée avec critères MC
    return classify_by_improved_rules_with_mc(features, mc_criteria)

def adapt_classification_with_mc_criteria(base_classification, mc_criteria):
    """
    Adapte la classification en fonction des critères MC spécifiques
    """
    # Supprimer partiellement_pleine et adapter en binaire
    if base_classification == 'partiellement_pleine':
        base_classification = 'pleine'  # Convertir en pleine par défaut
    
    if not mc_criteria:
        return base_classification
    
    # Facteurs d'ajustement selon les critères MC
    adjustment_score = 0
    
    # Éclairage : impact sur la visibilité des déchets
    eclairage = mc_criteria.get('eclairage', 'normal')
    if eclairage in ['faible', 'nuit', 'sombre']:
        adjustment_score -= 5  # Plus difficile de voir les déchets
    elif eclairage in ['fort', 'soleil', 'lumineux']:
        adjustment_score += 3  # Meilleure visibilité
    
    # Poubelle ouverte vs fermée
    if mc_criteria.get('ouverte', False):
        adjustment_score += 8  # Si ouverte, plus facile de voir le contenu
    else:
        adjustment_score -= 5  # Si fermée, peut masquer le contenu
    
    # Chevrons (système de protection/collecte)
    if mc_criteria.get('chevrons', False):
        adjustment_score -= 3  # Système organisé, moins de débordement
    
    # Exposition (environnement)
    exposition = mc_criteria.get('exposition', 'normale')
    if exposition == 'pleine':
        adjustment_score += 2  # Plus exposé aux intempéries, débordement possible
    
    # Logique de décision finale (binaire uniquement)
    if base_classification == 'pleine':
        # Si c'était pleine, vérifier si les critères suggèrent le contraire
        if adjustment_score <= -8:
            return 'vide'  # Conditions masquent vraiment le contenu
        else:
            return 'pleine'
    else:  # base_classification == 'vide'
        # Si c'était vide, vérifier si les critères suggèrent qu'il y a des déchets
        if adjustment_score >= 8:
            return 'pleine'  # Bonnes conditions révèlent des déchets
        else:
            return 'vide'


def classify_by_improved_rules_with_mc(features, mc_criteria=None):
    """
    Classification améliorée avec prise en compte des critères MC
    Retourne uniquement 'pleine' ou 'vide' (suppression de partiellement_pleine)
    """
    # Classification de base
    base_result = classify_by_improved_rules(features)
    
    # Adapter avec les critères MC
    return adapt_classification_with_mc_criteria(base_result, mc_criteria)


def classify_by_improved_rules(features):
    """
    Classification améliorée basée sur les caractéristiques observées dans vos images
    """
    # Récupérer les valeurs pertinentes
    brightness = features['technical']['brightness']
    contrast = features['technical']['contrast']
    
    # Caractéristiques standard
    contour_pixels = features['technical'].get('contour_pixels', 0)
    r_mean = features['technical'].get('r_mean', 0)
    g_mean = features['technical'].get('g_mean', 0)
    b_mean = features['technical'].get('b_mean', 0)
    
    # Nouvelles caractéristiques
    edge_count = features['technical'].get('edge_count', 0)
    texture_variance = features['technical'].get('texture_variance', 0)
    dark_ratio = features['technical'].get('dark_ratio', 0)
    bright_ratio = features['technical'].get('bright_ratio', 0)
    
    # Score de classification (0 = vide, positif = pleine)
    score = 0
    
    # NOUVELLES RÈGLES BASÉES SUR VOS IMAGES
    
    # Règle 1: Détection de débris au sol (contraste élevé dans zones sombres)
    if dark_ratio > 0.3 and contrast > 0.3:
        score += 15  # Sacs noirs et débris visibles
    
    # Règle 2: Chaos visuel (beaucoup de contours = objets éparpillés)
    normalized_edges = edge_count / features['technical'].get('dimensions_pixels', 1000000)
    if normalized_edges > 0.001:  # Beaucoup d'activité visuelle
        score += 10
    
    # Règle 3: Dominance de couleur sombre (sacs poubelles noirs)
    if r_mean < 50 and g_mean < 50 and b_mean < 50:  # Très sombre
        score += 12
    elif r_mean < 80 and g_mean < 80 and b_mean < 80:  # Sombre
        score += 8
    
    # Règle 4: Faible luminosité avec fort contraste (objets qui dépassent)
    if brightness < 0.5 and contrast > 0.4:
        score += 10
    
    # Règle 5: Variance de texture élevée (surface irrégulière)
    if texture_variance > 0.15:
        score += 8
    
    # Règle 6: Combinaison critique (très probable d'être pleine)
    if dark_ratio > 0.4 and contrast > 0.5 and normalized_edges > 0.0015:
        score += 20  # Bonus pour combinaison critique
    
    # Règles négatives (indicateurs de poubelle vide)
    
    # Surface uniforme et claire
    if brightness > 0.7 and contrast < 0.2:
        score -= 10
    
    # Dominance de couleur verte (poubelle vide visible)
    if g_mean > r_mean + 20 and g_mean > b_mean + 20:
        score -= 8
    
    # Très peu d'activité visuelle
    if normalized_edges < 0.0005 and texture_variance < 0.05:
        score -= 15
    
    # Classification finale binaire (suppression de partiellement_pleine)
    if score >= 15:  # Seuil ajusté pour classification binaire
        return 'pleine'
    else:
        return 'vide'

def export_features_to_csv(features_list, output_path='image_features.csv', generate_viz=True):
    """
    Exporte les caractéristiques extraites des images vers un fichier CSV
    et génère des visualisations automatiques
    
    Args:
        features_list (list): Liste de dictionnaires de caractéristiques d'images
        output_path (str): Chemin du fichier CSV de sortie
        generate_viz (bool): Si True, génère des visualisations automatiques
    
    Returns:
        dict: Chemins des fichiers générés (CSV, JSON, visualisations)
    """
    if not features_list:
        raise ValueError("La liste de caractéristiques est vide")
    
    # Préparer les données pour le DataFrame
    data = []
    
    for i, features in enumerate(features_list):
        if 'filename' in features:
            img_name = features['filename']
        else:
            img_name = f"image_{i}"
            
        tech = features['technical']
        temp = features['temporal']
        
        # Extraire les caractéristiques pertinentes
        data.append([
            img_name,
            tech['file_size'],
            tech['dimensions'].split('x')[0],
            tech['dimensions'].split('x')[1],
            tech.get('r_mean', 0),
            tech.get('g_mean', 0),
            tech.get('b_mean', 0),
            tech['brightness'] * 255,
            tech['contrast'],
            tech.get('contour_pixels', 0),
            temp['day_of_week'],
            features.get('classification', None)
        ])
    
    # Créer le DataFrame
    columns = [
        "Nom de l'image", "Taille (octets)", "Largeur", "Hauteur",
        "Rouge moyen", "Vert moyen", "Bleu moyen", "Luminosité moyenne",
        "Contraste", "Pixels Contours", "Jour de la semaine", "Classification"
    ]
    
    df = pd.DataFrame(data, columns=columns)
    
    # Chemins de sortie
    result_paths = {}
    
    # 1. Exporter au format CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    result_paths['csv'] = output_path
    
    # 2. Exporter au format JSON
    json_path = output_path.replace('.csv', '.json')
    
    # Préparer une structure JSON plus riche
    json_data = {
        'metadata': {
            'date': datetime.now().isoformat(),
            'total_images': len(features_list),
            'pleines_count': sum(1 for f in features_list if f.get('classification') == 'pleine'),
            'vides_count': sum(1 for f in features_list if f.get('classification') == 'vide')
        },
        'images': []
    }
    
    # Ajouter des données pour chaque image
    for i, features in enumerate(features_list):
        if 'filename' in features:
            img_name = features['filename']
        else:
            img_name = f"image_{i}"
            
        tech = features['technical']
        temp = features['temporal']
        
        json_data['images'].append({
            'filename': img_name,
            'classification': features.get('classification', None),
            'technical': {
                'file_size': tech['file_size'],
                'dimensions': tech['dimensions'],
                'brightness': tech['brightness'],
                'contrast': tech['contrast'],
                'rgb': {
                    'r_mean': tech.get('r_mean', 0),
                    'g_mean': tech.get('g_mean', 0),
                    'b_mean': tech.get('b_mean', 0)
                },
                'contour_pixels': tech.get('contour_pixels', 0)
            },
            'temporal': {
                'day_of_week': temp['day_of_week'],
                'timestamp': temp.get('timestamp', None)
            }
        })
    
    # Écrire le JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
        
    result_paths['json'] = json_path
    
    # 3. Génération de visualisations si demandée
    if generate_viz:
        # Vérifier si matplotlib est disponible sans l'importer directement
        viz_available = False
        try:
            # Import conditionnel pour éviter les erreurs de linting
            matplotlib = __import__('matplotlib.pyplot', fromlist=[''])
            plt = matplotlib
            viz_available = True
        except ImportError:
            # matplotlib n'est pas disponible, désactiver les visualisations
            viz_available = False

        if viz_available:
            # Dossier de sortie pour les visualisations
            viz_dir = os.path.join(os.path.dirname(output_path), 'visualisations')
            os.makedirs(viz_dir, exist_ok=True)

            # 1. Diagramme en barres des classifications
            plt.figure(figsize=(10, 6))
            classification_counts = df['Classification'].value_counts()
            plt.bar(classification_counts.index, classification_counts.values, 
                    color=['#e74c3c', '#2ecc71'])
            plt.title('Distribution des poubelles pleines et vides')
            plt.xlabel('Classification')
            plt.ylabel('Nombre d\'images')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.savefig(os.path.join(viz_dir, 'classification_distribution.png'))
            plt.close()

            # 2. Nuage de points: Luminosité vs Contraste par classification
            plt.figure(figsize=(12, 8))
            for cls in df['Classification'].unique():
                subset = df[df['Classification'] == cls]
                color = '#e74c3c' if cls == 'pleine' else '#2ecc71'
                plt.scatter(subset['Luminosité moyenne'], subset['Contraste'], 
                           c=color, label=cls, alpha=0.7, s=80)

            plt.title('Relation entre luminosité et contraste par classification')
            plt.xlabel('Luminosité moyenne')
            plt.ylabel('Contraste')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(viz_dir, 'brightness_vs_contrast.png'))
            plt.close()

            # 3. Histogramme des valeurs RGB moyennes
            plt.figure(figsize=(12, 6))
            plt.hist(df['Rouge moyen'], bins=25, alpha=0.7, color='red', label='Rouge')
            plt.hist(df['Vert moyen'], bins=25, alpha=0.5, color='green', label='Vert')
            plt.hist(df['Bleu moyen'], bins=25, alpha=0.5, color='blue', label='Bleu')
            plt.title('Distribution des valeurs RGB moyennes')
            plt.xlabel('Valeur (0-255)')
            plt.ylabel('Nombre d\'images')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(viz_dir, 'rgb_distribution.png'))
            plt.close()

            # 4. Boxplot des pixels de contour par classification
            plt.figure(figsize=(10, 6))
            order = sorted(df['Classification'].unique())
            data = [df[df['Classification'] == cls]['Pixels Contours'] for cls in order]
            plt.boxplot(data, labels=order)
            plt.title('Distribution des pixels de contour par classification')
            plt.ylabel('Nombre de pixels de contour')
            plt.grid(True, alpha=0.3)
            plt.savefig(os.path.join(viz_dir, 'contours_boxplot.png'))
            plt.close()

            result_paths['visualizations'] = viz_dir
            print(f"Visualisations générées dans {viz_dir}")
    
    return result_paths

def process_image_folder(folder_path, output_path=None, generate_viz=True):
    """
    Traite toutes les images d'un dossier, extrait leurs caractéristiques,
    les classifie et exporte les résultats
    
    Args:
        folder_path (str): Chemin du dossier contenant les images
        output_path (str): Chemin du fichier CSV de sortie (facultatif)
        generate_viz (bool): Si True, génère des visualisations automatiques
    
    Returns:
        dict: Statistiques du traitement et chemins des fichiers générés
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"Le chemin {folder_path} n'est pas un dossier valide")
    
    # Si aucun chemin de sortie n'est spécifié, en créer un
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(os.path.dirname(folder_path), f"analyse_images_{timestamp}.csv")
    
    # Types de fichiers d'image à considérer
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    
    # Lister tous les fichiers du dossier
    features_list = []
    error_count = 0
    processed_count = 0
    
    print(f"Traitement des images dans {folder_path}...")
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Vérifier si c'est un fichier et une image
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in image_extensions:
            try:
                # Extraire les caractéristiques
                with open(file_path, 'rb') as img_file:
                    features = extract_features(img_file)
                    
                # Classifier l'image
                classification = classify_by_rules(features)
                
                # Ajouter la classification et le nom de fichier aux caractéristiques
                features['classification'] = classification
                features['filename'] = filename
                
                features_list.append(features)
                processed_count += 1
                
                print(f"Traité: {filename} - Classification: {classification}")
                
            except Exception as e:
                print(f"Erreur lors du traitement de {filename}: {str(e)}")
                error_count += 1
    
    # Si des images ont été traitées, exporter les résultats
    if features_list:
        result_paths = export_features_to_csv(features_list, output_path, generate_viz)
        
        stats = {
            'processed': processed_count,
            'errors': error_count,
            'total': processed_count + error_count,
            'pleines': sum(1 for f in features_list if f.get('classification') == 'pleine'),
            'vides': sum(1 for f in features_list if f.get('classification') == 'vide'),
            'output_paths': result_paths
        }
        
        return stats
    else:
        print("Aucune image n'a pu être traitée.")
        return None

# Pas de bloc main ici, ce module est destiné à être importé et utilisé par d'autres scripts.
