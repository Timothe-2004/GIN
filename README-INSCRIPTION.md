# Améliorations du Module d'Inscription

Ce document résume toutes les améliorations apportées au module d'inscription du projet GIN_backend.

## 1. Amélioration de la cohérence des serializers

- Harmonisation des noms de champs entre les serializers et les modèles
- Ajout d'un mécanisme de conversion entre le champ `nom` des API externes et `titre` utilisé en interne
- Amélioration du `FormationExterneSerializer` avec une méthode `to_representation`

## 2. Validation des données améliorée

- Validation stricte du format du numéro de téléphone avec expressions régulières
- Vérification automatique des places disponibles lors d'une inscription
- Détection et prévention des inscriptions en double
- Validation améliorée des noms, prénoms et email

## 3. Harmonisation des vues

- Standardisation des réponses entre `InscriptionView` et `FormationViewSet.inscrire`
- Transformation de `VerificationStatutInscriptionView` en `ListAPIView` avec pagination
- Amélioration de la gestion des erreurs et de leur journalisation

## 4. Sécurité et limitation de débit

- Mise en place d'un système de throttling pour les points d'accès sensibles:
  - Limitation des tentatives de connexion (5/minute)
  - Limitation des inscriptions (10/heure)
  - Limitation des vérifications de code de suivi (10/minute)
- Amélioration des messages d'erreur pour guider l'utilisateur

## 5. Configuration multi-environnement

- Création d'une structure de configuration avec trois fichiers:
  - `base.py`: configuration commune
  - `development.py`: configuration de développement (DEBUG=True, logs verbeux)
  - `production.py`: configuration de production (sécurité renforcée)
- Utilisation de variables d'environnement pour les données sensibles

## 6. Documentation et architecture

- Ajout d'un fichier `architecture.md` documentant la structure du module
- Description des flux utilisateur et des interactions entre modules
- Documentation des dépendances entre modules

## 7. Tests unitaires et d'intégration

- Ajout de tests pour vérifier les nouvelles validations (téléphone, doublons, places)
- Tests du flux complet d'inscription pour utilisateurs authentifiés et non authentifiés
- Tests spécifiques pour le throttling et la limitation de débit

## 8. Cohérence avec le module de stages

- Vérification de la cohérence avec le module de stages
- Utilisation de mécanismes similaires (codes de suivi, statuts, etc.)

## Comment utiliser ces améliorations

### Configuration de l'environnement

Pour utiliser la configuration multi-environnement:

```bash
# Développement (par défaut)
python manage.py runserver

# Production
export DJANGO_ENVIRONMENT=production
python manage.py runserver
```

### Variables d'environnement pour la production

Voici les variables d'environnement requises en production:

```
DJANGO_SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=example.com,www.example.com
CORS_ALLOWED_ORIGINS=https://example.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gin_db
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=no-reply@example.com
EMAIL_HOST_PASSWORD=email_password
DEFAULT_FROM_EMAIL=no-reply@example.com
FORMATION_API_URL=https://api.formations.example.com
FORMATION_API_KEY=api_key_here
```

### Exécution des tests

Pour exécuter les tests unitaires et d'intégration:

```bash
# Tous les tests
python manage.py test

# Tests spécifiques au module d'inscription
python manage.py test inscription

# Tests avec couverture de code
coverage run --source='.' manage.py test inscription
coverage report
```