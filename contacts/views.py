from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiParameter

from .models import ContactMessage, ContactReponse
from .serializers import ContactMessageSerializer, ContactResponseSerializer, ContactMessageDetailSerializer
from accounts.permissions import IsAdminUser, IsEditorUser, IsResponsableDepartement


@extend_schema_view(
    list=extend_schema(
        summary="Lister tous les messages de contact",
        description="Retourne la liste des messages de contact (accès restreint).",
        tags=["Contacts"]
    ),
    retrieve=extend_schema(
        summary="Détail d'un message de contact",
        description="Retourne les informations détaillées d'un message de contact et ses réponses.",
        tags=["Contacts"]
    ),
    create=extend_schema(
        summary="Créer un message de contact",
        description="Envoie un nouveau message via le formulaire de contact.",
        tags=["Contacts"],
        examples=[
            OpenApiExample(
                name="Exemple de message de contact",
                value={
                    "nom": "Dupont",
                    "prenom": "Jean",
                    "email": "jean.dupont@exemple.com",
                    "telephone": "0123456789",
                    "sujet": "Demande d'information",
                    "message": "Je souhaiterais obtenir plus d'informations sur vos services.",
                    "departement_destinataire": 1
                },
                request_only=True,
                response_only=False
            )
        ]
    ),
    update=extend_schema(
        summary="Mettre à jour un message de contact",
        description="Met à jour les informations d'un message de contact (accès restreint).",
        tags=["Contacts"]
    ),
    partial_update=extend_schema(
        summary="Mettre à jour partiellement un message de contact",
        description="Modifie partiellement les champs d'un message de contact (accès restreint).",
        tags=["Contacts"]
    ),
    destroy=extend_schema(
        summary="Supprimer un message de contact",
        description="Supprime un message de contact (accès restreint).",
        tags=["Contacts"]
    )
)
class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les messages de contact.
    
    Les utilisateurs non authentifiés peuvent créer des messages.
    Seuls les administrateurs, éditeurs et responsables de département peuvent 
    voir, modifier ou supprimer les messages.
    """
    filterset_fields = ['statut', 'departement_destinataire']
    search_fields = ['nom', 'prenom', 'email', 'sujet', 'message']
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['date_creation', 'date_modification', 'statut']
    ordering = ['-date_creation']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ContactMessageDetailSerializer
        return ContactMessageSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated & (IsAdminUser | IsEditorUser | IsResponsableDepartement)]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        
        # Anonyme ou non authentifié ne peut pas lister les messages
        if not user.is_authenticated:
            return ContactMessage.objects.none()
            
        # Admin voit tout
        if user.is_admin():
            return ContactMessage.objects.all()
            
        # Responsable de département ne voit que les messages adressés à son département
        if user.is_responsable_departement() and user.department:
            return ContactMessage.objects.filter(departement_destinataire=user.department)
            
        # Éditeur voit tout
        if user.is_editor():
            return ContactMessage.objects.all()
            
        # Par défaut, aucun message n'est visible
        return ContactMessage.objects.none()
    
    @extend_schema(
        summary="Mettre à jour le statut d'un message",
        description="Modifie le statut d'un message de contact (ex: non_lu, en_cours, traite, archive).",
        tags=["Contacts"],
        parameters=[
            OpenApiParameter(
                name="statut",
                description="Nouveau statut du message",
                required=True,
                type=str,
                enum=["non_lu", "en_cours", "traite", "archive"]
            )
        ]
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Mettre à jour le statut d'un message."""
        message = self.get_object()
        new_status = request.data.get('statut')
        
        if new_status not in [status for status, _ in ContactMessage.STATUT_CHOICES]:
            return Response({'error': _('Statut invalide')}, status=status.HTTP_400_BAD_REQUEST)
        
        message.statut = new_status
        message.save()
        
        serializer = self.get_serializer(message)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Lister toutes les réponses aux messages",
        description="Retourne la liste des réponses aux messages de contact (accès restreint).",
        tags=["Contacts"]
    ),
    retrieve=extend_schema(
        summary="Détail d'une réponse",
        description="Retourne les informations détaillées d'une réponse à un message de contact.",
        tags=["Contacts"]
    ),
    create=extend_schema(
        summary="Créer une réponse à un message",
        description="Envoie une nouvelle réponse à un message de contact (accès restreint).",
        tags=["Contacts"],
        examples=[
            OpenApiExample(
                name="Exemple de réponse à un message",
                value={
                    "message_original": 1,
                    "reponse": "Merci pour votre message. Voici les informations demandées..."
                },
                request_only=True,
                response_only=False
            )
        ]
    ),
    update=extend_schema(
        summary="Mettre à jour une réponse",
        description="Met à jour une réponse à un message de contact (accès restreint).",
        tags=["Contacts"]
    ),
    partial_update=extend_schema(
        summary="Mettre à jour partiellement une réponse",
        description="Modifie partiellement une réponse à un message de contact (accès restreint).",
        tags=["Contacts"]
    ),
    destroy=extend_schema(
        summary="Supprimer une réponse",
        description="Supprime une réponse à un message de contact (accès restreint).",
        tags=["Contacts"]
    )
)
class ContactResponseViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les réponses aux messages de contact.
    
    Seuls les administrateurs, éditeurs et responsables de département peuvent 
    créer, voir, modifier ou supprimer les réponses.
    """
    serializer_class = ContactResponseSerializer
    permission_classes = [IsAuthenticated & (IsAdminUser | IsEditorUser | IsResponsableDepartement)]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin voit tout
        if user.is_admin():
            return ContactReponse.objects.all()
            
        # Responsable de département ne voit que les réponses aux messages adressés à son département
        if user.is_responsable_departement() and user.department:
            return ContactReponse.objects.filter(
                message_original__departement_destinataire=user.department
            )
            
        # Éditeur voit tout
        if user.is_editor():
            return ContactReponse.objects.all()
            
        # Par défaut, aucune réponse n'est visible
        return ContactReponse.objects.none()