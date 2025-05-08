from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _


def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exceptions personnalisé pour traiter les exceptions du REST framework.
    Fournit des messages d'erreur plus détaillés et un formatage.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If this is a 500 error or something not handled by DRF
    if response is None:
        return response
    
    # Format the response data
    if isinstance(response.data, dict):
        response_data = {
            'status': 'error',
            'status_code': response.status_code,
            'errors': {},
        }
        
        # Handle different types of error data
        if 'detail' in response.data:
            response_data['message'] = response.data['detail']
        else:
            response_data['message'] = _("An error occurred")
            response_data['errors'] = response.data
            
        response.data = response_data
    
    return response


def get_permissions_by_role(user):
    """
    Renvoie une liste de permissions basée sur le rôle de l'utilisateur.
    Utilisé pour les vérifications de permissions personnalisées.
    """
    from .models import User
    
    # Default permissions for all authenticated users
    permissions = ['can_view_public_content']
    
    if user.is_authenticated:
        permissions.append('can_view_user_only_content')
        
        if user.role == User.Roles.EDITOR:
            permissions.extend([
                'can_create_content',
                'can_edit_content',
                'can_delete_own_content',
            ])
            
        if user.role == User.Roles.ADMIN:
            permissions.extend([
                'can_create_content',
                'can_edit_content',
                'can_delete_any_content',
                'can_manage_users',
                'can_view_analytics',
            ])
    
    return permissions
