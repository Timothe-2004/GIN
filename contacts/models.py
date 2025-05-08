from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    """Modèle représentant un message envoyé via le formulaire de contact."""
    
    STATUT_CHOICES = [
        ('non_lu', 'Non lu'),
        ('en_cours', 'En cours de traitement'),
        ('traite', 'Traité'),
        ('archive', 'Archivé'),
    ]
    
    nom = models.CharField(_('nom'), max_length=100)
    prenom = models.CharField(_('prénom'), max_length=100)
    email = models.EmailField(_('email'))
    telephone = models.CharField(_('téléphone'), max_length=20, blank=True)
    sujet = models.CharField(_('sujet'), max_length=200)
    message = models.TextField(_('message'))
    departement_destinataire = models.ForeignKey(
        'accounts.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='messages_recus',
        verbose_name=_('département destinataire')
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUT_CHOICES,
        default='non_lu'
    )
    date_creation = models.DateTimeField(_('date de création'), auto_now_add=True)
    date_modification = models.DateTimeField(_('date de modification'), auto_now=True)
    
    class Meta:
        verbose_name = _('message de contact')
        verbose_name_plural = _('messages de contact')
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.sujet}"


class ContactReponse(models.Model):
    """Modèle représentant une réponse à un message de contact."""
    
    message_original = models.ForeignKey(
        ContactMessage,
        on_delete=models.CASCADE,
        related_name='reponses',
        verbose_name=_('message original')
    )
    reponse = models.TextField(_('réponse'))
    repondant = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reponses_contact',
        verbose_name=_('répondant')
    )
    date_reponse = models.DateTimeField(_('date de réponse'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('réponse à un contact')
        verbose_name_plural = _('réponses aux contacts')
        ordering = ['-date_reponse']
    
    def __str__(self):
        return f"Réponse à {self.message_original}"