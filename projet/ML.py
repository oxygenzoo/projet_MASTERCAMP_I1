# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 12:01:45 2025

@author: willi
"""

"""
Génération des fichiers de données avec MC unifié
"""
from MC_fusion import UnifiedWasteAnalyzer
import pandas as pd
import os

print(" Génération des fichiers de données avec MC unifié...")

# Configuration
TARGET_FEATURES = 250  # Nombre optimal de features

# Vérifier la structure des images
image_folder = "backend/media/uploads"
if os.path.exists(image_folder):
    print(f" Dossier d'images trouvé : {image_folder}")
    images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f" {len(images)} images trouvées")
    
    # Créer l'analyseur MC unifié
    analyzer = UnifiedWasteAnalyzer(target_features=TARGET_FEATURES)
    
    # Traiter toutes les images avec MC
    df_all = analyzer.process_image_folder(image_folder, output_path="mc_all_features.csv")
    print(f" Fichiers MC générés avec {len(df_all.columns)-1} features !")
    
    # Diviser les données pour l'entraînement (simulation)
    # TODO: Remplacer par vos vraies étiquettes
    n_images = len(df_all)
    n_clean = n_images // 2
    
    df_clean = df_all.iloc[:n_clean].copy()
    df_dirty = df_all.iloc[n_clean:].copy()
    
    # Ajouter les classifications
    df_clean['Classification'] = 'vide'
    df_dirty['Classification'] = 'pleine'
    
    # Sauvegarder les fichiers d'entraînement
    df_clean.to_csv("train_clean.csv", index=False)
    df_dirty.to_csv("train_dirty.csv", index=False)
    
    # Utiliser quelques images pour le test
    n_test = min(50, n_images // 10)
    df_test = df_all.iloc[-n_test:].copy()
    df_test.to_csv("test_features.csv", index=False)
    
    print(f" Données préparées : {len(df_clean)} vides, {len(df_dirty)} pleines, {len(df_test)} test")
    print(f" Features disponibles : {len(df_all.columns)-1}")
else:
    print(f" Dossier {image_folder} non trouvé")
    exit()

print("="*60)
print(" ENTRAÎNEMENT DU MODÈLE ML")
print("="*60)

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import train_test_split, cross_val_score, KFold, GridSearchCV, cross_validate
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

df_clean = pd.read_csv("train_clean.csv", sep=",")
df_dirty = pd.read_csv("train_dirty.csv", sep=",")

df_clean['Classification'] = 'vide'
df_dirty['Classification'] = 'pleine'

df_train = pd.concat([df_clean, df_dirty], ignore_index=True)
df_test = pd.read_csv("test_features.csv", sep=",")

# ANALYSE DES FEATURES DISPONIBLES
print("="*60)
print(" ANALYSE DES FEATURES DISPONIBLES")
print("="*60)

print(f" Colonnes dans df_train: {df_train.shape[1]} colonnes")
print(f" Colonnes dans df_test: {df_test.shape[1]} colonnes")
print(f" Nombre d'échantillons train: {df_train.shape[0]}")
print(f" Nombre d'échantillons test: {df_test.shape[0]}")

# Identifier les features numériques
numeric_train = df_train.select_dtypes(include=[np.number]).columns.tolist()
numeric_test = df_test.select_dtypes(include=[np.number]).columns.tolist()

print(f"\n FEATURES NUMÉRIQUES DISPONIBLES:")
print(f"Train: {len(numeric_train)} features numériques")
print(f"Test: {len(numeric_test)} features numériques")

# Enlever les colonnes non-features (index, etc.)
exclude_cols = ['Unnamed: 0', 'index'] 
available_features = [col for col in numeric_train if col not in exclude_cols]

print(f"\n FEATURES UTILISABLES: {len(available_features)}")
print("\nQuelques exemples de features MC:")
for i, feature in enumerate(available_features[:15], 1):
    print(f"{i:2d}. {feature}")
if len(available_features) > 15:
    print(f"    ... et {len(available_features) - 15} autres features MC!")

# Vérifier si toutes les features sont dans le test
missing_in_test = [f for f in available_features if f not in df_test.columns]
if missing_in_test:
    print(f"\n  FEATURES MANQUANTES DANS TEST: {missing_in_test}")
    available_features = [f for f in available_features if f not in missing_in_test]
    print(f" FEATURES FINALES UTILISABLES: {len(available_features)}")

print("\n" + "="*60)

#  OPTIMISATION AUTOMATIQUE DU NOMBRE DE FEATURES
print(" OPTIMISATION DU NOMBRE DE FEATURES")
print("="*60)

X_all = df_train[available_features]
y_all = df_train['Classification'].map({'vide': 0, 'pleine': 1})

# 🔧 NORMALISATION/STANDARDISATION DES DONNÉES
print("\n NORMALISATION/STANDARDISATION DES DONNÉES")
print("="*60)

# Tester différentes méthodes de normalisation
scalers = {
    'StandardScaler': StandardScaler(),
    'MinMaxScaler': MinMaxScaler(),
    'RobustScaler': RobustScaler(),
    'None': None
}

best_scaler_name = None
best_scaler_score = 0

scaler_results = {}

for scaler_name, scaler in scalers.items():
    print(f"\n Test avec {scaler_name}:")
    
    if scaler is not None:
        X_scaled = scaler.fit_transform(X_all)
    else:
        X_scaled = X_all.values
    
    # Test rapide avec validation croisée
    model_test = RandomForestClassifier(n_estimators=50, random_state=42, class_weight='balanced')
    cv_scores = cross_val_score(model_test, X_scaled, y_all, cv=3, scoring='accuracy')
    mean_score = cv_scores.mean()
    
    scaler_results[scaler_name] = {
        'mean': mean_score,
        'std': cv_scores.std(),
        'scaler': scaler
    }
    
    print(f"   Précision moyenne: {mean_score:.3f} (±{cv_scores.std()*2:.3f})")
    
    if mean_score > best_scaler_score:
        best_scaler_score = mean_score
        best_scaler_name = scaler_name

print(f"\n MEILLEURE MÉTHODE DE NORMALISATION: {best_scaler_name}")
print(f" Précision: {best_scaler_score:.3f}")

# Appliquer la meilleure normalisation
best_scaler = scaler_results[best_scaler_name]['scaler']
if best_scaler is not None:
    X_all_scaled = best_scaler.fit_transform(X_all)
    print(f" Données normalisées avec {best_scaler_name}")
else:
    X_all_scaled = X_all.values
    print(" Pas de normalisation appliquée")

# Tester différents nombres de features
feature_counts = [50, 100, 150, 200, 250, 300]
if len(available_features) < 300:
    feature_counts = [k for k in feature_counts if k <= len(available_features)]

best_score = 0
best_k = 50
results = {}

print(f"Test de performance avec différents nombres de features...")

for k in feature_counts:
    # Sélectionner les k meilleures features
    selector = SelectKBest(score_func=f_classif, k=k)
    X_selected = selector.fit_transform(X_all_scaled, y_all)
    
    # Cross-validation
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=min(15, k//15),
        min_samples_split=max(5, k//40),
        random_state=42,
        class_weight='balanced'
    )
    cv_scores = cross_val_score(model, X_selected, y_all, cv=5, scoring='accuracy')
    mean_score = cv_scores.mean()
    std_score = cv_scores.std()
    
    results[k] = {
        'mean': mean_score,
        'std': std_score
    }
    
    print(f" {k:3d} features → Précision: {mean_score:.3f} (±{std_score*2:.3f})")
    
    if mean_score > best_score:
        best_score = mean_score
        best_k = k

print(f"\n NOMBRE OPTIMAL: {best_k} features")
print(f" Meilleure précision: {best_score:.3f}")

# Utiliser le nombre optimal de features
optimal_features = best_k

# 🔧 OPTIMISATION DES HYPERPARAMÈTRES
print(f"\n OPTIMISATION DES HYPERPARAMÈTRES")
print("="*60)

# Sélectionner les meilleures features avec la normalisation
selector = SelectKBest(score_func=f_classif, k=optimal_features)
X_train_selected = selector.fit_transform(X_all_scaled, y_all)

# Obtenir les noms des features sélectionnées
selected_indices = selector.get_support(indices=True)
selected_features = [available_features[i] for i in selected_indices]

print(f"✅ {len(selected_features)} features sélectionnées")

# Définir la grille d'hyperparamètres
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 15, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Recherche par grille avec validation croisée
print(" Recherche des meilleurs hyperparamètres...")
rf_model = RandomForestClassifier(random_state=42, class_weight='balanced')
grid_search = GridSearchCV(
    rf_model, 
    param_grid, 
    cv=5, 
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train_selected, y_all)
best_params = grid_search.best_params_
best_grid_score = grid_search.best_score_

print(f"\n MEILLEURS HYPERPARAMÈTRES:")
for param, value in best_params.items():
    print(f"   {param}: {value}")
print(f" Meilleure précision (CV): {best_grid_score:.3f}")

#  VALIDATION CROISÉE K-FOLD COMPLÈTE
print(f"\n VALIDATION CROISÉE K-FOLD COMPLÈTE")
print("="*60)

# Utiliser le meilleur modèle
best_model = RandomForestClassifier(**best_params, random_state=42, class_weight='balanced')

# Définir K-Fold
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Métriques à calculer
scoring_metrics = ['accuracy', 'precision', 'recall', 'f1']
cv_results = cross_validate(
    best_model, 
    X_train_selected, 
    y_all, 
    cv=kf,
    scoring=scoring_metrics,
    return_train_score=True
)

# Afficher les résultats détaillés
print(" RÉSULTATS DE LA VALIDATION CROISÉE K-FOLD:")
print("-" * 60)

for metric in scoring_metrics:
    test_scores = cv_results[f'test_{metric}']
    train_scores = cv_results[f'train_{metric}']
    
    print(f"\n{metric.upper()}:")
    print(f"   Test  : {test_scores.mean():.3f} (±{test_scores.std()*2:.3f})")
    print(f"   Train : {train_scores.mean():.3f} (±{train_scores.std()*2:.3f})")
    print(f"   Détail: {[f'{score:.3f}' for score in test_scores]}")

# Détecter le surapprentissage
accuracy_gap = cv_results['train_accuracy'].mean() - cv_results['test_accuracy'].mean()
if accuracy_gap > 0.1:
    print(f"\n SURAPPRENTISSAGE DÉTECTÉ: Gap de {accuracy_gap:.3f}")
else:
    print(f"\n MODÈLE ÉQUILIBRÉ: Gap de {accuracy_gap:.3f}")

#   ENTRAÎNEMENT FINAL ET ÉVALUATION
print(f"\n ENTRAÎNEMENT FINAL ET ÉVALUATION")
print("="*60)

# Diviser en train/validation
X_train, X_val, y_train, y_val = train_test_split(
    X_train_selected, y_all, test_size=0.2, random_state=42, stratify=y_all
)

# Entraîner le modèle final
final_model = RandomForestClassifier(**best_params, random_state=42, class_weight='balanced')
final_model.fit(X_train, y_train)

# Prédictions
y_val_pred = final_model.predict(X_val)

#  MATRICE DE CONFUSION COMPLÈTE
print(f"\n MATRICE DE CONFUSION ET MÉTRIQUES DÉTAILLÉES")
print("="*60)

# Calculer toutes les métriques
accuracy = accuracy_score(y_val, y_val_pred)
precision = precision_score(y_val, y_val_pred, average='weighted')
recall = recall_score(y_val, y_val_pred, average='weighted')
f1 = f1_score(y_val, y_val_pred, average='weighted')

print(f" MÉTRIQUES DE PERFORMANCE:")
print(f"   Accuracy : {accuracy:.3f}")
print(f"   Precision: {precision:.3f}")
print(f"   Recall   : {recall:.3f}")
print(f"   F1-Score : {f1:.3f}")

# Matrice de confusion détaillée
conf_matrix = confusion_matrix(y_val, y_val_pred)
class_names = ['vide', 'pleine']

print(f"\n MATRICE DE CONFUSION:")
print(f"{'':>10} {'Prédit':>15}")
print(f"{'Réel':>10} {'vide':>7} {'pleine':>7}")
for i, true_class in enumerate(class_names):
    print(f"{true_class:>10} {conf_matrix[i][0]:>7} {conf_matrix[i][1]:>7}")

# Calculer les métriques par classe
tn, fp, fn, tp = conf_matrix.ravel()
sensitivity = tp / (tp + fn)  # Recall/Sensitivity
specificity = tn / (tn + fp)  # Specificity
precision_class = tp / (tp + fp)  # Precision

print(f"\n MÉTRIQUES PAR CLASSE:")
print(f"   Sensibilité (Recall) : {sensitivity:.3f}")
print(f"   Spécificité         : {specificity:.3f}")
print(f"   Précision           : {precision_class:.3f}")
print(f"   Vrais Positifs      : {tp}")
print(f"   Vrais Négatifs      : {tn}")
print(f"   Faux Positifs       : {fp}")
print(f"   Faux Négatifs       : {fn}")

# Analyser l'importance des features
feature_importance = pd.DataFrame({
    'feature': selected_features,
    'importance': final_model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n TOP 15 FEATURES LES PLUS IMPORTANTES:")
print(feature_importance.head(15))

# Prédictions sur le test avec normalisation
print(f"\n PRÉDICTIONS SUR LE TEST")
print("="*60)

X_test = df_test[selected_features]
if best_scaler is not None:
    X_test_scaled = best_scaler.transform(X_test)
else:
    X_test_scaled = X_test.values

X_test_selected = selector.transform(X_test_scaled)
y_pred_test = final_model.predict(X_test_selected)
y_pred_proba = final_model.predict_proba(X_test_selected)

df_test['Prediction'] = y_pred_test
df_test['Prediction_Label'] = df_test['Prediction'].map({0: 'vide', 1: 'pleine'})
df_test['Confidence'] = np.max(y_pred_proba, axis=1)

print(f"Prédictions générées avec confiance")
print(df_test[['filename', 'Prediction_Label', 'Confidence']].head(10))

# Sauvegarde des résultats
results_summary = {
    'optimal_features': optimal_features,
    'best_scaler': best_scaler_name,
    'best_params': best_params,
    'cv_accuracy': cv_results['test_accuracy'].mean(),
    'cv_precision': cv_results['test_precision'].mean(),
    'cv_recall': cv_results['test_recall'].mean(),
    'cv_f1': cv_results['test_f1'].mean(),
    'validation_accuracy': accuracy,
    'validation_precision': precision,
    'validation_recall': recall,
    'validation_f1': f1,
    'sensitivity': sensitivity,
    'specificity': specificity
}

# Sauvegarder dans un CSV
df_test.to_csv(f"predictions_optimized_{optimal_features}_features.csv", sep=";", index=False)
print(f"\n Prédictions sauvegardées dans 'predictions_optimized_{optimal_features}_features.csv'")

# Sauvegarder l'analyse des features
feature_importance.to_csv(f"feature_analysis_optimized_{optimal_features}.csv", index=False)
print(f" Analyse des features sauvegardée dans 'feature_analysis_optimized_{optimal_features}.csv'")

# Sauvegarder les résultats complets
pd.DataFrame([results_summary]).to_csv("model_performance_summary.csv", index=False)
print(f" Résumé des performances sauvegardé dans 'model_performance_summary.csv'")

# Si vous avez les vraies classes dans le test
if 'Classification' in df_test.columns:
    # y_test = vraies classes
    y_test = df_test['Classification'].map({'vide': 0, 'pleine': 1})
    
    print(f"\n ÉVALUATION COMPLÈTE SUR LE TEST")
    print("="*60)
    
    # Calculer toutes les métriques sur le test
    test_accuracy = accuracy_score(y_test, y_pred_test)
    test_precision = precision_score(y_test, y_pred_test, average='weighted')
    test_recall = recall_score(y_test, y_pred_test, average='weighted')
    test_f1 = f1_score(y_test, y_pred_test, average='weighted')
    
    print(f" MÉTRIQUES DE TEST:")
    print(f"   Accuracy : {test_accuracy:.3f}")
    print(f"   Precision: {test_precision:.3f}")
    print(f"   Recall   : {test_recall:.3f}")
    print(f"   F1-Score : {test_f1:.3f}")
    
    print(f"\n RAPPORT DE CLASSIFICATION DÉTAILLÉ:")
    print(classification_report(y_test, y_pred_test, target_names=['vide', 'pleine']))
    
    # Matrice de confusion pour le test
    conf_matrix_test = confusion_matrix(y_test, y_pred_test)
    
    #  VISUALISATIONS AVANCÉES
    plt.figure(figsize=(15, 12))
    
    # Subplot 1: Matrice de confusion du test
    plt.subplot(3, 3, 1)
    sns.heatmap(conf_matrix_test, annot=True, fmt='d', cmap='Blues',
                xticklabels=['vide', 'pleine'],
                yticklabels=['vide', 'pleine'])
    plt.xlabel("Prédit")
    plt.ylabel("Réel")
    plt.title(f"Matrice de confusion (Test)")
    
    # Subplot 2: Matrice de confusion de validation
    plt.subplot(3, 3, 2)
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Greens',
                xticklabels=['vide', 'pleine'],
                yticklabels=['vide', 'pleine'])
    plt.xlabel("Prédit")
    plt.ylabel("Réel")
    plt.title(f"Matrice de confusion (Validation)")
    
    # Subplot 3: Importance des features
    plt.subplot(3, 3, 3)
    top_features = feature_importance.head(10)
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), [f[:20] for f in top_features['feature']])
    plt.xlabel('Importance')
    plt.title('Top 10 Features')
    plt.gca().invert_yaxis()
    
    # Subplot 4: Performance par nombre de features
    plt.subplot(3, 3, 4)
    feature_counts_plot = list(results.keys())
    means = [results[k]['mean'] for k in feature_counts_plot]
    stds = [results[k]['std'] for k in feature_counts_plot]
    
    plt.errorbar(feature_counts_plot, means, yerr=stds, marker='o')
    plt.axvline(x=optimal_features, color='red', linestyle='--', alpha=0.7)
    plt.xlabel('Nombre de features')
    plt.ylabel('Précision (CV)')
    plt.title('Optimisation features')
    plt.grid(True, alpha=0.3)
    
    # Subplot 5: Comparaison des méthodes de normalisation
    plt.subplot(3, 3, 5)
    scaler_names = list(scaler_results.keys())
    scaler_scores = [scaler_results[name]['mean'] for name in scaler_names]
    bars = plt.bar(range(len(scaler_names)), scaler_scores)
    plt.xticks(range(len(scaler_names)), scaler_names, rotation=45)
    plt.ylabel('Précision')
    plt.title('Comparaison Normalisation')
    
    # Marquer le meilleur
    best_idx = scaler_names.index(best_scaler_name)
    bars[best_idx].set_color('red')
    
    # Subplot 6: Métriques K-Fold
    plt.subplot(3, 3, 6)
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    means = [cv_results[f'test_{metric}'].mean() for metric in metrics]
    stds = [cv_results[f'test_{metric}'].std() for metric in metrics]
    
    plt.errorbar(range(len(metrics)), means, yerr=stds, marker='o', capsize=5)
    plt.xticks(range(len(metrics)), metrics)
    plt.ylabel('Score')
    plt.title('Métriques K-Fold CV')
    plt.grid(True, alpha=0.3)
    
    # Subplot 7: Distribution des prédictions
    plt.subplot(3, 3, 7)
    confidence_scores = df_test['Confidence'].values
    plt.hist(confidence_scores, bins=20, alpha=0.7)
    plt.xlabel('Confiance')
    plt.ylabel('Fréquence')
    plt.title('Distribution Confiance')
    
    # Subplot 8: Comparaison Train vs Test
    plt.subplot(3, 3, 8)
    comparison_metrics = ['accuracy', 'precision', 'recall', 'f1']
    train_scores = [cv_results[f'train_{metric}'].mean() for metric in comparison_metrics]
    test_scores = [cv_results[f'test_{metric}'].mean() for metric in comparison_metrics]
    
    x = np.arange(len(comparison_metrics))
    width = 0.35
    
    plt.bar(x - width/2, train_scores, width, label='Train', alpha=0.7)
    plt.bar(x + width/2, test_scores, width, label='Test', alpha=0.7)
    plt.xticks(x, comparison_metrics)
    plt.ylabel('Score')
    plt.title('Train vs Test')
    plt.legend()
    
    # Subplot 9: Résumé des hyperparamètres
    plt.subplot(3, 3, 9)
    param_text = "Meilleurs hyperparamètres:\n"
    for param, value in best_params.items():
        param_text += f"{param}: {value}\n"
    param_text += f"\nNormalisation: {best_scaler_name}\n"
    param_text += f"Features: {optimal_features}\n"
    param_text += f"CV Score: {best_grid_score:.3f}"
    
    plt.text(0.1, 0.5, param_text, transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
    plt.axis('off')
    plt.title('Configuration')
    
    plt.tight_layout()
    plt.savefig('model_analysis_complete.png', dpi=300, bbox_inches='tight')
    plt.show()
    
else:
    # Si pas de vraies étiquettes, afficher quand même quelques visualisations
    plt.figure(figsize=(12, 8))
    
    # Subplot 1: Matrice de confusion de validation
    plt.subplot(2, 3, 1)
    sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                xticklabels=['vide', 'pleine'],
                yticklabels=['vide', 'pleine'])
    plt.xlabel("Prédit")
    plt.ylabel("Réel")
    plt.title(f"Matrice de confusion (Validation)")
    
    # Subplot 2: Importance des features
    plt.subplot(2, 3, 2)
    top_features = feature_importance.head(10)
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), [f[:20] for f in top_features['feature']])
    plt.xlabel('Importance')
    plt.title('Top 10 Features')
    plt.gca().invert_yaxis()
    
    # Subplot 3: Performance par nombre de features
    plt.subplot(2, 3, 3)
    feature_counts_plot = list(results.keys())
    means = [results[k]['mean'] for k in feature_counts_plot]
    stds = [results[k]['std'] for k in feature_counts_plot]
    
    plt.errorbar(feature_counts_plot, means, yerr=stds, marker='o')
    plt.axvline(x=optimal_features, color='red', linestyle='--', alpha=0.7)
    plt.xlabel('Nombre de features')
    plt.ylabel('Précision (CV)')
    plt.title('Optimisation features')
    plt.grid(True, alpha=0.3)
    
    # Subplot 4: Métriques K-Fold
    plt.subplot(2, 3, 4)
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    means = [cv_results[f'test_{metric}'].mean() for metric in metrics]
    stds = [cv_results[f'test_{metric}'].std() for metric in metrics]
    
    plt.errorbar(range(len(metrics)), means, yerr=stds, marker='o', capsize=5)
    plt.xticks(range(len(metrics)), metrics)
    plt.ylabel('Score')
    plt.title('Métriques K-Fold CV')
    plt.grid(True, alpha=0.3)
    
    # Subplot 5: Comparaison des méthodes de normalisation
    plt.subplot(2, 3, 5)
    scaler_names = list(scaler_results.keys())
    scaler_scores = [scaler_results[name]['mean'] for name in scaler_names]
    bars = plt.bar(range(len(scaler_names)), scaler_scores)
    plt.xticks(range(len(scaler_names)), scaler_names, rotation=45)
    plt.ylabel('Précision')
    plt.title('Comparaison Normalisation')
    
    # Marquer le meilleur
    best_idx = scaler_names.index(best_scaler_name)
    bars[best_idx].set_color('red')
    
    # Subplot 6: Distribution des prédictions
    plt.subplot(2, 3, 6)
    confidence_scores = df_test['Confidence'].values
    plt.hist(confidence_scores, bins=20, alpha=0.7)
    plt.xlabel('Confiance')
    plt.ylabel('Fréquence')
    plt.title('Distribution Confiance')
    
    plt.tight_layout()
    plt.savefig('model_analysis_validation.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n  Pas de vraies étiquettes dans le test pour l'évaluation complète")
    print("Seulement les prédictions et la validation sont disponibles.")

print(f"\n RÉSUMÉ FINAL COMPLET")
print("="*60)
print(f" Normalisation optimale      : {best_scaler_name}")
print(f" Features optimales          : {optimal_features}")
print(f"  Hyperparamètres optimisés   : {best_params}")
print(f" CV Accuracy                 : {cv_results['test_accuracy'].mean():.3f} (±{cv_results['test_accuracy'].std()*2:.3f})")
print(f" CV Precision                : {cv_results['test_precision'].mean():.3f} (±{cv_results['test_precision'].std()*2:.3f})")
print(f" CV Recall                   : {cv_results['test_recall'].mean():.3f} (±{cv_results['test_recall'].std()*2:.3f})")
print(f" CV F1-Score                 : {cv_results['test_f1'].mean():.3f} (±{cv_results['test_f1'].std()*2:.3f})")
print(f" Validation Accuracy         : {accuracy:.3f}")
print(f" Validation Precision        : {precision:.3f}")
print(f" Validation Recall           : {recall:.3f}")
print(f" Validation F1-Score         : {f1:.3f}")
print(f" Sensibilité                 : {sensitivity:.3f}")
print(f" Spécificité                 : {specificity:.3f}")
print(f" Modèle entraîné sur         : {len(df_train)} images")
print(f" Prédictions générées pour   : {len(df_test)} images test")
print(f" Surapprentissage            : {'  Détecté' if accuracy_gap > 0.1 else ' Contrôlé'}")

print(f"\n FICHIERS GÉNÉRÉS:")
print(f"   - predictions_optimized_{optimal_features}_features.csv")
print(f"   - feature_analysis_optimized_{optimal_features}.csv")
print(f"   - model_performance_summary.csv")
print(f"   - model_analysis_complete.png (ou model_analysis_validation.png)")

print(f"\n🎓 RECOMMANDATIONS:")
if accuracy_gap > 0.1:
    print("   - Réduire la complexité du modèle")
    print("   - Augmenter les données d'entraînement")
    print("   - Appliquer plus de régularisation")
elif cv_results['test_accuracy'].std() > 0.1:
    print("   - Stabiliser le modèle avec plus de données")
    print("   - Ajuster les hyperparamètres")
else:
    print("   - Modèle bien équilibré et stable")
    print("   - Prêt pour la production")

print("\n" + "="*60)
print(" ANALYSE MACHINE LEARNING COMPLÈTE TERMINÉE")
print("="*60)