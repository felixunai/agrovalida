from django.db import migrations


def create_planos(apps, schema_editor):
    Plano = apps.get_model('accounts', 'Plano')
    Plano.objects.get_or_create(
        nome='Gratuito',
        defaults={'preco': 0, 'descricao': 'Acesso básico ao sistema', 'ativo': True},
    )
    Plano.objects.get_or_create(
        nome='Profissional',
        defaults={'preco': 500, 'descricao': 'Acesso completo ao sistema com todas as funcionalidades', 'ativo': True},
    )


def reverse_planos(apps, schema_editor):
    Plano = apps.get_model('accounts', 'Plano')
    Plano.objects.filter(nome__in=['Gratuito', 'Profissional']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_planos, reverse_planos),
    ]