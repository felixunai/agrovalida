from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defensivos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defensivo',
            name='classe',
            field=models.CharField(choices=[('inseticida', 'Inseticida'), ('herbicida', 'Herbicida'), ('fungicida', 'Fungicida'), ('acaricida', 'Acaricida'), ('adjuvante', 'Adjuvante'), ('regulador', 'Regulador de Crescimento'), ('biologico', 'Biológico'), ('semente', 'Semente'), ('outro', 'Outro')], default='outro', max_length=20, verbose_name='classe'),
        ),
    ]