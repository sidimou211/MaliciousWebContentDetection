import logging
import pandas as pd
import re
import nltk
import requests
import joblib

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from bs4 import BeautifulSoup
from xgboost import XGBClassifier
from flask import Flask, jsonify, request
from flask_cors import CORS
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')
nltk.download('punkt')

# On configure le logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# On met des couleurs dans le logger
logging.addLevelName(logging.DEBUG, "\033[1;32m%s\033[1;0m" % logging.getLevelName(logging.DEBUG))
logging.addLevelName(logging.INFO, "\033[1;34m%s\033[1;0m" % logging.getLevelName(logging.INFO))
logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.CRITICAL, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.CRITICAL))

# Création de l'application Flask
app = Flask(__name__)

# Activation des CORS sur l'application Flask
CORS(app)


def preprocessing_content(df):
    """
    Permet de nettoyer le contenu des sites web en supprimant la ponctuation, 
    les chiffres, les stopwords, les mots de moins de 3 lettres et en appliquant le stemmer.
    """
    # On commence par supprimer les stopwords
    stop_words = set(stopwords.words('english'))

    df['content'] = df['content'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))

    # On supprime la ponctuation
    df['content'] = df['content'].apply(lambda x: re.sub(r'[^\w\s]', '', x.lower()))

    # On supprime les chiffres
    df['content'] = df['content'].apply(lambda x: re.sub(r'\d+', '', x))

    # On supprime les espaces en trop
    df['content'] = df['content'].apply(lambda x: x.strip())

    # On supprime les mots de moins de 3 lettres
    df['content'] = df['content'].apply(lambda x: ' '.join([word for word in x.split() if len(word) > 2]))

    # On applique le stemmer
    stemmer = PorterStemmer()

    # On applique le stemmer qui réduit les mots à leur racine
    df['content'] = df['content'].apply(lambda x: ' '.join([stemmer.stem(word) for word in x.split()]))

    return df


def extract_content(url):
    """
    Permet d'extraire le contenu d'un site web (avec BeautifulSoup)
    """
    # Récupération du contenu de la page web
    response = requests.get(url)
    html_content = response.text

    # On crée un objet BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    text = soup.get_text()

    # On applique le preprocessing
    df = pd.DataFrame({'content': [text]})
    df = preprocessing_content(df)

    df.to_csv('content.csv', index=False)

    return df


# On crée une route poste qui va nous permettre de dire si un site est malveillant ou non
# Jeu de données : https://data.mendeley.com/datasets/gdx3pkwp47/2
@app.route('/api/classify', methods=['POST'])
def post():
    # On récupère les données envoyées par le client
    data = request.get_json()

    # On vérifie que les données envoyées par le client sont bien au format JSON
    if not data:
        logging.error('No data provided')
        return jsonify({'error': 'No data provided'}), 400

    # On vérifie que les données envoyées par le client contiennent bien une clé 'url'
    if 'url' not in data:
        logging.error('No url provided')
        return jsonify({'error': 'No url provided'}), 400

    # On vérifie que la valeur associée à la clé 'url' est bien une chaîne de caractères
    if not isinstance(data['url'], str):
        logging.error('Invalid url')
        return jsonify({'error': 'Invalid url'}), 400
    
    # On charge le modèle
    model = joblib.load('../models/model.joblib')
    
    # On extrait le contenu du site web
    df = extract_content(data['url'])
    
    # On extrait les features
    X = df['content']
    
    # On transforme les features en vecteurs
    X = model['vectorizer'].transform(X)
    
    # On prédit la classe
    y_pred = model['classifier'].predict(X)

    # On recuprère la probabilité d'appartenance à la classe 1
    proba = model['classifier'].predict_proba(X)[0][1]


    # Identifiants de connexion au serveur SMTP de Gmail
    sender = 'benelam.kamel@gmail.com'
    password = 'xsqj kbmu sgbw eudf'
    
    try:
        # On se connecte au serveur SMTP de Gmail
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        
        # On démarre le chiffrement TLS (Transport Layer Security)
        smtp_server.starttls()
        
        # On se connecte à notre compte Gmail
        smtp_server.login(sender, password)
        
        # Titre du message
        subject = 'Résultat de la prédiction'
        
        if y_pred[0] == 1:
            # Contenu du message
            message = f'Selon notre analyse le site {data["url"]} est sûr à {round(proba * 100, 3)}%'
        else:
            # Contenu du message
            message = f'Selon notre analyse le site {data["url"]} est malveillant à {round(proba * 100, 3)}%'
        
        # On crée un objet MIMEText pour représenter le corps du message
        email_body = MIMEText(message, 'plain')
        
        # On crée un objet MIMEMultipart pour attacher le corps du message
        email_message = MIMEMultipart()
        
        # On ajoute l'expéditeur
        email_message['From'] = sender
        
        # On ajoute le destinataire
        email_message['To'] = data['email']
        
        # On ajoute le sujet
        email_message['Subject'] = subject
        
        # On attache le corps du message
        email_message.attach(email_body)
        
        # On envoie le message
        smtp_server.sendmail(sender, data['email'], email_message.as_string())
        
        # On ferme la connexion au serveur SMTP
        smtp_server.quit()
        
        logging.info("L'email a été envoyé avec succès : %s", email_body)
    except Exception as e:
        logging.error('Une erreur est survenue : %s', str(e)) 

    # On retourne un message de succès
    return jsonify({'message': 'Success', 'prediction': str(y_pred[0]), 'proba': str(proba)}), 200


if __name__ == '__main__':
    app.run(debug=True)
