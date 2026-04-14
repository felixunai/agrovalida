from django.db import models
from django.conf import settings
from django.urls import reverse

ESTADOS_BR = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
]


class Fazenda(models.Model):
    nome = models.CharField('nome da fazenda/propriedade', max_length=200, db_index=True)
    descricao = models.CharField('descrição', max_length=300, blank=True)
    cidade = models.CharField('cidade', max_length=100, blank=True)
    estado = models.CharField('estado', max_length=2, choices=ESTADOS_BR, blank=True)
    cadastrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='fazendas', verbose_name='cadastrado por',
    )
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'fazenda'
        verbose_name_plural = 'fazendas'

    def __str__(self):
        partes = [self.nome]
        if self.cidade:
            partes.append(self.cidade)
        if self.estado:
            partes.append(self.estado)
        return ' — '.join(partes)

    def get_absolute_url(self):
        return reverse('fazendas:detail', kwargs={'pk': self.pk})
