"""Prepara la edición PDF completa: render de Quarto, configuración y silabeo.

Uso: python3 preparar.py LIBRO TRABAJO [QUARTO]
  LIBRO    copia limpia de genetic-algorithms-lab-book (no se modifica salvo _book/ y
           los archivos que regenera el propio pre-render de Quarto)
  TRABAJO  carpeta temporal donde se escriben config.json, silabeo.json y quarto.log
  QUARTO   ejecutable de Quarto (por defecto, «quarto» del PATH)

No modifica ningún .qmd. Las adaptaciones de impresión se hacen después, en el DOM.
"""
from pathlib import Path
import hashlib, json, os, re, subprocess, sys
import yaml

BOOK = Path(sys.argv[1]).resolve()
WORK = Path(sys.argv[2]).resolve()
QUARTO = sys.argv[3] if len(sys.argv) > 3 else 'quarto'
WORK.mkdir(parents=True, exist_ok=True)

provenance_file = None
if '--procedencia' in sys.argv:
    provenance_file = Path(sys.argv[sys.argv.index('--procedencia') + 1]).resolve()
    provenance = json.loads(provenance_file.read_text(encoding='utf-8'))
    commit = provenance['base']
    changed = [' M ' + n for n in provenance['archivos_superpuestos']]
    for n, expected in provenance['archivos_superpuestos'].items():
        assert hashlib.sha256((BOOK / n).read_bytes()).hexdigest() == expected, 'Fuente modificada: ' + n
else:
    git = lambda *a: subprocess.check_output(['git', '-C', str(BOOK), *a], text=True).strip()
    commit = git('rev-parse', 'HEAD')
    changed = [l for l in git('status', '--porcelain', '--untracked-files=no').splitlines() if l.strip()]

if '--sin-render' not in sys.argv:
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    with (WORK / 'quarto.log').open('w', encoding='utf-8') as log:
        p = subprocess.run([QUARTO, 'render'], cwd=BOOK, env=env, stdout=log, stderr=subprocess.STDOUT)
    assert p.returncode == 0, 'Quarto terminó con error'
    assert 'WARN' not in (WORK / 'quarto.log').read_text(encoding='utf-8'), 'Quarto emitió avisos'

meta = yaml.safe_load((BOOK / '_quarto.yml').read_text(encoding='utf-8'))
book = meta['book']
files = [Path(c).with_suffix('.html').name for c in book['chapters']]
# El índice general web (indice.qmd) se sustituye en el PDF por un índice con páginas.
included = [f for f in files if f != 'indice.html']

def key_for(name):
    m = re.match(r'(\d\d)-', name)
    if m: return 'c' + m.group(1)
    return {'index.html': 'leer', 'actividades.html': 'actividades', 'avisos.html': 'avisos'}[name]

authors = []
for a in book['author']:
    authors.append({'name': a['name'], 'orcid': a.get('orcid'), 'url': a.get('url'),
                    'corresponding': bool(a.get('corresponding')),
                    'affiliations': [', '.join(x for x in [af.get('department'), af.get('name'), af.get('city'), af.get('country')] if x)
                                     for af in a.get('affiliations', [])]})

config = {
    'title': book['title'], 'subtitle': book['subtitle'], 'authors': authors,
    'version': meta['libro-version'], 'revision': meta['libro-revision'], 'first_published': str(book['date']),
    'doi': meta.get('libro-doi'), 'portal_doi': meta.get('portal-doi'),
    'procedencia': str(provenance_file) if provenance_file else None,
    'site': book['site-url'].rstrip('/') + '/', 'repo': book['repo-url'],
    'commit': commit, 'cambios_locales': changed,
    'files': [{'file': f, 'key': key_for(f)} for f in included],
    'replaced': {'indice.html': 'pdf-indice'},
}
(WORK / 'config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Puntos de corte discrecionales (Pyphen, español, mínimo tres letras a cada lado), como en el piloto.
import pyphen
dic = pyphen.Pyphen(lang='es', left=3, right=3)
words = set()
for f in included:
    words |= set(re.findall(r'\b[a-záéíóúüñ]{7,}\b', (BOOK / '_book' / f).read_text(encoding='utf-8')))
mapping = {w: dic.inserted(w, hyphen='­') for w in sorted(words)}
mapping = {w: v for w, v in mapping.items() if w != v}
(WORK / 'silabeo.json').write_text(json.dumps(mapping, ensure_ascii=False), encoding='utf-8')

procedencia = {
    'commit': commit, 'cambios_locales': changed, 'pyphen': pyphen.__version__,
    'diccionario': 'es; mínimo tres letras a cada lado', 'palabras_con_puntos_de_corte': len(mapping),
    'html': {f: hashlib.sha256((BOOK / '_book' / f).read_bytes()).hexdigest() for f in included},
    'sha256_bibliografia': hashlib.sha256((BOOK / 'referencias.bib').read_bytes()).hexdigest(),
}
(WORK / 'procedencia.json').write_text(json.dumps(procedencia, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'commit': commit, 'cambios_locales': changed, 'archivos': len(included), 'silabeo': len(mapping)}, ensure_ascii=False))
