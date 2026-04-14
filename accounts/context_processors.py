from .models import Plano


def plan_context(request):
    if not request.user.is_authenticated:
        return {'is_pro': False, 'plan_limits': {}, 'planos': Plano.objects.filter(ativo=True)}

    is_pro = getattr(request, 'is_pro', False)
    plan_limits = getattr(request, 'plan_limits', {})

    try:
        profile = request.user.profile
        plano_nome = str(profile.plano) if profile.plano else 'Gratuito'
    except Exception:
        plano_nome = 'Gratuito'

    return {
        'is_pro': is_pro,
        'plan_limits': plan_limits,
        'plano_nome': plano_nome if not request.user.is_superuser else 'Administrador',
        'planos': Plano.objects.filter(ativo=True),
    }