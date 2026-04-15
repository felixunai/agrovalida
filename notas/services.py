import os
import re
from calendar import monthrange
from datetime import datetime, date as date_cls
from django.conf import settings
from lxml import etree

NFE_NS = 'http://www.portalfiscal.inf.br/nfe'
NFE_NAMESPACES = {'nfe': NFE_NS}

PALAVRAS_CLASSE = {
    'inseticida': 'inseticida',
    'herbicida': 'herbicida',
    'fungicida': 'fungicida',
    'acaricida': 'acaricida',
    'adjuvante': 'adjuvante',
    'regulador': 'regulador',
    'biologico': 'biologico',
    'biológico': 'biologico',
    'semente': 'semente',
    'sementes': 'semente',
    'defensivo': 'outro',
    'adubo': 'outro',
    'fertilizante': 'outro',
}

PALAVRAS_UNIDADE = {
    'l': 'L', 'lt': 'L', 'litro': 'L', 'litros': 'L',
    'ml': 'mL', 'mililitro': 'mL',
    'kg': 'kg', 'quilo': 'kg', 'quilos': 'kg',
    'g': 'g', 'grama': 'g', 'gramas': 'g',
    'cx': 'cx', 'caixa': 'cx', 'saco': 'cx', 'pacote': 'cx',
    'bag': 'BAG', 'bolsa': 'BAG',
    'un': 'un', 'unidade': 'un',
}


def inferir_classe(descricao):
    desc_lower = descricao.lower()
    for palavra, classe in PALAVRAS_CLASSE.items():
        if palavra in desc_lower:
            return classe
    return 'outro'


def inferir_unidade(unidade_nota):
    if not unidade_nota:
        return 'L'
    return PALAVRAS_UNIDADE.get(unidade_nota.lower(), unidade_nota)


def _parse_data(texto):
    """Parse date string. Supports DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD,
    two-digit years, and Brazilian MM/AAAA (returns last day of month)."""
    if not texto:
        return None
    texto = texto.strip()

    for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%y', '%d/%m/%y'):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue

    # MM/AAAA or MM-AAAA — very common on Brazilian agro product labels
    m = re.match(r'^(\d{1,2})[\-/](\d{4})$', texto)
    if m:
        try:
            month, year = int(m.group(1)), int(m.group(2))
            if 1 <= month <= 12 and 2000 <= year <= 2100:
                last_day = monthrange(year, month)[1]
                return date_cls(year, month, last_day)
        except Exception:
            pass

    return None


def _parse_money(val):
    if not val:
        return None
    val = str(val).strip().replace('R$', '').replace('\xa0', '').strip()
    val = re.sub(r'\.(?=\d{3})', '', val).replace(',', '.')
    try:
        return float(val)
    except ValueError:
        return None


def _parse_inf_ad_prod(texto):
    """
    Parse lot number, manufacturing date and validity from the NF-e infAdProd field.

    Handles formats like:
      "Lote: 660/49Pen.: 6,0 - At. Gar.: 0317/23 - Germ.: 94,0% - Val.: 30-11-2023 - Fab.: 12-06-2023 -"
      "Lote: ABC123 Val.: 11/2024 Fab.: 06/2023"
    """
    resultado = {
        'numero_lote': '',
        'data_fabricacao': None,
        'data_validade': None,
    }
    if not texto:
        return resultado

    # Lot number: stop at the next known field label or " - " separator
    # Non-greedy match until Pen., At., Germ., Pur., Val., Fab., RENASEM, or " - " + digit
    m = re.search(
        r'Lote:\s*(.+?)(?=\s*(?:Pen\.|At\.|Germ\.|Pur\.|Val\.|Fab\.|RENASEM|[-–]\s*\d|\s*$))',
        texto, re.IGNORECASE,
    )
    if m:
        resultado['numero_lote'] = m.group(1).strip().rstrip(' -–')

    # Validity: "Val.: DD-MM-YYYY" or "Val.: MM/YYYY"
    m = re.search(
        r'Val\.?:?\s*(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}|\d{1,2}[\-/]\d{4})',
        texto, re.IGNORECASE,
    )
    if m:
        resultado['data_validade'] = _parse_data(m.group(1))

    # Manufacturing date: "Fab.: DD-MM-YYYY"
    m = re.search(
        r'Fab\.?:?\s*(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4})',
        texto, re.IGNORECASE,
    )
    if m:
        resultado['data_fabricacao'] = _parse_data(m.group(1))

    return resultado


# ─────────────────────────────────────────────
# XML helpers
# ─────────────────────────────────────────────

def _rfind(parent, tag):
    """Recursive search — finds first element with local name `tag` anywhere in subtree."""
    el = parent.find(f'.//{{{NFE_NS}}}{tag}')
    if el is None:
        el = parent.find(f'.//{tag}')  # fallback for NFs without default namespace
    return el


def _rfindall(parent, tag):
    """Recursive search — finds all elements with local name `tag` in subtree."""
    els = parent.findall(f'.//{{{NFE_NS}}}{tag}')
    if not els:
        els = parent.findall(f'.//{tag}')
    return els


def _txt(el):
    return (el.text or '').strip() if el is not None else ''


def _flt(el):
    """Return float value of element text, or None."""
    if el is None or not el.text:
        return None
    try:
        return float(el.text.strip().replace(',', '.'))
    except ValueError:
        return None


# ─────────────────────────────────────────────
# XML parsing
# ─────────────────────────────────────────────

def parse_nfe_xml(caminho_arquivo):
    """
    Parse NF-e XML file (versão 4.00 / nfeProc wrapper or raw NFe).

    Key structural note:
      nfeProc > NFe > infNFe > ide / emit / dest / det
    The previous _find_element helper only looked at direct children of root,
    which broke ide/emit extraction. We now use recursive _rfind throughout.
    """
    resultado = {
        'numero': '',
        'data_emissao': None,
        'fornecedor': '',
        'cnpj_fornecedor': '',
        'itens': [],
    }

    try:
        tree = etree.parse(caminho_arquivo)
        root = tree.getroot()

        # ── IDE ─────────────────────────────────────
        ide = _rfind(root, 'ide')
        if ide is not None:
            numero = _txt(_rfind(ide, 'nNF'))
            serie  = _txt(_rfind(ide, 'serie'))
            # Combine NF number with series: "13957/1"
            if serie and serie not in ('0', ''):
                resultado['numero'] = f'{numero}/{serie}'
            else:
                resultado['numero'] = numero

            # dhEmi (NF-e 4.x) or dEmi (NF-e 3.x)
            d = _rfind(ide, 'dhEmi') or _rfind(ide, 'dEmi')
            if d is not None and d.text:
                try:
                    resultado['data_emissao'] = datetime.strptime(d.text[:10], '%Y-%m-%d').date()
                except ValueError:
                    pass

        # ── EMIT ────────────────────────────────────
        emit = _rfind(root, 'emit')
        if emit is not None:
            # Prefer fantasy name (xFant) over legal name (xNome)
            nome = _rfind(emit, 'xFant') or _rfind(emit, 'xNome')
            resultado['fornecedor'] = _txt(nome)
            resultado['cnpj_fornecedor'] = _txt(_rfind(emit, 'CNPJ'))

        # ── DET (items) ─────────────────────────────
        for det in _rfindall(root, 'det'):
            prod = _rfind(det, 'prod')
            if prod is None:
                continue

            item = {
                'descricao':      _txt(_rfind(prod, 'xProd')),
                'codigo_produto': _txt(_rfind(prod, 'cProd')),
                'ncm':            _txt(_rfind(prod, 'NCM')),
                'quantidade':     _flt(_rfind(prod, 'qCom')) or 1,
                'unidade':        _txt(_rfind(prod, 'uCom')),
                'valor_unitario': _flt(_rfind(prod, 'vUnCom')),
                'valor_total':    _flt(_rfind(prod, 'vProd')),
                'numero_lote':    '',
                'data_fabricacao': None,
                'data_validade':   None,
            }

            # Lot / date from infAdProd (direct child of det, not prod)
            inf_ad = _rfind(det, 'infAdProd')
            if inf_ad is not None and inf_ad.text:
                dados = _parse_inf_ad_prod(inf_ad.text)
                item['numero_lote']    = dados['numero_lote']
                item['data_fabricacao'] = dados['data_fabricacao']
                item['data_validade']  = dados['data_validade']

            resultado['itens'].append(item)

    except Exception:
        pass

    return resultado


# ─────────────────────────────────────────────
# Main orchestration
# ─────────────────────────────────────────────

def processar_nota(nota):
    from .models import ItemNotaFiscal

    caminho = nota.arquivo.path
    ext = os.path.splitext(caminho)[1].lower()

    if ext != '.xml':
        raise ValueError(
            f'Formato "{ext}" não suportado. Envie o arquivo XML da NF-e.'
        )

    dados = parse_nfe_xml(caminho)
    nota.numero = dados['numero']
    nota.data_emissao = dados['data_emissao']
    nota.fornecedor = dados['fornecedor']
    nota.cnpj_fornecedor = dados['cnpj_fornecedor']
    nota.tipo = 'xml'

    for item_dados in dados['itens']:
        ItemNotaFiscal.objects.create(
            nota=nota,
            descricao=item_dados['descricao'],
            codigo_produto=item_dados['codigo_produto'],
            ncm=item_dados['ncm'],
            quantidade=item_dados.get('quantidade', 1),
            unidade=item_dados.get('unidade', ''),
            valor_unitario=item_dados.get('valor_unitario'),
            valor_total=item_dados.get('valor_total'),
            numero_lote=item_dados.get('numero_lote', ''),
            data_fabricacao=item_dados.get('data_fabricacao'),
            data_validade=item_dados.get('data_validade'),
        )

    nota.processado = True
    nota.status_importacao = 'processado'
    nota.save()


def importar_nota_automatico(nota, user=None, classes_por_item=None, fazenda=None):
    from .models import ItemNotaFiscal
    from defensivos.models import Defensivo
    from lotes.models import Lote, UnidadeMedida

    itens = nota.itens.filter(defensivo__isnull=True)
    if not itens.exists():
        return 0, 0

    defensivos_criados = 0
    lotes_criados = 0

    for item in itens:
        descricao = item.descricao.strip()
        codigo = item.codigo_produto.strip() if item.codigo_produto else ''

        classe = inferir_classe(descricao)
        if classes_por_item and item.pk in classes_por_item:
            classe = classes_por_item[item.pk]

        defensivo = None
        if codigo:
            defensivo = Defensivo.objects.filter(
                registro_mapa=codigo, ativo=True
            ).first()

        if not defensivo:
            defensivo = Defensivo.objects.filter(
                nome_comercial__iexact=descricao, ativo=True
            ).first()

        if not defensivo:
            defensivo = Defensivo.objects.create(
                nome_comercial=descricao,
                classe=classe,
                registro_mapa=codigo,
                fabricante=nota.fornecedor or '',
                ativo=True,
                cadastrado_por=user,
            )
            defensivos_criados += 1

        item.defensivo = defensivo

        numero_lote = item.numero_lote or (codigo or descricao[:100])
        data_fab = item.data_fabricacao or nota.data_emissao
        data_val = item.data_validade

        if not data_val and data_fab:
            from dateutil.relativedelta import relativedelta
            data_val = data_fab + relativedelta(months=24)

        lote = Lote.objects.filter(
            numero_lote=numero_lote,
            defensivo=defensivo,
        ).first()

        if not lote:
            unidade = inferir_unidade(item.unidade)
            if unidade not in dict(UnidadeMedida.choices).keys():
                unidade = 'un'

            lote = Lote.objects.create(
                defensivo=defensivo,
                numero_lote=numero_lote,
                data_fabricacao=data_fab,
                data_validade=data_val or data_fab,
                quantidade=item.quantidade,
                unidade=unidade,
                fornecedor=nota.fornecedor or '',
                nota_fiscal=nota.numero or '',
                fazenda=fazenda,
                cadastrado_por=user,
            )
            lotes_criados += 1

        item.lote = lote
        item.save()

    nota.status_importacao = 'importado'
    nota.save()

    return defensivos_criados, lotes_criados
