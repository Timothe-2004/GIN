from django.db import models

class Realisation(models.Model):
    projet = models.CharField(max_length=255)
    entreprise = models.CharField(max_length=255)
    avis = models.TextField()
    type_personne = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.projet} - {self.entreprise}"
