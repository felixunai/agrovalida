from django.contrib import admin
from .models import NotaFiscal, ItemNotaFiscal


class ItemNotaFiscalInline(admin.TabularInline):
    model = ItemNotaFiscal
    extra = 0
    readonly_fields = ('descricao', 'codigo_produto', 'ncm', 'quantidade', 'unidade')


@admin.register(NotaFiscal)
class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fornecedor', 'data_emissao', 'tipo', 'processado', 'criado_em')
    list_filter = ('tipo', 'processado')
    search_fields = ('numero', 'fornecedor', 'cnpj_fornecedor')
    inlines = [ItemNotaFiscalInline]