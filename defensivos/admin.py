from django.contrib import admin
from .models import Defensivo


@admin.register(Defensivo)
class DefensivoAdmin(admin.ModelAdmin):
    list_display = ('nome_comercial', 'classe', 'registro_mapa', 'fabricante', 'ativo')
    list_filter = ('classe', 'classe_toxicologica', 'ativo')
    search_fields = ('nome_comercial', 'principio_ativo', 'registro_mapa', 'fabricante')