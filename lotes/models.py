from django.db import models
from django.conf import settings
from django.urls import reverse


class StatusVencimento(models.TextChoices):
    VIGENTE = 'vigente', 'Vigente'
    VENCENDO = 'vencendo', 'Vencendo em breve'
    VENCIDO = 'vencido', 'Vencido'


class UnidadeMedida(models.TextChoices):
    LITRO = 'L', 'Litro'
    MILILITRO = 'mL', 'Mililitro'
    QUILOGRAMA = 'kg', 'Quilograma'
    GRAMA = 'g', 'Grama'
    BAG = 'BAG', 'Bag'
    UNIDADE = 'un', 'Unidade'


class Lote(models.Model):
    defensivo = models.ForeignKey(
        'defensivos.Defensivo', on_delete=models.PROTECT, related_name='lotes',
        verbose_name='produto',
    )
    numero_lote = models.CharField('número do lote', max_length=100, db_index=True)
    data_fabricacao = models.DateField('data de fabricação', blank=True, null=True)
    data_validade = models.DateField('data de validade', db_index=True)
    quantidade = models.DecimalField('quantidade', max_digits=12, decimal_places=3)
    unidade = models.CharField(
        'unidade', max_length=3, choices=UnidadeMedida.choices, default=UnidadeMedida.LITRO
    )
    fornecedor = models.CharField('fornecedor', max_length=200, blank=True)
    nota_fiscal = models.CharField('nota fiscal', max_length=100, blank=True, db_index=True)
    local_armazenamento = models.CharField('local de armazenamento', max_length=200, blank=True)
    observacoes = models.TextField('observações', blank=True)
    fazenda = models.ForeignKey(
        'fazendas.Fazenda', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='lotes', verbose_name='fazenda',
    )
    cadastrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='cadastrado por',
    )
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['data_validade']
        verbose_name = 'lote'
        verbose_name_plural = 'lotes'
        unique_together = ['numero_lote', 'defensivo']

    def __str__(self):
        return f'{self.numero_lote} - {self.defensivo.nome_comercial}'

    def get_absolute_url(self):
        return reverse('lotes:detail', kwargs={'pk': self.pk})

    @property
    def status_vencimento(self):
        from django.utils import timezone
        hoje = timezone.now().date()
        dias_limite = getattr(settings, 'ALERTA_DIAS_VENCIMENTO', 90)
        if self.data_validade < hoje:
            return StatusVencimento.VENCIDO
        elif (self.data_validade - hoje).days <= dias_limite:
            return StatusVencimento.VENCENDO
        return StatusVencimento.VIGENTE

    @property
    def dias_para_vencer(self):
        from django.utils import timezone
        return (self.data_validade - timezone.now().date()).days