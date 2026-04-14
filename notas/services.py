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

_QTD_RE = re.compile(
    r'(\d+[\.,]?\d*)\s*(UN|KG|L|LT|ML|BAG|CX|PC|SC|TON|g|mL|l|kg|bag|cx|un|Un)',
    re.IGNORECASE,
)

_SKIP_WORDS = [
    'total', 'nota fiscal', 'nfe', 'cnpj', 'ie', 'icms', 'ipi', 'cofins',
    'pis', 'fatura', 'duplicata', 'pagamento', 'destinat', 'emitente',
    'endere', 'telefone', 'inscri', 'natureza', 'base de', 'aliquota',
    'origem', 'destino', 'frete', 'seguro', 'desconto', 'subtotal',
]


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
# PDF parsing — table-based (primary strategy)
# ─────────────────────────────────────────────

def _extract_pdf_data(caminho_arquivo):
    """Extract plain text and tables from a PDF in a single pdfplumber pass."""
    text_pages = []
    all_tables = []
    try:
        import pdfplumber
        with pdfplumber.open(caminho_arquivo) as pdf:
            for pagina in pdf.pages:
                t = pagina.extract_text()
                if t:
                    text_pages.append(t)
                tables = pagina.extract_tables()
                if tables:
                    all_tables.extend(tables)
    except ImportError:
        pass
    except Exception:
        pass
    return '\n'.join(text_pages), all_tables


def _find_col(header, *keywords):
    for kw in keywords:
        for i, h in enumerate(header):
            if kw in str(h or '').lower():
                return i
    return None


def _is_product_table(header):
    header_str = ' '.join(str(h or '').lower() for h in header)
    has_descr = any(k in header_str for k in ['descri', 'produto', 'mercadoria', 'item'])
    has_other = any(k in header_str for k in ['qtd', 'quant', 'valor', 'ncm', 'cfop', 'unid', 'vl '])
    return has_descr and has_other


def _extract_lote_validade_from_text(texto):
    numero_lote = ''
    data_fabricacao = None
    data_validade = None

    m = re.search(r'[Ll]ote[:\s]+([A-Za-z0-9/\-\.]+)', texto)
    if m:
        numero_lote = m.group(1).strip()

    m = re.search(
        r'(?:validade|val\.?|vencim(?:ento)?)[:\s]+(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}|\d{1,2}[\-/]\d{4})',
        texto, re.IGNORECASE
    )
    if m:
        data_validade = _parse_data(m.group(1))

    m = re.search(
        r'(?:fabr(?:ica[çã][ao])?\.?|fab\.?)[:\s]+(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4})',
        texto, re.IGNORECASE
    )
    if m:
        data_fabricacao = _parse_data(m.group(1))

    return numero_lote, data_fabricacao, data_validade


def _parse_nfe_pdf_tables(texto_completo, all_tables):
    """Parse NF-e data from pdfplumber tables (primary strategy for structured PDFs)."""
    resultado = {
        'numero': '',
        'data_emissao': None,
        'fornecedor': '',
        'cnpj_fornecedor': '',
        'itens': [],
    }

    # Extract header metadata from text regardless
    if texto_completo:
        m = re.search(r'(?:NF-?e|NFe|Nota\s*Fiscal)[^\d]*(\d{1,10})', texto_completo, re.IGNORECASE)
        if not m:
            m = re.search(r'(?:n[°ºo]|número|numero)[^\d]*(\d{4,10})', texto_completo, re.IGNORECASE)
        if m:
            resultado['numero'] = m.group(1)

        for padrao in [
            r'(?:data\s*(?:de\s*)?emiss[ãa]o|dhEmi)[^\d]*(\d{2}[\-/]\d{2}[\-/]\d{4})',
            r'(\d{2}[\-/]\d{2}[\-/]\d{4})',
        ]:
            m = re.search(padrao, texto_completo, re.IGNORECASE)
            if m:
                resultado['data_emissao'] = _parse_data(m.group(1))
                break

        m = re.search(
            r'(?:emitente|fornecedor|raz[ãa]o\s*social)[^0-9A-Z]*([A-Z][A-ZÀ-ÿ0-9\s&.\-]{3,60})',
            texto_completo, re.IGNORECASE
        )
        if m:
            resultado['fornecedor'] = m.group(1).strip()

        m = re.search(r'CNPJ[:\s]*(\d{2}\.?\d{3}\.?\d{3}[\/]?\d{4}[\-]?\d{2})', texto_completo)
        if m:
            resultado['cnpj_fornecedor'] = re.sub(r'[.\-/]', '', m.group(1))

    for table in all_tables:
        if not table or len(table) < 2:
            continue
        header = table[0]
        if not _is_product_table(header):
            continue

        col_descr = _find_col(header, 'descri', 'produto', 'mercadoria')
        col_qtd   = _find_col(header, 'qtd', 'quant')
        col_un    = _find_col(header, 'un ', 'unid', 'un.')
        col_vt    = _find_col(header, 'vl total', 'valor total', 'vlr total', 'vl prod', 'v. total')
        col_cod   = _find_col(header, 'cód', 'cod ', 'código')

        if col_descr is None:
            continue

        for row in table[1:]:
            if not row or all(not c for c in row):
                continue

            def cell(idx, default=''):
                if idx is not None and idx < len(row):
                    return str(row[idx] or '').strip()
                return default

            descricao = cell(col_descr)
            if len(descricao) < 3:
                continue
            if any(s in descricao.lower() for s in _SKIP_WORDS):
                continue

            qtd = 1.0
            try:
                q = re.sub(r'[^\d,.]', '', cell(col_qtd, '1')).replace(',', '.') or '1'
                qtd = float(q)
            except (ValueError, AttributeError):
                pass

            vt = None
            try:
                vt_str = cell(col_vt)
                if vt_str:
                    vt = _parse_money(vt_str)
            except Exception:
                pass

            numero_lote, data_fab, data_val = _extract_lote_validade_from_text(descricao)

            resultado['itens'].append({
                'descricao': descricao[:200],
                'codigo_produto': cell(col_cod),
                'ncm': '',
                'quantidade': qtd,
                'unidade': cell(col_un),
                'valor_unitario': None,
                'valor_total': vt,
                'numero_lote': numero_lote,
                'data_fabricacao': data_fab,
                'data_validade': data_val,
            })

    return resultado


# ─────────────────────────────────────────────
# PDF parsing — text-based (fallback strategy)
# ─────────────────────────────────────────────

def extract_text_from_pdf(caminho_arquivo):
    try:
        import pdfplumber
        texto = []
        with pdfplumber.open(caminho_arquivo) as pdf:
            for pagina in pdf.pages:
                t = pagina.extract_text()
                if t:
                    texto.append(t)
        return '\n'.join(texto)
    except ImportError:
        return ''


def parse_nfe_pdf_text(texto):
    resultado = {
        'numero': '',
        'data_emissao': None,
        'fornecedor': '',
        'cnpj_fornecedor': '',
        'itens': [],
    }
    try:
        if not texto:
            return resultado

        m = re.search(r'(?:NF-?e|NFe|Nota\s*Fiscal)[^\d]*(\d{1,10})', texto, re.IGNORECASE)
        if not m:
            m = re.search(r'(?:n[°ºo]|número|numero)[^\d]*(\d{4,10})', texto, re.IGNORECASE)
        if m:
            resultado['numero'] = m.group(1)

        for padrao in [
            r'(?:data\s*(?:de\s*)?emiss[ãa]o|dhEmi)[^\d]*(\d{2}[\-/]\d{2}[\-/]\d{4})',
            r'(\d{2}[\-/]\d{2}[\-/]\d{4})',
        ]:
            m = re.search(padrao, texto, re.IGNORECASE)
            if m:
                resultado['data_emissao'] = _parse_data(m.group(1))
                break

        m = re.search(
            r'(?:emitente|fornecedor|raz[ãa]o\s*social)[^0-9A-Z]*([A-Z][A-ZÀ-ÿ0-9\s&.\-]{3,60})',
            texto, re.IGNORECASE
        )
        if m:
            resultado['fornecedor'] = m.group(1).strip()

        m = re.search(r'CNPJ[:\s]*(\d{2}\.?\d{3}\.?\d{3}[\/]?\d{4}[\-]?\d{2})', texto)
        if m:
            resultado['cnpj_fornecedor'] = re.sub(r'[.\-/]', '', m.group(1))

        blocos = re.split(r'(?:\n|\r)\s*(?:\n|\r)', texto)
        for bloco in blocos:
            bloco = bloco.strip()
            if len(bloco) < 5:
                continue

            m_qtd    = _QTD_RE.search(bloco)
            m_val    = re.search(r'R?\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))', bloco)
            m_lote   = re.search(r'[Ll]ote[:\s]+([A-Za-z0-9/\-\.]+)', bloco, re.IGNORECASE)
            m_val_dt = re.search(
                r'(?:validade|val\.?|vencim(?:ento)?)[:\s]+(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}|\d{1,2}[\-/]\d{4})',
                bloco, re.IGNORECASE
            )
            m_fab_dt = re.search(
                r'(?:fabr(?:ica[çã][ao])?\.?|fab\.?)[:\s]+(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4})',
                bloco, re.IGNORECASE
            )

            if m_qtd or m_val or m_lote:
                linhas = bloco.split('\n')
                descricao = linhas[0].strip()[:200] if linhas else bloco[:200]
                descricao = re.sub(r'^\d+\s*', '', descricao)

                if any(s in descricao.lower() for s in _SKIP_WORDS):
                    continue

                resultado['itens'].append({
                    'descricao': descricao,
                    'codigo_produto': '',
                    'ncm': '',
                    'quantidade': float(m_qtd.group(1).replace(',', '.')) if m_qtd else 1,
                    'unidade': m_qtd.group(2).upper() if m_qtd else '',
                    'valor_unitario': None,
                    'valor_total': _parse_money(m_val.group(1)) if m_val else None,
                    'numero_lote': m_lote.group(1).strip() if m_lote else '',
                    'data_fabricacao': _parse_data(m_fab_dt.group(1)) if m_fab_dt else None,
                    'data_validade': _parse_data(m_val_dt.group(1)) if m_val_dt else None,
                })

        if not resultado['itens']:
            _PROD_WORDS = [
                'semente', 'defensivo', 'herbicida', 'fungicida', 'inseticida',
                'acaricida', 'adjuvante', 'regulador', 'biológico', 'biologico',
                'adubo', 'fertilizante', 'npk', 'ureia', 'glifosato', 'roundup',
            ]
            for linha in texto.split('\n'):
                linha = linha.strip()
                if len(linha) < 5 or any(s in linha.lower() for s in _SKIP_WORDS):
                    continue
                if any(w in linha.lower() for w in _PROD_WORDS):
                    m_qtd2  = _QTD_RE.search(linha)
                    m_lote2 = re.search(r'[Ll]ote[:\s]+([A-Za-z0-9/\-\.]+)', linha, re.IGNORECASE)
                    m_val2  = re.search(
                        r'(?:validade|val\.?|vencim(?:ento)?)[:\s]+(\d{1,2}[\-/]\d{1,2}[\-/]\d{2,4}|\d{1,2}[\-/]\d{4})',
                        linha, re.IGNORECASE
                    )
                    resultado['itens'].append({
                        'descricao': linha[:200],
                        'codigo_produto': '',
                        'ncm': '',
                        'quantidade': float(m_qtd2.group(1).replace(',', '.')) if m_qtd2 else 1,
                        'unidade': m_qtd2.group(2).upper() if m_qtd2 else '',
                        'valor_unitario': None,
                        'valor_total': None,
                        'numero_lote': m_lote2.group(1).strip() if m_lote2 else '',
                        'data_fabricacao': None,
                        'data_validade': _parse_data(m_val2.group(1)) if m_val2 else None,
                    })

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

    if ext == '.xml':
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

    elif ext == '.pdf':
        texto, all_tables = _extract_pdf_data(caminho)
        nota.texto_extraido = texto
        nota.tipo = 'pdf'

        # Strategy 1: table-based (most reliable for structured NF-e PDFs)
        dados = _parse_nfe_pdf_tables(texto, all_tables)

        # Strategy 2: text-based fallback if no items found via tables
        if not dados['itens']:
            dados_texto = parse_nfe_pdf_text(texto)
            dados['itens'] = dados_texto['itens']
            if not dados['numero']:
                dados['numero'] = dados_texto['numero']
            if not dados['data_emissao']:
                dados['data_emissao'] = dados_texto['data_emissao']
            if not dados['fornecedor']:
                dados['fornecedor'] = dados_texto['fornecedor']
            if not dados['cnpj_fornecedor']:
                dados['cnpj_fornecedor'] = dados_texto['cnpj_fornecedor']

        if dados['numero']:
            nota.numero = dados['numero']
        if dados['data_emissao']:
            nota.data_emissao = dados['data_emissao']
        if dados['fornecedor']:
            nota.fornecedor = dados['fornecedor']
        if dados['cnpj_fornecedor']:
            nota.cnpj_fornecedor = dados['cnpj_fornecedor']

        for item_dados in dados['itens']:
            ItemNotaFiscal.objects.create(
                nota=nota,
                descricao=item_dados['descricao'],
                codigo_produto=item_dados.get('codigo_produto', ''),
                ncm=item_dados.get('ncm', ''),
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


def importar_nota_automatico(nota, user=None, classes_por_item=None):
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
                cadastrado_por=user,
            )
            lotes_criados += 1

        item.lote = lote
        item.save()

    nota.status_importacao = 'importado'
    nota.save()

    return defensivos_criados, lotes_criados
