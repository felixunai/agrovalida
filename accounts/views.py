from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import RegisterForm
from .models import UserProfile, Plano


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
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