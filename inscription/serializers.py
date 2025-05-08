# inscription/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Utilisateur, Inscription, RechercheFormation, Formation
from datetime import date

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        # Utiliser create_user pour hacher le mot de passe correctement
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class UtilisateurSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    date_naissance = serializers.DateField(required=False)

    class Meta:
        model = Utilisateur
        fields = ('id', 'user', 'telephone', 'adresse', 'date_naissance')
        read_only_fields = ('id',)

    def validate_date_naissance(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("La date de naissance ne peut pas être dans le futur")
        return value

    def create(self, validated_data):
        """
        Crée un utilisateur et son profil associé en une seule transaction.
        Cette approche évite les problèmes de NoneType lors de la sérialisation.
        """
        # Extraire les données de l'utilisateur
        user_data = validated_data.pop('user')
        
        # Créer l'utilisateur d'abord
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        # Puis créer le profil de l'utilisateur
        utilisateur = Utilisateur.objects.create(user=user, **validated_data)
        
        return utilisateur

class InscriptionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les inscriptions aux formations."""
    formation_titre = serializers.CharField(source='formation.titre', read_only=True)
    
    class Meta:
        model = Inscription
        fields = [
            'id', 'formation', 'formation_titre', 'user', 'nom', 'prenom',
            'email', 'telephone', 'commentaire', 'tracking_code',
            'statut', 'date_inscription', 'date_modification'
        ]
        read_only_fields = ['tracking_code', 'date_inscription', 'date_modification']
    
    def validate(self, data):
        """Validation complète des données d'inscription."""
        # Vérifier si la formation a encore des places disponibles
        formation = data.get('formation')
        if formation and formation.places_disponibles <= 0:
            raise serializers.ValidationError({
                "formation": "Plus de places disponibles pour cette formation"
            })
        
        # Vérifier les inscriptions en double
        email = data.get('email')
        if email and formation:
            if Inscription.objects.filter(email=email, formation=formation).exists():
                raise serializers.ValidationError({
                    "email": "Une inscription avec cet email existe déjà pour cette formation"
                })
        
        # Validation des noms et prénoms
        nom = data.get('nom')
        prenom = data.get('prenom')
        if nom and len(nom.strip()) < 2:
            raise serializers.ValidationError({
                "nom": "Le nom doit contenir au moins 2 caractères"
            })
        if prenom and len(prenom.strip()) < 2:
            raise serializers.ValidationError({
                "prenom": "Le prénom doit contenir au moins 2 caractères"
            })
        
        return data
        
    def validate_telephone(self, value):
        """Validation stricte du format du téléphone."""
        import re
        # Format international accepté: +XXX XX XX XX XX ou formats nationaux courants
        if not re.match(r'^\+?[0-9]{1,4}[-\s]?([0-9]{2,3}[-\s]?){2,4}[0-9]{2,4}$', value):
            raise serializers.ValidationError(
                "Format de numéro de téléphone invalide. Utilisez un format international (+XXX) ou national."
            )
        return value
    
    def validate_email(self, value):
        """Validation supplémentaire de l'email."""
        import re
        # Vérifie le format de base de l'email et des domaines courants
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', value):
            raise serializers.ValidationError("Format d'email invalide")
        return value
    
    def create(self, validated_data):
        """Crée une inscription en associant l'utilisateur authentifié si disponible."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
            # Si l'utilisateur est authentifié, on peut pré-remplir certaines informations
            if not validated_data.get('nom') and request.user.last_name:
                validated_data['nom'] = request.user.last_name
            if not validated_data.get('prenom') and request.user.first_name:
                validated_data['prenom'] = request.user.first_name
            if not validated_data.get('email') and request.user.email:
                validated_data['email'] = request.user.email
            # On pourrait également chercher le téléphone dans le profil utilisateur si disponible
        
        return super().create(validated_data)

class RechercheFormationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechercheFormation
        fields = ('id', 'utilisateur', 'terme_recherche', 'date_recherche')
        read_only_fields = ('date_recherche',)

class FormationExterneSerializer(serializers.Serializer):
    """Sérialiseur pour les formations externes provenant d'APIs tierces."""
    id = serializers.CharField()
    titre = serializers.CharField(source='nom')  # Map 'nom' vers 'titre' pour cohérence avec notre modèle
    description = serializers.CharField(required=False)
    date_debut = serializers.DateField()
    date_fin = serializers.DateField()
    prix = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    lieu = serializers.CharField(required=False)
    capacite = serializers.IntegerField(required=False)

    def validate(self, data):
        """Valide la cohérence des dates."""
        if data.get('date_debut') and data.get('date_fin'):
            if data['date_debut'] > data['date_fin']:
                raise serializers.ValidationError("La date de début doit être antérieure à la date de fin")
        return data
        
    def to_representation(self, instance):
        """Convertit le format externe vers notre format interne."""
        ret = super().to_representation(instance)
        # Si le champ original était 'nom', on le transforme en 'titre' pour l'affichage
        if 'nom' in instance and 'titre' not in instance:
            ret['titre'] = instance['nom']
        return ret

class FormationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les formations."""
    places_disponibles = serializers.IntegerField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Formation
        fields = [
            'id', 'titre', 'description', 'duree', 'prerequis', 'objectifs',
            'date_session', 'lieu', 'capacite', 'places_disponibles', 
            'department', 'department_name', 'statut', 
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Ajoute automatiquement l'utilisateur courant comme créateur."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class TrackingCodeVerificationSerializer(serializers.Serializer):
    """Sérialiseur pour la vérification du statut d'une inscription via code de suivi."""
    tracking_code = serializers.CharField(max_length=12)

class InscriptionStatusSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour afficher le statut d'une inscription."""
    formation_titre = serializers.CharField(source='formation.titre', read_only=True)
    formation_date = serializers.DateField(source='formation.date_session', read_only=True)
    formation_lieu = serializers.CharField(source='formation.lieu', read_only=True)
    
    class Meta:
        model = Inscription
        fields = [
            'tracking_code', 'nom', 'prenom', 'email',
            'formation_titre', 'formation_date', 'formation_lieu',
            'statut', 'date_inscription', 'date_modification'
        ]
        read_only_fields = [
            'tracking_code', 'nom', 'prenom', 'email',
            'formation_titre', 'formation_date', 'formation_lieu',
            'statut', 'date_inscription', 'date_modification'
        ]
