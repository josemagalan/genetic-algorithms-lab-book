"""Comprueba enlaces locales, selectores y avisos del sitio bilingüe generado."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit

BOOK = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.selector_links, self.text = [], [], [], []
        self.selector_count = 0
        self.in_selector = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'nav' and 'ediciones' in attrs.get('class', '').split():
            self.in_selector = True
            self.selector_count += 1
        if tag == 'a' and self.in_selector and 'href' in attrs:
            self.selector_links.append(attrs['href'])
        if tag in ('a', 'img', 'script', 'link', 'iframe'):
            for attr in ('href', 'src'):
                if attrs.get(attr):
                    self.links.append((tag, attrs[attr]))

    def handle_endtag(self, tag):
        if tag == 'nav':
            self.in_selector = False

    def handle_data(self, data):
        self.text.append(data)


def comprobar(site, meta):
    pages, errors = {}, []
    links = resources = 0
    for folder in (site, site / 'en'):
        for file in folder.glob('*.html'):
            source = file.read_text(encoding='utf-8')
            pages[file] = Page(source)
            duplicates = [key for key, n in Counter(pages[file].ids).items() if n > 1]
            if duplicates:
                errors.append(f'{file.relative_to(site)}: identificadores duplicados {duplicates}')
            if re.search(r'quarto-unresolved-ref|katex-error|\?@(?:sec|fig)-', source):
                errors.append(f'{file.relative_to(site)}: referencia o fórmula sin resolver')
    for file, page in list(pages.items()):
        base = 'https://book.invalid/' + file.relative_to(site).as_posix()
        for tag, raw in page.links:
            url = urlsplit(urljoin(base, raw))
            if url.netloc != 'book.invalid' or url.scheme != 'https':
                continue
            target = site / unquote(url.path.lstrip('/'))
            if url.path.endswith('/'):
                target /= 'index.html'
            target = target.resolve()
            if not target.is_relative_to(site) or not target.is_file():
                errors.append(f'{file.relative_to(site)}: destino ausente {raw}')
                continue
            if url.fragment and target.suffix == '.html':
                if target not in pages:
                    pages[target] = Page(target.read_text(encoding='utf-8'))
                if unquote(url.fragment) not in pages[target].ids:
                    errors.append(f'{file.relative_to(site)}: ancla ausente {raw}')
            if tag == 'a':
                links += 1
            else:
                resources += 1
    names = ['index.html', 'indice.html', 'actividades.html', 'avisos.html']
    names += [str(Path(name).with_suffix('.html')) for name in meta['translated_chapters']]
    for prefix, other in (('', 'en/'), ('en/', '../')):
        for name in names:
            page = pages.get(site / prefix / name)
            if page is None:
                errors.append(f'{prefix}{name}: falta una página de la edición')
            elif page.selector_count != 1 or other + name not in page.selector_links:
                errors.append(f'{prefix}{name}: selector de edición ausente o incorrecto')
    for name, phrase in (('index.html', 'AI-generated translation'),
                         ('avisos.html', 'AI-generated English translation')):
        page = pages.get(site / 'en' / name)
        text = ' '.join(' '.join(page.text).split()) if page else ''
        if phrase not in text or meta['source_doi'] not in text:
            errors.append(f'en/{name}: aviso de traducción u original no identificado')
        if not re.search(r'reviewed the English text manually', text, re.IGNORECASE):
            errors.append(f'en/{name}: estado de revisión humana no identificado')
        if meta.get('doi') and meta['doi'] not in text:
            errors.append(f'en/{name}: falta el DOI propio de la traducción')
    return {'pages': len(pages), 'links': links, 'resources': resources,
            'edition_pages': len(names), 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, required=True)
    parser.add_argument('--informe', type=Path)
    args = parser.parse_args()
    meta = json.loads((BOOK / 'en/traduccion.json').read_text(encoding='utf-8'))
    report = comprobar(args.site.resolve(), meta)
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.informe:
        args.informe.parent.mkdir(parents=True, exist_ok=True)
        args.informe.write_text(text, encoding='utf-8')
    print(text, end='')
    raise SystemExit(bool(report['errors']))


if __name__ == '__main__':
    main()
