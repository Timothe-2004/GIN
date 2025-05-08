from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'offres', views.StageOfferViewSet, basename='stageoffer')
router.register(r'candidatures', views.StageApplicationViewSet, basename='stageapplication')
router.register(r'domaines', views.DomaineStageViewSet, basename='domainestage')
router.register(r'demandes', views.DemandeStageViewSet, basename='demandestage')

urlpatterns = [
    path('', include(router.urls)),
    path('verifier-statut/', views.VerificationStatutView.as_view(), name='verifier-statut'),
    path('domaines-liste/', views.DomaineStageListView.as_view(), name='domaines-liste'),
    path('creer-demande/', views.DemandeStageCreateView.as_view(), name='creer-demande'),
    path('tracking/', views.TrackingViewSet.as_view({'post': 'verify'}), name='tracking-verify'),
]