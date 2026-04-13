from django.db import models
from django.conf import settings


class NotaFiscal(models.Model):
    TIPO_CHOICES = [
        ('xml', 'XML (NF-e)'),
        ('pdf', 'PDF'),
    ]

    arquivo = models.FileField('arquivo', upload_to='notas/')
    tipo = models.CharField('tipo', max_length=3, choices=TIPO_CHOICES)
    numero = models.CharField('número', max_length=50, blank=True, db_index=True)
    data_emissao = models.DateField('data de emissão', null=True, blank=True)
    fornecedor = models.CharField('fornecedor', max_length=300, blank=True)
    cnpj_fornecedor = models.CharField('CNPJ fornecedor', max_length=18, blank=True)
    texto_extraido = models.TextField('texto extraído', blank=True)
    processado = models.BooleanField('processado', default=False)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    cadastrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='cadastrado por',
    )

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'nota fiscal'
        verbose_name_plural = 'notas fiscais'

    def __str__(self):
        return f'NF {self.numero or "sem número"} - {self.fornecedor or "fornecedor não identificado"}'


class ItemNotaFiscal(models.Model):
    nota = models.ForeignKey(NotaFiscal, on_delete=models.CASCADE, related_name='itens')
    descricao = models.CharField('descrição', max_length=500)
    codigo_produto = models.CharField('código do produto', max_length=50, blank=True)
    ncm = models.CharField('NCM', max_length=8, blank=True)
    quantidade = models.DecimalField('quantidade', max_digits=12, decimal_places=3, default=1)
    unidade = models.CharField('unidade', max_length=10, blank=True)
    valor_unitario = models.DecimalField('valor unitário', max_digits=12, decimal_places=2, null=True, blank=True)
    valor_total = models.DecimalField('valor total', max_digits=12, decimal_places=2, null=True, blank=True)
    lote_importado = models.BooleanField('lote importado', default=False)

    class Meta:
        verbose_name = 'item da nota fiscal'
        verbose_name_plural = 'itens da nota fiscal'

    def __str__(self):
        return f'{self.descricao} ({self.quantidade} {self.unidade})'