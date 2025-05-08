from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.plumbing import build_basic_type
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

class SchemaConfig:
    """Configuration centralisée pour le schéma OpenAPI."""

    TAGS = [
        {'name': 'Formations', 'description': 'Gestion des formations'},
        {'name': 'Services', 'description': 'Gestion des services'},
        {'name': 'Inscription', 'description': 'Gestion des inscriptions'},
        {'name': 'Authentication', 'description': 'Gestion des utilisateurs et authentification'},
        {'name': 'Stages', 'description': 'Gestion des stages et candidatures'},
        {'name': 'Partenaires', 'description': 'Gestion des partenaires'},
        {'name': 'Réalisations', 'description': 'Gestion des réalisations et témoignages'},
        {'name': 'Contacts', 'description': 'Gestion des messages de contact'},
    ]

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

# Ajout des paramètres pour Swagger et ReDoc
SPECTACULAR_SETTINGS = {
    'TITLE': 'GIN API Documentation',
    'DESCRIPTION': 'Documentation complète des API du projet GIN, incluant les API de formations, services, partenaires, réalisations, contacts, inscriptions et stages.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': False,
    'TAGS': SchemaConfig.TAGS,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayOperationId': True,
        'syntaxHighlight.theme': 'monokai',
    },
    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': True,
        'expandResponses': '200,201',
    },
}

# Exemples d'extensions personnalisées
class FormationViewExtension(OpenApiViewExtension):
    target_class = 'gin.views.FormationViewSet'
    
    def view_replacement(self):
        return extend_schema(
            tags=['Formations'],
            examples=SchemaConfig.FORMATION_EXAMPLES,
        )(self.target_class)