from django.db import models
from django.conf import settings


class Plano(models.Model):
    nome = models.CharField('nome', max_length=100)
    preco = models.DecimalField('preço mensal (R$)', max_digits=10, decimal_places=2)
    preco_anual = models.DecimalField('preço anual (R$)', max_digits=10, decimal_places=2, null=True, blank=True)
    descricao = models.TextField('descrição / benefícios', blank=True)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        ordering = ['preco']
        verbose_name = 'plano'
        verbose_name_plural = 'planos'

    def __str__(self):
        return f'{self.nome} - R$ {self.preco:.2f}/mês'


PERIODO_CHOICES = [
    ('mensal', 'Mensal — R$ 399/mês'),
    ('anual', 'Anual — R$ 4.000/ano'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    telefone = models.CharField('telefone', max_length=20, blank=True)
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='plano')
    plano_ativo = models.BooleanField('plano ativo', default=False)
    ativo = models.BooleanField('ativo', default=True)
    # Stripe
    stripe_customer_id = models.CharField('Stripe customer ID', max_length=100, blank=True)
    stripe_subscription_id = models.CharField('Stripe subscription ID', max_length=100, blank=True)
    periodo_plano = models.CharField('período', max_length=10, choices=PERIODO_CHOICES, blank=True)
    data_fim_plano = models.DateField('plano válido até', null=True, blank=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'

    def __str__(self):
        return f'{self.user.username} - {self.plano or "Sem plano"}'