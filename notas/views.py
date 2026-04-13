from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import NotaFiscal, ItemNotaFiscal
from .forms import NotaFiscalUploadForm
from .services import processar_nota, importar_nota_automatico, inferir_classe
from defensivos.models import Defensivo, ClasseDefensivo
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
                messages.success(request, f'Nota {nota.numero or ""} processada com sucesso. Selecione o tipo de cada item e clique em Importar.')
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
    classes = ClasseDefensivo.choices
    for item in itens:
        if not hasattr(item, '_classe_sugerida'):
            item._classe_sugerida = inferir_classe(item.descricao)
    return render(request, 'notas/detail.html', {
        'nota': nota,
        'itens': itens,
        'classes': classes,
    })


@login_required
def nota_list(request):
    notas = NotaFiscal.objects.all()
    return render(request, 'notas/list.html', {'object_list': notas})


@login_required
@require_POST
def nota_importar(request, pk):
    nota = get_object_or_404(NotaFiscal, pk=pk)
    if nota.status_importacao == 'importado':
        messages.info(request, 'Esta nota já foi importada.')
        return redirect('notas:detail', pk=nota.pk)

    tipos = {}
    for key, value in request.POST.items():
        if key.startswith('classe_'):
            try:
                item_id = int(key.replace('classe_', ''))
                tipos[item_id] = value
            except (ValueError, TypeError):
                pass

    defensivos_criados, lotes_criados = importar_nota_automatico(nota, user=request.user, classes_por_item=tipos)
    messages.success(
        request,
        f'Importação concluída: {defensivos_criados} produto(s) e {lotes_criados} lote(s) criados.'
    )
    return redirect('notas:detail', pk=nota.pk)


@login_required
@require_POST
def nota_limpar(request, pk):
    nota = get_object_or_404(NotaFiscal, pk=pk)
    for item in nota.itens.all():
        if item.lote:
            item.lote.delete()
        if item.defensivo:
            item.defensivo.delete()
    nota.itens.all().delete()
    nota.processado = False
    nota.status_importacao = 'pendente'
    nota.numero = ''
    nota.data_emissao = None
    nota.fornecedor = ''
    nota.cnpj_fornecedor = ''
    nota.texto_extraido = ''
    nota.save()
    messages.success(request, 'Processamento da nota limpo. Você pode reprocessar fazendo upload novamente.')
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