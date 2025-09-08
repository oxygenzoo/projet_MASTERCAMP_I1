# -*- coding: utf-8 -*-
"""
MC_fusion.py - Méthode Conditionnelle Fusionnée
Fusion optimisée des 3 analyseurs existants pour extraction de 200 caractéristiques
Focus sur l'analyse pure des pixels pour détection d'état des poubelles
Version sans classification automatique - extraction de features uniquement
"""

import cv2
import numpy as np
from PIL import Image
import os
import pandas as pd
from datetime import datetime
from skimage import segmentation, measure, feature, filters, morphology
from skimage.color import rgb2hsv, rgb2gray
from skimage.util import img_as_ubyte
import warnings
warnings.filterwarnings('ignore')

class UnifiedWasteAnalyzer:
    """
    Analyseur unifié fusionnant les 3 méthodes existantes
    Extraction de 200 caractéristiques basées sur l'analyse des pixels
    """
    
    def __init__(self, target_features=200):
        self.target_features = target_features
        
        # Seuils d'analyse optimisés
        self.pixel_thresholds = {
            'dark_intensity': 60,
            'bright_intensity': 200,
            'edge_sensitivity': 50,
            'min_object_size': 100
        }
        
        # Zones d'analyse pour modèles conditionnels
        self.analysis_zones = {
            'ground': (0.6, 1.0),     # Zone sol (60-100% de l'image)
            'container': (0.2, 0.8),  # Zone conteneur (20-80% de l'image)
            'overflow': (0.0, 0.6)    # Zone débordement (0-60% de l'image)
        }
    
    def _prepare_image(self, image_path):
        """Chargement et préparation de l'image"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Redimensionner pour optimiser les performances
            height, width = image.shape[:2]
            if width > 800:
                scale = 800 / width
                new_width = 800
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            return image
        except Exception as e:
            print(f"Erreur chargement {image_path}: {e}")
            return None
    
    def _define_analysis_zones(self, gray):
        """Définit les zones d'analyse optimisées pour les modèles conditionnels"""
        height, width = gray.shape
        zones = {}
        
        # Zone sol (partie basse) - critique pour débris
        ground_start = int(height * self.analysis_zones['ground'][0])
        zones['ground'] = gray[ground_start:, :]
        
        # Zone conteneur (partie centrale)
        container_start = int(height * self.analysis_zones['container'][0])
        container_end = int(height * self.analysis_zones['container'][1])
        zones['container'] = gray[container_start:container_end, :]
        
        # Zone débordement (partie haute)
        overflow_end = int(height * self.analysis_zones['overflow'][1])
        zones['overflow'] = gray[:overflow_end, :]
        
        # Zones latérales pour objets éparpillés
        side_width = int(width * 0.3)
        zones['left_side'] = gray[:, :side_width]
        zones['right_side'] = gray[:, -side_width:]
        
        # Zone centrale verticale
        center_start = int(width * 0.3)
        center_end = int(width * 0.7)
        zones['center'] = gray[:, center_start:center_end]
        
        return zones
    
    def extract_basic_features(self, image):
        """Extraction des caractéristiques de base (50 features)"""
        features = {}
        
        # Conversion espaces colorimétriques
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        height, width = gray.shape
        total_pixels = height * width
        
        # Métadonnées image (5 features)
        features['image_width'] = width
        features['image_height'] = height
        features['total_pixels'] = total_pixels
        features['aspect_ratio'] = width / height
        features['diagonal'] = np.sqrt(width**2 + height**2)
        
        # Statistiques d'intensité globales (15 features)
        features['global_mean'] = float(np.mean(gray))
        features['global_std'] = float(np.std(gray))
        features['global_min'] = int(np.min(gray))
        features['global_max'] = int(np.max(gray))
        features['global_median'] = float(np.median(gray))
        features['global_range'] = float(np.max(gray) - np.min(gray))
        features['global_q25'] = float(np.percentile(gray, 25))
        features['global_q75'] = float(np.percentile(gray, 75))
        features['global_iqr'] = features['global_q75'] - features['global_q25']
        features['global_skewness'] = float(np.mean(((gray - np.mean(gray)) / (np.std(gray) + 1e-10))**3))
        features['global_kurtosis'] = float(np.mean(((gray - np.mean(gray)) / (np.std(gray) + 1e-10))**4))
        
        # Ratios de pixels par intensité (4 features)
        dark_pixels = np.sum(gray < self.pixel_thresholds['dark_intensity'])
        bright_pixels = np.sum(gray > self.pixel_thresholds['bright_intensity'])
        features['dark_pixels_ratio'] = float(dark_pixels / total_pixels)
        features['bright_pixels_ratio'] = float(bright_pixels / total_pixels)
        features['mid_pixels_ratio'] = float(1 - features['dark_pixels_ratio'] - features['bright_pixels_ratio'])
        features['contrast_ratio'] = float(features['bright_pixels_ratio'] / (features['dark_pixels_ratio'] + 1e-10))
        
        # Analyse HSV globale (12 features)
        h_channel, s_channel, v_channel = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
        features['hue_mean'] = float(np.mean(h_channel))
        features['hue_std'] = float(np.std(h_channel))
        features['saturation_mean'] = float(np.mean(s_channel))
        features['saturation_std'] = float(np.std(s_channel))
        features['value_mean'] = float(np.mean(v_channel))
        features['value_std'] = float(np.std(v_channel))
        features['hue_range'] = float(np.max(h_channel) - np.min(h_channel))
        features['saturation_range'] = float(np.max(s_channel) - np.min(s_channel))
        features['value_range'] = float(np.max(v_channel) - np.min(v_channel))
        features['hsv_mean_combined'] = float((features['hue_mean'] + features['saturation_mean'] + features['value_mean']) / 3)
        features['hsv_std_combined'] = float((features['hue_std'] + features['saturation_std'] + features['value_std']) / 3)
        features['color_diversity'] = float(features['hue_std'] * features['saturation_std'])
        
        # Analyse RGB (14 features)
        if len(image.shape) == 3:
            b, g, r = cv2.split(image)
            for channel, name in [(r, 'red'), (g, 'green'), (b, 'blue')]:
                features[f'{name}_mean'] = float(np.mean(channel))
                features[f'{name}_std'] = float(np.std(channel))
                features[f'{name}_min'] = float(np.min(channel))
                features[f'{name}_max'] = float(np.max(channel))
            features['rgb_balance'] = float(abs(features['red_mean'] - features['green_mean']) + 
                                          abs(features['green_mean'] - features['blue_mean']) + 
                                          abs(features['blue_mean'] - features['red_mean']))
            features['dominant_channel'] = float(np.argmax([features['red_mean'], features['green_mean'], features['blue_mean']]))
        
        return features
    
    def extract_texture_features(self, image):
        """Extraction des caractéristiques de texture (40 features)"""
        features = {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # 1. LBP - Local Binary Patterns (15 features)
        try:
            # LBP avec différents rayons
            for radius in [1, 2, 3]:
                n_points = 8 * radius
                lbp = feature.local_binary_pattern(gray, n_points, radius, method='uniform')
                lbp_hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
                if lbp_hist.sum() > 0:
                    lbp_hist = lbp_hist.astype(float) / lbp_hist.sum()
                    features[f'lbp_r{radius}_mean'] = float(np.mean(lbp))
                    features[f'lbp_r{radius}_std'] = float(np.std(lbp))
                    features[f'lbp_r{radius}_entropy'] = float(-np.sum(lbp_hist * np.log2(lbp_hist + 1e-10)))
                    features[f'lbp_r{radius}_uniformity'] = float(np.sum(lbp_hist ** 2))
                    features[f'lbp_r{radius}_contrast'] = float(np.sum([(i - j) ** 2 * lbp_hist[i] * lbp_hist[j] 
                                                                       for i in range(len(lbp_hist)) 
                                                                       for j in range(len(lbp_hist))]))
                else:
                    for metric in ['mean', 'std', 'entropy', 'uniformity', 'contrast']:
                        features[f'lbp_r{radius}_{metric}'] = 0.0
        except:
            for radius in [1, 2, 3]:
                for metric in ['mean', 'std', 'entropy', 'uniformity', 'contrast']:
                    features[f'lbp_r{radius}_{metric}'] = 0.0
        
        # 2. Matrice de co-occurrence (GLCM) (8 features)
        try:
            # Quantifier l'image pour GLCM
            gray_quantized = (gray / 32).astype(np.uint8)
            glcm = feature.greycomatrix(gray_quantized, [1], [0, np.pi/4, np.pi/2, 3*np.pi/4], 
                                       levels=8, symmetric=True, normed=True)
            
            # Propriétés GLCM
            features['glcm_contrast'] = float(np.mean(feature.greycoprops(glcm, 'contrast')))
            features['glcm_dissimilarity'] = float(np.mean(feature.greycoprops(glcm, 'dissimilarity')))
            features['glcm_homogeneity'] = float(np.mean(feature.greycoprops(glcm, 'homogeneity')))
            features['glcm_energy'] = float(np.mean(feature.greycoprops(glcm, 'energy')))
            features['glcm_correlation'] = float(np.mean(feature.greycoprops(glcm, 'correlation')))
            features['glcm_ASM'] = float(np.mean(feature.greycoprops(glcm, 'ASM')))
            
            # Moyennes par direction
            contrast_values = feature.greycoprops(glcm, 'contrast')[0]
            features['glcm_contrast_std'] = float(np.std(contrast_values))
            features['glcm_contrast_range'] = float(np.max(contrast_values) - np.min(contrast_values))
            
        except:
            for prop in ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation', 'ASM']:
                features[f'glcm_{prop}'] = 0.0
            features['glcm_contrast_std'] = 0.0
            features['glcm_contrast_range'] = 0.0
        
        # 3. Filtres de Gabor (8 features)
        try:
            gabor_responses = []
            for theta in [0, np.pi/4, np.pi/2, 3*np.pi/4]:
                for frequency in [0.1, 0.3]:
                    real, _ = filters.gabor(gray, frequency=frequency, theta=theta)
                    gabor_responses.append(real)
            
            # Statistiques des réponses Gabor
            all_responses = np.concatenate([resp.flatten() for resp in gabor_responses])
            features['gabor_mean'] = float(np.mean(all_responses))
            features['gabor_std'] = float(np.std(all_responses))
            features['gabor_min'] = float(np.min(all_responses))
            features['gabor_max'] = float(np.max(all_responses))
            features['gabor_range'] = features['gabor_max'] - features['gabor_min']
            
            # Énergie par orientation
            energies = [np.sum(resp ** 2) for resp in gabor_responses]
            features['gabor_energy_mean'] = float(np.mean(energies))
            features['gabor_energy_std'] = float(np.std(energies))
            features['gabor_energy_max'] = float(np.max(energies))
            
        except:
            for prop in ['mean', 'std', 'min', 'max', 'range', 'energy_mean', 'energy_std', 'energy_max']:
                features[f'gabor_{prop}'] = 0.0
        
        # 4. Analyse de texture locale (9 features)
        try:
            # Variance locale
            kernel = np.ones((5, 5), np.float32) / 25
            local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            local_sq_mean = cv2.filter2D((gray.astype(np.float32)) ** 2, -1, kernel)
            local_variance = local_sq_mean - local_mean ** 2
            
            features['local_variance_mean'] = float(np.mean(local_variance))
            features['local_variance_std'] = float(np.std(local_variance))
            features['local_variance_max'] = float(np.max(local_variance))
            features['local_variance_min'] = float(np.min(local_variance))
            
            # Entropie locale (simplifiée)
            hist, _ = np.histogram(gray, bins=16, range=(0, 256))
            hist = hist + 1e-10
            hist = hist / np.sum(hist)
            features['local_entropy'] = float(-np.sum(hist * np.log2(hist)))
            
            # Variabilité de texture
            features['texture_variance'] = float(np.var(gray))
            features['texture_energy'] = float(np.sum(gray ** 2))
            features['texture_homogeneity'] = float(1.0 / (1.0 + np.var(gray)))
            features['texture_contrast'] = float(np.max(gray) - np.min(gray))
            
        except:
            for metric in ['local_variance_mean', 'local_variance_std', 'local_variance_max', 
                          'local_variance_min', 'local_entropy', 'texture_variance', 
                          'texture_energy', 'texture_homogeneity', 'texture_contrast']:
                features[metric] = 0.0
        
        return features
    
    def extract_edge_features(self, image):
        """Extraction des caractéristiques de contours (30 features)"""
        features = {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        total_pixels = height * width
        
        # 1. Détection de contours multi-échelle (12 features)
        try:
            scales = [(1, 50, 150), (2, 30, 100), (3, 20, 80)]
            
            for i, (sigma, low, high) in enumerate(scales):
                blurred = cv2.GaussianBlur(gray, (0, 0), sigma)
                edges = cv2.Canny(blurred, low, high)
                
                edge_density = np.sum(edges > 0) / total_pixels
                features[f'edge_density_scale_{i}'] = float(edge_density)
                
                # Analyse des contours
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                features[f'contour_count_scale_{i}'] = len(contours)
                
                if contours:
                    # Longueur totale des contours
                    total_length = sum(cv2.arcLength(c, True) for c in contours)
                    features[f'contour_length_scale_{i}'] = float(total_length)
                    
                    # Complexité moyenne des contours
                    complexities = []
                    for contour in contours:
                        area = cv2.contourArea(contour)
                        if area > 10:
                            perimeter = cv2.arcLength(contour, True)
                            if perimeter > 0:
                                complexity = (perimeter ** 2) / (4 * np.pi * area)
                                complexities.append(complexity)
                    
                    if complexities:
                        features[f'contour_complexity_scale_{i}'] = float(np.mean(complexities))
                    else:
                        features[f'contour_complexity_scale_{i}'] = 0.0
                else:
                    features[f'contour_length_scale_{i}'] = 0.0
                    features[f'contour_complexity_scale_{i}'] = 0.0
        except:
            for i in range(3):
                features[f'edge_density_scale_{i}'] = 0.0
                features[f'contour_count_scale_{i}'] = 0
                features[f'contour_length_scale_{i}'] = 0.0
                features[f'contour_complexity_scale_{i}'] = 0.0
        
        # 2. Détection de lignes (6 features)
        try:
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=50)
            
            if lines is not None:
                features['hough_lines_count'] = len(lines)
                
                # Analyse des angles des lignes
                angles = [line[0][1] for line in lines]
                features['hough_lines_angle_mean'] = float(np.mean(angles))
                features['hough_lines_angle_std'] = float(np.std(angles))
                
                # Lignes horizontales vs verticales
                horizontal_lines = sum(1 for angle in angles if abs(angle) < np.pi/4 or abs(angle - np.pi) < np.pi/4)
                vertical_lines = sum(1 for angle in angles if abs(angle - np.pi/2) < np.pi/4)
                features['horizontal_lines'] = horizontal_lines
                features['vertical_lines'] = vertical_lines
                features['line_orientation_ratio'] = float(horizontal_lines / (vertical_lines + 1e-10))
            else:
                for key in ['hough_lines_count', 'hough_lines_angle_mean', 'hough_lines_angle_std',
                           'horizontal_lines', 'vertical_lines', 'line_orientation_ratio']:
                    features[key] = 0.0
        except:
            for key in ['hough_lines_count', 'hough_lines_angle_mean', 'hough_lines_angle_std',
                       'horizontal_lines', 'vertical_lines', 'line_orientation_ratio']:
                features[key] = 0.0
        
        # 3. Analyse directionnelle des gradients (12 features)
        try:
            # Gradients de Sobel
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Magnitude et direction
            magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            direction = np.arctan2(sobel_y, sobel_x)
            
            features['gradient_magnitude_mean'] = float(np.mean(magnitude))
            features['gradient_magnitude_std'] = float(np.std(magnitude))
            features['gradient_magnitude_max'] = float(np.max(magnitude))
            
            # Histogramme des directions
            direction_hist, _ = np.histogram(direction, bins=8, range=(-np.pi, np.pi))
            direction_hist = direction_hist.astype(float) / np.sum(direction_hist)
            
            # Entropie directionnelle
            features['gradient_direction_entropy'] = float(-np.sum(direction_hist * np.log2(direction_hist + 1e-10)))
            
            # Dominance directionnelle
            features['gradient_direction_dominance'] = float(np.max(direction_hist))
            
            # Analyse par quadrant
            for i, direction_range in enumerate([(-np.pi, -np.pi/2), (-np.pi/2, 0), (0, np.pi/2), (np.pi/2, np.pi)]):
                mask = (direction >= direction_range[0]) & (direction < direction_range[1])
                features[f'gradient_quadrant_{i}'] = float(np.sum(mask) / total_pixels)
            
            # Cohérence directionnelle
            dx_mean = np.mean(sobel_x)
            dy_mean = np.mean(sobel_y)
            features['gradient_coherence'] = float(np.sqrt(dx_mean**2 + dy_mean**2) / (np.mean(magnitude) + 1e-10))
            
            # Anisotropie
            features['gradient_anisotropy'] = float(np.std(direction_hist))
            
        except:
            for key in ['gradient_magnitude_mean', 'gradient_magnitude_std', 'gradient_magnitude_max',
                       'gradient_direction_entropy', 'gradient_direction_dominance', 'gradient_coherence',
                       'gradient_anisotropy']:
                features[key] = 0.0
            for i in range(4):
                features[f'gradient_quadrant_{i}'] = 0.0
        
        return features
    
    def extract_morphological_features(self, image):
        """Extraction des caractéristiques morphologiques (25 features)"""
        features = {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # 1. Opérations morphologiques de base (10 features)
        try:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            gray_uint8 = (gray * 255).astype(np.uint8) if gray.dtype != np.uint8 else gray
            
            # Opérations morphologiques
            opened = cv2.morphologyEx(gray_uint8, cv2.MORPH_OPEN, kernel)
            closed = cv2.morphologyEx(gray_uint8, cv2.MORPH_CLOSE, kernel)
            gradient = cv2.morphologyEx(gray_uint8, cv2.MORPH_GRADIENT, kernel)
            tophat = cv2.morphologyEx(gray_uint8, cv2.MORPH_TOPHAT, kernel)
            blackhat = cv2.morphologyEx(gray_uint8, cv2.MORPH_BLACKHAT, kernel)
            
            features['morpho_opening_mean'] = float(np.mean(opened))
            features['morpho_closing_mean'] = float(np.mean(closed))
            features['morpho_gradient_mean'] = float(np.mean(gradient))
            features['morpho_tophat_mean'] = float(np.mean(tophat))
            features['morpho_blackhat_mean'] = float(np.mean(blackhat))
            
            # Différences morphologiques
            features['opening_closing_diff'] = float(np.mean(np.abs(opened.astype(float) - closed.astype(float))))
            features['tophat_blackhat_diff'] = float(np.mean(np.abs(tophat.astype(float) - blackhat.astype(float))))
            
            # Complexité morphologique
            features['morpho_complexity'] = float(np.std(gradient) / (np.mean(gradient) + 1e-10))
            features['morpho_gradient_max'] = float(np.max(gradient))
            features['morpho_gradient_range'] = float(np.max(gradient) - np.min(gradient))
            
        except:
            for key in ['morpho_opening_mean', 'morpho_closing_mean', 'morpho_gradient_mean',
                       'morpho_tophat_mean', 'morpho_blackhat_mean', 'opening_closing_diff',
                       'tophat_blackhat_diff', 'morpho_complexity', 'morpho_gradient_max',
                       'morpho_gradient_range']:
                features[key] = 0.0
        
        # 2. Analyse de squelettisation (5 features)
        try:
            # Binarisation
            _, binary = cv2.threshold(gray_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Squelettisation
            skeleton = morphology.skeletonize(binary // 255)
            
            features['skeleton_length'] = float(np.sum(skeleton))
            features['skeleton_density'] = float(np.sum(skeleton) / (height * width))
            
            # Branches du squelette
            labeled_skeleton = measure.label(skeleton)
            regions = measure.regionprops(labeled_skeleton)
            
            if regions:
                features['skeleton_branches'] = len(regions)
                branch_lengths = [r.area for r in regions]
                features['skeleton_branch_mean'] = float(np.mean(branch_lengths))
                features['skeleton_branch_std'] = float(np.std(branch_lengths))
            else:
                features['skeleton_branches'] = 0
                features['skeleton_branch_mean'] = 0.0
                features['skeleton_branch_std'] = 0.0
                
        except:
            for key in ['skeleton_length', 'skeleton_density', 'skeleton_branches',
                       'skeleton_branch_mean', 'skeleton_branch_std']:
                features[key] = 0.0
        
        # 3. Analyse granulométrique (10 features)
        try:
            # Granulométrie par ouverture
            sizes = [1, 3, 5, 7, 9]
            opening_sizes = []
            
            for size in sizes:
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
                opened = cv2.morphologyEx(gray_uint8, cv2.MORPH_OPEN, kernel)
                remaining = np.sum(opened > 0)
                opening_sizes.append(remaining)
            
            # Courbe granulométrique
            features['granulo_mean'] = float(np.mean(opening_sizes))
            features['granulo_std'] = float(np.std(opening_sizes))
            features['granulo_slope'] = float((opening_sizes[-1] - opening_sizes[0]) / len(opening_sizes))
            
            # Taille caractéristique
            if len(opening_sizes) > 1:
                diffs = np.diff(opening_sizes)
                max_diff_idx = np.argmax(np.abs(diffs))
                features['granulo_char_size'] = float(sizes[max_diff_idx])
            else:
                features['granulo_char_size'] = 0.0
            
            # Propriétés par taille
            for i, size in enumerate(sizes[:5]):
                features[f'granulo_size_{size}'] = float(opening_sizes[i])
            
            # Uniformité granulométrique
            features['granulo_uniformity'] = float(1.0 / (1.0 + np.var(opening_sizes)))
            
        except:
            for key in ['granulo_mean', 'granulo_std', 'granulo_slope', 'granulo_char_size',
                       'granulo_uniformity']:
                features[key] = 0.0
            for size in [1, 3, 5, 7, 9]:
                features[f'granulo_size_{size}'] = 0.0
        
        return features
    
    def extract_spatial_features(self, image):
        """Extraction des caractéristiques spatiales (30 features)"""
        features = {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # 1. Analyse par quadrants (16 features)
        try:
            h_mid, w_mid = height // 2, width // 2
            
            # Définir les quadrants
            quadrants = {
                'top_left': gray[:h_mid, :w_mid],
                'top_right': gray[:h_mid, w_mid:],
                'bottom_left': gray[h_mid:, :w_mid],
                'bottom_right': gray[h_mid:, w_mid:]
            }
            
            # Statistiques par quadrant
            for quad_name, quad_data in quadrants.items():
                if quad_data.size > 0:
                    features[f'{quad_name}_mean'] = float(np.mean(quad_data))
                    features[f'{quad_name}_std'] = float(np.std(quad_data))
                    
                    # Entropie simplifiée
                    hist, _ = np.histogram(quad_data, bins=8, range=(0, 256))
                    hist = hist + 1e-10
                    hist = hist / np.sum(hist)
                    features[f'{quad_name}_entropy'] = float(-np.sum(hist * np.log2(hist)))
                    
                    # Activité (différences)
                    features[f'{quad_name}_activity'] = float(np.sum(np.abs(np.diff(quad_data.flatten()))))
                else:
                    features[f'{quad_name}_mean'] = 0.0
                    features[f'{quad_name}_std'] = 0.0
                    features[f'{quad_name}_entropy'] = 0.0
                    features[f'{quad_name}_activity'] = 0.0
            
        except:
            for quad_name in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
                for metric in ['mean', 'std', 'entropy', 'activity']:
                    features[f'{quad_name}_{metric}'] = 0.0
        
        # 2. Analyse des zones définies (14 features)
        try:
            zones = self._define_analysis_zones(gray)
            
            zone_names = ['ground', 'container', 'overflow', 'left_side', 'right_side', 'center']
            for zone_name in zone_names:
                if zone_name in zones and zones[zone_name].size > 0:
                    zone_data = zones[zone_name]
                    features[f'zone_{zone_name}_mean'] = float(np.mean(zone_data))
                    features[f'zone_{zone_name}_std'] = float(np.std(zone_data))
                    
                    # Contraste local
                    local_contrast = np.max(zone_data) - np.min(zone_data)
                    features[f'zone_{zone_name}_contrast'] = float(local_contrast)
                else:
                    features[f'zone_{zone_name}_mean'] = 0.0
                    features[f'zone_{zone_name}_std'] = 0.0
                    features[f'zone_{zone_name}_contrast'] = 0.0
        except:
            zone_names = ['ground', 'container', 'overflow', 'left_side', 'right_side', 'center']
            for zone_name in zone_names:
                for metric in ['mean', 'std', 'contrast']:
                    features[f'zone_{zone_name}_{metric}'] = 0.0
        
        return features
    
    def extract_color_features(self, image):
        """Extraction des caractéristiques couleur avancées (25 features)"""
        features = {}
        
        height, width = image.shape[:2]
        total_pixels = height * width
        
        # 1. Analyse HSV avancée (10 features)
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h_channel, s_channel, v_channel = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
            
            # Masques de couleurs spécifiques
            color_masks = {
                'green': cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255])),
                'dark': cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60])),
                'bright': cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255])),
                'red': cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255])),
                'blue': cv2.inRange(hsv, np.array([100, 50, 50]), np.array([130, 255, 255]))
            }
            
            # Ratios de couleurs
            for color_name, mask in color_masks.items():
                pixel_count = np.sum(mask > 0)
                features[f'{color_name}_pixel_ratio'] = float(pixel_count / total_pixels)
            
            # Diversité de couleurs
            features['color_diversity_hsv'] = float(np.std(h_channel) * np.std(s_channel))
            features['saturation_coverage'] = float(np.sum(s_channel > 50) / total_pixels)
            features['brightness_coverage'] = float(np.sum(v_channel > 100) / total_pixels)
            features['hue_concentration'] = float(1.0 / (1.0 + np.std(h_channel)))
            features['color_uniformity'] = float(1.0 / (1.0 + np.std(s_channel)))
            
        except:
            for color in ['green', 'dark', 'bright', 'red', 'blue']:
                features[f'{color}_pixel_ratio'] = 0.0
            for metric in ['color_diversity_hsv', 'saturation_coverage', 'brightness_coverage',
                          'hue_concentration', 'color_uniformity']:
                features[metric] = 0.0
        
        # 2. Segmentation couleur (15 features)
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Segmentation SLIC
            segments = segmentation.slic(rgb_image, n_segments=50, compactness=10, sigma=1)
            n_segments = len(np.unique(segments))
            features['color_segments'] = int(n_segments)
            
            # Propriétés des segments
            props = measure.regionprops(segments, rgb_image)
            if props:
                segment_areas = [prop.area for prop in props if prop.area > 10]
                segment_colors = [prop.mean_intensity for prop in props if prop.area > 10]
                
                if segment_areas and segment_colors:
                    features['segment_area_mean'] = float(np.mean(segment_areas))
                    features['segment_area_std'] = float(np.std(segment_areas))
                    features['segment_area_max'] = float(np.max(segment_areas))
                    
                    # Analyse des couleurs des segments
                    segment_colors = np.array(segment_colors)
                    features['segment_color_diversity'] = float(np.std(segment_colors))
                    features['segment_brightness_mean'] = float(np.mean(segment_colors))
                    features['segment_brightness_std'] = float(np.std(segment_colors))
                    
                    # Répartition des segments par région
                    h_mid = height // 2
                    segments_top = np.sum(segments < h_mid)
                    segments_bottom = np.sum(segments >= h_mid)
                    features['segments_top_bottom_ratio'] = float(segments_top / (segments_bottom + 1e-10))
                    
                    # Compacité des segments
                    compactness_scores = []
                    for prop in props:
                        if prop.area > 10:
                            compactness = 4 * np.pi * prop.area / (prop.perimeter ** 2) if prop.perimeter > 0 else 0
                            compactness_scores.append(compactness)
                    
                    if compactness_scores:
                        features['segment_compactness_mean'] = float(np.mean(compactness_scores))
                        features['segment_compactness_std'] = float(np.std(compactness_scores))
                    else:
                        features['segment_compactness_mean'] = 0.0
                        features['segment_compactness_std'] = 0.0
                    
                    # Entropie des segments
                    segment_hist, _ = np.histogram(segments, bins=min(50, n_segments))
                    segment_hist = segment_hist + 1e-10
                    segment_hist = segment_hist / np.sum(segment_hist)
                    features['segment_entropy'] = float(-np.sum(segment_hist * np.log2(segment_hist)))
                    
                    # Uniformité des segments
                    features['segment_uniformity'] = float(np.sum(segment_hist ** 2))
                    
                    # Dominance du plus grand segment
                    features['largest_segment_dominance'] = float(np.max(segment_areas) / total_pixels)
                    
                    # Fragmentation des couleurs
                    features['color_fragmentation'] = float(n_segments / np.sqrt(total_pixels))
                    
                else:
                    # Valeurs par défaut si pas de segments valides
                    for key in ['segment_area_mean', 'segment_area_std', 'segment_area_max',
                               'segment_color_diversity', 'segment_brightness_mean', 'segment_brightness_std',
                               'segments_top_bottom_ratio', 'segment_compactness_mean', 'segment_compactness_std',
                               'segment_entropy', 'segment_uniformity', 'largest_segment_dominance',
                               'color_fragmentation']:
                        features[key] = 0.0
            else:
                for key in ['segment_area_mean', 'segment_area_std', 'segment_area_max',
                           'segment_color_diversity', 'segment_brightness_mean', 'segment_brightness_std',
                           'segments_top_bottom_ratio', 'segment_compactness_mean', 'segment_compactness_std',
                           'segment_entropy', 'segment_uniformity', 'largest_segment_dominance',
                           'color_fragmentation']:
                    features[key] = 0.0
                    
        except:
            features['color_segments'] = 0
            for key in ['segment_area_mean', 'segment_area_std', 'segment_area_max',
                       'segment_color_diversity', 'segment_brightness_mean', 'segment_brightness_std',
                       'segments_top_bottom_ratio', 'segment_compactness_mean', 'segment_compactness_std',
                       'segment_entropy', 'segment_uniformity', 'largest_segment_dominance',
                       'color_fragmentation']:
                features[key] = 0.0
        
        return features
    
    def extract_all_features(self, image_path):
        """Extraction complète de toutes les caractéristiques (~200 features)"""
        
        # Chargement de l'image
        image = self._prepare_image(image_path)
        if image is None:
            return None
        
        # Extraction par catégorie
        all_features = {}
        
        try:
            # 1. Caractéristiques de base (50 features)
            basic_features = self.extract_basic_features(image)
            all_features.update(basic_features)
            
            # 2. Caractéristiques de texture (40 features)
            texture_features = self.extract_texture_features(image)
            all_features.update(texture_features)
            
            # 3. Caractéristiques de contours (30 features)
            edge_features = self.extract_edge_features(image)
            all_features.update(edge_features)
            
            # 4. Caractéristiques morphologiques (25 features)
            morpho_features = self.extract_morphological_features(image)
            all_features.update(morpho_features)
            
            # 5. Caractéristiques spatiales (30 features)
            spatial_features = self.extract_spatial_features(image)
            all_features.update(spatial_features)
            
            # 6. Caractéristiques couleur (25 features)
            color_features = self.extract_color_features(image)
            all_features.update(color_features)
            
            # Ajouter métadonnées
            all_features['filename'] = os.path.basename(image_path)
            all_features['timestamp'] = datetime.now().isoformat()
            all_features['total_features'] = len(all_features)
            
            return all_features
            
        except Exception as e:
            print(f"Erreur lors de l'extraction des caractéristiques pour {image_path}: {e}")
            return None
    
    def process_image_folder(self, folder_path, output_csv=None):
        """Traitement d'un dossier d'images avec sauvegarde CSV"""
        
        if not os.path.exists(folder_path):
            print(f"Erreur: Le dossier {folder_path} n'existe pas")
            return None
        
        # Recherche des images
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend([f for f in os.listdir(folder_path) if f.lower().endswith(ext)])
        
        if not image_files:
            print(f"Aucune image trouvée dans {folder_path}")
            return None
        
        print(f"Traitement de {len(image_files)} images...")
        
        # Extraction des caractéristiques
        all_features = []
        
        for i, image_file in enumerate(image_files):
            image_path = os.path.join(folder_path, image_file)
            print(f"Traitement {i+1}/{len(image_files)}: {image_file}")
            
            features = self.extract_all_features(image_path)
            if features:
                all_features.append(features)
        
        if not all_features:
            print("Aucune caractéristique extraite")
            return None
        
        # Conversion en DataFrame
        df = pd.DataFrame(all_features)
        
        # Sauvegarde CSV
        if output_csv is None:
            output_csv = os.path.join(folder_path, f'features_MC_fusion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"Caractéristiques sauvegardées dans: {output_csv}")
        
        # Résumé
        print(f"\nRésumé:")
        print(f"- {len(all_features)} images traitées")
        print(f"- {len(df.columns)} caractéristiques extraites par image")
        print(f"- Fichier CSV: {output_csv}")
        
        return df
    
    def analyze_django_image(self, image_file):
        """
        Méthode spéciale pour l'intégration Django
        
        Args:
            image_file: Fichier image depuis un Django ImageField ou UploadedFile
                        (peut être le chemin complet ou l'objet fichier)
        
        Returns:
            dict: Dictionnaire de caractéristiques extraites, prêt pour sérialisation JSON
                 Retourne None en cas d'erreur
        """
        try:
            # Si c'est un objet fichier Django
            if hasattr(image_file, 'path'):
                image_path = image_file.path
            # Si c'est déjà un chemin de fichier
            elif isinstance(image_file, str):
                image_path = image_file
            # Si c'est un UploadedFile temporaire
            elif hasattr(image_file, 'temporary_file_path'):
                image_path = image_file.temporary_file_path()
            # Si c'est un fichier en mémoire, écrire dans un fichier temporaire
            else:
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp:
                    for chunk in image_file.chunks():
                        temp.write(chunk)
                    image_path = temp.name
            
            # Extraire les caractéristiques
            features = self.extract_all_features(image_path)
            
            # Nettoyer les valeurs pour JSON (convertir numpy types en Python natifs)
            if features:
                for key, value in features.items():
                    if isinstance(value, np.integer):
                        features[key] = int(value)
                    elif isinstance(value, np.floating):
                        features[key] = float(value)
                    elif isinstance(value, np.ndarray):
                        features[key] = value.tolist()
            
            # Supprimer le fichier temporaire si créé
            if 'temp' in locals():
                import os
                os.unlink(image_path)
                
            return features
            
        except Exception as e:
            print(f"Erreur d'analyse Django: {e}")
            import traceback
            traceback.print_exc()
            return None
