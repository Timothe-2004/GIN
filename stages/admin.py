from django.contrib import admin
from .models import StageOffer, StageApplication

@admin.register(StageOffer)
class StageOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('status', 'created_at')

@admin.register(StageApplication)
class StageApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('status', 'created_at')

# Suppression des enregistrements dans l'admin pour DemandeStage et DomaineStage
# Ces modèles ne sont plus nécessaires.

# Les autres enregistrements restent inchangés.
