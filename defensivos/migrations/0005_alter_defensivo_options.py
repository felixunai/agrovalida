from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('defensivos', '0004_alter_defensivo_classe'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='defensivo',
            options={
                'ordering': ['nome_comercial'],
                'verbose_name': 'produto',
                'verbose_name_plural': 'produtos',
            },
        ),
    ]
