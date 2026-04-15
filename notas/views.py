from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import NotaFiscal, ItemNotaFiscal
from .forms import NotaFiscalUploadForm
from .services import processar_nota, importar_nota_automatico, inferir_classe
from defensivos.models import Defensivo, ClasseDefensivo
from lotes.models import Lote


def _limpar_nota(nota):
    itens = nota.itens.select_related('defensivo', 'lote').all()
    lotes_ids = set()
    defensivos_ids = set()
    for item in itens:
        if item.lote_id:
            lotes_ids.add(item.lote_id)
        if item.defensivo_id:
            defensivos_ids.add(item.defensivo_id)
    Lote.objects.filter(pk__in=lotes_ids).delete()
    Defensivo.objects.filter(pk__in=defensivos_ids).delete()
    nota.itens.all().delete()


@login_required
def nota_upload(request):
    from accounts.middleware import get_plan_limits
    if request.method == 'POST':
        form = NotaFiscalUploadForm(request.POST, request.FILES)
        if form.is_valid():
            arquivos = form.cleaned_data['arquivo']  # list of files after clean_arquivo

            # Check plan limit before creating anything
            if not request.user.is_superuser and not getattr(request, 'is_pro', False):
                limits = get_plan_limits(request.user)
                max_notas = limits.get('max_notas')
                if max_notas is not None:
                    atual = NotaFiscal.objects.filter(cadastrado_por=request.user).count()
                    disponivel = max_notas - atual
                    if disponivel <= 0:
                        messages.warning(
                            request,
                            f'Você atingiu o limite de {max_notas} notas fiscais no plano Gratuito. '
                            'Atualize para o Profissional para importar mais.'
                        )
                        return redirect('accounts:upgrade')
                    if len(arquivos) > disponivel:
                        arquivos = arquivos[:disponivel]
                        messages.warning(
                            request,
                            f'Você só pode importar {disponivel} nota(s) com o plano Gratuito. '
                            f'Apenas os primeiros {disponivel} arquivo(s) foram processados.'
                        )

            notas_criadas = []
            erros = []

            for arquivo in arquivos:
                nota = NotaFiscal(arquivo=arquivo, cadastrado_por=request.user)
                nota.save()
                try:
                    processar_nota(nota)
                    notas_criadas.append(nota)
                except Exception as e:
                    erros.append(f'{arquivo.name}: {e}')

            if not notas_criadas:
                messages.error(request, 'Nenhuma nota pôde ser processada.')
                return redirect('notas:upload')

            if erros:
                messages.warning(request, f'Erros durante o processamento: {"; ".join(erros)}')

            if len(notas_criadas) == 1:
                nota = notas_criadas[0]
                messages.success(
                    request,
                    f'Nota {nota.numero or ""} processada com sucesso. '
                    'Selecione o tipo de cada item e clique em Importar.'
                )
                return redirect('notas:detail', pk=nota.pk)
            else:
                messages.success(
                    request,
                    f'{len(notas_criadas)} nota(s) processada(s) com sucesso.'
                )
                return redirect('notas:list')
    else:
        form = NotaFiscalUploadForm()
    return render(request, 'notas/upload.html', {'form': form})


@login_required
def nota_detail(request, pk):
    from fazendas.models import Fazenda
    nota = get_object_or_404(NotaFiscal, pk=pk, cadastrado_por=request.user)
    itens = nota.itens.select_related('defensivo', 'lote').all()
    classes = ClasseDefensivo.choices
    fazendas = Fazenda.objects.filter(cadastrado_por=request.user)
    for item in itens:
        item.classe_sugerida = inferir_classe(item.descricao)
    return render(request, 'notas/detail.html', {
        'nota': nota,
        'itens': itens,
        'classes': classes,
        'fazendas': fazendas,
    })


@login_required
def nota_list(request):
    notas = NotaFiscal.objects.filter(cadastrado_por=request.user)
    return render(request, 'notas/list.html', {'object_list': notas})


@login_required
@require_POST
def nota_importar(request, pk):
    nota = get_object_or_404(NotaFiscal, pk=pk, cadastrado_por=request.user)
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

    fazenda = None
    fazenda_id = request.POST.get('fazenda_id')
    if fazenda_id:
        from fazendas.models import Fazenda
        try:
            fazenda = Fazenda.objects.get(pk=fazenda_id, cadastrado_por=request.user)
        except Fazenda.DoesNotExist:
            pass

    local_armazenamento = request.POST.get('local_armazenamento', '').strip()

    defensivos_criados, lotes_criados = importar_nota_automatico(
        nota, user=request.user, classes_por_item=tipos, fazenda=fazenda,
        local_armazenamento=local_armazenamento,
    )
    messages.success(
        request,
        f'Importação concluída: {defensivos_criados} produto(s) e {lotes_criados} lote(s) criados.'
    )
    return redirect('notas:detail', pk=nota.pk)


@login_required
@require_POST
def nota_apagar(request, pk):
    nota = get_object_or_404(NotaFiscal, pk=pk, cadastrado_por=request.user)
    _limpar_nota(nota)
    nota.delete()
    messages.success(request, 'Nota fiscal excluída com sucesso.')
    return redirect('notas:list')


@login_required
@require_POST
def nota_limpar(request, pk):
    nota = get_object_or_404(NotaFiscal, pk=pk, cadastrado_por=request.user)
    _limpar_nota(nota)
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
    item = get_object_or_404(ItemNotaFiscal, pk=item_pk, nota__cadastrado_por=request.user)
    if request.method == 'POST':
        defensivo_id = request.POST.get('defensivo')
        defensivo = get_object_or_404(Defensivo, pk=defensivo_id, cadastrado_por=request.user)

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

    defensivos = Defensivo.objects.filter(ativo=True, cadastrado_por=request.user)
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