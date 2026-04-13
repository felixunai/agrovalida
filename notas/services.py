import os
import re
from datetime import datetime
from django.conf import settings
from lxml import etree

NFE_NAMESPACES = {
    'nfe': 'http://www.portalfiscal.inf.br/nfe',
}

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
    'bag': 'BAG', 'saco': 'BAG', 'bolsa': 'BAG',
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
    if not texto:
        return None
    texto = texto.strip()
    for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None


def _parse_inf_ad_prod(texto):
    resultado = {
        'numero_lote': '',
        'data_fabricacao': None,
        'data_validade': None,
    }
    if not texto:
        return resultado

    match_lote = re.search(r'Lote:\s*(.+?)(?:\s*Pen\.|\s*At\.|\s*Germ\.|\s*Pur\.|\s*Val\.|\s*Fab\.|\s*RENASEM|\s*-\s*\d{2}|\s*$)', texto, re.IGNORECASE)
    if match_lote:
        resultado['numero_lote'] = match_lote.group(1).strip().rstrip(' -')

    match_val = re.search(r'Val\.?:\s*(\d{2}[\-\/]\d{2}[\-\/]\d{4})', texto)
    if match_val:
        resultado['data_validade'] = _parse_data(match_val.group(1))

    match_fab = re.search(r'Fab\.?:\s*(\d{2}[\-\/]\d{2}[\-\/]\d{4})', texto)
    if match_fab:
        resultado['data_fabricacao'] = _parse_data(match_fab.group(1))

    return resultado


def _find_element(parent, tag):
    el = parent.find(f'nfe:{tag}', NFE_NAMESPACES)
    if el is None:
        el = parent.find(tag)
    return el


def parse_nfe_xml(caminho_arquivo):
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

        ide = _find_element(root, 'ide')
        if ide is not None:
            n = _find_element(ide, 'nNF')
            if n is not None:
                resultado['numero'] = n.text or ''
            d = _find_element(ide, 'dhEmi')
            if d is None:
                d = _find_element(ide, 'dEmi')
            if d is not None and d.text:
                data_str = d.text[:10]
                resultado['data_emissao'] = datetime.strptime(data_str, '%Y-%m-%d').date()

        emit = _find_element(root, 'emit')
        if emit is not None:
            nome = _find_element(emit, 'xFant')
            if nome is None:
                nome = _find_element(emit, 'xNome')
            if nome is not None:
                resultado['fornecedor'] = nome.text or ''
            cnpj = _find_element(emit, 'CNPJ')
            if cnpj is not None:
                resultado['cnpj_fornecedor'] = cnpj.text or ''

        det_list = root.findall('.//nfe:det', NFE_NAMESPACES)
        if not det_list:
            det_list = root.findall('.//det')

        for det in det_list:
            prod = _find_element(det, 'prod')
            if prod is None:
                continue

            item = {
                'descricao': '',
                'codigo_produto': '',
                'ncm': '',
                'quantidade': 1,
                'unidade': '',
                'valor_unitario': None,
                'valor_total': None,
                'numero_lote': '',
                'data_fabricacao': None,
                'data_validade': None,
            }

            for campo, tag in [
                ('descricao', 'xProd'), ('codigo_produto', 'cProd'),
                ('ncm', 'NCM'), ('unidade', 'uCom'),
            ]:
                el = _find_element(prod, tag)
                if el is not None:
                    item[campo] = el.text or ''

            for campo, tag in [
                ('quantidade', 'qCom'), ('valor_unitario', 'vUnCom'),
                ('valor_total', 'vProd'),
            ]:
                el = _find_element(prod, tag)
                if el is not None and el.text:
                    try:
                        item[campo] = float(el.text.replace(',', '.'))
                    except ValueError:
                        pass

            inf_ad_el = _find_element(det, 'infAdProd')
            if inf_ad_el is not None and inf_ad_el.text:
                dados_lote = _parse_inf_ad_prod(inf_ad_el.text)
                item['numero_lote'] = dados_lote['numero_lote']
                item['data_fabricacao'] = dados_lote['data_fabricacao']
                item['data_validade'] = dados_lote['data_validade']

            resultado['itens'].append(item)

    except Exception:
        pass

    return resultado


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
        texto = extract_text_from_pdf(caminho)
        nota.texto_extraido = texto
        nota.tipo = 'pdf'

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
            unidade = inferir_unidade(item.unidade)

            defensivo = Defensivo.objects.create(
                nome_comercial=descricao,
                classe=classe,
                registro_mapa=codigo,
                fabricante=nota.fornecedor or '',
                ativo=True,
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