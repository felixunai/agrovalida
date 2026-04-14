from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0002_lote_unidade_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lote',
            name='data_fabricacao',
            field=models.DateField(blank=True, null=True, verbose_name='data de fabricação'),
        ),
    ]
