from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Formation, Service
from .serializer import FormationSerializer, ServiceSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

"""
ON UTILISE LES VIEWSETS CAR C'EST PLUS RAPIDE ET SIMPLE,
ET ÇA PERMET DE FAIRE TOUTES LES OPÉRATIONS CRUD DANS UNE CLASSE EN SUIVANT LA LOGIQUE REST.
"""

@extend_schema_view(
    list=extend_schema(
        summary="Lister toutes les formations",
        description="Retourne la liste de toutes les formations enregistrées dans le système.",
        tags=["Formations"]
    ),
    retrieve=extend_schema(
        summary="Détail d'une formation",
        description="Retourne les informations détaillées d'une formation en fonction de son ID.",
        tags=["Formations"]
    ),
     create=extend_schema(
        summary="Créer une formation",
        description="Crée une nouvelle formation avec les informations fournies.",
        tags=["Formations"],
        examples=[
            OpenApiExample(
                name="Exemple de création de formation",
                value={
                    "titre": "Développement Web",
                    "description": "Formation complète sur HTML, CSS, JavaScript, Django et React.",
                    "date_debut": "2025-05-10",
                    "date_fin": "2025-08-10",
                    "lieu": "Campus principal"
                },
                request_only=True,
                response_only=False
            )
        ]
    ),
    update=extend_schema(
        summary="Mettre à jour une formation",
        description="Met à jour les informations d'une formation existante.",
        tags=["Formations"]
    ),
    partial_update=extend_schema(
        summary="Mettre à jour partiellement une formation",
        description="Modifie partiellement les champs d'une formation.",
        tags=["Formations"]
    ),
    destroy=extend_schema(
        summary="Supprimer une formation",
        description="Supprime une formation en fonction de son ID.",
        tags=["Formations"]
    ),
)
class FormationViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les formations.
    
    Permet de créer, lister, modifier et supprimer des formations.
    Les méthodes GET (list et retrieve) sont accessibles sans authentification.
    """
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    
    def get_permissions(self):
        """
        Permet l'accès public pour les méthodes GET (list et retrieve),
        mais nécessite une authentification pour les autres méthodes (create, update, delete).
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


@extend_schema_view(
    list=extend_schema(
        summary="Lister tous les services",
        description="Retourne la liste de tous les services enregistrés dans le système.",
        tags=["Services"]
    ),
    retrieve=extend_schema(
        summary="Détail d'un service",
        description="Retourne les informations détaillées d'un service en fonction de son ID.",
        tags=["Services"]
    ),
    create=extend_schema(
        summary="Créer un service",
        description="Crée un nouveau service avec les informations fournies.",
        tags=["Services"],
        examples=[
            OpenApiExample(
                name="Exemple de création de service",
                value={
                    "nom": "Support technique",
                    "description": "Assistance aux utilisateurs pour résoudre leurs problèmes techniques."
                },
                request_only=True,
                response_only=False
            )
        ]
    ),
    update=extend_schema(
        summary="Mettre à jour un service",
        description="Met à jour les informations d'un service existant.",
        tags=["Services"]
    ),
    partial_update=extend_schema(
        summary="Mettre à jour partiellement un service",
        description="Modifie partiellement les champs d'un service.",
        tags=["Services"]
    ),
    destroy=extend_schema(
        summary="Supprimer un service",
        description="Supprime un service en fonction de son ID.",
        tags=["Services"]
    ),
)
class ServiceViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les services.
    
    Permet de créer, lister, modifier et supprimer des services.
    Les méthodes GET (list et retrieve) sont accessibles sans authentification.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    
    def get_permissions(self):
        """
        Permet l'accès public pour les méthodes GET (list et retrieve),
        mais nécessite une authentification pour les autres méthodes (create, update, delete).
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
