from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Utilisateur, Inscription, RechercheFormation
from datetime import date, timedelta
import json
from unittest.mock import patch
from django.conf import settings

# Configuration pour les tests
settings.FORMATION_API_URL = 'http://test-api.example.com'
settings.FORMATION_API_KEY = 'test-key'

class UtilisateurTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.valid_payload = {
            'user': {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            },
            'telephone': '0123456789',
            'adresse': '123 Test Street',
            'date_naissance': '1990-01-01'
        }

    def test_create_utilisateur(self):
        response = self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Utilisateur.objects.count(), 1)
        self.assertEqual(Utilisateur.objects.get().user.username, 'testuser')

    def test_create_utilisateur_invalid_date(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload['date_naissance'] = (date.today() + timedelta(days=1)).isoformat()
        response = self.client.post(
            self.register_url,
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        # Créer un utilisateur
        self.client.post(
            self.register_url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        # Tester la connexion
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class InscriptionTests(APITestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.utilisateur = Utilisateur.objects.create(
            user=self.user,
            telephone='0123456789'
        )
        
        # URLs
        self.inscription_url = reverse('inscription')
        self.recherche_url = reverse('recherche-formation')
        
        # Authentifier l'utilisateur
        self.client.force_authenticate(user=self.user)

    def test_create_inscription(self):
        inscription_data = {
            'formation_id': '123',
            'formation_nom': 'Test Formation'
        }
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(inscription_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Inscription.objects.count(), 1)
        self.assertEqual(Inscription.objects.get().formation_nom, 'Test Formation')

    @patch('requests.get')
    def test_recherche_formation(self, mock_get):
        # Configurer le mock
        mock_get.return_value.json.return_value = [
            {
                'id': '1',
                'nom': 'Python Formation',
                'description': 'Test Description',
                'date_debut': '2024-01-01',
                'date_fin': '2024-12-31'
            }
        ]
        mock_get.return_value.status_code = 200

        recherche_data = {
            'terme_recherche': 'python'
        }
        response = self.client.post(
            self.recherche_url,
            data=json.dumps(recherche_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RechercheFormation.objects.count(), 1)
        self.assertEqual(RechercheFormation.objects.get().terme_recherche, 'python')

class RechercheFormationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.utilisateur = Utilisateur.objects.create(
            user=self.user,
            telephone='0123456789'
        )
        self.recherche_url = reverse('recherche-formation')
        self.client.force_authenticate(user=self.user)

    def test_recherche_sans_terme(self):
        response = self.client.post(
            self.recherche_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('requests.get')
    def test_recherche_avec_terme(self, mock_get):
        # Configurer le mock
        mock_get.return_value.json.return_value = [
            {
                'id': '1',
                'nom': 'Python Formation',
                'description': 'Test Description',
                'date_debut': '2024-01-01',
                'date_fin': '2024-12-31'
            }
        ]
        mock_get.return_value.status_code = 200

        response = self.client.post(
            self.recherche_url,
            data=json.dumps({'terme_recherche': 'python'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RechercheFormation.objects.count(), 1)

class InscriptionValidationTests(APITestCase):
    """Tests pour les validations améliorées du module d'inscription."""
    
    def setUp(self):
        # Créer un utilisateur pour les tests
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.utilisateur = Utilisateur.objects.create(
            user=self.user,
            telephone='0123456789'
        )
        
        # Créer un département et une formation
        self.department = Department.objects.create(name="Informatique")
        self.formation = Formation.objects.create(
            titre="Formation Python",
            description="Description de la formation",
            duree="3 jours",
            prerequis="Connaissances en programmation",
            objectifs="Apprendre Python",
            date_session=date.today() + timedelta(days=30),
            lieu="Paris",
            capacite=10,
            department=self.department,
            created_by=self.user,
            statut="planifiee"
        )
        
        # URL pour les tests
        self.inscription_url = reverse('inscription')
        self.verify_tracking_url = reverse('inscription-verify-tracking', kwargs={'pk': None})
        
    def test_telephone_validation(self):
        """Test de la validation du format de téléphone."""
        # Format valide
        valid_data = {
            'formation': self.formation.id,
            'nom': 'Doe',
            'prenom': 'John',
            'email': 'john.doe@example.com',
            'telephone': '+33 6 12 34 56 78',
            'commentaire': 'Test'
        }
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Format invalide
        invalid_data = valid_data.copy()
        invalid_data['telephone'] = 'invalid-phone'
        invalid_data['email'] = 'john.doe2@example.com'  # Pour éviter le doublon
        
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('telephone', response.data['error'])
    
    def test_duplicate_inscription(self):
        """Test pour empêcher les doublons d'inscription."""
        # Première inscription - valide
        data = {
            'formation': self.formation.id,
            'nom': 'Doe',
            'prenom': 'John',
            'email': 'duplicate@example.com',
            'telephone': '+33 6 12 34 56 78',
            'commentaire': 'Test'
        }
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Deuxième inscription avec le même email - devrait échouer
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['error'])
    
    def test_places_disponibles(self):
        """Test de la validation des places disponibles."""
        # Créer une formation avec une seule place
        formation_complete = Formation.objects.create(
            titre="Formation Complète",
            description="Description",
            duree="1 jour",
            prerequis="Aucun",
            objectifs="Objectifs",
            date_session=date.today() + timedelta(days=15),
            lieu="Lyon",
            capacite=1,  # Une seule place
            department=self.department,
            created_by=self.user,
            statut="planifiee"
        )
        
        # Première inscription - valide
        data = {
            'formation': formation_complete.id,
            'nom': 'Smith',
            'prenom': 'Alice',
            'email': 'alice@example.com',
            'telephone': '+33 6 11 22 33 44',
            'commentaire': 'Test'
        }
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Deuxième inscription - plus de place disponible
        data['email'] = 'bob@example.com'  # Pour éviter le doublon
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('formation', response.data['error'])

class InscriptionFlowTests(APITestCase):
    """Tests pour le flux complet d'inscription."""
    
    def setUp(self):
        # Créer utilisateur, département, formation comme dans la classe précédente
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.utilisateur = Utilisateur.objects.create(
            user=self.user,
            telephone='0123456789'
        )
        
        self.department = Department.objects.create(name="Informatique")
        self.formation = Formation.objects.create(
            titre="Formation Python",
            description="Description de la formation",
            duree="3 jours",
            prerequis="Connaissances en programmation",
            objectifs="Apprendre Python",
            date_session=date.today() + timedelta(days=30),
            lieu="Paris",
            capacite=10,
            department=self.department,
            created_by=self.user,
            statut="planifiee"
        )
        
        # URLs pour les tests
        self.inscription_url = reverse('inscription')
        self.formation_inscrire_url = reverse('formation-inscrire', kwargs={'pk': self.formation.id})
        self.verify_status_url = reverse('verification-statut')
        
    def test_inscription_non_authentifie(self):
        """Test d'inscription pour un utilisateur non authentifié."""
        data = {
            'formation': self.formation.id,
            'nom': 'Public',
            'prenom': 'User',
            'email': 'public@example.com',
            'telephone': '+33 6 12 34 56 78',
            'commentaire': 'Test non authentifié'
        }
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tracking_code', response.data)
        
        # Vérifier que l'inscription a bien été créée
        inscription = Inscription.objects.get(email='public@example.com')
        self.assertEqual(inscription.nom, 'Public')
        self.assertEqual(inscription.formation.id, self.formation.id)
        self.assertIsNone(inscription.user)  # Utilisateur non authentifié, donc pas de user associé
    
    def test_inscription_authentifie(self):
        """Test d'inscription pour un utilisateur authentifié."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'formation': self.formation.id,
            'nom': 'Authenticated',
            'prenom': 'User',
            'email': 'auth@example.com',
            'telephone': '+33 6 98 76 54 32',
            'commentaire': 'Test authentifié'
        }
        response = self.client.post(
            self.inscription_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que l'inscription a bien été créée et associée à l'utilisateur
        inscription = Inscription.objects.get(email='auth@example.com')
        self.assertEqual(inscription.user.id, self.user.id)
    
    def test_verify_status_authentifie(self):
        """Test de vérification du statut des inscriptions pour un utilisateur authentifié."""
        # Créer une inscription pour l'utilisateur
        inscription = Inscription.objects.create(
            formation=self.formation,
            user=self.user,
            nom='Test',
            prenom='User',
            email=self.user.email,
            telephone='0123456789',
            commentaire='Test inscription',
            statut='en_attente'
        )
        
        # Authentifier l'utilisateur
        self.client.force_authenticate(user=self.user)
        
        # Vérifier le statut
        response = self.client.get(self.verify_status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tracking_code'], inscription.tracking_code)
    
    def test_formation_inscrire_endpoint(self):
        """Test de l'endpoint FormationViewSet.inscrire."""
        data = {
            'nom': 'Via',
            'prenom': 'Formation',
            'email': 'via.formation@example.com',
            'telephone': '+33 6 11 22 33 44',
            'commentaire': 'Test via formation'
        }
        response = self.client.post(
            self.formation_inscrire_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que l'inscription a bien été créée
        inscription = Inscription.objects.get(email='via.formation@example.com')
        self.assertEqual(inscription.formation.id, self.formation.id)
        self.assertEqual(inscription.nom, 'Via')

class ThrottlingTests(APITestCase):
    """Tests pour les limitations de débit (throttling)."""
    
    def setUp(self):
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Override les settings de throttling pour les tests
        self.original_throttle_rates = settings.REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {})
        throttle_rates = {
            'anon': '3/minute',
            'user': '5/minute',
            'login': '2/minute',
            'inscription': '3/minute',
            'verify_tracking': '2/minute'
        }
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = throttle_rates
    
    def tearDown(self):
        # Restaurer les settings de throttling
        settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = self.original_throttle_rates
    
    def test_login_throttling(self):
        """Test pour vérifier que le throttling fonctionne sur la vue login."""
        # Données de connexion valides et invalides
        valid_data = {'username': 'testuser', 'password': 'testpass123'}
        invalid_data = {'username': 'testuser', 'password': 'wrongpass'}
        
        # Première tentative réussie
        response = self.client.post(
            self.login_url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Deuxième tentative échouée
        response = self.client.post(
            self.login_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Troisième tentative - devrait être limitée par le throttling
        response = self.client.post(
            self.login_url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
