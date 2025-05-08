# Guide de sécurité pour les API de GLOBAL IT NET

## Introduction

Ce document présente les meilleures pratiques de sécurité mises en œuvre pour les API de GLOBAL IT NET, ainsi que des recommandations pour les développeurs travaillant sur le projet.

## 1. Authentification et autorisation

### 1.1 Authentification par JWT

Le système utilise des JSON Web Tokens (JWT) pour l'authentification :
- Les tokens ont une durée de validité limitée (60 minutes pour l'access token)
- Les tokens de rafraîchissement expirent après 24 heures
- Les tokens sont signés avec un algorithme HMAC SHA-256 (HS256)

Exemple d'utilisation :
```http
GET /api/users/me/ HTTP/1.1
Host: api.globalitnet.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 1.2 Autorisations basées sur les rôles

Trois rôles principaux sont définis avec des permissions différentes :
- **Administrateur** : Accès complet (CRUD) à toutes les ressources
- **Éditeur** : Création et modification de contenu, accès limité aux données utilisateurs
- **Utilisateur** : Accès limité en lecture seule pour la plupart des ressources

## 2. Protection des données

### 2.1 Validation des entrées

Toutes les entrées utilisateur sont validées à plusieurs niveaux :
- Validation des modèles Django (niveau base de données)
- Validation des sérialiseurs DRF (niveau API)
- Validation spécifique dans les vues pour les logiques métier complexes

### 2.2 Protection CSRF

La protection contre les attaques CSRF est active pour toutes les requêtes non-GET :
- Middleware CSRF de Django activé
- Exemption uniquement pour les endpoints JWT nécessaires

### 2.3 Rate limiting

Des limites de taux sont configurées pour prévenir les attaques par force brute :
- 5 tentatives de connexion par minute par IP
- 60 requêtes API par minute pour les utilisateurs authentifiés
- 30 requêtes API par minute pour les utilisateurs non authentifiés

## 3. Sécurité des communications

### 3.1 HTTPS obligatoire

Toutes les communications avec l'API doivent utiliser HTTPS :
- Redirection automatique de HTTP vers HTTPS en production
- Entêtes HSTS (HTTP Strict Transport Security) activés

### 3.2 Politique CORS

La politique CORS est configurée pour n'autoriser que les domaines approuvés :
- https://www.globalitnet.com
- https://admin.globalitnet.com
- http://localhost:3000 (développement uniquement)

## 4. Journalisation et surveillance

### 4.1 Journalisation des activités

Toutes les actions importantes sont journalisées :
- Tentatives de connexion (réussies et échouées)
- Modifications de données sensibles
- Erreurs d'authentification et d'autorisation

### 4.2 Alertes de sécurité

Des alertes sont configurées pour les événements suspects :
- Multiples tentatives de connexion échouées
- Accès ou tentatives d'accès à des ressources protégées
- Activité anormale des utilisateurs

## 5. Bonnes pratiques pour les développeurs

### 5.1 Gestion des secrets

- Ne jamais stocker de secrets (clés API, mots de passe) dans le code source
- Utiliser des variables d'environnement ou des gestionnaires de secrets

### 5.2 Requêtes à la base de données

- Éviter les requêtes SQL brutes
- Utiliser les ORM et les requêtes paramétrées
- Limiter les résultats des requêtes pour éviter les attaques par déni de service

### 5.3 Tests de sécurité

- Écrire des tests pour vérifier les contrôles d'accès
- Tester les cas limites et les entrées malveillantes
- Exécuter régulièrement des outils d'analyse de sécurité

## 6. Procédure de réponse aux incidents

En cas de suspicion de faille de sécurité :

1. **Confinement** : Isoler immédiatement les systèmes affectés
2. **Analyse** : Identifier la source et l'étendue de la faille
3. **Correction** : Appliquer les correctifs nécessaires
4. **Communication** : Informer les parties prenantes concernées
5. **Prévention** : Mettre à jour les procédures pour éviter des incidents similaires
