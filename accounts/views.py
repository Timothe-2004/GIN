from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UserProfile
from .permissions import IsAdminUser, IsOwnerOrAdmin
from .serializers import UserSerializer, UserProfileSerializer

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue personnalisée pour l'obtention de token qui ajoute les détails de l'utilisateur à la réponse.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            user_data = UserSerializer(user).data
            response.data['user'] = user_data
        
        return response


class UserViewSet(viewsets.ModelViewSet):
    """
    Point d'accès API pour la gestion des utilisateurs.
    Les administrateurs peuvent lister, créer, modifier et supprimer des utilisateurs.
    Les utilisateurs réguliers peuvent uniquement consulter et mettre à jour leurs propres profils.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_permissions(self):
        """
        Renvoie les permissions appropriées selon l'action.
        """
        if self.action == 'create':
            permission_classes = [IsAdminUser]
        elif self.action in ['list', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'me':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    def get_queryset(self):
        """
        Restreint les utilisateurs à ne voir qu'eux-mêmes, sauf s'ils sont administrateurs.
        """
        user = self.request.user
        if user.is_authenticated and user.role == User.Roles.ADMIN:
            return self.queryset
        return self.queryset.filter(id=user.id)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Obtenir ou mettre à jour les informations de l'utilisateur actuel.
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    Point d'accès API pour les profils utilisateurs.
    Les utilisateurs ne peuvent consulter et mettre à jour que leurs propres profils.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    def get_queryset(self):
        """
        Restreint les profils à ne voir que leur propre profil, sauf s'ils sont administrateurs.
        """
        user = self.request.user
        if user.is_authenticated and user.role == User.Roles.ADMIN:
            return self.queryset
        return self.queryset.filter(user=user)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Get or update the current user's profile.
        """
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
            
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RoleBasedAccessView(APIView):
    """
    Vue d'exemple démontrant le contrôle d'accès basé sur les rôles.
    Cette vue renvoie différentes données selon le rôle de l'utilisateur.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
          # Réponse de base pour tous les utilisateurs authentifiés
        response_data = {
            'status': 'success',
            'user_role': user.get_role_display(),
            'permissions': [],
        }
        
        # Ajouter des données spécifiques au rôle
        if user.role == User.Roles.ADMIN:
            response_data['permissions'] = [
                'can_create_users', 
                'can_edit_users', 
                'can_delete_users',
                'can_create_content',
                'can_edit_content',
                'can_delete_content',
                'can_view_analytics'
            ]
            response_data['message'] = _("Welcome, Administrator. You have full access to the system.")
            
        elif user.role == User.Roles.EDITOR:
            response_data['permissions'] = [
                'can_create_content',
                'can_edit_content',
                'can_delete_own_content'
            ]
            response_data['message'] = _("Welcome, Content Editor. You can manage website content.")
            
        else:  # Regular user
            response_data['permissions'] = ['can_view_content']
            response_data['message'] = _("Welcome, User. You have view-only access.")
        
        return Response(response_data)
