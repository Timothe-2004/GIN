from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FormationViewSet, ServiceViewSet
from drf_spectacular.utils import extend_schema

# On crée un objet router
router = DefaultRouter()

# On enregistre les viewsets avec une url racine et une description pour la documentation
router.register(r"formations", FormationViewSet, basename="formations")
router.register(r"services", ServiceViewSet, basename="services")

# Application de documentation sur les URLs
urlpatterns = [
    # Inclusion des routes générées par DefaultRouter
    path('', include(router.urls)),
]
