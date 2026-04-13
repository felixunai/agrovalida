from django import forms
from .models import NotaFiscal


class NotaFiscalUploadForm(forms.ModelForm):
    class Meta:
        model = NotaFiscal
        fields = ['arquivo']

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            ext = arquivo.name.rsplit('.', 1)[-1].lower()
            if ext not in ('xml', 'pdf'):
                raise forms.ValidationError('Apenas arquivos XML ou PDF são aceitos.')
        return arquivo


class ItemNotaForm(forms.Form):
    defensivo = forms.IntegerField(widget=forms.HiddenInput())
    numero_lote = forms.CharField(max_length=100, required=False)
    data_fabricacao = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_validade = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    quantidade = forms.DecimalField(max_digits=12, decimal_places=3, required=False)
    unidade = forms.CharField(max_length=10, required=False)
    fornecedor = forms.CharField(max_length=200, required=False)
    local_armazenamento = forms.CharField(max_length=200, required=False)