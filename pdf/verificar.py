"""Comprobaciones automáticas del PDF completo. Uso: python3 verificar.py LIBRO TRABAJO PDF
Escribe TRABAJO/resultado.json y termina con error si alguna comprobación falla."""
from pathlib import Path
import glob, hashlib, json, re, subprocess, sys
from pypdf import PdfReader

BOOK, WORK, PDF = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
est = json.loads((WORK / 'estructura.json').read_text(encoding='utf-8'))
render = json.loads((WORK / 'render.json').read_text(encoding='utf-8'))
r = PdfReader(PDF)
n = len(r.pages); names = r.named_destinations
fails = []
def check(cond, msg):
    if not cond: fails.append(msg)

# Paginación y etiquetas.
labels = r.page_labels
body = est['map'][next(p['key'] for p in est['structure'] if p['number'])]
check(labels[body] == '1', 'el capítulo 1 no empieza en la página 1')
check(all(re.fullmatch(r'[ivxlc]+', labels[i]) for i in range(body)), 'preliminares sin numeración romana')
check(n == est['total'], 'el número de páginas cambió en el posproceso')

# Enlaces internos y externos.
internal, invalid, uris, fwd, back, cross = 0, [], [], set(), set(), 0
sol_start = {p['key']: est['map'][s['id']] for p in est['structure'] for s in p['sections'] if s['id'].endswith('--soluciones-ejercicios')}
for i, page in enumerate(r.pages):
    for ref in page.get('/Annots', []) or []:
        a = ref.get_object(); act = a.get('/A')
        if act and act.get('/S') == '/URI': uris.append(str(act['/URI'])); continue
        d = a.get('/Dest') or (act.get('/D') if act and act.get('/S') == '/GoTo' else None)
        if d is None: continue
        internal += 1
        key = str(d).lstrip('/')
        if key not in names and '/' + key not in names: invalid.append({'pagina': i + 1, 'destino': key}); continue
        target = r.get_destination_page_number(names.get(key) or names.get('/' + key))
        m = re.match(r'(c\d\d)--', key)
        part_here = max((est['map'][p['key']], p['key']) for p in est['structure'] if est['map'][p['key']] <= i)[1] if i >= body else None
        if m and part_here and m.group(1) != part_here: cross += 1
        if '--pdf-solucion-' in key: fwd.add(key.replace('pdf-solucion-', ''))
        elif re.match(r'c\d\d--ejercicio-', key) and target < i and i >= sol_start.get(key[:3], n): back.add(key)
check(not invalid, f'{len(invalid)} enlaces internos sin destino')
local = [u for u in uris if re.search(r'localhost|127\.0\.0\.1|file:', u)]
check(not local, 'URLs locales en el PDF')
# En las soluciones también hay remisiones a otros ejercicios; basta con que cada ida tenga su vuelta.
check(len(fwd) == render['geometry']['counts']['solutions'], f'enlaces de ida: {len(fwd)}')
check(fwd <= back, f'soluciones sin enlace de vuelta: {sorted(fwd - back)[:5]}')

# Enlaces a las aplicaciones: todos los del HTML (con parámetros) siguen en el PDF.
apps = set()
for f in est['config']['files']:
    html = (BOOK / '_book' / f['file']).read_text(encoding='utf-8')
    main = html[html.find('<main'):html.find('</main>')]
    main = re.sub(r'<details class="incrustada">.*?</details>', '', main, flags=re.S)
    for h in re.findall(r'href="(https://[^"]+)"', main):
        h = h.replace('&amp;', '&')
        if re.match(r'https://(josemagalan\.github\.io/(?!genetic-algorithms-lab-book)|evotraveller\.|josemagalan\.shinyapps)', h): apps.add(h)
missing_apps = sorted(apps - set(uris))
check(not missing_apps, f'{len(missing_apps)} enlaces de aplicaciones perdidos')

# Marcadores con destino válido.
outline = []
def walk(items, depth=0):
    for it in items:
        if isinstance(it, list): walk(it, depth + 1)
        else:
            p = r.get_destination_page_number(it); outline.append((depth, str(it['/Title']), p + 1))
            check(p is not None and 0 <= p < n, f'marcador sin página: {it["/Title"]}')
walk(r.outline)

# Índice: los números impresos son los de los destinos.
toc_text = ''.join(r.pages[i].extract_text() or '' for i in range(2, body))
sample = [(s['number'], labels[est['map'][s['id']]]) for p in est['structure'] if p['number'] for s in p['sections'] if s['number']]
missing_toc = [s for s, pg in sample if not re.search(rf'{re.escape(s)}\s.*?{pg}\s*$', toc_text, re.M)]
check(not missing_toc, f'índice: {len(missing_toc)} secciones con página no localizada {missing_toc[:5]}')

# Fuentes incrustadas: inspección de los objetos PDF (el Poppler incluido no trae pdffonts).
fonts, not_emb = set(), set()
for page in r.pages:
    resources = page.get('/Resources')
    for font_ref in ((resources.get_object().get('/Font') or {}).get_object().values() if resources and resources.get_object().get('/Font') else []):
        font = font_ref.get_object()
        descendants = font.get('/DescendantFonts') or [font_ref]
        for item in descendants:
            leaf = item.get_object()
            name = str(leaf.get('/BaseFont') or font.get('/BaseFont'))
            fonts.add(name)
            descriptor = leaf.get('/FontDescriptor')
            if leaf.get('/Subtype') == '/Type3':
                # Type 3: los glifos se definen en el propio PDF (/CharProcs); no hay fichero de fuente
                # externo ni /BaseFont. Es incrustación por definición (pdffonts lo marca emb=yes).
                if '/BaseFont' not in leaf: name = '[Type3 sin nombre]'; fonts.add(name)
                embedded = '/CharProcs' in leaf
            else:
                embedded = descriptor and any(key in descriptor.get_object() for key in ('/FontFile', '/FontFile2', '/FontFile3'))
            if not embedded: not_emb.add(name)
fonts.discard('None')
# Contraste con pdffonts cuando está disponible (Poppler completo); si no, basta la inspección de objetos.
import shutil
if shutil.which('pdffonts'):
    rows = subprocess.run(['pdffonts', str(PDF)], capture_output=True, text=True).stdout.splitlines()[2:]
    not_emb |= {'pdffonts: ' + l.split()[0] for l in rows if l.split()[-5] != 'yes'}
check(not not_emb, f'fuentes sin incrustar: {sorted(not_emb)}')
meta = r.metadata
check('Evolución a la vista' in (meta.title or ''), 'título de metadatos')
check(all(a['name'] in (meta.author or '') for a in est['config']['authors']), 'autoría de metadatos')

# La web no cambia: soluciones plegadas en su caja y sin apéndice de impresión.
web = {'soluciones_plegadas': 0, 'apendice_impresion': 0}
for f in glob.glob(str(BOOK / '_book' / '[01][0-9]-*.html')):
    h = Path(f).read_text(encoding='utf-8')
    web['soluciones_plegadas'] += len(re.findall(r'<summary>\s*(?:<strong>)?\s*Ver la solución\s*(?:</strong>)?\s*</summary>', h))
    web['apendice_impresion'] += h.count('pdf-solution') + h.count('Soluciones de los ejercicios')
check(web['soluciones_plegadas'] == render['geometry']['counts']['solutions'] and web['apendice_impresion'] == 0, f'web: {web}')
config = est['config']
if config.get('procedencia'):
    provenance = json.loads(Path(config['procedencia']).read_text(encoding='utf-8'))
    cambios = config['cambios_locales']
    for name, expected in provenance['archivos_superpuestos'].items():
        check(hashlib.sha256((BOOK / name).read_bytes()).hexdigest() == expected, 'fuente alterada: ' + name)
    source_commit = provenance['base']
else:
    git = lambda *a: subprocess.check_output(['git', '-C', str(BOOK), *a], text=True).strip()
    cambios = [l for l in git('status', '--porcelain', '--untracked-files=no').splitlines() if l]
    source_commit = git('rev-parse', 'HEAD')
# Cambios locales declarados (p. ej. «M index.qmd») se admiten con PERMITIR_CAMBIOS y se registran.
import os
permitidos = [x for x in os.environ.get('PERMITIR_CAMBIOS', '').split(',') if x]
check(all(any(l.endswith(' ' + f) for f in permitidos) for l in cambios), f'cambios en las fuentes: {cambios}')

if shutil.which('pdftotext'):
    text = subprocess.run(['pdftotext', '-layout', str(PDF), '-'], capture_output=True, text=True, encoding='utf-8').stdout
else:  # el Poppler del runtime de Windows no trae pdftotext; pdfplumber es mucho más lento.
    import pdfplumber
    with pdfplumber.open(PDF) as document:
        text = '\n'.join(page.extract_text(layout=True) or '' for page in document.pages)
for doi in (config.get('doi'), config.get('portal_doi')):
    if doi: check('https://doi.org/' + doi in uris, 'DOI sin enlace en PDF: ' + doi)
hyphen_lines = len(re.findall(r'[a-záéíóúñ]\u00ad?-[ \t]*\n', text))
unresolved = re.findall(r'\?\?|@\w+\d{4}', text)
check(not unresolved, f'referencias sin resolver: {unresolved[:5]}')

res = {'pdf': str(PDF), 'paginas': n, 'bytes': PDF.stat().st_size, 'sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(),
       'commit_base': source_commit, 'cambios_en_fuentes': cambios, 'inicio_cuerpo': body + 1,
       'partes': {p['key']: {'pdf': est['map'][p['key']] + 1, 'folio': labels[est['map'][p['key']]]} for p in est['structure']},
       'enlaces_internos': internal, 'remisiones_entre_capitulos': cross, 'enlaces_externos': len(uris),
       'enlaces_aplicaciones_html': len(apps), 'enlaces_aplicaciones_perdidos': missing_apps,
       'pares_ida_vuelta': len(fwd & back), 'marcadores': len(outline), 'secciones_en_indice': len(sample),
       'lineas_con_guion_final': hyphen_lines, 'fuentes': sorted({re.sub(r'^/[A-Z]{6}\+', '', name) for name in fonts}),
       'web': web, 'conteos': render['geometry']['counts'], 'fallos': fails}
(WORK / 'resultado.json').write_text(json.dumps(res, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in res.items() if k not in ('partes', 'fuentes')}, ensure_ascii=False))
sys.exit(1 if fails else 0)
