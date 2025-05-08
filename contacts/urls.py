from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ContactMessageViewSet, ContactResponseViewSet

# Création du routeur pour les vues API
router = DefaultRouter()
router.register(r'messages', ContactMessageViewSet, basename='contact-messages')
router.register(r'reponses', ContactResponseViewSet, basename='contact-responses')

urlpatterns = [
    path('', include(router.urls)),
]