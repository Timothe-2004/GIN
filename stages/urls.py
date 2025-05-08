from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'offres', views.StageOfferViewSet, basename='stageoffer')
router.register(r'candidatures', views.StageApplicationViewSet, basename='stageapplication')

urlpatterns = [
    path('', include(router.urls)),
    path('tracking/', views.TrackingViewSet.as_view({'post': 'verify'}), name='tracking-verify'),
]