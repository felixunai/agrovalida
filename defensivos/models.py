from django.db import models
from django.conf import settings
from django.urls import reverse


class ClasseDefensivo(models.TextChoices):
    INSETICIDA = 'inseticida', 'Inseticida'
    HERBICIDA = 'herbicida', 'Herbicida'
    FUNGICIDA = 'fungicida', 'Fungicida'
    ACARICIDA = 'acaricida', 'Acaricida'
    ADJUVANTE = 'adjuvante', 'Adjuvante'
    REGULADOR = 'regulador', 'Regulador de Crescimento'
    BIOLOGICO = 'biologico', 'Biológico'
    SEMENTE = 'semente', 'Semente'
    OUTRO = 'outro', 'Outro'


class ClasseToxicologica(models.TextChoices):
    I_EXTREMAMENTE = '1', 'I - Extremamente Tóxico'
    II_ALTAMENTE = '2', 'II - Altamente Tóxico'
    III_MEDIANAMENTE = '3', 'III - Medianamente Tóxico'
    IV_POUCO = '4', 'IV - Pouco Tóxico'


class Defensivo(models.Model):
    nome_comercial = models.CharField('nome comercial', max_length=200, db_index=True)
    principio_ativo = models.CharField('princípio ativo', max_length=300, blank=True)
    classe = models.CharField(
        'classe', max_length=20, choices=ClasseDefensivo.choices, default=ClasseDefensivo.OUTRO
    )
    classe_toxicologica = models.CharField(
        'classe toxicológica', max_length=1, choices=ClasseToxicologica.choices, blank=True
    )
    registro_mapa = models.CharField('registro MAPA', max_length=50, blank=True, db_index=True)
    fabricante = models.CharField('fabricante', max_length=200, blank=True)
    formulacao = models.CharField('formulação', max_length=100, blank=True)
    concentracao = models.CharField('concentração', max_length=100, blank=True)
    ativo = models.BooleanField('ativo', default=True)
    cadastrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='cadastrado por',
    )

    class Meta:
        ordering = ['nome_comercial']
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'

    def __str__(self):
        return self.nome_comercial

    def get_absolute_url(self):
        return reverse('defensivos:detail', kwargs={'pk': self.pk})