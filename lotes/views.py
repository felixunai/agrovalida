from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Lote
from .forms import LoteForm
from .filters import LoteFilter
from accounts.decorators import limite_alcancado

LOTES_PER_PAGE = 25


@login_required
def lote_list(request):
    queryset = Lote.objects.filter(cadastrado_por=request.user).select_related('defensivo')
    filtro = LoteFilter(request.GET, queryset=queryset)

    paginator = Paginator(filtro.qs, LOTES_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Preserve filter params in pagination links
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'lotes/list.html', {
        'filter': filtro,
        'object_list': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'query_string': query_params.urlencode(),
        'total_count': filtro.qs.count(),
    })


@login_required
@limite_alcancado('lote')
def lote_create(request):
    if request.method == 'POST':
        form = LoteForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.cadastrado_por = request.user
            obj.save()
            messages.success(request, f'Lote "{obj.numero_lote}" cadastrado com sucesso.')
            return redirect(obj)
    else:
        form = LoteForm(user=request.user)
    return render(request, 'lotes/form.html', {'form': form, 'titulo': 'Novo Lote'})


@login_required
def lote_update(request, pk):
    obj = get_object_or_404(Lote, pk=pk, cadastrado_por=request.user)
    if request.method == 'POST':
        form = LoteForm(request.POST, instance=obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lote "{obj.numero_lote}" atualizado com sucesso.')
            return redirect(obj)
    else:
        form = LoteForm(instance=obj, user=request.user)
    return render(request, 'lotes/form.html', {'form': form, 'titulo': 'Editar Lote'})


@login_required
def lote_detail(request, pk):
    obj = get_object_or_404(Lote, pk=pk, cadastrado_por=request.user)
    return render(request, 'lotes/detail.html', {'object': obj})


@login_required
def lote_delete(request, pk):
    obj = get_object_or_404(Lote, pk=pk, cadastrado_por=request.user)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'Lote "{obj.numero_lote}" excluído.')
        return redirect('lotes:list')
    return render(request, 'lotes/confirm_delete.html', {'object': obj})