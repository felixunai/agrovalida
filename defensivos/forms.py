from django import forms
from .models import Defensivo


class DefensivoForm(forms.ModelForm):
    class Meta:
        model = Defensivo
        fields = [
            'nome_comercial', 'principio_ativo', 'classe',
            'classe_toxicologica', 'registro_mapa', 'fabricante',
            'formulacao', 'concentracao', 'ativo',
        ]
        widgets = {
            'nome_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'principio_ativo': forms.TextInput(attrs={'class': 'form-control'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
            'classe_toxicologica': forms.Select(attrs={'class': 'form-select'}),
            'registro_mapa': forms.TextInput(attrs={'class': 'form-control'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'formulacao': forms.TextInput(attrs={'class': 'form-control'}),
            'concentracao': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }