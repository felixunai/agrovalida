from django import forms
from django.forms.widgets import Input
from .models import NotaFiscal


class MultipleFileInput(Input):
    """FileInput that accepts multiple files without Django's built-in restriction."""
    input_type = 'file'
    needs_multipart_form = True
    allow_multiple_selected = True


class NotaFiscalUploadForm(forms.Form):
    """
    Multi-file upload form. Accepts one or more XML/PDF files.
    Uses a plain Form (not ModelForm) so Django's FileField.getlist works correctly.
    """
    arquivo = forms.FileField(
        label='Arquivo(s) da Nota Fiscal (XML ou PDF)',
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': '.xml,.pdf',
            'class': 'form-control',
        }),
        help_text='Selecione um ou mais arquivos XML (NF-e) ou PDF.',
    )

    def clean_arquivo(self):
        files = self.files.getlist('arquivo')
        if not files:
            raise forms.ValidationError('Nenhum arquivo selecionado.')
        for f in files:
            ext = f.name.rsplit('.', 1)[-1].lower()
            if ext not in ('xml', 'pdf'):
                raise forms.ValidationError(
                    f'"{f.name}": apenas arquivos XML ou PDF são aceitos.'
                )
        return files


class ItemNotaForm(forms.Form):
    defensivo = forms.IntegerField(widget=forms.HiddenInput())
    numero_lote = forms.CharField(max_length=100, required=False)
    data_fabricacao = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_validade = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    quantidade = forms.DecimalField(max_digits=12, decimal_places=3, required=False)
    unidade = forms.CharField(max_length=10, required=False)
    fornecedor = forms.CharField(max_length=200, required=False)
    local_armazenamento = forms.CharField(max_length=200, required=False)
