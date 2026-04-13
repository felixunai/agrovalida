from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notas', '0001_initial'),
        ('defensivos', '0001_initial'),
        ('lotes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='status_importacao',
            field=models.CharField(choices=[('pendente', 'Pendente'), ('processado', 'Processado'), ('importado', 'Importado')], default='pendente', max_length=10, verbose_name='status importação'),
        ),
        migrations.AddField(
            model_name='itemnotafiscal',
            name='numero_lote',
            field=models.CharField(blank=True, max_length=100, verbose_name='número do lote'),
        ),
        migrations.AddField(
            model_name='itemnotafiscal',
            name='data_fabricacao',
            field=models.DateField(blank=True, null=True, verbose_name='data de fabricação'),
        ),
        migrations.AddField(
            model_name='itemnotafiscal',
            name='data_validade',
            field=models.DateField(blank=True, null=True, verbose_name='data de validade'),
        ),
        migrations.AddField(
            model_name='itemnotafiscal',
            name='defensivo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='itens_nota', to='defensivos.defensivo', verbose_name='defensivo cadastrado'),
        ),
        migrations.AddField(
            model_name='itemnotafiscal',
            name='lote',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item_nota', to='lotes.lote', verbose_name='lote cadastrado'),
        ),
        migrations.RemoveField(
            model_name='itemnotafiscal',
            name='lote_importado',
        ),
    ]