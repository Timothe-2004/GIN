from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Créer ou mettre à jour une instance UserProfile lorsque le modèle User est enregistré.
    """
    if created:
        # Créer un profil uniquement si aucun n'existe
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Mettre à jour le profil existant
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
            # Créer un profil si aucun n'existe
            UserProfile.objects.create(user=instance)
