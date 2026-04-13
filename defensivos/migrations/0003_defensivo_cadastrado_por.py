from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('defensivos', '0002_defensivo_classe_semente'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='defensivo',
            name='cadastrado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user', verbose_name='cadastrado por'),
        ),
    ]