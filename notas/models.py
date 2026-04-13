from django.db import models
from django.conf import settings


class NotaFiscal(models.Model):
    TIPO_CHOICES = [
        ('xml', 'XML (NF-e)'),
        ('pdf', 'PDF'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processado', 'Processado'),
        ('importado', 'Importado'),
    ]

    arquivo = models.FileField('arquivo', upload_to='notas/')
    tipo = models.CharField('tipo', max_length=3, choices=TIPO_CHOICES, default='xml')
    numero = models.CharField('número', max_length=50, blank=True, db_index=True)
    data_emissao = models.DateField('data de emissão', null=True, blank=True)
    fornecedor = models.CharField('fornecedor', max_length=300, blank=True)
    cnpj_fornecedor = models.CharField('CNPJ fornecedor', max_length=18, blank=True)
    texto_extraido = models.TextField('texto extraído', blank=True)
    processado = models.BooleanField('processado', default=False)
    status_importacao = models.CharField(
        'status importação', max_length=10, choices=STATUS_CHOICES, default='pendente'
    )
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
    numero_lote = models.CharField('número do lote', max_length=100, blank=True)
    data_fabricacao = models.DateField('data de fabricação', null=True, blank=True)
    data_validade = models.DateField('data de validade', null=True, blank=True)
    defensivo = models.ForeignKey(
        'defensivos.Defensivo', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='itens_nota', verbose_name='produto cadastrado',
    )
    lote = models.ForeignKey(
        'lotes.Lote', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='item_nota', verbose_name='lote cadastrado',
    )

    class Meta:
        verbose_name = 'item da nota fiscal'
        verbose_name_plural = 'itens da nota fiscal'

    def __str__(self):
        return f'{self.descricao} ({self.quantidade} {self.unidade})'