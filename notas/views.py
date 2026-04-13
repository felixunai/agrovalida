from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NotaFiscal, ItemNotaFiscal
from .forms import NotaFiscalUploadForm
from .services import processar_nota
from defensivos.models import Defensivo
from lotes.models import Lote


@login_required
def nota_upload(request):
    if request.method == 'POST':
        form = NotaFiscalUploadForm(request.POST, request.FILES)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.cadastrado_por = request.user
            nota.save()
            try:
                processar_nota(nota)
                messages.success(request, f'Nota {nota.numero or ""} processada com sucesso.')
            except Exception as e:
                messages.warning(request, f'Nota salva, mas houve erro no processamento: {e}')
            return redirect('notas:detail', pk=nota.pk)
    else:
        form = NotaFiscalUploadForm()
    return render(request, 'notas/upload.html', {'form': form})


@login_required
def nota_detail(request, pk):
    nota = get_object_or_404(NotaFiscal, pk=pk)
    itens = nota.itens.all()
    return render(request, 'notas/detail.html', {'nota': nota, 'itens': itens})


@login_required
def nota_list(request):
    notas = NotaFiscal.objects.all()
    return render(request, 'notas/list.html', {'object_list': notas})


@login_required
def importar_item_lote(request, item_pk):
    item = get_object_or_404(ItemNotaFiscal, pk=item_pk)
    if request.method == 'POST':
        defensivo_id = request.POST.get('defensivo')
        defensivo = get_object_or_404(Defensivo, pk=defensivo_id)

        lote = Lote.objects.create(
            defensivo=defensivo,
            numero_lote=request.POST.get('numero_lote', item.descricao[:100]),
            data_fabricacao=request.POST.get('data_fabricacao') or None,
            data_validade=request.POST.get('data_validade') or None,
            quantidade=item.quantidade,
            unidade=item.unidade or 'L',
            fornecedor=item.nota.fornecedor,
            nota_fiscal=item.nota.numero or '',
            local_armazenamento=request.POST.get('local_armazenamento', ''),
            cadastrado_por=request.user,
        )
        item.lote_importado = True
        item.save()
        messages.success(request, f'Lote "{lote.numero_lote}" importado com sucesso.')
        return redirect('lotes:detail', pk=lote.pk)

    defensivos = Defensivo.objects.filter(ativo=True)
    return render(request, 'notas/importar_item.html', {'item': item, 'defensivos': defensivos})