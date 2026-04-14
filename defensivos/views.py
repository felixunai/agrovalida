from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Defensivo
from .forms import DefensivoForm
from .filters import DefensivoFilter
from accounts.decorators import limite_alcancado

DEFENSIVOS_PER_PAGE = 25


@login_required
def defensivo_list(request):
    queryset = Defensivo.objects.filter(cadastrado_por=request.user)
    filtro = DefensivoFilter(request.GET, queryset=queryset)

    paginator = Paginator(filtro.qs, DEFENSIVOS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'defensivos/list.html', {
        'filter': filtro,
        'object_list': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'query_string': query_params.urlencode(),
        'total_count': filtro.qs.count(),
    })


@login_required
@limite_alcancado('defensivo')
def defensivo_create(request):
    if request.method == 'POST':
        form = DefensivoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.cadastrado_por = request.user
            obj.save()
            messages.success(request, f'Produto "{obj.nome_comercial}" cadastrado com sucesso.')
            return redirect(obj)
    else:
        form = DefensivoForm()
    return render(request, 'defensivos/form.html', {'form': form, 'titulo': 'Novo Produto'})


@login_required
def defensivo_update(request, pk):
    obj = get_object_or_404(Defensivo, pk=pk, cadastrado_por=request.user)
    if request.method == 'POST':
        form = DefensivoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Produto "{obj.nome_comercial}" atualizado com sucesso.')
            return redirect(obj)
    else:
        form = DefensivoForm(instance=obj)
    return render(request, 'defensivos/form.html', {'form': form, 'titulo': 'Editar Produto'})


@login_required
def defensivo_detail(request, pk):
    obj = get_object_or_404(Defensivo, pk=pk, cadastrado_por=request.user)
    from lotes.models import Lote
    lotes = Lote.objects.filter(defensivo=obj).select_related('defensivo')
    return render(request, 'defensivos/detail.html', {'object': obj, 'lotes': lotes})


@login_required
def defensivo_delete(request, pk):
    obj = get_object_or_404(Defensivo, pk=pk, cadastrado_por=request.user)
    if request.method == 'POST':
        novo_estado = not obj.ativo
        obj.ativo = novo_estado
        obj.save()
        acao = 'reativado' if novo_estado else 'desativado'
        messages.success(request, f'Produto "{obj.nome_comercial}" {acao}.')
        return redirect('defensivos:list')
    return render(request, 'defensivos/confirm_delete.html', {'object': obj})