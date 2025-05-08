# Import du module de sérialisation de DRF
from rest_framework import serializers
# Import des modèles à sérialiser
from .models import StageOffer, StageApplication

class StageOfferSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les offres de stage."""
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StageOffer
        fields = [
            'id', 'title', 'department', 'description', 'missions', 
            'required_skills', 'start_date', 'duration', 'stage_type', 
            'status', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"
    
    def create(self, validated_data):
        """Ajoute automatiquement l'utilisateur courant comme créateur."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class StageApplicationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les candidatures aux stages."""
    stage_offer_title = serializers.SerializerMethodField()
    
    class Meta:
        model = StageApplication
        fields = [
            'id', 'stage_offer', 'stage_offer_title', 'first_name', 'last_name', 
            'email', 'phone', 'cv', 'motivation_letter', 'tracking_code',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['tracking_code', 'status', 'created_at', 'updated_at']
    
    def get_stage_offer_title(self, obj):
        return obj.stage_offer.title

class TrackingCodeSerializer(serializers.Serializer):
    """Sérialiseur pour la vérification des codes de suivi."""
    tracking_code = serializers.CharField(max_length=12)

class VerificationStatutSerializer(serializers.Serializer):
    """
    Sérialiseur pour la vérification du statut d'une demande.
    Utilisé uniquement pour la validation du code unique.
    """
    # Champ pour le code unique de la demande
    code_unique = serializers.UUIDField()