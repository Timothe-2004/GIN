from django.db import models
from accounts.models import User, Department
from django.utils.crypto import get_random_string
import uuid

class Utilisateur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    date_naissance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.username


class Formation(models.Model):
    """Modèle représentant une formation proposée."""
    
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    titre = models.CharField(max_length=200)
    description = models.TextField()
    duree = models.CharField(max_length=50)  # Ex: "3 jours", "35 heures"
    prerequis = models.TextField(blank=True)
    objectifs = models.TextField()
    date_session = models.DateField()
    lieu = models.CharField(max_length=200)
    capacite = models.PositiveIntegerField()
    department = models.ForeignKey(
        Department, 
        on_delete=models.CASCADE,
        related_name='formations',
        verbose_name="Département"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='planifiee'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='formations_creees'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ['-date_session']
    
    def __str__(self):
        return self.titre
    
    @property
    def places_disponibles(self):
        """Calcule le nombre de places encore disponibles."""
        inscriptions_validees = self.inscriptions.filter(statut__in=['validee', 'en_attente']).count()
        return max(0, self.capacite - inscriptions_validees)


class Inscription(models.Model):
    """Modèle représentant une inscription à une formation."""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('validee', 'Validée'),
        ('refusee', 'Refusée'),
        ('annulee', 'Annulée'),
    ]
    
    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inscriptions',
        null=True,
        blank=True
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    commentaire = models.TextField(blank=True)
    tracking_code = models.CharField(max_length=12, unique=True, editable=False)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.formation.titre}"
    
    def save(self, *args, **kwargs):
        """Génère un code de suivi unique lors de la création."""
        if not self.tracking_code:
            self.tracking_code = get_random_string(12).upper()
        super().save(*args, **kwargs)


class RechercheFormation(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    terme_recherche = models.CharField(max_length=255)
    date_recherche = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recherche de {self.utilisateur.user.username}: {self.terme_recherche}"
