from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NotaFiscal, ItemNotaFiscal
from .forms import NotaFiscalUploadForm
from .services import processar_nota, importar_nota_automatico
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
                importar_nota_automatico(nota, user=request.user)
                messages.success(request, f'Nota {nota.numero or ""} processada e importada com sucesso.')
            except Exception as e:
                messages.warning(request, f'Nota salva, mas houve erro no processamento: {e}')
            return redirect('notas:detail', pk=nota.pk)
    else:
        form = NotaFiscalUploadForm()
    return render(request, 'notas/upload.html', {'form': form})


@login_required
def nota_detail(request, pk):
    nota = get_object_or_404(NotaFiscal, pk=pk)
    itens = nota.itens.select_related('defensivo', 'lote').all()
    return render(request, 'notas/detail.html', {'nota': nota, 'itens': itens})


@login_required
def nota_list(request):
    notas = NotaFiscal.objects.all()
    return render(request, 'notas/list.html', {'object_list': notas})


@login_required
def nota_importar(request, pk):
    nota = get_object_or_404(NotaFiscal, pk=pk)
    if nota.status_importacao == 'importado':
        messages.info(request, 'Esta nota já foi importada.')
        return redirect('notas:detail', pk=nota.pk)

    defensivos_criados, lotes_criados = importar_nota_automatico(nota, user=request.user)
    messages.success(
        request,
        f'Importação concluída: {defensivos_criados} defensivo(s) e {lotes_criados} lote(s) criados.'
    )
    return redirect('notas:detail', pk=nota.pk)


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
        item.defensivo = defensivo
        item.lote = lote
        item.save()
        messages.success(request, f'Lote "{lote.numero_lote}" importado com sucesso.')
        return redirect('lotes:detail', pk=lote.pk)

    defensivos = Defensivo.objects.filter(ativo=True)
    return render(request, 'notas/importar_item.html', {
        'item': item,
        'defensivos': defensivos,
        'numero_lote_default': item.numero_lote or item.descricao[:100],
        'data_fabricacao_default': item.data_fabricacao.isoformat() if item.data_fabricacao else '',
        'data_validade_default': item.data_validade.isoformat() if item.data_validade else '',
        'quantidade_default': item.quantidade,
        'unidade_default': item.unidade or 'L',
        'fornecedor_default': item.nota.fornecedor or '',
    })