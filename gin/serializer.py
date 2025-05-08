from rest_framework import serializers
from .models import Formation,Service

class FormationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Formation
        fields=('titre','description','date_debut','date_fin','lieu')
    
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Service
        fields=('nom','description')
        

    