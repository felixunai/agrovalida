import django_filters
from django import forms
from .models import Defensivo, ClasseDefensivo


class DefensivoFilter(django_filters.FilterSet):
    nome_comercial = django_filters.CharFilter(
        lookup_expr='icontains', label='Nome comercial',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar por nome…', 'class': 'form-control form-control-sm'}),
    )
    classe = django_filters.ChoiceFilter(
        choices=[('', 'Todas as classes')] + list(ClasseDefensivo.choices),
        label='Classe',
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    fabricante = django_filters.CharFilter(
        lookup_expr='icontains', label='Fabricante',
        widget=forms.TextInput(attrs={'placeholder': 'Fabricante…', 'class': 'form-control form-control-sm'}),
    )
    ativo = django_filters.ChoiceFilter(
        choices=[('', 'Ativos e inativos'), ('true', 'Somente ativos'), ('false', 'Somente inativos')],
        label='Situação',
        empty_label=None,
        method='filter_ativo',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )

    class Meta:
        model = Defensivo
        fields = ['nome_comercial', 'classe', 'fabricante']

    def filter_ativo(self, queryset, name, value):
        if value == 'true':
            return queryset.filter(ativo=True)
        if value == 'false':
            return queryset.filter(ativo=False)
        return queryset