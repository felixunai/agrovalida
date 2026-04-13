from django.contrib import admin
from .models import Lote


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('numero_lote', 'defensivo', 'data_validade', 'quantidade', 'unidade', 'fornecedor')
    list_filter = ('defensivo__classe', 'unidade', 'data_validade')
    search_fields = ('numero_lote', 'defensivo__nome_comercial', 'nota_fiscal', 'fornecedor')
    date_hierarchy = 'data_validade'