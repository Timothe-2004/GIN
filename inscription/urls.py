# inscription/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('recherche-formation/', views.RechercheFormationView.as_view(), name='recherche-formation'),
    path('inscription/', views.InscriptionView.as_view(), name='inscription'),
    path('verification-statut/', views.VerificationStatutInscriptionView.as_view(), name='verification-statut'),
]
