from django.shortcuts import render
from rest_framework import status, generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import DomaineStage, DemandeStage, StageOffer, StageApplication
from .serializers import (
    DomaineStageSerializer, 
    DemandeStageSerializer,
    VerificationStatutSerializer,
    StatutDemandeSerializer,
    StageOfferSerializer, 
    StageApplicationSerializer, 
    TrackingCodeSerializer
)
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from accounts.permissions import IsAdminUser, IsEditorUser, ReadOnly

# Create your views here.

@extend_schema_view(
    list=extend_schema(summary="List all stage offers", description="Returns a list of all published stage offers."),
    retrieve=extend_schema(summary="Retrieve a stage offer", description="Returns details of a specific stage offer."),
    create=extend_schema(summary="Create a stage offer", description="Create a new stage offer (admin/editor only)."),
    update=extend_schema(summary="Update a stage offer", description="Update an existing stage offer (admin/editor only)."),
    partial_update=extend_schema(summary="Partially update a stage offer", description="Partially update an existing stage offer (admin/editor only)."),
    destroy=extend_schema(summary="Delete a stage offer", description="Delete an existing stage offer (admin/editor only).")
)
class StageOfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les offres de stage.
    Les utilisateurs peuvent consulter les offres publiées.
    Seuls les administrateurs et les éditeurs peuvent créer/modifier des offres.
    """
    serializer_class = StageOfferSerializer
    
    def get_permissions(self):
        """Définir les permissions selon l'action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsEditorUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filtrer les offres selon le rôle de l'utilisateur:
        - Admin/Éditeur: toutes les offres
        - Utilisateurs non authentifiés: uniquement les offres publiées
        """
        user = self.request.user
        if user.is_authenticated and (user.is_admin() or user.is_editor()):
            return StageOffer.objects.all()
        return StageOffer.objects.filter(status='published')
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def postuler(self, request, pk=None):
        """
        Endpoint pour postuler à une offre de stage.
        Crée une nouvelle candidature et retourne le code de suivi.
        """
        stage_offer = self.get_object()
        serializer = StageApplicationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Ajouter l'offre de stage à la candidature
            serializer.save(stage_offer=stage_offer)
            return Response({
                'message': 'Candidature envoyée avec succès',
                'tracking_code': serializer.instance.tracking_code
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StageApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les candidatures aux stages.
    Seuls les administrateurs et les éditeurs peuvent voir/gérer les candidatures.
    """
    serializer_class = StageApplicationSerializer
    permission_classes = [IsEditorUser]
    
    def get_queryset(self):
        """
        Filtrer les candidatures selon le rôle et le département de l'utilisateur.
        """
        user = self.request.user
        if user.is_admin():
            return StageApplication.objects.all()
        
        # Pour les éditeurs, filtrer par leurs départements
        # Note: nécessite d'ajouter un champ département au modèle User
        # return StageApplication.objects.filter(stage_offer__department=user.department)
        return StageApplication.objects.all()  # À modifier avec la logique de départements
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Mettre à jour le statut d'une candidature."""
        application = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in [status for status, _ in APPLICATION_STATUS]:
            return Response({'error': 'Statut invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = new_status
        application.save()
        
        return Response({
            'id': application.id,
            'tracking_code': application.tracking_code,
            'status': application.status
        })


@extend_schema_view(
    verify=extend_schema(
        summary="Vérifier le statut d'une candidature",
        description="Vérifie le statut d'une candidature à partir du code de suivi"
    )
)
class TrackingViewSet(viewsets.ViewSet):
    """ViewSet pour vérifier le statut des candidatures via code de suivi."""
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Vérifier le statut d'une candidature via son code de suivi."""
        serializer = TrackingCodeSerializer(data=request.data)
        
        if serializer.is_valid():
            tracking_code = serializer.validated_data['tracking_code']
            
            try:
                application = StageApplication.objects.get(tracking_code=tracking_code)
                return Response({
                    'tracking_code': application.tracking_code,
                    'stage': application.stage_offer.title,
                    'candidate': f"{application.first_name} {application.last_name}",
                    'status': application.status,
                    'application_date': application.created_at
                })
            except StageApplication.DoesNotExist:
                return Response(
                    {'error': 'Code de suivi invalide'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DomaineStageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les domaines de stage.
    
    Permet de lister, créer, modifier et supprimer les domaines de stage.
    Seuls les utilisateurs authentifiés peuvent effectuer des modifications.
    """
    queryset = DomaineStage.objects.all()
    serializer_class = DomaineStageSerializer
    
    def get_permissions(self):
        """
        Définit les permissions selon l'action :
        - Liste et détail : accessible à tous
        - Création, modification, suppression : utilisateurs authentifiés uniquement
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

class DemandeStageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les demandes de stage.
    
    Permet de :
    - Créer une nouvelle demande de stage
    - Vérifier le statut d'une demande via son code unique
    - Lister et gérer les demandes (admin uniquement)
    """
    serializer_class = DemandeStageSerializer
    
    def get_permissions(self):
        """
        Définit les permissions selon l'action :
        - Création et vérification de statut : accessible à tous
        - Autres actions : utilisateurs authentifiés uniquement
        """
        if self.action in ['create', 'verifier_statut']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """
        Filtrer les demandes selon le rôle de l'utilisateur.
        """
        user = self.request.user
        if user.is_admin():
            return DemandeStage.objects.all()
        
        # Pour les éditeurs, filtrer par leurs départements
        # Note: nécessite d'ajouter un champ département au modèle User
        # return DemandeStage.objects.filter(domaine__nom=user.department)
        return DemandeStage.objects.all()  # À modifier avec la logique de départements
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_status(self, request):
        """
        Vérifier le statut d'une demande via son code unique.
        Accessible publiquement pour permettre aux candidats de vérifier leur statut.
        """
        from django.shortcuts import get_object_or_404
        from rest_framework.exceptions import ValidationError
        import uuid
        
        try:
            code = request.data.get('code_unique')
            if not code:
                return Response({'error': 'Code unique requis'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                code_uuid = uuid.UUID(code)
            except ValueError:
                return Response({'error': 'Format de code invalide'}, status=status.HTTP_400_BAD_REQUEST)
            
            demande = get_object_or_404(DemandeStage, code_unique=code_uuid)
            
            return Response({
                'code_unique': str(demande.code_unique),
                'domaine': demande.domaine.nom,
                'statut': demande.statut,
                'date_demande': demande.date_demande,
                'date_modification': demande.date_modification
            })
            
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def verifier_statut(self, request):
        """
        Vérifie le statut d'une demande de stage via son code unique.
        
        Args:
            request: Requête contenant le paramètre 'code_unique'
            
        Returns:
            Response: Statut de la demande ou message d'erreur
        """
        code = request.query_params.get('code_unique')
        if not code:
            return Response(
                {'error': 'Le code unique est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            demande = DemandeStage.objects.get(code_unique=code)
            serializer = self.get_serializer(demande)
            return Response(serializer.data)
        except DemandeStage.DoesNotExist:
            return Response(
                {'error': 'Demande non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

class DomaineStageListView(generics.ListAPIView):
    queryset = DomaineStage.objects.all()
    serializer_class = DomaineStageSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Liste tous les domaines de stage disponibles",
        responses={
            200: DomaineStageSerializer(many=True),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class DemandeStageCreateView(generics.CreateAPIView):
    queryset = DemandeStage.objects.all()
    serializer_class = DemandeStageSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Créer une nouvelle demande de stage",
        request_body=DemandeStageSerializer,
        responses={
            201: openapi.Response('Demande créée avec succès', DemandeStageSerializer),
            400: 'Données invalides'
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class VerificationStatutView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Vérifier le statut d'une demande de stage",
        request_body=VerificationStatutSerializer,
        responses={
            200: StatutDemandeSerializer,
            404: 'Demande non trouvée'
        }
    )
    def post(self, request):
        serializer = VerificationStatutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                demande = DemandeStage.objects.get(code_unique=serializer.validated_data['code_unique'])
                return Response(StatutDemandeSerializer(demande).data)
            except DemandeStage.DoesNotExist:
                return Response(
                    {'error': 'Aucune demande trouvée avec ce code'},
                    status=status.HTTP_404_NOT_FOUND
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DemandeStageDetailView(generics.RetrieveUpdateAPIView):
    queryset = DemandeStage.objects.all()
    serializer_class = DemandeStageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'code_unique'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def check_object_permissions(self, request, obj):
        if request.method in ['PUT', 'PATCH']:
            if not request.user.is_staff:
                raise PermissionDenied("Seuls les administrateurs peuvent modifier le statut des demandes.")
        return super().check_object_permissions(request, obj)

    @swagger_auto_schema(
        operation_description="Récupérer ou mettre à jour une demande de stage",
        responses={
            200: DemandeStageSerializer,
            404: 'Demande non trouvée'
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Mettre à jour le statut d'une demande de stage",
        request_body=DemandeStageSerializer,
        responses={
            200: DemandeStageSerializer,
            400: 'Données invalides',
            403: 'Permission refusée',
            404: 'Demande non trouvée'
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.check_object_permissions(request, instance)
            
            if 'statut' in request.data:
                instance.statut = request.data['statut']
                instance.save()
                return Response(self.get_serializer(instance).data)
            else:
                return Response(
                    {'error': 'Le champ statut est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
