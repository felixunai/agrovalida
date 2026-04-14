from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_seed_planos'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Stripe customer ID'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Stripe subscription ID'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='periodo_plano',
            field=models.CharField(
                blank=True, max_length=10,
                choices=[('mensal', 'Mensal — R$ 399/mês'), ('anual', 'Anual — R$ 4.000/ano')],
                verbose_name='período',
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='data_fim_plano',
            field=models.DateField(blank=True, null=True, verbose_name='plano válido até'),
        ),
    ]
