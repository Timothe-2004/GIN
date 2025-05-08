from django.db import models

# Create your models here.

#Modèle Formation
class Formation(models.Model):
    titre=models.CharField(max_length=100)
    description=models.TextField()
    date_debut=models.DateField()
    date_fin=models.DateField(null=True,blank=True)
    lieu=models.CharField(max_length=100)
    
    def __str__(self):
        return self.titre
    
#Modèle Service
class Service(models.Model):
    nom=models.CharField(max_length=100)
    description=models.TextField()
    
    def __str__(self):
        return self.nom
    

    