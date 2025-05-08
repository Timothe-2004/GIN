from django.shortcuts import render
from rest_framework import status, generics, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import StageOffer, StageApplication, APPLICATION_STATUS
from .serializers import (
    StageOfferSerializer, 
    StageApplicationSerializer, 
    TrackingCodeSerializer
)
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from accounts.permissions import IsAdminUser, IsEditorUser, ReadOnly, IsResponsableDepartement

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
        if user.is_authenticated and user.is_responsable_departement():
            return StageOffer.objects.filter(department=user.department)
        return StageOffer.objects.filter(status='published')
    
    def perform_create(self, serializer):
        """Automatically associate the stage offer with the creator's department."""
        user = self.request.user
        if user.is_authenticated and user.is_responsable_departement():
            serializer.save(department=user.department, created_by=user)
        else:
            serializer.save(created_by=user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def postuler(self, request, pk=None):
        """
        Endpoint pour postuler à une offre de stage.
        Crée une nouvelle candidature et retourne le code de suivi.
        """
        stage_offer = self.get_object()

        # Vérifier que l'offre est publiée
        if stage_offer.status != 'published':
            return Response({
                'error': 'Vous ne pouvez postuler qu’à des offres publiées.'
            }, status=status.HTTP_400_BAD_REQUEST)

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

        if user.is_editor():
            # Filtrer par département pour les éditeurs
            return StageApplication.objects.filter(stage_offer__department=user.department)

        return StageApplication.objects.none()  # Aucun accès pour les autres utilisateurs
    
    @action(detail=True, methods=['patch'], permission_classes=[IsEditorUser])
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
