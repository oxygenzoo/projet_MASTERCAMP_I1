# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 15:45:00 2025

@author: willi
"""

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from roboflow import Roboflow
from ultralytics import YOLO
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import confusion_matrix, classification_report
from matplotlib.colors import ListedColormap
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score




#import de roboflow
#!pip install roboflow

rf = Roboflow(api_key="vT1XHpjzg7l3YdPp1TgS")
project = rf.workspace("will-yr7ef").project("trash-pmizu")
version = project.version(6)
dataset = version.download("yolov11")

#entrainement du modele 

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

model = YOLO("yolo11n.pt") 

results = model.train(
    data="trash-6/data.yaml",   
    epochs=50,
    imgsz=640,
    name="train_yolo11",        
    device=0, 
    workers=0 
)


#Test du modele

trained_model = YOLO("runs/detect/train_yolo11/weights/best.pt")

predict_results = trained_model.predict(
    source="Data/test/unknown",   
    save=True,                  
    save_txt=True,            
    conf=0.3,
    save_conf=True
)


#chargement des datasets

IMAGE_DIR = "Data/test/unknown" 
LABEL_DIR = "runs/detect/predict3/labels"

CLASS_MAP = {
    1: "clean",    
    0: "dirty"
}

results = []

for img_name in os.listdir(IMAGE_DIR):
    if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    txt_name = os.path.splitext(img_name)[0] + ".txt"
    txt_path = os.path.join(LABEL_DIR, txt_name)

    if os.path.exists(txt_path):
        with open(txt_path, "r") as f:
            lines = f.readlines()
        classes = [int(line.split()[0]) for line in lines]

        if 0 in classes:
            classification = "dirty"
        elif 1 in classes:
            classification = "clean"
        else:
            classification = "clean"
    else:
        classification = "clean"  

    results.append((img_name, classification))

df = pd.DataFrame(results, columns=["nom", "label"])
df.to_csv("classifications_globales.csv", index=False)
print(df)


#normalisation
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import os


df_true = pd.read_csv("test_attribution.csv", sep = ';')  
df_pred = pd.read_csv("classifications_globales.csv") 

def normalize_filename(filename):
    filename = str(filename).strip().lower()
    filename = os.path.basename(filename)
    filename = filename.replace('.jpeg', '.jpg') 
    return filename

df_true['nom'] = df_true['nom'].apply(normalize_filename)
df_pred['nom'] = df_pred['nom'].apply(normalize_filename)


print(df_true)
print(df_pred)


#Concaténation des datasets

df_true['label'] = df_true['label'].map({'c': 'clean', 'd': 'dirty'})

print(df_true)

df_true['nom'] = df_true['nom'].str.strip().str.lower()
df_pred['nom'] = df_pred['nom'].str.strip().str.lower()

print(df_true)
print(df_pred)


df_merged = pd.merge(df_true, df_pred, on='nom', how='inner')

print(df_merged)


#Graphique

y_true = df_merged['label_x']
y_pred = df_merged['label_y']

print("=== Rapport de classification ===")
print(classification_report(y_true, y_pred, target_names=['clean', 'dirty']))

conf_matrix = confusion_matrix(y_true, y_pred, labels=['clean', 'dirty'])

custom_cmap = ListedColormap(['#a6d9d0', '#fefecb', '#cfcde3', '#f08e7e'])

plt.figure(figsize=(6, 5))
sns.heatmap(conf_matrix,
            annot=True,
            fmt='d',
            cmap=custom_cmap,
            xticklabels=['clean', 'dirty'],
            yticklabels=['clean', 'dirty'])

plt.xlabel("Prédit")
plt.ylabel("Réel")
plt.title("Matrice de confusion - Modèle YOLO vs vérité terrain")
plt.tight_layout()
plt.show()


counts = df_pred["label"].value_counts()

plt.figure(figsize=(6, 6))
plt.pie(
    counts,
    labels=counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=["#a6d9d0", "#f08e7e"]
)
plt.title("Répartition des classes prédites")
plt.axis("equal")  
plt.show()


counts = df_true["label"].value_counts()

plt.figure(figsize=(6, 6))
plt.pie(
    counts,
    labels=counts.index,
    autopct='%1.1f%%',
    startangle=90,
    colors=["#a6d9d0", "#f08e7e"]
)
plt.title("Répartition des classes prédites")
plt.axis("equal")  
plt.show()


df_merged["correct"] = df_merged["label_x"] == df_merged["label_y"]
sns.countplot(x=df_merged["correct"].map({True: "Correct", False: "Incorrect"}), palette="Set3")
plt.title("Prédictions correctes vs incorrectes")
plt.ylabel("Nombre d’images")
plt.show()



precision = precision_score(df_merged["label_x"], df_merged["label_y"], pos_label="dirty")
recall = recall_score(df_merged["label_x"], df_merged["label_y"], pos_label="dirty")
f1 = f1_score(df_merged["label_x"], df_merged["label_y"], pos_label="dirty")
acc = accuracy_score(df_merged["label_x"], df_merged["label_y"])

metrics = {"Precision": precision, "Recall": recall, "F1-Score": f1, "Accuracy": acc}
sns.barplot(x=list(metrics.keys()), y=list(metrics.values()), palette="Set3")
plt.ylim(0, 1)
plt.title("Scores de performance du modèle")
plt.ylabel("Score")
plt.show()
