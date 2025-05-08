"""
Module contenant les classes de throttling (limitation de débit) personnalisées
pour protéger les points d'accès sensibles contre les attaques par force brute.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle pour limiter les tentatives de connexion.
    Particulièrement utile pour prévenir les attaques par force brute.
    """
    scope = 'login'
    rate = '5/minute'  # Limite à 5 tentatives par minute


class VerifyTrackingRateThrottle(AnonRateThrottle):
    """
    Throttle pour limiter les requêtes de vérification de code de suivi.
    Prévient le scraping et les tentatives de découverte de codes valides.
    """
    scope = 'verify_tracking'
    rate = '10/minute'  # Limite à 10 vérifications par minute


class InscriptionRateThrottle(AnonRateThrottle):
    """
    Throttle pour limiter les inscriptions.
    Prévient les inscriptions automatisées et les spams.
    """
    scope = 'inscription'
    rate = '10/hour'  # Limite à 10 inscriptions par heure


class APIRateThrottle(UserRateThrottle):
    """
    Throttle pour limiter les appels API des utilisateurs authentifiés.
    """
    scope = 'api'
    rate = '1000/day'  # Limite à 1000 requêtes par jour