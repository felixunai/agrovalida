from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0003_lote_data_fabricacao_optional'),
        ('fazendas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lote',
            name='fazenda',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lotes',
                to='fazendas.fazenda',
                verbose_name='fazenda',
            ),
        ),
    ]
