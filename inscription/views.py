from django.shortcuts import render, get_object_or_404
from rest_framework import status, generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Utilisateur, Inscription, RechercheFormation, Formation
from .serializers import (
    UserSerializer, 
    UtilisateurSerializer, 
    InscriptionSerializer,
    RechercheFormationSerializer,
    FormationExterneSerializer,
    FormationSerializer,
    TrackingCodeVerificationSerializer,
    InscriptionStatusSerializer
)
from .throttling import (
    LoginRateThrottle,
    InscriptionRateThrottle,
    VerifyTrackingRateThrottle,
    APIRateThrottle
)
import requests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from rest_framework.exceptions import ValidationError, APIException
import logging
from rest_framework.decorators import action
from accounts.permissions import IsEditorUser, IsResponsableDepartement, IsInSameDepartment

logger = logging.getLogger(__name__)

class APIError(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporairement indisponible.'
    default_code = 'service_unavailable'

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UtilisateurSerializer,
        responses={
            201: openapi.Response('User successfully registered', UtilisateurSerializer),
            400: 'Invalid data provided'
        }
    )
    def post(self, request):
        try:
            # Ajout de logs pour déboguer
            logger.info(f"Données de requête: {request.data}")
            
            serializer = UtilisateurSerializer(data=request.data)
            if serializer.is_valid():
                utilisateur = serializer.save()
                refresh = RefreshToken.for_user(utilisateur.user)
                return Response({
                    'user': serializer.data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            
            # Ajout de logs d'erreur de validation
            logger.error(f"Erreurs de validation: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log détaillé de l'exception
            import traceback
            logger.error(f"Erreur lors de l'inscription: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response(
                {'error': 'Une erreur est survenue lors de l\'inscription', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]  # Limite les tentatives de connexion

    @swagger_auto_schema(
        operation_description="Se connecter avec un compte existant",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response('Connexion réussie', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            401: 'Identifiants invalides',
            429: 'Trop de tentatives, veuillez réessayer plus tard'
        }
    )
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response(
                    {'error': 'Username et password requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response(
                {'error': 'Identifiants invalides'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {str(e)}")
            return Response(
                {'error': 'Une erreur est survenue lors de la connexion'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RechercheFormationView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Rechercher une formation",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['terme_recherche'],
            properties={
                'terme_recherche': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: FormationExterneSerializer(many=True),
            400: 'Terme de recherche requis',
            503: 'Service de recherche indisponible'
        }
    )
    def post(self, request):
        try:
            terme_recherche = request.data.get('terme_recherche')
            if not terme_recherche:
                return Response(
                    {'error': 'Terme de recherche requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Enregistrer la recherche
            RechercheFormation.objects.create(
                utilisateur=request.user.utilisateur,
                terme_recherche=terme_recherche
            )
            
            # Appeler l'API externe
            try:
                response = requests.get(
                    f"{settings.FORMATION_API_URL}/search",
                    params={'q': terme_recherche},
                    headers={'Authorization': f'Bearer {settings.FORMATION_API_KEY}'},
                    timeout=5
                )
                response.raise_for_status()
                formations = response.json()
                
                # Valider les données reçues
                serializer = FormationExterneSerializer(data=formations, many=True)
                if serializer.is_valid():
                    return Response(serializer.data)
                return Response(
                    {'error': 'Données invalides reçues du service externe'},
                    status=status.HTTP_502_BAD_GATEWAY
                )
                
            except requests.RequestException as e:
                logger.error(f"Erreur API externe: {str(e)}")
                raise APIError()
                
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            return Response(
                {'error': 'Une erreur est survenue lors de la recherche'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InscriptionView(generics.CreateAPIView):
    """Vue pour créer une nouvelle inscription à une formation.
    
    Cette vue est accessible aux utilisateurs authentifiés et non-authentifiés.
    Pour les utilisateurs authentifiés, certaines informations sont pré-remplies.
    """
    queryset = Inscription.objects.all()
    serializer_class = InscriptionSerializer
    permission_classes = [AllowAny]
    throttle_classes = [InscriptionRateThrottle]  # Limite les inscriptions pour prévenir le spam

    @swagger_auto_schema(
        operation_description="S'inscrire à une formation",
        request_body=InscriptionSerializer,
        responses={
            201: openapi.Response(
                description="Inscription créée avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'tracking_code': openapi.Schema(type=openapi.TYPE_STRING),
                        'statut': openapi.Schema(type=openapi.TYPE_STRING),
                        'formation': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: openapi.Response(
                description="Données invalides",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_OBJECT),
                    }
                )
            ),
            500: 'Erreur serveur'
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            # Ajout de la requête au contexte du serializer pour accéder à l'utilisateur
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            inscription = self.perform_create(serializer)
            
            # Format standardisé de réponse pour toutes les inscriptions
            return Response({
                'message': 'Inscription effectuée avec succès',
                'tracking_code': inscription.tracking_code,
                'statut': inscription.statut,
                'formation': inscription.formation.titre
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.warning(f"Erreur de validation lors de l'inscription: {str(e)}")
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription à la formation: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Une erreur est survenue lors de l\'inscription à la formation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        return serializer.save()

class VerificationStatutInscriptionView(generics.ListAPIView):
    """Vue pour lister les inscriptions d'un utilisateur authentifié."""
    serializer_class = InscriptionStatusSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Récupérer la liste de vos inscriptions",
        responses={
            200: InscriptionStatusSerializer(many=True),
            404: 'Aucune inscription trouvée'
        }
    )
    def list(self, request, *args, **kwargs):
        inscriptions = self.get_queryset()
        if not inscriptions.exists():
            return Response(
                {'message': 'Aucune inscription trouvée pour cet utilisateur'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        page = self.paginate_queryset(inscriptions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(inscriptions, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """Récupérer toutes les inscriptions de l'utilisateur connecté."""
        return Inscription.objects.filter(user=self.request.user)

class FormationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les formations.
    Les utilisateurs non authentifiés peuvent voir les formations.
    Seuls les admins, éditeurs et responsables de département peuvent créer/modifier.
    """
    serializer_class = FormationSerializer
    
    def get_permissions(self):
        """Définir les permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsEditorUser|IsResponsableDepartement]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filtrer les formations selon le rôle et le département de l'utilisateur.
        """
        user = self.request.user
        queryset = Formation.objects.all()
        
        if user.is_authenticated:
            if user.is_admin():
                # Admin voit tout
                return queryset
            elif user.is_responsable_departement() and user.department:
                # Responsable ne voit que les formations de son département
                return queryset.filter(department=user.department)
            elif user.is_editor():
                # Éditeur voit tout
                return queryset
        
        # Utilisateurs non authentifiés ne voient que les formations planifiées ou en cours
        return queryset.filter(statut__in=['planifiee', 'en_cours'])
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def inscrire(self, request, pk=None):
        """
        Endpoint pour s'inscrire à une formation spécifique.
        Crée une nouvelle inscription et retourne le code de suivi.
        """
        formation = self.get_object()
        
        # Ajouter la formation aux données de la requête
        data = request.data.copy()
        data['formation'] = formation.id
        
        # Utiliser le même serializer et le même contexte que InscriptionView
        serializer = InscriptionSerializer(data=data, context={'request': request})
        
        try:
            if serializer.is_valid(raise_exception=True):
                inscription = serializer.save()
                # Format de réponse identique à InscriptionView pour cohérence
                return Response({
                    'message': 'Inscription effectuée avec succès',
                    'tracking_code': inscription.tracking_code,
                    'statut': inscription.statut,
                    'formation': formation.titre
                }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.warning(f"Erreur de validation lors de l'inscription via FormationViewSet: {str(e)}")
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription à la formation via FormationViewSet: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Une erreur est survenue lors de l\'inscription à la formation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les inscriptions aux formations.
    Seuls les admins, éditeurs et responsables de département peuvent gérer les inscriptions.
    """
    serializer_class = InscriptionSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsEditorUser|IsResponsableDepartement]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filtrer les inscriptions selon le rôle et le département de l'utilisateur.
        """
        user = self.request.user
        
        if user.is_admin():
            # Admin voit tout
            return Inscription.objects.all()
        elif user.is_responsable_departement() and user.department:
            # Responsable de département ne voit que les inscriptions aux formations de son département
            return Inscription.objects.filter(formation__department=user.department)
        elif user.is_editor():
            # Éditeur voit tout
            return Inscription.objects.all()
        
        # Pour les utilisateurs normaux, renvoyer uniquement leurs propres inscriptions
        if user.is_authenticated:
            return Inscription.objects.filter(user=user)
        
        # Pour les utilisateurs non authentifiés, ne rien renvoyer
        return Inscription.objects.none()
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Mettre à jour le statut d'une inscription."""
        inscription = self.get_object()
        new_status = request.data.get('statut')
        
        if new_status not in [status for status, _ in Inscription.STATUT_CHOICES]:
            return Response({'error': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        inscription.statut = new_status
        inscription.save()
        
        return Response({
            'id': inscription.id,
            'tracking_code': inscription.tracking_code,
            'statut': inscription.statut
        })
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], throttle_classes=[VerifyTrackingRateThrottle])
    def verify_tracking(self, request):
        """
        Vérifier le statut d'une inscription via son code de suivi.
        Accessible publiquement pour permettre aux inscrits de vérifier leur statut.
        Limité à 10 tentatives par minute pour prévenir les attaques par force brute.
        """
        serializer = TrackingCodeVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            tracking_code = serializer.validated_data['tracking_code']
            
            try:
                inscription = Inscription.objects.get(tracking_code=tracking_code)
                response_serializer = InscriptionStatusSerializer(inscription)
                logger.info(f"Vérification réussie du code de suivi: {tracking_code}")
                return Response(response_serializer.data)
            except Inscription.DoesNotExist:
                logger.warning(f"Tentative de vérification avec un code de suivi invalide: {tracking_code}")
                return Response(
                    {'error': 'Code de suivi invalide ou inexistant'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        logger.warning(f"Données invalides pour la vérification du code: {request.data}")
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
