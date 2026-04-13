from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notas', '0002_itemnotafiscal_lote_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notafiscal',
            name='tipo',
            field=models.CharField(choices=[('xml', 'XML (NF-e)'), ('pdf', 'PDF')], default='xml', max_length=3, verbose_name='tipo'),
        ),
    ]