from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defensivos', '0005_alter_defensivo_options'),
        ('lotes', '0005_lote_ativo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lote',
            name='defensivo',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='lotes',
                to='defensivos.defensivo',
                verbose_name='produto',
            ),
        ),
    ]
