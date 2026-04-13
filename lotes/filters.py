import django_filters
from django.utils import timezone
from .models import Lote


class LoteFilter(django_filters.FilterSet):
    STATUS_CHOICES = (
        ('vencido', 'Vencido'),
        ('vencendo', 'Vencendo em breve'),
        ('vigente', 'Vigente'),
    )

    defensivo__nome_comercial = django_filters.CharFilter(
        lookup_expr='icontains', label='Nome do produto'
    )
    numero_lote = django_filters.CharFilter(lookup_expr='icontains', label='Nº do lote')
    fornecedor = django_filters.CharFilter(lookup_expr='icontains')
    status_vencimento = django_filters.ChoiceFilter(
        choices=STATUS_CHOICES, method='filter_status', label='Status'
    )
    data_validade_inicio = django_filters.DateFilter(
        field_name='data_validade', lookup_expr='gte', label='Validade a partir de'
    )
    data_validade_fim = django_filters.DateFilter(
        field_name='data_validade', lookup_expr='lte', label='Validade até'
    )

    class Meta:
        model = Lote
        fields = []

    def filter_status(self, queryset, name, value):
        hoje = timezone.now().date()
        from django.conf import settings
        dias = getattr(settings, 'ALERTA_DIAS_VENCIMENTO', 90)
        if value == 'vencido':
            return queryset.filter(data_validade__lt=hoje)
        elif value == 'vencendo':
            limite = hoje + timezone.timedelta(days=dias)
            return queryset.filter(data_validade__gte=hoje, data_validade__lte=limite)
        elif value == 'vigente':
            limite = hoje + timezone.timedelta(days=dias)
            return queryset.filter(data_validade__gt=limite)
        return queryset