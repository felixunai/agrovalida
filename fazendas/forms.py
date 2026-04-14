from django import forms
from .models import Fazenda


class FazendaForm(forms.ModelForm):
    class Meta:
        model = Fazenda
        fields = ['nome', 'descricao', 'cidade', 'estado']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Fazenda Santa Rosa'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição opcional'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
