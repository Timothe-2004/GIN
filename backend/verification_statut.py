from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import serializers
from inscription.models import Inscription
from stages.models import StageApplication, DemandeStage

class VerificationStatutSerializer(serializers.Serializer):
    """Serializer pour la vérification de statut."""
    code = serializers.CharField(required=True, help_text="Code de suivi à vérifier")
    type = serializers.ChoiceField(
        choices=['formation', 'stage', 'all'],
        default='all',
        help_text="Type de vérification à effectuer"
    )

class VerificationStatutView(views.APIView):
    """
    Vue pour vérifier le statut d'une inscription ou d'une candidature.
    
    Permet de vérifier le statut d'une inscription à une formation, 
    d'une candidature à un stage ou d'une demande de stage, 
    en fonction du code de suivi fourni.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Vérifier le statut d'une inscription ou candidature",
        description="Permet de vérifier le statut d'une inscription à une formation, d'une candidature à un stage ou d'une demande de stage, en fonction du code de suivi fourni.",
        request=VerificationStatutSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "Type de l'élément trouvé (formation, stage, demande)"},
                    "code": {"type": "string", "description": "Code de suivi vérifié"},
                    "statut": {"type": "string", "description": "Statut actuel"},
                    "titre": {"type": "string", "description": "Titre de la formation ou du stage"},
                    "date": {"type": "string", "format": "date-time", "description": "Date d'inscription ou de candidature"}
                }
            },
            404: {"description": "Aucun élément trouvé avec ce code"},
            400: {"description": "Paramètres invalides"}
        },
        examples=[
            OpenApiExample(
                name="Exemple de requête",
                value={"code": "ABC123456789", "type": "all"},
                request_only=True
            ),
            OpenApiExample(
                name="Exemple de réponse pour une formation",
                value={
                    "type": "formation",
                    "code": "ABC123456789",
                    "statut": "en_attente",
                    "titre": "Développement Web avec Django",
                    "date": "2025-05-01T14:30:00Z",
                    "nom": "Dupont",
                    "prenom": "Jean"
                },
                response_only=True
            )
        ]
    )
    def post(self, request):
        """
        Vérifier le statut d'une inscription, candidature ou demande via son code de suivi.
        
        Args:
            request: Requête contenant le code de suivi et le type (optionnel)
            
        Returns:
            Response: Statut de l'élément trouvé ou message d'erreur
        """
        serializer = VerificationStatutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        code = serializer.validated_data['code']
        type_recherche = serializer.validated_data['type']
        
        # Recherche dans les inscriptions aux formations
        if type_recherche in ['all', 'formation']:
            try:
                inscription = Inscription.objects.get(tracking_code=code)
                return Response({
                    "type": "formation",
                    "code": inscription.tracking_code,
                    "statut": inscription.statut,
                    "titre": inscription.formation.titre,
                    "date": inscription.date_inscription,
                    "nom": inscription.nom,
                    "prenom": inscription.prenom
                })
            except Inscription.DoesNotExist:
                # Continuer la recherche si type_recherche est 'all'
                if type_recherche == 'formation':
                    return Response(
                        {"error": "Aucune inscription à une formation trouvée avec ce code"},
                        status=status.HTTP_404_NOT_FOUND
                    )
        
        # Recherche dans les candidatures aux stages
        if type_recherche in ['all', 'stage']:
            try:
                candidature = StageApplication.objects.get(tracking_code=code)
                return Response({
                    "type": "stage",
                    "code": candidature.tracking_code,
                    "statut": candidature.status,
                    "titre": candidature.stage_offer.title,
                    "date": candidature.created_at,
                    "nom": candidature.last_name,
                    "prenom": candidature.first_name
                })
            except StageApplication.DoesNotExist:
                # Si on n'a pas trouvé, essayer dans les demandes de stage
                try:
                    demande = DemandeStage.objects.get(code_unique=code)
                    return Response({
                        "type": "demande_stage",
                        "code": str(demande.code_unique),
                        "statut": demande.statut,
                        "titre": f"Demande de stage en {demande.domaine.nom}",
                        "date": demande.date_demande,
                        "nom": demande.nom,
                        "prenom": demande.prenom
                    })
                except DemandeStage.DoesNotExist:
                    if type_recherche == 'stage':
                        return Response(
                            {"error": "Aucune candidature ou demande de stage trouvée avec ce code"},
                            status=status.HTTP_404_NOT_FOUND
                        )
        
        # Si on arrive ici, c'est qu'on n'a rien trouvé pour le code
        return Response(
            {"error": "Aucun élément trouvé avec ce code"},
            status=status.HTTP_404_NOT_FOUND
        )