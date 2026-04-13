import os
from django.conf import settings
from lxml import etree

NFE_NAMESPACES = {
    'nfe': 'http://www.portalfiscal.inf.br/nfe',
}


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

        inf_nfe = root.find('.//nfe:infNFe', NFE_NAMESPACES)
        if inf_nfe is None:
            inf_nfe = root.find('.//infNFe')

        ide = root.find('.//nfe:ide', NFE_NAMESPACES)
        if ide is None:
            ide = root.find('.//ide')

        if ide is not None:
            n = ide.find('nNF')
            if n is not None:
                resultado['numero'] = n.text or ''
            d = ide.find('dhEmi')
            if d is None:
                d = ide.find('dEmi')
            if d is not None and d.text:
                from datetime import datetime
                data_str = d.text[:10]
                resultado['data_emissao'] = datetime.strptime(data_str, '%Y-%m-%d').date()

        emit = root.find('.//nfe:emit', NFE_NAMESPACES)
        if emit is None:
            emit = root.find('.//emit')

        if emit is not None:
            nome = emit.find('nfe:xFant', NFE_NAMESPACES)
            if nome is None:
                nome = emit.find('xFant')
            if nome is None:
                nome = emit.find('nfe:xNome', NFE_NAMESPACES)
                if nome is None:
                    nome = emit.find('xNome')
            if nome is not None:
                resultado['fornecedor'] = nome.text or ''

            cnpj = emit.find('nfe:CNPJ', NFE_NAMESPACES)
            if cnpj is None:
                cnpj = emit.find('CNPJ')
            if cnpj is not None:
                resultado['cnpj_fornecedor'] = cnpj.text or ''

        det_list = root.findall('.//nfe:det', NFE_NAMESPACES)
        if not det_list:
            det_list = root.findall('.//det')

        for det in det_list:
            prod = det.find('nfe:prod', NFE_NAMESPACES)
            if prod is None:
                prod = det.find('prod')
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
            }

            for campo, tag in [
                ('descricao', 'xProd'), ('codigo_produto', 'cProd'),
                ('ncm', 'NCM'), ('unidade', 'uCom'),
            ]:
                el = prod.find(f'nfe:{tag}', NFE_NAMESPACES)
                if el is None:
                    el = prod.find(tag)
                if el is not None:
                    item[campo] = el.text or ''

            for campo, tag in [
                ('quantidade', 'qCom'), ('valor_unitario', 'vUnCom'),
                ('valor_total', 'vProd'),
            ]:
                el = prod.find(f'nfe:{tag}', NFE_NAMESPACES)
                if el is None:
                    el = prod.find(tag)
                if el is not None and el.text:
                    try:
                        item[campo] = float(el.text.replace(',', '.'))
                    except ValueError:
                        pass

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
            )

    elif ext == '.pdf':
        texto = extract_text_from_pdf(caminho)
        nota.texto_extraido = texto
        nota.tipo = 'pdf'

    nota.processado = True
    nota.save()