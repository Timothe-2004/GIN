from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'sujet', 'statut', 'date_creation')
    search_fields = ('nom', 'prenom', 'email', 'sujet')
    list_filter = ('statut', 'date_creation')