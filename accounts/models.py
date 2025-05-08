from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Department(models.Model):
    """Modèle représentant les départements de l'entreprise."""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')
    
    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """Gestionnaire d'utilisateur personnalisé pour le modèle User."""
    def create_user(self, email, password=None, **extra_fields):
        """Créer et enregistrer un utilisateur régulier avec l'email et le mot de passe fournis."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Créer et enregistrer un superutilisateur avec l'email et le mot de passe fournis."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Roles.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Modèle d'utilisateur personnalisé avec l'email comme identifiant unique."""
    
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        EDITOR = 'EDITOR', _('Content Editor')
        USER = 'USER', _('Regular User')
        RESPONSABLE_DEPARTEMENT = 'RESP_DEPT', _('Responsable de Département')
    
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER,
    )
    department = models.ForeignKey(
        Department, 
        verbose_name=_('department'),
        related_name='users',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into the admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """Renvoie le prénom et le nom, avec un espace entre les deux."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Renvoie le nom court de l'utilisateur."""
        return self.first_name

    def is_admin(self):
        """Vérifie si l'utilisateur est un administrateur."""
        return self.role == self.Roles.ADMIN

    def is_editor(self):
        """Vérifie si l'utilisateur est un éditeur de contenu."""
        return self.role == self.Roles.EDITOR
    
    def is_responsable_departement(self):
        """Vérifie si l'utilisateur est un responsable de département."""
        return self.role == self.Roles.RESPONSABLE_DEPARTEMENT
    
    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """Informations de profil étendues pour les utilisateurs."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(_('biography'), blank=True)
    profile_picture = models.ImageField(
        _('profile picture'), 
        upload_to='profile_pics/', 
        blank=True,
        null=True
    )
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    position = models.CharField(_('position'), max_length=100, blank=True)
    # Le champ department est maintenant directement dans le modèle User
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"{self.user.email}'s profile"
