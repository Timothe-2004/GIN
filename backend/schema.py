from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

class SchemaConfig:
    """Configuration centralisée pour le schéma OpenAPI."""
    
    TAGS = [
        # Tags principaux pour regrouper les endpoints
        {'name': 'Formations', 'description': 'Gestion des formations'},
        {'name': 'Services', 'description': 'Gestion des services'},
        {'name': 'Inscription', 'description': 'Gestion des inscriptions'},
        {'name': 'Authentication', 'description': 'Gestion des utilisateurs et authentification'},
        {'name': 'Stages', 'description': 'Gestion des stages et candidatures'},
    ]
    
    # Exemples pour la documentation
    FORMATION_EXAMPLES = [
        OpenApiExample(
            name="Formation exemple",
            value={
                "titre": "Master en développement web",
                "description": "Formation complète de développement web avec Django et React",
                "date_debut": "2025-09-01",
                "date_fin": "2026-06-30",
                "lieu": "Campus principal"
            },
            request_only=True
        )
    ]

# Exemples d'extensions personnalisées
class FormationViewExtension(OpenApiViewExtension):
    target_class = 'gin.views.FormationViewSet'
    
    def view_replacement(self):
        return extend_schema(
            tags=['Formations'],
            examples=SchemaConfig.FORMATION_EXAMPLES,
        )(self.target_class)