from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile_stripe'),
    ]

    operations = [
        migrations.AddField(
            model_name='plano',
            name='preco_anual',
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10,
                null=True, verbose_name='preço anual (R$)',
            ),
        ),
    ]
