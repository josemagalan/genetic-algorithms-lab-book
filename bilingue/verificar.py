"""Cotejo de integridad entre una traducción y la edición española fijada.

No evalúa la calidad lingüística. Comprueba elementos que una traducción no
debe alterar: estructura, citas, fórmulas, tablas y parámetros de actividades.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import re
import subprocess
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit

BOOK = Path(__file__).resolve().parents[1]


def clean(text):
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)
    return re.sub(r'<!--.*?-->', '', text, flags=re.S)


def normalizar_math(text):
    text = text.replace('{,}', '.')
    for a, b in [('coste', 'cost'), ('peso', 'weight'), ('valor', 'value'),
                 ('maximizar', 'maximize'), ('minimizar', 'minimize'),
                 ('\\mathrm{EE}', '\\mathrm{SE}')]:
        text = text.replace(a, b)
    return re.sub(r'\s+', '', text)


def formulas(text):
    return [normalizar_math(a or b) for a, b in re.findall(r'\$\$(.*?)\$\$|\$([^$\n]+)\$', text, re.S)]


def url_neutra(text):
    u = urlsplit(text)
    u = u._replace(query=urlencode([(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if k != 'lang']))
    fragment = parse_qsl(u.fragment, keep_blank_values=True)
    if fragment and any(k == 'lang' for k, _ in fragment):
        u = u._replace(fragment=urlencode([(k, v) for k, v in fragment if k != 'lang']))
    return urlunsplit(u)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--informe', required=True, type=Path)
    args = p.parse_args()
    meta = json.loads((BOOK / 'en/traduccion.json').read_text(encoding='utf-8'))
    result = {'source_tag': meta['source_tag'], 'source_doi': meta['source_doi'], 'chapters': {}, 'failures': []}
    for name in meta['translated_chapters']:
        source = subprocess.check_output(['git', '-C', str(BOOK), 'show', f'{meta["source_tag"]}:{name}']).decode('utf-8')
        target = (BOOK / 'en' / name).read_text(encoding='utf-8')
        es, en = clean(source), clean(target)
        checks = {}
        checks['identifiers'] = re.findall(r'\{[^}\n]*#([\w-]+)', es) == re.findall(r'\{[^}\n]*#([\w-]+)', en)
        checks['citations_and_crossreferences'] = Counter(re.findall(r'@([\w-]+)', es)) == Counter(re.findall(r'@([\w-]+)', en))
        checks['formulas'] = formulas(es) == formulas(en)
        checks['activity_types'] = re.findall(r'\.(ejemplo|ejercicio|en-app)\b', es) == re.findall(r'\.(ejemplo|ejercicio|en-app)\b', en)
        checks['levels'] = re.findall(r'\{\.nivel \.(\w[\w-]*)\}', es) == re.findall(r'\{\.nivel \.(\w[\w-]*)\}', en)
        checks['folded_content'] = es.count('<details') == en.count('<details') and es.count('</details>') == en.count('</details>')
        urls = lambda t: Counter(url_neutra(u) for u in re.findall(r'https?://[^\s)\]"<>]+', t))
        checks['urls_and_activity_parameters'] = urls(es) == urls(en)
        # Comparar cada fila: sus números no deben cambiar ni de valor ni de orden.
        table_numbers = lambda t: [[x.replace(',', '.') for x in re.findall(r'\d+(?:[.,]\d+)?', line.replace('{,}', '.'))] for line in t.splitlines() if line.startswith('|')]
        checks['table_values'] = table_numbers(es) == table_numbers(en)
        numbers = lambda t: Counter(re.findall(r'(?<![\w])\d+(?:\.\d+)?', t.replace('{,}', '.').replace(',', '.')))
        a, b = numbers(es), numbers(en)
        checks['numeric_tokens'] = a == b
        result['chapters'][name] = {'checks': checks, 'identifiers': len(re.findall(r'\{[^}\n]*#([\w-]+)', es)),
                                    'formulas': len(formulas(es)), 'folded_blocks': es.count('<details'),
                                    'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                                    'translation_sha256': hashlib.sha256((BOOK / 'en' / name).read_bytes()).hexdigest(),
                                    'translation_text_lf_sha256': hashlib.sha256(target.encode()).hexdigest(),
                                    'numbers_missing': dict(a-b), 'numbers_added': dict(b-a)}
        result['failures'] += [name + ': ' + k for k, v in checks.items() if not v]
    args.informe.parent.mkdir(parents=True, exist_ok=True)
    args.informe.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['failures']))


if __name__ == '__main__':
    main()
