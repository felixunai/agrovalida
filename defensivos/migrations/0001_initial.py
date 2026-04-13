from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Defensivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_comercial', models.CharField(db_index=True, max_length=200, verbose_name='nome comercial')),
                ('principio_ativo', models.CharField(blank=True, max_length=300, verbose_name='princípio ativo')),
                ('classe', models.CharField(choices=[('inseticida', 'Inseticida'), ('herbicida', 'Herbicida'), ('fungicida', 'Fungicida'), ('acaricida', 'Acaricida'), ('adjuvante', 'Adjuvante'), ('regulador', 'Regulador de Crescimento'), ('biologico', 'Biológico'), ('outro', 'Outro')], default='outro', max_length=20, verbose_name='classe')),
                ('classe_toxicologica', models.CharField(blank=True, choices=[('1', 'I - Extremamente Tóxico'), ('2', 'II - Altamente Tóxico'), ('3', 'III - Medianamente Tóxico'), ('4', 'IV - Pouco Tóxico')], max_length=1, verbose_name='classe toxicológica')),
                ('registro_mapa', models.CharField(blank=True, db_index=True, max_length=50, verbose_name='registro MAPA')),
                ('fabricante', models.CharField(blank=True, max_length=200, verbose_name='fabricante')),
                ('formulacao', models.CharField(blank=True, max_length=100, verbose_name='formulação')),
                ('concentracao', models.CharField(blank=True, max_length=100, verbose_name='concentração')),
                ('ativo', models.BooleanField(default=True, verbose_name='ativo')),
            ],
            options={
                'verbose_name': 'defensivo',
                'verbose_name_plural': 'defensivos',
                'ordering': ['nome_comercial'],
            },
        ),
    ]