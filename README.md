Knowledge Learning

Knowledge Learning est une application web développée avec Django pour l’apprentissage en ligne. Elle permet aux utilisateurs de s’inscrire, d’activer leur compte par email, de se connecter, et d’acheter des leçons ou des cursus via Stripe (mode test). Les utilisateurs peuvent marquer les leçons comme terminées, les valider, et obtenir des certifications en complétant toutes les leçons d’un thème. Une interface d’administration Django est disponible pour les utilisateurs ayant le rôle "admin", leur permettant de gérer les utilisateurs, thèmes, cursus et leçons.

Fonctionnalités





Authentification utilisateur : Inscription, activation par email, connexion/déconnexion.



Cursus et leçons : Parcourir et acheter des cursus ou des leçons individuelles.



Paiement : Intégration sécurisée avec Stripe (mode test).



Validation et certification : Marquer les leçons comme terminées, les valider, et obtenir des certifications pour un thème complet.



Interface d’administration : Gestion des utilisateurs, thèmes, cursus et leçons (réservé aux admins).

Prérequis





Python 3.8+



Django 4.2



Compte Stripe (clés API de test)



GraphViz (pour générer le diagramme de modèle physique)

Installation





Clonez le dépôt :

git clone https://github.com/Papinte/knowledge_learning.git
cd knowledge_learning



Créez un environnement virtuel et activez-le :

python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate



Installez les dépendances :

pip install -r requirements.txt



Créez un fichier .env avec les variables suivantes (utilisez vos propres clés Stripe de test) :

SECRET_KEY=votre-cle-secrete
DEBUG=True
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...



Appliquez les migrations :

python manage.py migrate



Peuplez la base de données avec des données d’exemple :

python manage.py populate_data



Créez un superutilisateur (admin) :

python manage.py createsuperuser



Lancez le serveur de développement :

python manage.py runserver

Accédez à l’application sur http://localhost:8000.

Utilisation





Inscrivez-vous et activez votre compte via le lien envoyé par email.



Parcourez les cursus disponibles sur /cursuses/.



Achetez une leçon ou un cursus avec la carte de test Stripe : 4242 4242 4242 4242 (date future, CVC quelconque).



Marquez les leçons comme terminées et validez-les pour obtenir des certifications.



Les admins (rôle admin) peuvent gérer les données sur /admin/.

Structure du projet





learning/models.py : Modèles de la base de données (Utilisateur, Theme, Cursus, Lesson, etc.).



learning/views.py : Logique de l’application (inscription, achats, validations).



learning/tests.py : Tests unitaires pour l’authentification, les achats et les validations.



templates/ : Templates HTML pour l’application.



static/ : Fichiers statiques (CSS, images).

Tests

Exécutez les tests unitaires pour vérifier les fonctionnalités :

python manage.py test

Les tests couvrent l’inscription, l’activation par email, la connexion/déconnexion, les achats, la validation des leçons et les composants d’accès aux données.
