from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Realisation
from .serializers import RealisationSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

@extend_schema_view(
    get=extend_schema(
        summary="Lister toutes les réalisations",
        description="Retourne la liste de toutes les réalisations et témoignages.",
        tags=["Réalisations"]
    ),
    post=extend_schema(
        summary="Créer une réalisation",
        description="Ajoute une nouvelle réalisation ou témoignage.",
        tags=["Réalisations"],
        examples=[
            OpenApiExample(
                name="Exemple de création de réalisation",
                value={
                    "projet": "Développement d'une application web",
                    "entreprise": "Entreprise XYZ",
                    "avis": "Excellente prestation, équipe professionnelle et réactive.",
                    "type_personne": "Client"
                },
                request_only=True,
                response_only=False
            )
        ]
    )
)
class RealisationListCreateView(generics.ListCreateAPIView):
    """
    API pour lister et créer des réalisations/témoignages.
    
    La méthode GET est accessible sans authentification,
    mais la méthode POST nécessite une authentification.
    """
    queryset = Realisation.objects.all()
    serializer_class = RealisationSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

@extend_schema_view(
    get=extend_schema(
        summary="Détail d'une réalisation",
        description="Retourne les informations détaillées d'une réalisation en fonction de son ID.",
        tags=["Réalisations"]
    ),
    put=extend_schema(
        summary="Mettre à jour une réalisation",
        description="Met à jour les informations d'une réalisation existante.",
        tags=["Réalisations"]
    ),
    patch=extend_schema(
        summary="Mettre à jour partiellement une réalisation",
        description="Modifie partiellement les champs d'une réalisation.",
        tags=["Réalisations"]
    ),
    delete=extend_schema(
        summary="Supprimer une réalisation",
        description="Supprime une réalisation en fonction de son ID.",
        tags=["Réalisations"]
    )
)
class RealisationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API pour récupérer, mettre à jour et supprimer des réalisations/témoignages.
    
    La méthode GET est accessible sans authentification,
    mais les méthodes PUT, PATCH et DELETE nécessitent une authentification.
    """
    queryset = Realisation.objects.all()
    serializer_class = RealisationSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
