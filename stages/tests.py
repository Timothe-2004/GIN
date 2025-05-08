from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import DomaineStage, DemandeStage
import json
import uuid
from django.core.files.uploadedfile import SimpleUploadedFile

class DomaineStageTests(APITestCase):
    def setUp(self):
        self.domaine_url = reverse('domaines-list')
        self.domaine = DomaineStage.objects.create(
            nom="Développement Web",
            description="Stages en développement web"
        )

    def test_list_domaines(self):
        response = self.client.get(self.domaine_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nom'], "Développement Web")

class DemandeStageTests(APITestCase):
    def setUp(self):
        # Créer un domaine de stage
        self.domaine = DomaineStage.objects.create(
            nom="Développement Web",
            description="Stages en développement web"
        )
        
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # URLs
        self.demande_url = reverse('demande-create')
        self.verification_url = reverse('verification-statut')
        
        # Créer un fichier CV de test
        self.cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_create_demande(self):
        data = {
            'email': 'test@example.com',
            'domaine': self.domaine.id,
            'requete': 'Je souhaite faire un stage en développement web',
            'cv': self.cv_file
        }
        
        response = self.client.post(
            self.demande_url,
            data=data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DemandeStage.objects.count(), 1)
        self.assertEqual(DemandeStage.objects.get().email, 'test@example.com')

    def test_verification_statut(self):
        # Créer une demande de stage
        demande = DemandeStage.objects.create(
            email='test@example.com',
            domaine=self.domaine,
            requete='Test requête',
            cv=self.cv_file
        )
        
        # Tester la vérification du statut
        data = {'code_unique': str(demande.code_unique)}
        response = self.client.post(
            self.verification_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['statut'], 'en_cours')

    def test_verification_statut_invalid_code(self):
        data = {'code_unique': str(uuid.uuid4())}
        response = self.client.post(
            self.verification_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class DemandeStageDetailTests(APITestCase):
    def setUp(self):
        # Créer un domaine de stage
        self.domaine = DomaineStage.objects.create(
            nom="Développement Web",
            description="Stages en développement web"
        )
        
        # Créer un utilisateur admin
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Créer un fichier CV de test
        self.cv_file = SimpleUploadedFile(
            "test_cv.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        # Créer une demande de stage
        self.demande = DemandeStage.objects.create(
            email='test@example.com',
            domaine=self.domaine,
            requete='Test requête',
            cv=self.cv_file
        )
        
        # URL pour la mise à jour
        self.detail_url = reverse('demande-detail', kwargs={'code_unique': self.demande.code_unique})
        
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)

    def test_update_statut(self):
        data = {
            'statut': 'accepte'
        }
        response = self.client.patch(
            self.detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(DemandeStage.objects.get().statut, 'accepte')

    def test_update_statut_unauthorized(self):
        # Créer un utilisateur non-admin
        user = User.objects.create_user(
            username='user',
            password='userpass123'
        )
        self.client.force_authenticate(user=user)
        
        data = {
            'statut': 'accepte'
        }
        response = self.client.patch(
            self.detail_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
