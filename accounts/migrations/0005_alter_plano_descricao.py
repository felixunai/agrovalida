from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_plano_preco_anual'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plano',
            name='descricao',
            field=models.TextField(blank=True, verbose_name='descrição / benefícios'),
        ),
    ]
