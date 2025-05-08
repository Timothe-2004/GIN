from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer

from .models import UserProfile

User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    """Sérialiseur pour la création de comptes utilisateurs."""
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    def validate(self, attrs):
        """Valider que le mot de passe et la confirmation du mot de passe correspondent."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        return attrs

    def create(self, validated_data):
        """Créer un nouveau compte utilisateur."""
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm', None)
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les profils utilisateurs."""

    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'phone_number', 'position']  # Removed 'department'


class UserSerializer(BaseUserSerializer):
    """Sérialiseur pour les comptes utilisateurs avec les informations de profil."""
    
    profile = UserProfileSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'role_display', 
                  'is_active', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined', 'is_active']
