from rest_framework import serializers
from .models import ContactMessage, ContactReponse


class ContactMessageSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les messages de contact."""
    departement_name = serializers.CharField(source='departement_destinataire.name', read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'nom', 'prenom', 'email', 'telephone', 'sujet', 'message',
            'departement_destinataire', 'departement_name', 'statut',
            'date_creation', 'date_modification'
        ]
        read_only_fields = ['statut', 'date_creation', 'date_modification']


class ContactResponseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les réponses aux messages de contact."""
    repondant_name = serializers.CharField(source='repondant.get_full_name', read_only=True)
    
    class Meta:
        model = ContactReponse
        fields = [
            'id', 'message_original', 'reponse', 'repondant', 'repondant_name',
            'date_reponse'
        ]
        read_only_fields = ['repondant', 'date_reponse']
    
    def create(self, validated_data):
        """Ajoute automatiquement l'utilisateur courant comme répondant."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['repondant'] = request.user
        return super().create(validated_data)


class ContactMessageDetailSerializer(ContactMessageSerializer):
    """Sérialiseur détaillé pour les messages de contact incluant les réponses."""
    reponses = ContactResponseSerializer(many=True, read_only=True)
    
    class Meta(ContactMessageSerializer.Meta):
        fields = ContactMessageSerializer.Meta.fields + ['reponses']