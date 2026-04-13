from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lote
from .forms import LoteForm
from .filters import LoteFilter


@login_required
def lote_list(request):
    queryset = Lote.objects.select_related('defensivo').all()
    filtro = LoteFilter(request.GET, queryset=queryset)
    return render(request, 'lotes/list.html', {'filter': filtro, 'object_list': filtro.qs})


@login_required
def lote_create(request):
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.cadastrado_por = request.user
            obj.save()
            messages.success(request, f'Lote "{obj.numero_lote}" cadastrado com sucesso.')
            return redirect(obj)
    else:
        form = LoteForm()
    return render(request, 'lotes/form.html', {'form': form, 'titulo': 'Novo Lote'})


@login_required
def lote_update(request, pk):
    obj = get_object_or_404(Lote, pk=pk)
    if request.method == 'POST':
        form = LoteForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lote "{obj.numero_lote}" atualizado com sucesso.')
            return redirect(obj)
    else:
        form = LoteForm(instance=obj)
    return render(request, 'lotes/form.html', {'form': form, 'titulo': 'Editar Lote'})


@login_required
def lote_detail(request, pk):
    obj = get_object_or_404(Lote, pk=pk)
    return render(request, 'lotes/detail.html', {'object': obj})


@login_required
def lote_delete(request, pk):
    obj = get_object_or_404(Lote, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'Lote "{obj.numero_lote}" excluído.')
        return redirect('lotes:list')
    return render(request, 'lotes/confirm_delete.html', {'object': obj})