"""
Script d'analyse d'images de poubelles pour Wild Dump Prevention (WDP)

Ce script permet:
1. De nettoyer automatiquement le dossier media/uploads/
2. D'y copier de nouvelles images (d'un ZIP ou d'un dossier)
3. D'analyser ces images pour déterminer si les poubelles sont pleines ou vides
4. D'exporter les résultats dans un fichier CSV

Usage:
  - Double-cliquez sur ce fichier pour une utilisation interactive
  - Ou lancez-le en ligne de commande: python run_batch_analysis.py
"""

import os
import sys
import glob
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Ajouter le chemin du backend au PYTHONPATH
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)

# Fonctions utilitaires pour remplacer celles de batch_analysis.py
def clean_uploads_folder():
    """
    Supprime toutes les images du dossier media/uploads/ avant une nouvelle analyse
    
    Returns:
        int: Nombre de fichiers supprimés
    """
    # Détermine le chemin du dossier uploads
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'media', 'uploads')
    
    # Vérifier que le dossier existe
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        print(f"Dossier {uploads_dir} créé car il n'existait pas")
        return 0
    
    # Supprimer tous les fichiers d'image
    count = 0
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    for ext in image_extensions:
        for file in glob.glob(os.path.join(uploads_dir, f'*{ext}')):
            try:
                os.remove(file)
                count += 1
            except Exception as e:
                print(f"Erreur lors de la suppression de {file}: {str(e)}")
    
    print(f"{count} images supprimées du dossier {uploads_dir}")
    return count

def find_images_in_directory(directory):
    """
    Recherche récursivement des images dans un répertoire
    
    Args:
        directory (str): Chemin du répertoire à explorer
        
    Returns:
        list: Liste des chemins d'images trouvées
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    image_files = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                image_files.append(os.path.join(root, file))
    
    return image_files

def get_uploads_folder():
    """
    Retourne le chemin absolu du dossier media/uploads/
    
    Returns:
        str: Chemin absolu du dossier uploads
    """
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'media', 'uploads')
    
    # Vérifier que le dossier existe
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
        
    return uploads_dir

def copy_images_to_uploads(source_paths):
    """
    Copie les images sources vers le dossier media/uploads/
    
    Args:
        source_paths (list): Liste des chemins d'images sources
    
    Returns:
        list: Liste des chemins d'images dans le dossier uploads
    """
    uploads_dir = get_uploads_folder()
    copied_paths = []
    
    for src_path in source_paths:
        try:
            # Copier uniquement le fichier, pas la structure de répertoire
            filename = os.path.basename(src_path)
            dst_path = os.path.join(uploads_dir, filename)
            
            shutil.copy2(src_path, dst_path)
            copied_paths.append(dst_path)
            print(f"Copié: {filename} -> {dst_path}")
        except Exception as e:
            print(f"Erreur lors de la copie de {src_path}: {str(e)}")
    
    return copied_paths

def analyze_images(image_paths):
    """
    Analyse une liste d'images et extrait leurs caractéristiques
    
    Args:
        image_paths (list): Liste de chemins d'images
        
    Returns:
        list: Liste des caractéristiques extraites
    """
    features_list = []
    
    for path in image_paths:
        try:
            with open(path, 'rb') as img_file:
                # Extraire les caractéristiques
                features = extract_features(img_file)
                
                # Classifier l'image
                classification = classify_by_rules(features)
                
                # Ajouter la classification au dictionnaire de caractéristiques
                features['classification'] = classification
                
                # Ajouter le nom de fichier
                features['filename'] = os.path.basename(path)
                
                features_list.append(features)
                
                print(f"Analysé: {os.path.basename(path)} - Classification: {classification}")
        except Exception as e:
            print(f"Erreur lors de l'analyse de {path}: {str(e)}")
    
    return features_list

# Fonction pour analyser et exporter les images
def analyze_and_export_images(image_paths):
    """
    Analyse des images et exporte les résultats en CSV
    
    Args:
        image_paths (list): Liste des chemins d'images à analyser
    """
    from datetime import datetime
    
    try:
        # Déterminer le dossier uploads
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'media', 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Copier les images
        copied_paths = []
        for src_path in image_paths:
            try:
                filename = os.path.basename(src_path)
                dst_path = os.path.join(uploads_dir, filename)
                shutil.copy2(src_path, dst_path)
                copied_paths.append(dst_path)
                print(f"Copié: {filename} -> {dst_path}")
            except Exception as e:
                print(f"Erreur lors de la copie de {src_path}: {str(e)}")
        
        # Analyser les images avec le module de traitement
        try:
            from backend.api.image_processing import extract_features, classify_by_rules, export_features_to_csv
            
            print("\nAnalyse des images en cours...")
            features_list = []
            
            for path in copied_paths:
                try:
                    with open(path, 'rb') as img_file:
                        # Extraire les caractéristiques
                        features = extract_features(img_file)
                        
                        # Classifier l'image
                        classification = classify_by_rules(features)
                        
                        # Ajouter la classification au dictionnaire
                        features['classification'] = classification
                        features['filename'] = os.path.basename(path)
                        
                        features_list.append(features)
                        
                        print(f"Analysé: {os.path.basename(path)} - Classification: {classification}")
                except Exception as e:
                    print(f"Erreur lors de l'analyse de {path}: {str(e)}")
            
            # Exporter les résultats vers un CSV
            output_filename = f"analyse_poubelles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
            
            csv_path = export_features_to_csv(features_list, output_path)
            print(f"\nRésultats exportés vers: {csv_path}")
            
            # Afficher un message de confirmation
            messagebox.showinfo(
                "Analyse terminée", 
                f"{len(features_list)} images analysées.\nRésultats exportés vers: {csv_path}"
            )
        except ImportError as e:
            print(f"Erreur lors de l'importation du module d'analyse d'images: {str(e)}")
            messagebox.showerror("Erreur", f"Module d'analyse non disponible: {str(e)}")
    except Exception as e:
        print(f"Erreur pendant l'analyse: {str(e)}")
        messagebox.showerror("Erreur", f"Une erreur s'est produite: {str(e)}")

try:
    # Importer les fonctions nécessaires depuis Extraction_caracteristiques.py
    from Extraction_caracteristiques import extract_features, classify_by_rules, export_features_to_csv, process_image_folder
    
    print("=== Wild Dump Prevention - Analyse d'Images de Poubelles ===\n")
    
    # Nettoyer le dossier uploads avant toute chose
    try:
        print("Nettoyage du dossier media/uploads/...")
        clean_uploads_folder()
    except Exception as e:
        # Si l'erreur est liée aux paramètres Django, utilisons une approche manuelle
        print("Utilisation d'une méthode alternative pour nettoyer media/uploads/...")
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'media', 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            print(f"Dossier {uploads_dir} créé car il n'existait pas")
        else:
            # Supprimer manuellement les images
            count = 0
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
            for ext in image_extensions:
                for file in glob.glob(os.path.join(uploads_dir, f'*{ext}')):
                    try:
                        os.remove(file)
                        count += 1
                    except Exception as e:
                        print(f"Erreur lors de la suppression de {file}: {str(e)}")
            print(f"{count} images supprimées du dossier {uploads_dir}")
    
    # Initialiser Tkinter pour les boîtes de dialogue
    root = tk.Tk()
    root.withdraw()
    
    # Demander à l'utilisateur de choisir la source d'images
    choice = messagebox.askquestion(
        "Wild Dump Prevention - Analyse d'images",
        "Voulez-vous analyser des images à partir d'un fichier ZIP?\nSi vous répondez 'Non', vous pourrez sélectionner un dossier."
    )
    
    image_paths = []
    
    if choice == 'yes':
        # Sélectionner un fichier ZIP
        zip_path = filedialog.askopenfilename(
            title="Sélectionnez un fichier ZIP contenant des images",
            filetypes=[("Fichiers ZIP", "*.zip")]
        )
        
        if not zip_path:
            print("Aucun fichier sélectionné. Opération annulée.")
            input("\nAppuyez sur Entrée pour quitter...")
            sys.exit(0)
        
        print(f"Fichier sélectionné: {zip_path}")
        
        try:
            # Utiliser la fonction batch_analyze_from_source du module
            from backend.api.batch_analysis import batch_analyze_from_source
            batch_analyze_from_source()
        except Exception as e:
            print(f"Erreur lors de l'analyse: {str(e)}")
            print("Utilisation d'une méthode alternative...")
            
            # Code alternatif si l'import échoue
            import zipfile
            import tempfile
            from datetime import datetime
            
            # Créer un répertoire temporaire pour extraire le ZIP
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extraire le ZIP
                try:
                    print(f"Extraction du fichier ZIP dans {temp_dir}...")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                except Exception as e:
                    print(f"Erreur lors de l'extraction du ZIP: {str(e)}")
                    input("\nAppuyez sur Entrée pour quitter...")
                    sys.exit(1)
                
                # Rechercher des images dans le dossier extrait
                image_paths = find_images_in_directory(temp_dir)
                
                if not image_paths:
                    print("Aucune image trouvée dans l'archive ZIP.")
                    input("\nAppuyez sur Entrée pour quitter...")
                    sys.exit(0)
                
                print(f"{len(image_paths)} images trouvées.")
                
                # Continuer avec l'analyse
                analyze_and_export_images(image_paths)
        
    else:
        # Sélectionner un dossier
        folder_path = filedialog.askdirectory(
            title="Sélectionnez un dossier contenant des images"
        )
        
        if not folder_path:
            print("Aucun dossier sélectionné. Opération annulée.")
            input("\nAppuyez sur Entrée pour quitter...")
            sys.exit(0)
        
        print(f"Dossier sélectionné: {folder_path}")
        
        # Rechercher des images dans le dossier
        image_paths = find_images_in_directory(folder_path)
        
        if not image_paths:
            print("Aucune image trouvée dans le dossier sélectionné.")
            input("\nAppuyez sur Entrée pour quitter...")
            sys.exit(0)
        
        print(f"{len(image_paths)} images trouvées.")
        
        # Copier les images dans le dossier uploads
        uploads_paths = copy_images_to_uploads(image_paths)
        
        # Analyser les images
        print("\nAnalyse des images en cours...")
        features_list = analyze_images(uploads_paths)
        
        # Exporter les résultats avec visualisations
        from datetime import datetime
        output_filename = f"analyse_poubelles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
        
        # Utiliser la fonction d'export améliorée
        result_paths = export_features_to_csv(features_list, output_path, generate_viz=True)
        
        # Afficher les chemins des fichiers générés
        print(f"\nRésultats exportés:")
        print(f"- CSV: {result_paths.get('csv')}")
        print(f"- JSON: {result_paths.get('json')}")
        if 'visualizations' in result_paths:
            print(f"- Visualisations: {result_paths.get('visualizations')}")
        
        # Afficher un message de confirmation plus riche
        viz_msg = f"\nDes visualisations ont été générées dans {result_paths.get('visualizations')}" if 'visualizations' in result_paths else ""
        
        messagebox.showinfo(
            "Analyse terminée", 
            f"{len(features_list)} images analysées.\n\n"
            f"Fichiers générés:\n"
            f"- CSV: {os.path.basename(result_paths.get('csv'))}\n"
            f"- JSON: {os.path.basename(result_paths.get('json'))}{viz_msg}"
        )
    
    print("\nAnalyse terminée. Vous pouvez fermer cette fenêtre.")
    
    # Garder la fenêtre ouverte jusqu'à ce que l'utilisateur appuie sur Entrée
    input("\nAppuyez sur Entrée pour quitter...")
    
except ImportError as e:
    print(f"Erreur lors de l'importation du module: {str(e)}")
    print("Vérifiez que vous êtes dans le bon répertoire et que le module existe.")
    input("\nAppuyez sur Entrée pour quitter...")
except Exception as e:
    print(f"Une erreur s'est produite: {str(e)}")
    input("\nAppuyez sur Entrée pour quitter...")
