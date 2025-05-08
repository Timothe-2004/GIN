from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Contact
from .serializers import ContactSerializer

class ContactTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.contact_data = {'name': 'John Doe', 'email': 'john@example.com', 'message': 'Hello'}
        self.contact = Contact.objects.create(**self.contact_data)

    def test_create_contact(self):
        response = self.client.post('/api/contacts/', self.contact_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contact.objects.count(), 2)
        self.assertEqual(Contact.objects.get(id=2).name, 'John Doe')

    def test_get_contact(self):
        response = self.client.get(f'/api/contacts/{self.contact.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.contact.name)

    def test_update_contact(self):
        updated_data = {'name': 'Jane Doe', 'email': 'jane@example.com', 'message': 'Hi'}
        response = self.client.put(f'/api/contacts/{self.contact.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.name, 'Jane Doe')

    def test_delete_contact(self):
        response = self.client.delete(f'/api/contacts/{self.contact.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Contact.objects.count(), 0)

    def test_contact_serializer(self):
        serializer = ContactSerializer(instance=self.contact)
        self.assertEqual(serializer.data['name'], self.contact.name)
        self.assertEqual(serializer.data['email'], self.contact.email)
        self.assertEqual(serializer.data['message'], self.contact.message)