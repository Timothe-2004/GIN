from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .verification_statut import VerificationStatutView

schema_view = get_schema_view(
   openapi.Info(
      title="GIN API",
      default_version='v1',
      description="Documentation de l'API backend de GIN",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="maxaraye18@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gin.urls')),  # Redirige la racine vers les URLs de l'application principale
    path('api/', include('gin.urls')),
    path('api/', include('inscription.urls')),
    path('api/stages/', include('stages.urls')),
    path('api/accounts/', include('accounts.urls')),
    
    # Nouveaux points d'entrée API
    path('api/partenaires/', include('partenaires.urls')),
    path('api/realisations/', include('realisations.urls')),
    path('api/contacts/', include('contacts.urls')),
    
    # Vérification de statut (accès public)
    path('api/verification-statut/', VerificationStatutView.as_view(), name='verification-statut'),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Documentation API
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
