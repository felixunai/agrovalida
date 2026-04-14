import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.conf import settings
from .forms import RegisterForm, PerfilForm, PasswordChangeForm
from .models import UserProfile, Plano
from .middleware import get_plan_limits

logger = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.telefone = form.cleaned_data['telefone']
            profile.save()
            login(request, user)
            messages.success(request, f'Conta criada com sucesso! Bem-vindo, {user.first_name or user.username}.')
            return redirect('dashboard:index')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


def landing(request):
    planos = Plano.objects.filter(ativo=True)
    return render(request, 'landing.html', {'planos': planos})


@login_required
def gerenciar_usuarios(request):
    if not request.user.is_superuser:
        messages.error(request, 'Acesso restrito a administradores.')
        return redirect('dashboard:index')

    usuarios = UserProfile.objects.select_related('user', 'plano').all()
    planos = Plano.objects.filter(ativo=True)
    return render(request, 'accounts/usuarios.html', {'usuarios': usuarios, 'planos': planos})


@login_required
@require_POST
def toggle_usuario(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Acesso restrito a administradores.')
        return redirect('dashboard:index')

    profile = get_object_or_404(UserProfile, pk=pk)
    profile.ativo = not profile.ativo
    profile.save()
    profile.user.is_active = profile.ativo
    profile.user.save()
    status = 'ativado' if profile.ativo else 'desativado'
    messages.success(request, f'Usuário {profile.user.username} {status} com sucesso.')
    return redirect('accounts:usuarios')


@login_required
@require_POST
def atribuir_plano(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Acesso restrito a administradores.')
        return redirect('dashboard:index')

    profile = get_object_or_404(UserProfile, pk=pk)
    plano_id = request.POST.get('plano_id')
    ativar = request.POST.get('plano_ativo') == 'on'

    if plano_id:
        profile.plano_id = plano_id
    else:
        profile.plano_id = None

    profile.plano_ativo = ativar
    profile.save()
    messages.success(request, f'Plano atualizado para {profile.user.username}.')
    return redirect('accounts:usuarios')


@login_required
def upgrade(request):
    planos = Plano.objects.filter(ativo=True)
    limits = get_plan_limits(request.user)
    return render(request, 'accounts/upgrade.html', {
        'planos': planos,
        'limits': limits,
        'is_pro': request.user.is_superuser or getattr(request, 'is_pro', False),
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
    })


@login_required
def editar_perfil(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            profile.telefone = form.cleaned_data.get('telefone', '')
            profile.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('accounts:perfil')
    else:
        form = PerfilForm(instance=request.user, initial={'telefone': profile.telefone})
    return render(request, 'accounts/perfil.html', {
        'form': form,
        'profile': profile,
        'is_pro': request.user.is_superuser or getattr(request, 'is_pro', False),
    })


@login_required
def alterar_senha(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('accounts:perfil')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/alterar_senha.html', {'form': form})


@login_required
def assinar(request):
    """Inicia o checkout do Stripe para plano Profissional."""
    import stripe
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

    if not stripe.api_key:
        messages.error(request, 'Pagamento não configurado. Entre em contato com o suporte.')
        return redirect('accounts:upgrade')

    periodo = request.GET.get('periodo', 'mensal')
    price_id = (
        getattr(settings, 'STRIPE_PRICE_ANUAL', '')
        if periodo == 'anual'
        else getattr(settings, 'STRIPE_PRICE_MENSAL', '')
    )

    if not price_id:
        messages.error(request, 'Plano não configurado. Entre em contato com o suporte.')
        return redirect('accounts:upgrade')

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Cria ou recupera customer no Stripe
    if not profile.stripe_customer_id:
        customer = stripe.Customer.create(
            email=request.user.email,
            name=request.user.get_full_name() or request.user.username,
            metadata={'user_id': request.user.pk},
        )
        profile.stripe_customer_id = customer.id
        profile.save(update_fields=['stripe_customer_id'])

    success_url = request.build_absolute_uri('/accounts/assinar/sucesso/')
    cancel_url = request.build_absolute_uri('/accounts/upgrade/')

    session = stripe.checkout.Session.create(
        customer=profile.stripe_customer_id,
        payment_method_types=['card'],
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='subscription',
        success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=cancel_url,
        metadata={'user_id': request.user.pk, 'periodo': periodo},
        locale='pt-BR',
    )
    return redirect(session.url, permanent=False)


@login_required
def checkout_sucesso(request):
    """Página de retorno após pagamento bem-sucedido no Stripe."""
    return render(request, 'accounts/checkout_sucesso.html')


@csrf_exempt
def stripe_webhook(request):
    """Recebe eventos do Stripe e atualiza status do plano."""
    import stripe
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.warning('Stripe webhook inválido: %s', e)
        return HttpResponse(status=400)

    event_type = event['type']
    data = event['data']['object']

    if event_type == 'checkout.session.completed':
        _ativar_plano_stripe(data)

    elif event_type in ('invoice.paid', 'invoice.payment_succeeded'):
        sub_id = data.get('subscription')
        if sub_id:
            _renovar_plano_stripe(sub_id, data)

    elif event_type in ('customer.subscription.deleted', 'customer.subscription.paused'):
        _desativar_plano_stripe(data)

    elif event_type == 'invoice.payment_failed':
        customer_id = data.get('customer')
        try:
            profile = UserProfile.objects.get(stripe_customer_id=customer_id)
            logger.warning('Pagamento falhou para %s', profile.user.email)
        except UserProfile.DoesNotExist:
            pass

    return HttpResponse(status=200)


def _ativar_plano_stripe(session):
    from django.utils import timezone
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    metadata = session.get('metadata', {})
    periodo = metadata.get('periodo', 'mensal')

    try:
        profile = UserProfile.objects.select_related('user').get(stripe_customer_id=customer_id)
    except UserProfile.DoesNotExist:
        user_id = metadata.get('user_id')
        if not user_id:
            return
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            profile.stripe_customer_id = customer_id
        except UserProfile.DoesNotExist:
            return

    hoje = timezone.now().date()
    from dateutil.relativedelta import relativedelta
    delta = relativedelta(years=1) if periodo == 'anual' else relativedelta(months=1)

    plano_pro = Plano.objects.filter(nome='Profissional').first()
    profile.plano = plano_pro
    profile.plano_ativo = True
    profile.stripe_subscription_id = subscription_id or ''
    profile.periodo_plano = periodo
    profile.data_fim_plano = hoje + delta
    profile.save()
    logger.info('Plano Pro ativado via Stripe para %s', profile.user.email)


def _renovar_plano_stripe(subscription_id, invoice):
    import stripe
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    from django.utils import timezone
    from dateutil.relativedelta import relativedelta

    try:
        profile = UserProfile.objects.get(stripe_subscription_id=subscription_id)
    except UserProfile.DoesNotExist:
        return

    # Pega data de fim do período da assinatura via API
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
        import datetime
        data_fim = datetime.date.fromtimestamp(sub['current_period_end'])
    except Exception:
        hoje = timezone.now().date()
        delta = relativedelta(years=1) if profile.periodo_plano == 'anual' else relativedelta(months=1)
        data_fim = hoje + delta

    profile.plano_ativo = True
    profile.data_fim_plano = data_fim
    profile.save(update_fields=['plano_ativo', 'data_fim_plano'])
    logger.info('Plano renovado via Stripe para %s até %s', profile.user.email, data_fim)


def _desativar_plano_stripe(subscription):
    sub_id = subscription.get('id')
    try:
        profile = UserProfile.objects.get(stripe_subscription_id=sub_id)
        profile.plano_ativo = False
        profile.stripe_subscription_id = ''
        profile.save(update_fields=['plano_ativo', 'stripe_subscription_id'])
        logger.info('Plano desativado via Stripe para %s', profile.user.email)
    except UserProfile.DoesNotExist:
        pass