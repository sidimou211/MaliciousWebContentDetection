# MaliciousWebContentDetection

Projet de détection de contenu web malveillant. Il expose une API Flask qui récupère le contenu d’une page, le prétraite, puis applique un modèle XGBoost sérialisé pour estimer la probabilité de sûreté. Une interface web simple permet de soumettre une URL et un email.

**Fonctionnalités**
1. Extraction du texte d’une page web (BeautifulSoup)
2. Prétraitement NLP (stopwords, stemming, nettoyage)
3. Classification via modèle XGBoost + vectorizer (joblib)
4. API HTTP `POST /api/classify`
5. Envoi du résultat par email (SMTP Gmail)

**Prérequis**
1. Python 3.9+
2. Accès Internet (téléchargement NLTK et pages web)

**Installation**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Lancer l’API**
Le chemin du modèle est relatif au dossier `src/api/src`, donc il faut lancer l’API depuis ce dossier.
```powershell
cd src\api\src
python main.py
```
L’API démarre par défaut sur `http://127.0.0.1:5000`.

**Lancer l’interface web**
```powershell
python -m http.server 5173 --directory src\web
```
Ouvrir `http://127.0.0.1:5173` dans le navigateur.

**Utilisation de l’API**
Requête :
```bash
curl -X POST http://127.0.0.1:5000/api/classify \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://example.com\",\"email\":\"you@example.com\"}"
```
Réponse (exemple) :
```json
{
  "message": "Success",
  "prediction": "1",
  "proba": "0.9234"
}
```
`prediction` vaut `1` (site sûr) ou `0` (site malveillant). `proba` est la probabilité associée à la classe 1.

**Structure du projet**
1. `src/api/src/main.py` : API Flask et pipeline NLP
2. `src/api/models/model.joblib` : modèle XGBoost + vectorizer
3. `src/api/notebooks/` : notebooks d’exploration et d’entraînement
4. `src/web/` : interface web (HTML/CSS/JS)

**Données**
Le dataset utilisé est indiqué dans `src/api/src/main.py` :
`https://data.mendeley.com/datasets/gdx3pkwp47/2`

**Configuration email (important)**
L’API envoie un email via SMTP Gmail. Les identifiants sont actuellement codés en dur dans `src/api/src/main.py`. Pour un usage réel, remplacez-les par des variables d’environnement ou un fichier de configuration sécurisé.

**Notes**
1. Les ressources NLTK `stopwords` et `punkt` sont téléchargées au premier lancement.
2. Le fichier `content.csv` est généré lors de l’analyse d’une URL.
