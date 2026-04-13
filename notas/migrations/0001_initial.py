from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotaFiscal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.FileField(upload_to='notas/', verbose_name='arquivo')),
                ('tipo', models.CharField(choices=[('xml', 'XML (NF-e)'), ('pdf', 'PDF')], max_length=3, verbose_name='tipo')),
                ('numero', models.CharField(blank=True, db_index=True, max_length=50, verbose_name='número')),
                ('data_emissao', models.DateField(blank=True, null=True, verbose_name='data de emissão')),
                ('fornecedor', models.CharField(blank=True, max_length=300, verbose_name='fornecedor')),
                ('cnpj_fornecedor', models.CharField(blank=True, max_length=18, verbose_name='CNPJ fornecedor')),
                ('texto_extraido', models.TextField(blank=True, verbose_name='texto extraído')),
                ('processado', models.BooleanField(default=False, verbose_name='processado')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('cadastrado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user', verbose_name='cadastrado por')),
            ],
            options={
                'verbose_name': 'nota fiscal',
                'verbose_name_plural': 'notas fiscais',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='ItemNotaFiscal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.CharField(max_length=500, verbose_name='descrição')),
                ('codigo_produto', models.CharField(blank=True, max_length=50, verbose_name='código do produto')),
                ('ncm', models.CharField(blank=True, max_length=8, verbose_name='NCM')),
                ('quantidade', models.DecimalField(decimal_places=3, default=1, max_digits=12, verbose_name='quantidade')),
                ('unidade', models.CharField(blank=True, max_length=10, verbose_name='unidade')),
                ('valor_unitario', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='valor unitário')),
                ('valor_total', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='valor total')),
                ('lote_importado', models.BooleanField(default=False, verbose_name='lote importado')),
                ('nota', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='notas.notafiscal')),
            ],
            options={
                'verbose_name': 'item da nota fiscal',
                'verbose_name_plural': 'itens da nota fiscal',
            },
        ),
    ]