from rest_framework import permissions
from .models import User


class IsAdminUser(permissions.BasePermission):
    """
    Vérification des permissions pour les administrateurs uniquement.
    """
    message = "Only administrators can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Roles.ADMIN


class IsEditorUser(permissions.BasePermission):
    """
    Vérification des permissions pour les éditeurs de contenu.
    """
    message = "Only content editors can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == User.Roles.EDITOR or 
            request.user.role == User.Roles.ADMIN
        )


class IsResponsableDepartement(permissions.BasePermission):
    """
    Vérification des permissions pour les responsables de département.
    """
    message = "Only department managers can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == User.Roles.RESPONSABLE_DEPARTEMENT or
            request.user.role == User.Roles.ADMIN
        )
    
    def has_object_permission(self, request, view, obj):
        # Les admins peuvent tout faire
        if request.user.role == User.Roles.ADMIN:
            return True
        
        # Si l'utilisateur est responsable de département
        if request.user.role == User.Roles.RESPONSABLE_DEPARTEMENT:
            # Si l'objet a un département associé
            if hasattr(obj, 'department') and obj.department:
                return obj.department == request.user.department
            # Si l'objet a un domaine qui peut être associé à un département
            elif hasattr(obj, 'domaine') and hasattr(obj.domaine, 'department'):
                return obj.domaine.department == request.user.department
            # Si l'objet a une formation avec un département
            elif hasattr(obj, 'formation') and hasattr(obj.formation, 'department'):
                return obj.formation.department == request.user.department
            # Si l'objet a une offre de stage avec un département
            elif hasattr(obj, 'stage_offer') and hasattr(obj.stage_offer, 'department'):
                return obj.stage_offer.department == request.user.department
        
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Vérification des permissions pour la propriété d'objet ou le rôle d'administrateur.
    """
    message = "You must be the owner of this object or an administrator."

    def has_object_permission(self, request, view, obj):        
        # If the user is an admin, allow access
        if request.user.role == User.Roles.ADMIN:
            return True
            
        # Vérifier si l'objet a un champ utilisateur ou un champ propriétaire
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class IsInSameDepartment(permissions.BasePermission):
    """
    Vérification si l'utilisateur est dans le même département que l'objet
    ou si l'utilisateur est un administrateur.
    """
    message = "You must be in the same department as this object or an administrator."
    
    def has_object_permission(self, request, view, obj):
        # Les admins peuvent tout faire
        if request.user.role == User.Roles.ADMIN:
            return True
        
        # Si l'utilisateur n'a pas de département, refuser
        if not request.user.department:
            return False
            
        # Vérifier si l'objet a un département associé
        if hasattr(obj, 'department') and obj.department:
            return obj.department == request.user.department
        # Si l'objet a un domaine qui peut être associé à un département
        elif hasattr(obj, 'domaine') and hasattr(obj.domaine, 'department'):
            return obj.domaine.department == request.user.department
        # Si l'objet a une formation avec un département
        elif hasattr(obj, 'formation') and hasattr(obj.formation, 'department'):
            return obj.formation.department == request.user.department
        # Si l'objet a une offre de stage avec un département
        elif hasattr(obj, 'stage_offer') and hasattr(obj.stage_offer, 'department'):
            return obj.stage_offer.department == request.user.department
        
        return False


class ReadOnly(permissions.BasePermission):
    """
    Vérification des permissions pour l'accès en lecture seule.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
