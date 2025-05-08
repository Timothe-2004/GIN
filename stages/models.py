from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.crypto import get_random_string
from accounts.models import User, Department

# Choix pour le type de stage
STAGE_TYPES = [
    ('initiation', 'Stage d\'initiation'),
    ('perfectionnement', 'Stage de perfectionnement'),
    ('professionnalisation', 'Stage de professionnalisation'),
    ('fin_etude', 'Stage de fin d\'études'),
]

# Choix pour le statut de l'offre
OFFER_STATUS = [
    ('draft', 'Brouillon'),
    ('published', 'Publié'),
    ('closed', 'Clôturé'),
    ('archived', 'Archivé'),
]

# Choix pour le statut de candidature
APPLICATION_STATUS = [
    ('pending', 'En attente'),
    ('accepted', 'Acceptée'),
    ('rejected', 'Refusée'),
]

class StageOffer(models.Model):
    """Modèle pour les offres de stage."""
    title = models.CharField(max_length=200, verbose_name="Titre")
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='stage_offers',
        verbose_name="Département"
    )
    description = models.TextField(verbose_name="Description")
    missions = models.TextField(verbose_name="Missions")
    required_skills = models.TextField(verbose_name="Compétences requises")
    start_date = models.DateField(verbose_name="Date de début")
    duration = models.CharField(max_length=50, verbose_name="Durée")
    stage_type = models.CharField(
        max_length=50, 
        choices=STAGE_TYPES, 
        default='initiation',
        verbose_name="Type de stage"
    )
    status = models.CharField(
        max_length=20, 
        choices=OFFER_STATUS, 
        default='draft',
        verbose_name="Statut"
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='stage_offers',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Offre de stage"
        verbose_name_plural = "Offres de stage"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class StageApplication(models.Model):
    """Modèle pour les candidatures aux stages."""
    stage_offer = models.ForeignKey(
        StageOffer, 
        on_delete=models.CASCADE, 
        related_name='applications',
        verbose_name="Offre de stage"
    )
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    cv = models.FileField(upload_to='cvs/', verbose_name="CV")
    motivation_letter = models.FileField(upload_to='motivation_letters/', verbose_name="Lettre de motivation")
    tracking_code = models.CharField(max_length=12, unique=True, editable=False, verbose_name="Code de suivi")
    status = models.CharField(
        max_length=20, 
        choices=APPLICATION_STATUS, 
        default='pending',
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Candidature déposée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    class Meta:
        verbose_name = "Candidature de stage"
        verbose_name_plural = "Candidatures de stage"
        ordering = ['-created_at']

    def __str__(self):
        return f"Candidature de {self.first_name} {self.last_name} pour {self.stage_offer.title}"

    def save(self, *args, **kwargs):
        # Générer un code de suivi unique si c'est une nouvelle candidature
        if not self.tracking_code:
            self.tracking_code = get_random_string(12).upper()
        super().save(*args, **kwargs)
