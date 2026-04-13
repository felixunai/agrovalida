from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='nome')),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='preço mensal')),
                ('descricao', models.TextField(blank=True, verbose_name='descrição')),
                ('ativo', models.BooleanField(default=True, verbose_name='ativo')),
            ],
            options={
                'verbose_name': 'plano',
                'verbose_name_plural': 'planos',
                'ordering': ['preco'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefone', models.CharField(blank=True, max_length=20, verbose_name='telefone')),
                ('plano_ativo', models.BooleanField(default=False, verbose_name='plano ativo')),
                ('ativo', models.BooleanField(default=True, verbose_name='ativo')),
                ('plano', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.plano', verbose_name='plano')),
                ('user', models.OneToOneField(on_delete=django.db.models.CASCADE, related_name='profile', to='auth.user', verbose_name='user')),
            ],
            options={
                'verbose_name': 'perfil',
                'verbose_name_plural': 'perfis',
            },
        ),
    ]