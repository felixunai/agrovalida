import django_filters
from .models import Defensivo


class DefensivoFilter(django_filters.FilterSet):
    nome_comercial = django_filters.CharFilter(lookup_expr='icontains', label='Nome')
    classe = django_filters.ChoiceFilter(choices=Defensivo.ClasseDefensivo.choices)
    fabricante = django_filters.CharFilter(lookup_expr='icontains', label='Fabricante')
    ativo = django_filters.BooleanFilter(label='Ativo')

    class Meta:
        model = Defensivo
        fields = ['nome_comercial', 'classe', 'fabricante', 'ativo']