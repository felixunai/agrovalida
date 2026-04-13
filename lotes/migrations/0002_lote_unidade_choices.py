from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lote',
            name='unidade',
            field=models.CharField(choices=[('L', 'Litro'), ('mL', 'Mililitro'), ('kg', 'Quilograma'), ('g', 'Grama'), ('BAG', 'Bag'), ('un', 'Unidade')], default='L', max_length=3, verbose_name='unidade'),
        ),
    ]