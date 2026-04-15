from django import forms
from django.forms.widgets import Input
from .models import NotaFiscal


class MultipleFileInput(Input):
    """FileInput that accepts multiple files without Django's built-in restriction."""
    input_type = 'file'
    needs_multipart_form = True
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        # FileField expects a single file object for required-field validation;
        # clean_arquivo() fetches the full list via self.files.getlist().
        return files.get(name)

    def value_omitted_from_data(self, data, files, name):
        return name not in files


class NotaFiscalUploadForm(forms.Form):
    """
    Multi-file upload form. Accepts one or more XML files (NF-e).
    Uses a plain Form (not ModelForm) so Django's FileField.getlist works correctly.
    """
    arquivo = forms.FileField(
        label='Arquivo(s) XML da Nota Fiscal',
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'accept': '.xml',
            'class': 'form-control',
        }),
        help_text='Selecione um ou mais arquivos XML (NF-e).',
    )

    def clean_arquivo(self):
        files = self.files.getlist('arquivo')
        if not files:
            raise forms.ValidationError('Nenhum arquivo selecionado.')
        for f in files:
            ext = f.name.rsplit('.', 1)[-1].lower()
            if ext != 'xml':
                raise forms.ValidationError(
                    f'"{f.name}": apenas arquivos XML são aceitos. '
                    'Solicite o XML ao seu fornecedor.'
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
