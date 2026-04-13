from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Defensivo
from .forms import DefensivoForm
from .filters import DefensivoFilter


@login_required
def defensivo_list(request):
    queryset = Defensivo.objects.all()
    filtro = DefensivoFilter(request.GET, queryset=queryset)
    return render(request, 'defensivos/list.html', {'filter': filtro, 'object_list': filtro.qs})


@login_required
def defensivo_create(request):
    if request.method == 'POST':
        form = DefensivoForm(request.POST)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Defensivo "{obj.nome_comercial}" cadastrado com sucesso.')
            return redirect(obj)
    else:
        form = DefensivoForm()
    return render(request, 'defensivos/form.html', {'form': form, 'titulo': 'Novo Defensivo'})


@login_required
def defensivo_update(request, pk):
    obj = get_object_or_404(Defensivo, pk=pk)
    if request.method == 'POST':
        form = DefensivoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Defensivo "{obj.nome_comercial}" atualizado com sucesso.')
            return redirect(obj)
    else:
        form = DefensivoForm(instance=obj)
    return render(request, 'defensivos/form.html', {'form': form, 'titulo': 'Editar Defensivo'})


@login_required
def defensivo_detail(request, pk):
    obj = get_object_or_404(Defensivo, pk=pk)
    from lotes.models import Lote
    lotes = Lote.objects.filter(defensivo=obj).select_related('defensivo')
    return render(request, 'defensivos/detail.html', {'object': obj, 'lotes': lotes})


@login_required
def defensivo_delete(request, pk):
    obj = get_object_or_404(Defensivo, pk=pk)
    if request.method == 'POST':
        obj.ativo = False
        obj.save()
        messages.success(request, f'Defensivo "{obj.nome_comercial}" desativado.')
        return redirect('defensivos:list')
    return render(request, 'defensivos/confirm_delete.html', {'object': obj})