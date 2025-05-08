import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class TestUserModel(TestCase):
    """Cas de tests pour le modèle User personnalisé."""
    def setUp(self):
        """Configurer les données de test."""
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            role=User.Roles.ADMIN
        )
        
        self.editor_user = User.objects.create_user(
            email='editor@test.com',
            password='editorpass123',
            first_name='Editor',
            last_name='User',
            role=User.Roles.EDITOR
        )
        
        self.regular_user = User.objects.create_user(
            email='user@test.com',
            password='userpass123',
            first_name='Regular',
            last_name='User',
            role=User.Roles.USER
        )
        
        self.superuser = User.objects.create_superuser(
            email='super@test.com',
            password='superpass123'
        )
    def test_create_user(self):
        """Tester la création d'un utilisateur régulier."""
        self.assertEqual(self.regular_user.email, 'user@test.com')
        self.assertEqual(self.regular_user.role, User.Roles.USER)
        self.assertTrue(self.regular_user.is_active)
        self.assertFalse(self.regular_user.is_staff)
        self.assertFalse(self.regular_user.is_superuser)

    def test_create_superuser(self):
        """Tester la création d'un superutilisateur."""
        self.assertEqual(self.superuser.email, 'super@test.com')
        self.assertEqual(self.superuser.role, User.Roles.ADMIN)
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)
    
    def test_user_full_name(self):
        """Test the get_full_name method."""
        self.assertEqual(self.regular_user.get_full_name(), 'Regular User')
        self.assertEqual(self.regular_user.get_short_name(), 'Regular')
    
    def test_user_roles_permissions(self):
        """Test the role-based permission methods."""
        # Admin user
        self.assertTrue(self.admin_user.is_admin())
        self.assertFalse(self.admin_user.is_editor())
        
        # Editor user
        self.assertFalse(self.editor_user.is_admin())
        self.assertTrue(self.editor_user.is_editor())
        
        # Regular user
        self.assertFalse(self.regular_user.is_admin())
        self.assertFalse(self.regular_user.is_editor())
    
    def test_user_string_representation(self):
        """Test the string representation of a user."""
        self.assertEqual(str(self.regular_user), 'user@test.com')
    
    def test_user_profile_creation(self):
        """Test that a profile is automatically created for a new user."""
        self.assertIsNotNone(self.regular_user.profile)
        self.assertEqual(self.regular_user.profile.user, self.regular_user)
    
    @pytest.mark.django_db
    def test_empty_email_raises_error(self):
        """Test that creating a user without an email raises an error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')
