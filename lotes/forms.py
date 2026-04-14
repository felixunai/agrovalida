from django import forms
from .models import Lote


class LoteForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            from defensivos.models import Defensivo
            from fazendas.models import Fazenda
            self.fields['defensivo'].queryset = Defensivo.objects.filter(
                cadastrado_por=user, ativo=True
            ).order_by('nome_comercial')
            self.fields['fazenda'].queryset = Fazenda.objects.filter(
                cadastrado_por=user
            ).order_by('nome')

    class Meta:
        model = Lote
        fields = [
            'defensivo', 'fazenda', 'numero_lote', 'data_fabricacao', 'data_validade',
            'quantidade', 'unidade', 'fornecedor', 'nota_fiscal',
            'local_armazenamento', 'observacoes',
        ]
        widgets = {
            'defensivo': forms.Select(attrs={'class': 'form-select'}),
            'numero_lote': forms.TextInput(attrs={'class': 'form-control'}),
            'data_fabricacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_validade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'fornecedor': forms.TextInput(attrs={'class': 'form-control'}),
            'nota_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
            'local_armazenamento': forms.TextInput(attrs={'class': 'form-control'}),
            'fazenda': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned = super().clean()
        fab = cleaned.get('data_fabricacao')
        val = cleaned.get('data_validade')
        if fab and val and val < fab:
            self.add_error('data_validade', 'Data de validade não pode ser anterior à fabricação.')
        return cleaned