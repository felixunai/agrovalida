from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Fazenda
from .forms import FazendaForm


@login_required
def fazenda_list(request):
    fazendas = Fazenda.objects.filter(cadastrado_por=request.user)
    return render(request, 'fazendas/list.html', {'object_list': fazendas})


@login_required
def fazenda_create(request):
    if request.method == 'POST':
        form = FazendaForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.cadastrado_por = request.user
            obj.save()
            messages.success(request, f'Fazenda "{obj.nome}" cadastrada com sucesso.')
            return redirect(obj)
    else:
        form = FazendaForm()
    return render(request, 'fazendas/form.html', {'form': form, 'titulo': 'Nova Fazenda'})


@login_required
def fazenda_update(request, pk):
    obj = get_object_or_404(Fazenda, pk=pk, cadastrado_por=request.user)
    if request.method == 'POST':
        form = FazendaForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fazenda "{obj.nome}" atualizada com sucesso.')
            return redirect(obj)
    else:
        form = FazendaForm(instance=obj)
    return render(request, 'fazendas/form.html', {'form': form, 'titulo': 'Editar Fazenda'})


@login_required
def fazenda_detail(request, pk):
    obj = get_object_or_404(Fazenda, pk=pk, cadastrado_por=request.user)
    from lotes.models import Lote
    lotes = Lote.objects.filter(fazenda=obj).select_related('defensivo').order_by('data_validade')
    return render(request, 'fazendas/detail.html', {'object': obj, 'lotes': lotes})


@login_required
def fazenda_delete(request, pk):
    obj = get_object_or_404(Fazenda, pk=pk, cadastrado_por=request.user)
    if request.method == 'POST':
        nome = obj.nome
        obj.delete()
        messages.success(request, f'Fazenda "{nome}" excluída. Os lotes associados não foram afetados.')
        return redirect('fazendas:list')
    return render(request, 'fazendas/confirm_delete.html', {'object': obj})
