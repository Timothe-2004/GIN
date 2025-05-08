from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from django.urls import reverse

from accounts.serializers import UserCreateSerializer, UserSerializer, UserProfileSerializer
from accounts.models import UserProfile
from accounts.permissions import IsAdminUser, IsEditorUser, IsOwnerOrAdmin, ReadOnly

User = get_user_model()


class SerializerTests(TestCase):
    """Cas de tests pour les sérialiseurs."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'test@test.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        self.user = User.objects.create_user(
            email='existing@test.com',
            password='existingpass123',
            first_name='Existing',
            last_name='User'
        )
        
        # Ensure user profile exists
        if not hasattr(self.user, 'profile'):
            UserProfile.objects.create(user=self.user)

    def test_user_create_serializer_valid(self):
        """Tester UserCreateSerializer avec des données valides."""
        serializer = UserCreateSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
    
    def test_user_create_serializer_password_mismatch(self):
        """Test UserCreateSerializer with mismatched passwords."""
        data = self.user_data.copy()
        data['password_confirm'] = 'wrongpass123'
        
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_user_serializer(self):
        """Test UserSerializer."""
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertIn('profile', data)
    
    def test_profile_serializer(self):
        """Test UserProfileSerializer."""
        profile = self.user.profile
        profile.bio = "Test bio"
        profile.position = "Developer"
        profile.save()
        
        serializer = UserProfileSerializer(instance=profile)
        data = serializer.data
        
        self.assertEqual(data['bio'], "Test bio")
        self.assertEqual(data['position'], "Developer")


class PermissionTests(TestCase):
    """Test cases for permission classes."""
    
    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            role=User.Roles.ADMIN
        )
        
        self.editor_user = User.objects.create_user(
            email='editor@test.com',
            password='editorpass123',
            role=User.Roles.EDITOR
        )
        
        self.regular_user = User.objects.create_user(
            email='user@test.com',
            password='userpass123',
            role=User.Roles.USER
        )
        
        # Create profiles for tests
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            bio="Admin bio"
        )
        self.editor_profile = UserProfile.objects.create(
            user=self.editor_user,
            bio="Editor bio"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.regular_user,
            bio="User bio"
        )
    
    def test_is_admin_user_permission(self):
        """Test IsAdminUser permission."""
        permission = IsAdminUser()
        
        # Admin request
        request = self.factory.get('/')
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Editor request
        request.user = self.editor_user
        self.assertFalse(permission.has_permission(request, None))
        
        # Regular user request
        request.user = self.regular_user
        self.assertFalse(permission.has_permission(request, None))
    
    def test_is_editor_user_permission(self):
        """Test IsEditorUser permission."""
        permission = IsEditorUser()
        
        # Admin request
        request = self.factory.get('/')
        request.user = self.admin_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Editor request
        request.user = self.editor_user
        self.assertTrue(permission.has_permission(request, None))
        
        # Regular user request
        request.user = self.regular_user
        self.assertFalse(permission.has_permission(request, None))
    
    def test_is_owner_or_admin_permission(self):
        """Test IsOwnerOrAdmin permission."""
        permission = IsOwnerOrAdmin()
        
        # Admin request (can access any profile)
        request = self.factory.get('/')
        request.user = self.admin_user
        self.assertTrue(permission.has_object_permission(request, None, self.user_profile))
        
        # User request (own profile)
        request.user = self.regular_user
        self.assertTrue(permission.has_object_permission(request, None, self.user_profile))
        
        # User request (another user's profile)
        request.user = self.regular_user
        self.assertFalse(permission.has_object_permission(request, None, self.editor_profile))
    
    def test_read_only_permission(self):
        """Test ReadOnly permission."""
        permission = ReadOnly()
        
        # GET request
        request = self.factory.get('/')
        self.assertTrue(permission.has_permission(request, None))
        
        # POST request
        request = self.factory.post('/')
        self.assertFalse(permission.has_permission(request, None))
        
        # PUT request
        request = self.factory.put('/')
        self.assertFalse(permission.has_permission(request, None))
        
        # DELETE request
        request = self.factory.delete('/')
        self.assertFalse(permission.has_permission(request, None))
