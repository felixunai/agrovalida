from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
from lotes.models import Lote
from defensivos.models import Defensivo, ClasseDefensivo
from notas.models import NotaFiscal


@login_required
def dashboard(request):
    hoje = timezone.now().date()
    dias_alerta = getattr(settings, 'ALERTA_DIAS_VENCIMENTO', 90)
    limite_alerta = hoje + timezone.timedelta(days=dias_alerta)

    user_lotes = Lote.objects.filter(cadastrado_por=request.user)

    lotes_vencidos = user_lotes.filter(data_validade__lt=hoje).select_related('defensivo')
    lotes_vencendo = user_lotes.filter(
        data_validade__gte=hoje, data_validade__lte=limite_alerta
    ).select_related('defensivo')
    lotes_vigentes = user_lotes.filter(data_validade__gt=limite_alerta).select_related('defensivo')

    total_defensivos = Defensivo.objects.filter(cadastrado_por=request.user, ativo=True).count()
    total_lotes = user_lotes.count()
    total_vencidos = lotes_vencidos.count()
    total_vencendo = lotes_vencendo.count()
    total_vigentes = lotes_vigentes.count()
    notas_pendentes = NotaFiscal.objects.filter(cadastrado_por=request.user, processado=False).count()

    lotes_proximos = (lotes_vencendo | lotes_vencidos).order_by('data_validade')[:20]

    por_classe = user_lotes.values(
        'defensivo__classe'
    ).annotate(
        total=Count('id'),
        vencidos=Count('id', filter=Q(data_validade__lt=hoje)),
        vencendo=Count('id', filter=Q(
            data_validade__gte=hoje, data_validade__lte=limite_alerta
        )),
    ).order_by('-total')

    context = {
        'total_defensivos': total_defensivos,
        'total_lotes': total_lotes,
        'total_vencidos': total_vencidos,
        'total_vencendo': total_vencendo,
        'total_vigentes': total_vigentes,
        'notas_pendentes': notas_pendentes,
        'lotes_proximos': lotes_proximos,
        'por_classe': por_classe,
        'dias_alerta': dias_alerta,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def relatorio_vencimento(request):
    hoje = timezone.now().date()
    dias_alerta = getattr(settings, 'ALERTA_DIAS_VENCIMENTO', 90)
    limite_alerta = hoje + timezone.timedelta(days=dias_alerta)

    status = request.GET.get('status', 'todos')

    lotes = Lote.objects.filter(cadastrado_por=request.user).select_related('defensivo').order_by('data_validade')

    if status == 'vencido':
        lotes = lotes.filter(data_validade__lt=hoje)
    elif status == 'vencendo':
        lotes = lotes.filter(data_validade__gte=hoje, data_validade__lte=limite_alerta)
    elif status == 'vigente':
        lotes = lotes.filter(data_validade__gt=limite_alerta)

    classe = request.GET.get('classe')
    if classe:
        lotes = lotes.filter(defensivo__classe=classe)

    fornecedor = request.GET.get('fornecedor')
    if fornecedor:
        lotes = lotes.filter(fornecedor__icontains=fornecedor)

    context = {
        'lotes': lotes,
        'status': status,
        'classe': classe,
        'fornecedor': fornecedor,
        'classes': ClasseDefensivo.choices,
        'hoje': hoje,
        'dias_alerta': dias_alerta,
    }
    return render(request, 'dashboard/relatorio.html', context)