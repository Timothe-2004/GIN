from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    UserViewSet,
    UserProfileViewSet,
    RoleBasedAccessView
)

# Router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)

# URL patterns
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Role-based access example
    path('auth/roles/', RoleBasedAccessView.as_view(), name='role_based_access'),
    
    # Include djoser URLs for password reset, account activation, etc.
    path('auth/', include('djoser.urls')),
]
