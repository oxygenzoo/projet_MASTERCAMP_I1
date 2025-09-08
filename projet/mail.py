import pandas as pd
import smtplib
from email.message import EmailMessage
import os

def charger_predictions(mode='ML'):
    if mode == 'ML':
        fichier = [f for f in os.listdir() if f.startswith('predictions_optimized') and f.endswith('.csv')][0]
        df = pd.read_csv(fichier, sep=';')
        df_poubelles = df[df['Prediction_Label'] == 'pleine']
        return df_poubelles[['filename', 'Prediction_Label', 'Confidence']], 'pleine'
    
    elif mode == 'DL':
        df = pd.read_csv("classifications_globales.csv")
        df_poubelles = df[df['label'] == 'dirty']
        return df_poubelles, 'dirty'
    
    else:
        raise ValueError("Mode inconnu. Utilisez 'ML' ou 'DL'.")

def envoyer_mail(mail_destinataire, fichier_csv, nb_poubelles, seuil, mode):
    msg = EmailMessage()
    msg['Subject'] = f"[ALERTE POUBELLES] {nb_poubelles} cas détectés ({mode})"
    msg['From'] = "alerte@ville.fr"
    msg['To'] = mail_destinataire

    msg.set_content(f"""
Bonjour,

Une alerte automatique a été déclenchée car {nb_poubelles} poubelles ont été détectées comme pleines ou en dépôt sauvage, dépassant le seuil fixé de {seuil}.

Veuillez trouver ci-joint le fichier CSV listant les cas concernés.

Cordialement,
Système de surveillance automatique
""")

    with open(fichier_csv, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="csv", filename=os.path.basename(fichier_csv))

    with smtplib.SMTP("smtp.example.com", 587) as smtp:
        smtp.starttls()
        smtp.login("UTILISATEUR_SMTP", "MOTDEPASSE")
        smtp.send_message(msg)
        print("Mail envoyé avec succès.")

def verifier_et_envoyer_alerte(mail, seuil, mode='ML'):
    df_alertes, label_critique = charger_predictions(mode)
    nb_detectes = len(df_alertes)

    print(f"{nb_detectes} cas détectés comme {label_critique}")

    if nb_detectes >= seuil:
        fichier = f"alertes_{mode}.csv"
        df_alertes.to_csv(fichier, index=False)
        envoyer_mail(mail, fichier, nb_detectes, seuil, mode)
    else:
        print("Seuil non atteint. Aucun mail envoyé.")