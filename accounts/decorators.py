from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def plano_requerido(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if getattr(request, 'is_pro', False):
            return view_func(request, *args, **kwargs)
        messages.warning(request, 'Esta funcionalidade está disponível apenas no plano Profissional. Atualize seu plano para acessar.')
        return redirect('accounts:upgrade')
    return _wrapped_view


def limite_alcancado(tipo):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser or getattr(request, 'is_pro', False):
                return view_func(request, *args, **kwargs)

            limits = getattr(request, 'plan_limits', {})

            if tipo == 'defensivo':
                from defensivos.models import Defensivo
                count = Defensivo.objects.filter(cadastrado_por=request.user, ativo=True).count()
                max_val = limits.get('max_defensivos')
                if max_val and count >= max_val:
                    messages.warning(request, f'Você atingiu o limite de {max_val} produtos no plano Gratuito. Atualize para o Profissional para cadastrar mais.')
                    return redirect('accounts:upgrade')

            elif tipo == 'lote':
                from lotes.models import Lote
                count = Lote.objects.filter(cadastrado_por=request.user).count()
                max_val = limits.get('max_lotes')
                if max_val and count >= max_val:
                    messages.warning(request, f'Você atingiu o limite de {max_val} lotes no plano Gratuito. Atualize para o Profissional para cadastrar mais.')
                    return redirect('accounts:upgrade')

            elif tipo == 'nota':
                from notas.models import NotaFiscal
                count = NotaFiscal.objects.filter(cadastrado_por=request.user).count()
                max_val = limits.get('max_notas')
                if max_val and count >= max_val:
                    messages.warning(request, f'Você atingiu o limite de {max_val} notas fiscais no plano Gratuito. Atualize para o Profissional para importar mais.')
                    return redirect('accounts:upgrade')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator