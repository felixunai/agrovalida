from django.shortcuts import redirect
from django.urls import reverse
from .models import UserProfile


PLANO_GRATUITO_LIMITS = {
    'max_defensivos': 5,
    'max_lotes': 10,
    'max_notas': 3,
    'relatorios': False,
    'importacao_nfe': True,
}


PLANO_PRO_LIMITS = {
    'max_defensivos': None,
    'max_lotes': None,
    'max_notas': None,
    'relatorios': True,
    'importacao_nfe': True,
}


def get_plan_limits(user):
    if not user.is_authenticated:
        return PLANO_GRATUITO_LIMITS
    try:
        profile = user.profile
        if user.is_superuser:
            return PLANO_PRO_LIMITS
        if profile.plano_ativo and profile.plano and profile.plano.nome == 'Profissional':
            return PLANO_PRO_LIMITS
    except UserProfile.DoesNotExist:
        pass
    return PLANO_GRATUITO_LIMITS


def is_pro_user(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        profile = user.profile
        return profile.plano_ativo and profile.plano and profile.plano.nome == 'Profissional'
    except UserProfile.DoesNotExist:
        return False


class PlanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.plan_limits = get_plan_limits(request.user)
            request.is_pro = is_pro_user(request.user)
        else:
            request.plan_limits = PLANO_GRATUITO_LIMITS
            request.is_pro = False
        return self.get_response(request)