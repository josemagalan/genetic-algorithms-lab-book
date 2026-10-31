"""Folios, cabeceras, etiquetas de página, marcadores y metadatos del PDF completo.

Uso: python3 posproceso.py TRABAJO SALIDA.pdf
Lee TRABAJO/estructura.json y la última pasada de Chromium. Chromium imprime sin cabecera ni pie;
aquí se añaden en una capa aparte, para poder omitirlos en la portada, los créditos y las
páginas de apertura, y para numerar en romanos las páginas preliminares.
"""
from pathlib import Path
import io, json, sys
from fontTools.ttLib import TTFont
from pypdf import PdfReader, PdfWriter
from pypdf.generic import Fit
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLFont
from reportlab.lib.units import mm

WORK = Path(sys.argv[1]); OUT = Path(sys.argv[2])
HERE = Path(__file__).resolve().parent
data = json.loads((WORK / 'estructura.json').read_text(encoding='utf-8'))
src = WORK / f"pasada-{data['pass']}.pdf"
reader = PdfReader(src)
n = len(reader.pages)
pmap = data['map']; structure = data['structure']; config = data['config']; full = data['full']

# Fuente de folios y cabeceras: la misma Noto Sans (OFL), convertida de woff2 a TTF.
for weight in ('400', '600'):
    ttf = WORK / f'noto-sans-{weight}.ttf'
    if not ttf.exists():
        f = TTFont(HERE / f'fuentes/noto-sans-latin-{weight}-normal.woff2'); f.flavor = None; f.save(ttf)
    pdfmetrics.registerFont(RLFont(f'Noto{weight}', str(ttf)))

def roman(k):
    out = ''
    for s, v in [('m', 1000), ('cm', 900), ('d', 500), ('cd', 400), ('c', 100), ('xc', 90), ('l', 50), ('xl', 40), ('x', 10), ('ix', 9), ('v', 5), ('iv', 4), ('i', 1)]:
        while k >= v: out += s; k -= v
    return out

chapters = [p for p in structure if p['number']]
body = pmap[chapters[0]['key']] if (full and chapters) else 0
labels = [str(i - body + 1) if i >= body else roman(i + 1) for i in range(n)]
starts = sorted((pmap[p['key']], p) for p in structure)
running = [None] * n
for idx, (start, part) in enumerate(starts):
    end = starts[idx + 1][0] if idx + 1 < len(starts) else n
    head = f"{part['number']}  ·  {part['title']}" if part['number'] else part['title']
    for i in range(start + 1, end): running[i] = head
no_folio = set()
if full:
    no_folio = {0, 1}   # portada y créditos (una página; lo comprueba verificar.py)
openings = {s for s, _ in starts}

buf = io.BytesIO()
W, H = 210 * mm, 297 * mm
c = canvas.Canvas(buf, pagesize=(W, H), initialFontName='Noto400', initialFontSize=8.5)
grey = (0.45, 0.48, 0.52)
for i in range(n):
    if i not in no_folio:
        c.setFont('Noto400', 8.5); c.setFillColorRGB(*grey)
        c.drawCentredString(W / 2, 9 * mm, labels[i])
    if running[i] and i not in openings:
        c.setFont('Noto400', 7.5); c.setFillColorRGB(*grey)
        c.drawRightString(W - 18 * mm, H - 10 * mm, running[i])
        c.drawString(18 * mm, H - 10 * mm, config['title'])
        c.setStrokeColorRGB(0.82, 0.84, 0.86); c.setLineWidth(0.3)
        c.line(18 * mm, H - 11.6 * mm, W - 18 * mm, H - 11.6 * mm)
    c.showPage()
c.save()
overlay = PdfReader(io.BytesIO(buf.getvalue()))

writer = PdfWriter(clone_from=reader)
if full:   # portada a sangre, impresa aparte por libro.cjs
    writer.pages[0].merge_page(PdfReader(WORK / 'portada.pdf').pages[0])
for i, page in enumerate(writer.pages):
    page.merge_page(overlay.pages[i])
    page.compress_content_streams()   # pypdf descomprime al fusionar
writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)

# Etiquetas: preliminares en romanos y cuerpo en arábigos, iguales a los del índice.
if body > 0:
    writer.set_page_label(0, body - 1, style='/r', start=1)
writer.set_page_label(body, n - 1, style='/D', start=1)

# Marcadores limpios: partes y secciones de nivel 2, con sus destinos exactos.
names = reader.named_destinations
def dest(id_):
    d = names.get(id_) or names.get('/' + id_)
    if d is None: return None
    left = d.get('/Left') or 0; top = d.get('/Top')
    return reader.get_destination_page_number(d), Fit.xyz(left=left, top=top)
outline = []
if full:
    writer.add_outline_item('Portada', 0, fit=Fit.fit()); writer.add_outline_item('Créditos', 1, fit=Fit.fit()); outline += ['Portada', 'Créditos']
    if dest('pdf-indice'): p, fit = dest('pdf-indice'); writer.add_outline_item('Índice', p, fit=fit); outline.append('Índice')
for part in structure:
    d = dest(part['key'])
    p, fit = d if d else (pmap[part['key']], Fit.fit())
    title = f"{part['number']}. {part['title']}" if part['number'] else part['title']
    parent = writer.add_outline_item(title, p, fit=fit); outline.append(title)
    if not part['number']: continue
    for s in part['sections']:
        d = dest(s['id'])
        if not d: continue
        t = f"{s['number']} {s['title']}" if s['number'] else s['title']
        writer.add_outline_item(t, d[0], parent=parent, fit=d[1]); outline.append(t)
writer.page_mode = '/UseOutlines'

authors = '; '.join(a['name'] for a in config['authors'])
writer.add_metadata({
    '/Title': f"{config['title']}. {config['subtitle']}",
    '/Author': authors,
    '/Subject': f"Edición PDF de la versión {config['version']} (base {config['commit'][:7]}{' con cambios locales' if config.get('cambios_locales') else ''}). Texto CC BY 4.0. DOI {config.get('doi', '')}",
    '/DOI': config.get('doi', ''),
    '/Keywords': 'algoritmos genéticos, computación evolutiva, metaheurísticas, laboratorio interactivo, educación',
    '/Creator': 'Quarto 1.10.19 y Chromium (Playwright); generador de la edición PDF de Libro-GA',
})
from pypdf.generic import NameObject, TextStringObject
writer._root_object[NameObject('/Lang')] = TextStringObject('es-ES')
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('wb') as fh: writer.write(fh)
(WORK / 'posproceso.json').write_text(json.dumps({'paginas': n, 'inicio_cuerpo': body, 'marcadores': len(outline),
    'etiquetas': {'primera': labels[0], 'cuerpo': labels[body] if n else None, 'ultima': labels[-1]}}, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps({'pdf': str(OUT), 'paginas': n, 'inicio_cuerpo': body, 'marcadores': len(outline)}, ensure_ascii=False))
