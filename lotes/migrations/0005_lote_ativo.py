from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lotes', '0004_lote_fazenda'),
    ]

    operations = [
        migrations.AddField(
            model_name='lote',
            name='ativo',
            field=models.BooleanField(default=True, db_index=True, verbose_name='ativo'),
        ),
    ]
