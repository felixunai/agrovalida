from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Fazenda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(db_index=True, max_length=200, verbose_name='nome da fazenda/propriedade')),
                ('descricao', models.CharField(blank=True, max_length=300, verbose_name='descrição')),
                ('cidade', models.CharField(blank=True, max_length=100, verbose_name='cidade')),
                ('estado', models.CharField(blank=True, choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')], max_length=2, verbose_name='estado')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('cadastrado_por', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fazendas', to=settings.AUTH_USER_MODEL, verbose_name='cadastrado por')),
            ],
            options={
                'verbose_name': 'fazenda',
                'verbose_name_plural': 'fazendas',
                'ordering': ['nome'],
            },
        ),
    ]
