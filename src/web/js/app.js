const emailInput = document.getElementById('app-main-input-email');

// On récupère l'input de l'URL.
const urlInput = document.getElementById('app-main-input-url');

// On récupère le bouton de validation.
const urlSubmit = document.getElementById('app-main-button-submit');

// On récupère le loader.
const urlLoader = document.getElementById('app-main-loader');

// On récupère le message d'erreur.
const urlError = document.getElementById('app-main-error');

// On récupère la div qui contiendra le résultat.
const urlResult = document.getElementById('app-main-result');

// On ajoute un event listener sur le bouton de validation.
urlSubmit.addEventListener('click', () => {

    // On récupère l'email entré par l'utilisateur.
    const email = emailInput.value;

    // On récupère l'URL entrée par l'utilisateur.
    const url = urlInput.value;

    // On vide le résultat.
    urlResult.innerText = '';

    // On vide le message d'erreur.
    urlError.innerText = '';

    if (email === '') {
        // Si l'email est vide, on affiche un message d'erreur.
        urlError.innerText = 'Veuillez entrer un email.';
        return;
    }

    // Si l'URL est vide, on affiche un message d'erreur.
    if (url === '') {
        urlError.innerText = 'Veuillez entrer une URL.';
        return;
    }

    // On ajoute le texte "Chargement..." au loader.
    urlLoader.innerText = 'Chargement...';


    // On envoie une requête Post à l'URL 127.0.0.1:5000/api/classify.
    fetch('http://127.0.0.1:5000/api/classify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({url: url, email: email})
    })
        .then(response => response.json())
        .then(data => {
            // On vide le loader.
            urlLoader.innerText = '';

            // On affiche la probabilité de surté.
            urlResult.innerText = '\n\nProbabilité de sûreté : ' + data.proba * 100 + '%';

            // Si la probabilité est supérieur à 70%, on met la couleur en vert.
            if (data.proba * 100 > 70) {
                urlResult.style.color = 'green';
            }
            // Si la probabilité est inférieur à 30%, on met la couleur en rouge.
            else if (data.proba * 100 < 30) {
                urlResult.style.color = 'red';
            }
            // Sinon ont met la couleur en orange.
            else {
                urlResult.style.color = 'orange';
            }


        })
        .catch(error => {
            // On vide le loader.
            urlLoader.innerText = '';

            // On affiche le message d'erreur.
            urlError.innerText = 'Une erreur est survenue.';
        });

});