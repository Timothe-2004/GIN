import json
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthenticationTests(APITestCase):
    """Test cases for authentication endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
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
    
    def get_tokens_for_user(self, user):
        """Helper method to get JWT tokens for a user."""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def test_token_obtain_pair(self):
        """Test obtaining JWT token pair with valid credentials."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'user@test.com',
            'password': 'userpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'user@test.com')
    
    def test_token_obtain_pair_invalid_credentials(self):
        """Test obtaining JWT token with invalid credentials."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'user@test.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test refreshing JWT token."""
        tokens = self.get_tokens_for_user(self.regular_user)
        url = reverse('token_refresh')
        data = {'refresh': tokens['refresh']}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_token_refresh_invalid(self):
        """Test refreshing JWT token with an invalid refresh token."""
        url = reverse('token_refresh')
        data = {'refresh': 'invalid-token'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserAPITests(APITestCase):
    """Test cases for the User API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
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
    
    def authenticate_as(self, user):
        """Helper method to authenticate as a specific user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_me_endpoint_authenticated(self):
        """Test the 'me' endpoint with an authenticated user."""
        self.authenticate_as(self.regular_user)
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.regular_user.email)
    
    def test_me_endpoint_unauthenticated(self):
        """Test the 'me' endpoint without authentication."""
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_users_as_admin(self):
        """Test listing all users as an admin."""
        self.authenticate_as(self.admin_user)
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 3)  # At least our 3 test users
    
    def test_list_users_as_regular_user(self):
        """Test listing users as a regular user (should only see self)."""
        self.authenticate_as(self.regular_user)
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only the user themselves
        self.assertEqual(response.data['results'][0]['email'], self.regular_user.email)
    
    def test_create_user_as_admin(self):
        """Test creating a new user as an admin."""
        self.authenticate_as(self.admin_user)
        url = reverse('user-list')
        data = {
            'email': 'newuser@test.com',
            'password': 'newuserpass123',
            'password_confirm': 'newuserpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': User.Roles.USER
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())
    
    def test_create_user_as_regular_user(self):
        """Test creating a user as a regular user (should be forbidden)."""
        self.authenticate_as(self.regular_user)
        url = reverse('user-list')
        data = {
            'email': 'newuser2@test.com',
            'password': 'newuserpass123',
            'password_confirm': 'newuserpass123',
            'first_name': 'New',
            'last_name': 'User2',
            'role': User.Roles.USER
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(email='newuser2@test.com').exists())
    
    def test_update_own_user(self):
        """Test updating own user data."""
        self.authenticate_as(self.regular_user)
        url = reverse('user-detail', args=[self.regular_user.id])
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'Updated')
        self.assertEqual(self.regular_user.last_name, 'Name')
    
    def test_update_other_user_as_regular_user(self):
        """Test updating another user's data as a regular user (should be forbidden)."""
        self.authenticate_as(self.regular_user)
        url = reverse('user-detail', args=[self.editor_user.id])
        data = {
            'first_name': 'Hacked',
            'last_name': 'User'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Or 403 depending on implementation
        self.editor_user.refresh_from_db()
        self.assertNotEqual(self.editor_user.first_name, 'Hacked')
    
    def test_delete_user_as_admin(self):
        """Test deleting a user as an admin."""
        test_user = User.objects.create_user(
            email='delete@test.com',
            password='deletepass123'
        )
        
        self.authenticate_as(self.admin_user)
        url = reverse('user-detail', args=[test_user.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(email='delete@test.com').exists())
    
    def test_delete_user_as_regular_user(self):
        """Test deleting a user as a regular user (should be forbidden)."""
        test_user = User.objects.create_user(
            email='delete2@test.com',
            password='deletepass123'
        )
        
        self.authenticate_as(self.regular_user)
        url = reverse('user-detail', args=[test_user.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Or 403 depending on implementation
        self.assertTrue(User.objects.filter(email='delete2@test.com').exists())


class RoleBasedAccessTests(APITestCase):
    """Test cases for the role-based access endpoint."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
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
    
    def authenticate_as(self, user):
        """Helper method to authenticate as a specific user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_role_based_access_as_admin(self):
        """Test role-based access as admin."""
        self.authenticate_as(self.admin_user)
        url = reverse('role_based_access')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_role'], 'Administrator')
        self.assertIn('can_manage_users', response.data['permissions'])
        self.assertIn('can_view_analytics', response.data['permissions'])
    
    def test_role_based_access_as_editor(self):
        """Test role-based access as editor."""
        self.authenticate_as(self.editor_user)
        url = reverse('role_based_access')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_role'], 'Content Editor')
        self.assertIn('can_create_content', response.data['permissions'])
        self.assertNotIn('can_manage_users', response.data['permissions'])
    
    def test_role_based_access_as_regular_user(self):
        """Test role-based access as regular user."""
        self.authenticate_as(self.regular_user)
        url = reverse('role_based_access')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_role'], 'Regular User')
        self.assertIn('can_view_content', response.data['permissions'])
        self.assertNotIn('can_create_content', response.data['permissions'])
    
    def test_role_based_access_unauthenticated(self):
        """Test role-based access without authentication."""
        url = reverse('role_based_access')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
