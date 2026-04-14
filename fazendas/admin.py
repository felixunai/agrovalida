from django.contrib import admin
from .models import Fazenda

@admin.register(Fazenda)
class FazendaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cidade', 'estado', 'cadastrado_por']
    search_fields = ['nome', 'cidade']
