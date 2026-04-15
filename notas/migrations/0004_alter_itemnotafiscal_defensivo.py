from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defensivos', '0005_alter_defensivo_options'),
        ('notas', '0003_notafiscal_tipo_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemnotafiscal',
            name='defensivo',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='itens_nota',
                to='defensivos.defensivo',
                verbose_name='produto cadastrado',
            ),
        ),
    ]
