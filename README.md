# Guide d'exécution et de test de l'API de GLOBAL IT NET

Ce guide explique comment configurer, exécuter et tester l'API backend du site GLOBAL IT NET.

## Prérequis

- Python 3.9+ installé
- pip (gestionnaire de paquets Python)
- Environnement virtuel (recommandé)

## Installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/globalitnet/website-backend.git
cd website-backend
```

2. **Créer et activer un environnement virtuel**

```bash
# Sous Linux/macOS
python -m venv env
source env/bin/activate

# Sous Windows (PowerShell)
python -m venv env
.\env\Scripts\Activate.ps1
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```
DEBUG=True
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

En production, ajustez ces valeurs en conséquence.

## Initialisation de la base de données

1. **Appliquer les migrations**

```bash
python manage.py migrate
```

2. **Créer un superutilisateur**

```bash
python manage.py createsuperuser
```

## Exécution du serveur de développement

```bash
python manage.py runserver
```

Le serveur sera accessible à l'adresse `http://127.0.0.1:8000/`.

## Accès à l'API

- Interface d'administration : http://127.0.0.1:8000/admin/
- Documentation Swagger : http://127.0.0.1:8000/swagger/
- Documentation ReDoc : http://127.0.0.1:8000/redoc/
- API principale : http://127.0.0.1:8000/api/

## Authentification

Pour obtenir un token JWT :

```http
POST /api/auth/token/
Content-Type: application/json

{
  "email": "votre_email@example.com",
  "password": "votre_mot_de_passe"
}
```

La réponse contiendra les tokens d'accès et de rafraîchissement :

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "votre_email@example.com",
    "first_name": "Prénom",
    "last_name": "Nom",
    "role": "ADMIN",
    "role_display": "Administrator"
  }
}
```

Pour les requêtes qui nécessitent une authentification, ajoutez l'en-tête :

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Exécution des tests

### Tests unitaires et d'intégration

```bash
# Exécuter tous les tests
python -m pytest

# Avec couverture de code
python -m pytest --cov=accounts

# Tests spécifiques
python -m pytest accounts/tests/test_models.py
```

### Tests via PowerShell (Windows)

```powershell
# Exécuter tous les tests
.\run_tests.ps1 -all

# Tests unitaires uniquement
.\run_tests.ps1 -unit

# Tests d'intégration uniquement
.\run_tests.ps1 -integration

# Avec couverture de code
.\run_tests.ps1 -all -coverage
```

### Tests via shell (Linux/macOS)

```bash
# Exécuter tous les tests
./run_tests.sh --all

# Tests unitaires uniquement
./run_tests.sh --unit

# Tests d'intégration uniquement
./run_tests.sh --integration

# Avec couverture de code
./run_tests.sh --coverage
```

## Tests de charge

Pour les tests de charge, nous utilisons Locust :

```bash
# Installer Locust
pip install locust

# Exécuter les tests de charge
cd scripts
locust -f load_test.py
```

Puis accédez à l'interface web de Locust à l'adresse `http://localhost:8089/`.

## Sécurité

Consultez le guide de sécurité complet dans `docs/security-guide.md` pour les meilleures pratiques à suivre lors du développement ou de l'utilisation de l'API.
