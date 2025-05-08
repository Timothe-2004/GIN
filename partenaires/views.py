from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Partenaire
from .serializers import PartenaireSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample

@extend_schema_view(
    get=extend_schema(
        summary="Lister tous les partenaires",
        description="Retourne la liste de tous les partenaires enregistrés.",
        tags=["Partenaires"]
    ),
    post=extend_schema(
        summary="Créer un partenaire",
        description="Crée un nouveau partenaire avec les informations fournies.",
        tags=["Partenaires"],
        examples=[
            OpenApiExample(
                name="Exemple de création de partenaire",
                value={
                    "nom": "Entreprise Partenaire",
                    "site_web": "https://www.entreprisepartenaire.com",
                },
                request_only=True,
                response_only=False
            )
        ]
    )
)
class PartenaireListCreateView(generics.ListCreateAPIView):
    """
    API pour lister et créer des partenaires.
    
    La méthode GET est accessible sans authentification,
    mais la méthode POST nécessite une authentification.
    """
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

@extend_schema_view(
    get=extend_schema(
        summary="Détail d'un partenaire",
        description="Retourne les informations détaillées d'un partenaire en fonction de son ID.",
        tags=["Partenaires"]
    ),
    put=extend_schema(
        summary="Mettre à jour un partenaire",
        description="Met à jour les informations d'un partenaire existant.",
        tags=["Partenaires"]
    ),
    patch=extend_schema(
        summary="Mettre à jour partiellement un partenaire",
        description="Modifie partiellement les champs d'un partenaire.",
        tags=["Partenaires"]
    ),
    delete=extend_schema(
        summary="Supprimer un partenaire",
        description="Supprime un partenaire en fonction de son ID.",
        tags=["Partenaires"]
    )
)
class PartenaireRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    API pour récupérer, mettre à jour et supprimer des partenaires.
    
    La méthode GET est accessible sans authentification,
    mais les méthodes PUT, PATCH et DELETE nécessitent une authentification.
    """
    queryset = Partenaire.objects.all()
    serializer_class = PartenaireSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
