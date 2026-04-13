from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('defensivos', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_lote', models.CharField(db_index=True, max_length=100, verbose_name='número do lote')),
                ('data_fabricacao', models.DateField(verbose_name='data de fabricação')),
                ('data_validade', models.DateField(db_index=True, verbose_name='data de validade')),
                ('quantidade', models.DecimalField(max_digits=12, decimal_places=3, verbose_name='quantidade')),
                ('unidade', models.CharField(choices=[('L', 'Litro'), ('mL', 'Mililitro'), ('kg', 'Quilograma'), ('g', 'Grama')], default='L', max_length=2, verbose_name='unidade')),
                ('fornecedor', models.CharField(blank=True, max_length=200, verbose_name='fornecedor')),
                ('nota_fiscal', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='nota fiscal')),
                ('local_armazenamento', models.CharField(blank=True, max_length=200, verbose_name='local de armazenamento')),
                ('observacoes', models.TextField(blank=True, verbose_name='observações')),
                ('cadastrado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user', verbose_name='cadastrado por')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('defensivo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lotes', to='defensivos.defensivo', verbose_name='defensivo')),
            ],
            options={
                'verbose_name': 'lote',
                'verbose_name_plural': 'lotes',
                'ordering': ['data_validade'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='lote',
            unique_together={('numero_lote', 'defensivo')},
        ),
    ]