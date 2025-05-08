from django.db import models

class Partenaire(models.Model):
    nom = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partenaires/logos/', blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nom
