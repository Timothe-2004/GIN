from django.contrib import admin
from .models import Formation, Service
# Register your models here.

@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display=('titre','description','date_debut','date_fin','lieu')
    search_fields=['titre']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display=('nom','description')
    search_fields=['nom']
