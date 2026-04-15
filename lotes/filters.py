import django_filters
from django import forms
from django.utils import timezone
from .models import Lote


class LoteFilter(django_filters.FilterSet):
    STATUS_CHOICES = (
        ('vencido', 'Vencido'),
        ('vencendo', 'Vencendo em breve'),
        ('vigente', 'Vigente'),
    )

    defensivo__nome_comercial = django_filters.CharFilter(
        lookup_expr='icontains', label='Produto',
        widget=forms.TextInput(attrs={'placeholder': 'Buscar produto…', 'class': 'form-control form-control-sm'}),
    )
    numero_lote = django_filters.CharFilter(
        lookup_expr='icontains', label='Nº do lote',
        widget=forms.TextInput(attrs={'placeholder': 'Nº do lote…', 'class': 'form-control form-control-sm'}),
    )
    fornecedor = django_filters.CharFilter(
        lookup_expr='icontains', label='Fornecedor',
        widget=forms.TextInput(attrs={'placeholder': 'Fornecedor…', 'class': 'form-control form-control-sm'}),
    )
    status_vencimento = django_filters.ChoiceFilter(
        choices=[('', 'Todos os status')] + list(STATUS_CHOICES),
        method='filter_status', label='Status',
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    data_validade_inicio = django_filters.DateFilter(
        field_name='data_validade', lookup_expr='gte', label='Validade de',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
    )
    data_validade_fim = django_filters.DateFilter(
        field_name='data_validade', lookup_expr='lte', label='Validade até',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
    )
    fazenda = django_filters.ModelChoiceFilter(
        queryset=None, label='Fazenda',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
        empty_label='Todas as fazendas',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.request if hasattr(self, 'request') else None
        if request and hasattr(request, 'user'):
            from fazendas.models import Fazenda
            self.filters['fazenda'].queryset = Fazenda.objects.filter(
                cadastrado_por=request.user
            )
        else:
            from fazendas.models import Fazenda
            self.filters['fazenda'].queryset = Fazenda.objects.none()

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