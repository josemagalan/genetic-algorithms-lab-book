"""Genera el sitio bilingüe en copias aisladas, sin modificar las fuentes.

Español: HEAD del repositorio. Inglés: edición fijada en en/traduccion.json,
con las traducciones de en/ superpuestas. Los capítulos aún no traducidos son
páginas explícitas de acceso al original, no traducciones aparentes.
Solo biblioteca estándar; Quarto y Python deben estar instalados.
"""
from pathlib import Path
import argparse
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

BOOK = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(BOOK), *args], encoding='utf-8').strip()


def exportar(ref, destino, archivo):
    with archivo.open('wb') as out:
        subprocess.run(['git', '-C', str(BOOK), 'archive', '--format=zip', ref], stdout=out, check=True)
    destino.mkdir()
    with zipfile.ZipFile(archivo) as z:
        for name in z.namelist():
            if not (destino / name).resolve().is_relative_to(destino.resolve()):
                raise ValueError(f'Ruta fuera de la copia: {name}')
        z.extractall(destino)


def modulo_indices(raiz):
    spec = importlib.util.spec_from_file_location('indices_edicion', raiz / 'filtros/indices.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sin_hooks(texto):
    """Los índices ingleses se preparan antes; no ejecutar los hooks españoles."""
    resultado = []
    dentro = False
    for linea in texto.splitlines():
        if re.match(r'^  (pre-render|post-render):', linea):
            dentro = True
            continue
        if dentro and (not linea.strip() or len(linea) - len(linea.lstrip()) > 2):
            continue
        dentro = False
        if re.match(r'^  (cover-image|cover-image-alt|repo-actions):', linea):
            continue
        resultado.append(linea)
    return '\n'.join(resultado) + '\n'


NIVELES_EN = {'basico': ('Basic', 'B'), 'avanzado': ('Advanced', 'A'), 'saber-mas': ('Further reading', '+')}
HERRAMIENTAS_EN = {
    'portal': 'Genetic Algorithms Lab portal',
    'representation-ga': 'representation-ga · Representation',
    'initialization-and-evaluation-ga': 'initialization-and-evaluation-ga · Initialization and Evaluation',
    'selection-ga': 'selection-ga · Selection',
    'crossover-ga': 'crossover-ga · Crossover',
    'mutation-ga': 'mutation-ga · Mutation',
    'evotraveller': 'EvoTraveller',
    'selectionmechanisms': 'SelectionMechanisms',
}


def insignia_en(nivel, larga=False):
    largo, corto = NIVELES_EN[nivel]
    if larga:
        return f'[[{largo}]{{.largo}}[{corto}]{{.corto}}]{{.nivel .{nivel}}}'
    return f'[[{corto}]{{.corto}}]{{.nivel .{nivel} .solo-corto}}'


def enumerar_en(partes):
    if len(partes) < 3:
        return ' and '.join(partes)
    return ', '.join(partes[:-1]) + ', and ' + partes[-1]


def indices_ingles(module, caps, destino):
    """Índice general y de actividades en inglés, con la estructura de filtros/indices.py."""
    assert list(HERRAMIENTAS_EN) == list(module.HERRAMIENTAS), 'Herramientas distintas de filtros/indices.py'
    assert list(NIVELES_EN) == list(module.NIVELES), 'Niveles distintos de filtros/indices.py'
    tipos = ('ejemplo', 'en-app', 'ejercicio')
    total = {k: sum(1 for c in caps for s in c['secciones'] if s['nivel'] == k) for k in NIVELES_EN}
    cajas = {k: sum(1 for c in caps for b in c['cajas'] if b['tipo'] == k) for k in tipos}

    def enlace_caja(c, b):
        ancla = b['ancla'] or (b['seccion']['ancla'] if b['seccion'] else None)
        if b['tipo'] == 'en-app':
            texto = 'In the Application'
        else:
            texto = f"{'Example' if b['tipo'] == 'ejemplo' else 'Exercise'} {b['numero']}"
        return f"[{texto}]({c['archivo']}#{ancla})" if ancla else texto

    def nombre_caja(b):
        nombre = b['nombre']
        if b['tipo'] == 'en-app':
            # «selection-ga, “Steady state”» → «“Steady state”»; sin subtítulo, la caja explora la sección
            m = re.match(r'^[^,“]+(?:,\s*(.*))?$', nombre)
            nombre = (m.group(1) or '').strip() if m else nombre
            nombre = nombre or 'Free exploration'
        return module.celda(nombre)

    def nivel(b):
        return insignia_en(b['seccion']['nivel']) if b['seccion'] else ''

    herramientas = lambda claves: ', '.join(module.NOMBRE_CORTO.get(k, k) for k in claves) or '—'

    indice = ['# Contents {.unnumbered #sec-indice}', '',
              f"The book has {len(caps)} chapters and {sum(total.values())} sections: "
              f"{total['basico']} at the {insignia_en('basico', True)} level, {total['avanzado']} at the "
              f"{insignia_en('avanzado', True)} level, and {total['saber-mas']} at the {insignia_en('saber-mas', True)} level. "
              'The **basic path** consists of the blue sections: they can be read in order, chapter by chapter, '
              'without the others. The advanced sections extend the basic path and usually build on it; '
              '“Further reading” closes each chapter with readings and topics the book does not develop.', '',
              f"The activities—{cajas['ejemplo']} reproducible examples, {cajas['en-app']} “In the Application” "
              f"boxes, and {cajas['ejercicio']} exercises—are listed in the "
              '[activity index](actividades.qmd), by tool and by chapter.', '',
              '## The Book at a Glance {.unnumbered #vistazo}', '',
              '| Chapter | B | A | + | Examples | In the Application | Exercises |',
              '|---|:-:|:-:|:-:|:-:|:-:|:-:|']
    for c in caps:
        n = {k: sum(1 for s in c['secciones'] if s['nivel'] == k) for k in NIVELES_EN}
        b = {k: sum(1 for x in c['cajas'] if x['tipo'] == k) for k in tipos}
        indice.append(f"| [{c['numero']}. {module.celda(c['titulo'])}]({c['archivo']}) | {n['basico']} | "
                      f"{n['avanzado']} | {n['saber-mas']} | {b['ejemplo']} | {b['en-app']} | {b['ejercicio']} |")
    indice += [f"| **Total** | **{total['basico']}** | **{total['avanzado']}** | **{total['saber-mas']}** | "
               f"**{cajas['ejemplo']}** | **{cajas['en-app']}** | **{cajas['ejercicio']}** |", '']
    for c in caps:
        indice += [f"## {c['numero']}. {c['titulo']} {{.unnumbered #cap-{c['numero']}}}", '']
        indice += [f"- [{s['num']} {s['titulo']}]({c['archivo']}#{s['ancla']}) {insignia_en(s['nivel'])}"
                   for s in c['secciones']]
        indice += ['']

    actividades = ['# Activity Index {.unnumbered #sec-actividades}', '',
                   'This page lists every activity box in the book. **Reproducible examples** open the tool '
                   'in a fixed state, so the result matches the one in the book (with EvoTraveller and '
                   'SelectionMechanisms, the **⚙ Open and configure** button opens the application, and the '
                   'example gives the values to enter). **In the Application** boxes invite you to explore '
                   'without fixed results, and **exercises** are worked out with pencil and paper. The first '
                   'part sorts the boxes by tool, to help you prepare a session around a particular application; '
                   'the second sorts them by chapter. The level column gives the level of the section that '
                   'contains each box.', '',
                   '## By Tool {.unnumbered #por-herramienta}', '']
    for clave, nombre in HERRAMIENTAS_EN.items():
        filas = [(c, b) for c in caps for b in c['cajas'] if clave in b['herramientas']]
        if not filas:
            continue
        cuenta = {k: sum(1 for _, b in filas if b['tipo'] == k) for k in tipos}
        partes = [f'{n} {uno if n == 1 else varios}' for n, uno, varios in (
            (cuenta['ejemplo'], 'reproducible example', 'reproducible examples'),
            (cuenta['en-app'], '“In the Application” box', '“In the Application” boxes'),
            (cuenta['ejercicio'], 'exercise', 'exercises')) if n]
        frase = enumerar_en(partes)
        actividades += [f"### {nombre} {{.unnumbered #h-{clave}}}", '', frase[0].upper() + frase[1:] + '.', '',
                        '| Activity | Title | Section | Level |', '|---|---|:-:|:-:|']
        actividades += [f"| {enlace_caja(c, b)} | {nombre_caja(b)} | {module.enlace_seccion(c, b['seccion'])} | {nivel(b)} |"
                        for c, b in filas]
        actividades += ['']
    actividades += ['## By Chapter {.unnumbered #por-capitulo}', '']
    for c in caps:
        if not c['cajas']:
            continue
        actividades += [f"### {c['numero']}. {c['titulo']} {{.unnumbered #a-cap-{c['numero']}}}", '',
                        '| Activity | Title | Section | Tool | Level |', '|---|---|:-:|---|:-:|']
        actividades += [f"| {enlace_caja(c, b)} | {nombre_caja(b)} | {module.enlace_seccion(c, b['seccion'])} | "
                        f"{herramientas(b['herramientas'])} | {nivel(b)} |" for b in c['cajas']]
        actividades += ['']
    (destino / 'indice.qmd').write_text('\n'.join(indice) + '\n', encoding='utf-8')
    (destino / 'actividades.qmd').write_text('\n'.join(actividades) + '\n', encoding='utf-8')


def preparar_ingles(destino, meta):
    for fuente in (BOOK / 'en').glob('*.qmd'):
        shutil.copyfile(fuente, destino / fuente.name)
    spec = importlib.util.spec_from_file_location('figuras_ingles', BOOK / 'bilingue/figuras.py')
    figuras = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(figuras)
    variantes = figuras.generar(destino / 'figuras', destino / 'figuras', BOOK / 'en/figuras.json')
    # La portada necesita composición inglesa propia, además de traducir rótulos.
    # Se superpone solo en esta copia; el original español permanece intacto.
    portadas = {}
    for fuente in sorted((BOOK / 'en/figuras').glob('*.svg')):
        shutil.copyfile(fuente, destino / 'figuras' / fuente.name)
        portadas[fuente.name] = digest(fuente)
    module = modulo_indices(destino)
    caps = [module.leer(a, n) for n, a in enumerate(module.capitulos(), 1)]
    # Se calcula antes de preparar las páginas de acceso: conserva la numeración
    # completa de la edición fuente y las remisiones hacia sus secciones.
    (destino / '_numeracion.json').write_text(module.numeracion(caps), encoding='utf-8')
    traducidos = [c for c in caps if c['archivo'] in meta['translated_chapters']]
    indices_ingles(module, traducidos, destino)
    referencias_original = {}
    anclas_original = {}
    for c in caps:
        if c['archivo'] in meta['translated_chapters']:
            continue
        titulo = meta['chapter_titles'][c['archivo']]
        url = '../' + Path(c['archivo']).with_suffix('.html').name
        original = (destino / c['archivo']).read_text(encoding='utf-8')
        ids = list(dict.fromkeys(re.findall(r'\{[^}\n]*#([\w-]+)', original)))
        anclas_original.update({i: url + '#' + i for i in ids})
        anclas = '\n'.join(f'<span id="{html.escape(i, quote=True)}"></span>' for i in ids if i != c['id'])
        for s in c['secciones']:
            referencias_original[s['ancla']] = (s['num'], url + '#' + s['ancla'])
        texto = (f"# {titulo} · Spanish Original {{#{c['id']}}}\n\n"
                 '::: {.callout-note title="Spanish Original"}\n'
                 'This chapter has not yet been translated into English. '
                 'The entry preserves the chapter numbering and provides access to the original.\n\n'
                 f'[Read chapter {c["numero"]} in Spanish]({url})\n:::\n\n{anclas}\n')
        (destino / c['archivo']).write_text(texto, encoding='utf-8')
    # Los span de acceso no son secciones numeradas de Quarto. Resolver en la
    # copia de compilación las remisiones a secciones aún españolas, usando su
    # numeración original y enlazando directamente a la sección real en español.
    # Las fuentes editoriales inglesas conservan sus identificadores cotejables.
    for c in traducidos:
        p = destino / c['archivo']
        texto = p.read_text(encoding='utf-8')
        texto = re.sub(r'-@([\w-]+)', lambda m: ('[' + referencias_original[m[1]][0] + ']('
                       + referencias_original[m[1]][1] + ')') if m[1] in referencias_original else m[0], texto)
        texto = re.sub(r'(\[[^\]\n]+\])\(#([\w-]+)\)', lambda m: (m[1] + '(' + anclas_original[m[2]] + ')')
                       if m[2] in anclas_original else m[0], texto)
        p.write_text(texto, encoding='utf-8')
    config = destino / '_quarto.yml'
    config.write_text(sin_hooks(config.read_text(encoding='utf-8')), encoding='utf-8')
    shutil.copyfile(BOOK / 'en/_quarto-en.yml', destino / '_quarto-en.yml')
    # El resto de la copia sale de la etiqueta fuente (v1.0). La bibliografía y el
    # estilo de citas se toman de la copia de trabajo para que sus correcciones
    # posteriores lleguen también a la edición inglesa.
    shutil.copyfile(BOOK / 'referencias.bib', destino / 'referencias.bib')
    shutil.copyfile(BOOK / 'vendor/csl/apa.csl', destino / 'vendor/csl/apa.csl')
    # Número de artículo (APA): el .bib lo da en español, «Artículo 72».
    bib = destino / 'referencias.bib'
    bib.write_text(re.sub(r'(pages\s*=\s*\{)Artículo ', r'\1Article ', bib.read_text(encoding='utf-8')),
                   encoding='utf-8')
    # Versión inglesa del mismo CSL: se revierten los ajustes españoles
    # documentados en vendor/csl/LEEME.md. Se conserva su licencia CC BY-SA.
    csl = (destino / 'vendor/csl/apa.csl').read_text(encoding='utf-8')
    csl = csl.replace('default-locale="es-ES"', 'default-locale="en-US"').replace('and="text"', 'and="symbol"')
    # Etiqueta de capítulo (cambio 4 de vendor/csl/LEEME.md): en minúscula en
    # español («capítulo 5») y con mayúscula en inglés («Chapter 5»), como «Section».
    capitulo = '<else-if locator="chapter">\n          <label variable="locator"/>'
    assert capitulo in csl
    csl = csl.replace(capitulo, capitulo.replace('<label ', '<label text-case="capitalize-first" '))
    (destino / 'vendor/csl/apa-en.csl').write_text(csl, encoding='utf-8')
    for archivo, cambios in {
        'plantillas/title-metadata.html': {
            'Filiación ': 'Affiliation ', 'Autor de correspondencia': 'Corresponding author'},
        'comentarios.js': {
            'Enviar un comentario sobre esta página': 'Send a comment about this page',
            '¿Has visto una errata o un resultado distinto? ': 'Found a typo or a different result? ',
            ' (con una cuenta de GitHub) o ': ' (with a GitHub account), or ',
            'escribe a los autores': 'contact the authors'},
    }.items():
        path = destino / archivo
        texto = path.read_text(encoding='utf-8')
        for antes, despues in cambios.items():
            if antes not in texto:
                raise ValueError(f'El texto compartido ha cambiado: {archivo}: {antes}')
            texto = texto.replace(antes, despues)
        path.write_text(texto, encoding='utf-8')
    return {'chapters': len(traducidos), 'sections': sum(len(c['secciones']) for c in traducidos),
            'activities': sum(len(c['cajas']) for c in traducidos), 'translated_figures': variantes,
            'english_cover_files': portadas,
            'source_files': {c['archivo']: digest(BOOK / 'en' / c['archivo']) for c in traducidos}}


CSS = '''\n/* Navegación entre ediciones, añadida solo a la vista bilingüe. */
.ediciones {display:flex; flex-wrap:wrap; gap:.4rem 1rem; padding:.65rem 0;
border-bottom:1px solid #d9dde3; margin:0 0 1.2rem; font-size:.88rem;}
.ediciones a {text-decoration:none;} .ediciones [aria-current] {font-weight:700;}
'''
CSS_EN = '''\n/* La cita y la tabla de recapitulación caben también a 320 px. */
#como-citar a {overflow-wrap:anywhere;}
@media (max-width:400px) {
  #sec-recapitulacion-decisiones table {display:block; max-width:100%; overflow-x:auto;}
}
'''
JS = '''document.querySelectorAll('[data-edicion-equivalente]').forEach(a => {
  a.addEventListener('click', () => { if(location.hash) {
    const u = new URL(a.href, location.href); u.hash = location.hash; a.href = u.href;
  }});
});\n'''


def enlaces_idioma(site, lang, meta):
    equivalentes = {'index.html', 'indice.html', 'actividades.html', 'avisos.html'}
    equivalentes |= {str(Path(f).with_suffix('.html')) for f in meta['translated_chapters']}
    (site / 'idiomas.js').write_text(JS, encoding='utf-8')
    estilos = site / 'estilos.css'
    estilos.write_text(estilos.read_text(encoding='utf-8') + CSS + (CSS_EN if lang == 'en' else ''), encoding='utf-8')
    for p in site.glob('*.html'):
        if lang == 'en':
            nav = (f'<nav class="ediciones" aria-label="Book edition"><a href="../{p.name}" lang="es" data-edicion-equivalente>Español · Original</a>'
                   '<span lang="en" aria-current="page">English · AI translation</span></nav>')
        else:
            destino = p.name if p.name in equivalentes else 'index.html'
            atributo = ' data-edicion-equivalente' if p.name in equivalentes else ''
            nav = ('<nav class="ediciones" aria-label="Edición del libro"><span lang="es" aria-current="page">Español · Original</span>'
                   f'<a href="en/{destino}" lang="en"{atributo}>English · AI translation</a></nav>')
        texto = p.read_text(encoding='utf-8')
        texto = re.sub(r'(<main\b[^>]*>)', lambda m: m[1] + '\n' + nav, texto, count=1)
        texto = texto.replace('</body>', '<script src="idiomas.js"></script>\n</body>')
        p.write_text(texto, encoding='utf-8')
    if lang == 'en':
        search = site / 'search.json'
        texto = search.read_text(encoding='utf-8')
        for a, b in [('BasicB', 'Basic'), ('AdvancedA', 'Advanced'), ('Further reading+', 'Further reading')]:
            texto = texto.replace(a, b)
        search.write_text(texto, encoding='utf-8')


REDIRECCION = '''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{url}">
<title>{clave}</title>
<script>location.replace({js});</script>
</head>
<body><p>{texto} <a href="{url}">{url}</a></p></body>
</html>
'''


def redirecciones(site, lang):
    """Una página por clave QR del PDF (D100): base + clave → destino de qr/claves.json."""
    registro = json.loads((BOOK / 'qr/claves.json').read_text(encoding='utf-8'))[lang]
    base = 'https://josemagalan.github.io/genetic-algorithms-lab-book/' + ('en/' if lang == 'en' else '')
    if registro['base'] != base + 'a/':
        raise ValueError(f'qr/claves.json: base inesperada para {lang}: {registro["base"]}')
    texto = 'Opening:' if lang == 'en' else 'Abriendo:'
    for clave, destino in registro['claves'].items():
        if not re.fullmatch(r'\d+(\.\d+)?[a-z]', clave) or not destino.startswith('https://'):
            raise ValueError(f'qr/claves.json: clave o destino no válidos: {clave} → {destino}')
        carpeta = site / 'a' / clave
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'index.html').write_text(REDIRECCION.format(lang=lang, clave=html.escape(clave), texto=texto,
            url=html.escape(destino, quote=True), js=json.dumps(destino).replace('</', '<\\/')), encoding='utf-8')
    return len(registro['claves'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quarto', default='quarto', help='Ejecutable de Quarto')
    parser.add_argument('--salida', required=True, type=Path, help='Carpeta nueva de trabajo y salida')
    args = parser.parse_args()
    out = args.salida.resolve()
    if out.exists():
        parser.error('La carpeta de salida debe ser nueva: se conservan las ejecuciones anteriores.')
    meta = json.loads((BOOK / 'en/traduccion.json').read_text(encoding='utf-8'))
    source_commit = git('rev-parse', meta['source_tag'] + '^{}')
    if not source_commit.startswith(meta['source_commit']):
        raise ValueError('La etiqueta fuente no coincide con el manifiesto de traducción')
    head = git('rev-parse', 'HEAD')
    out.mkdir(parents=True)
    work = out / 'trabajo'
    work.mkdir()
    # Exportar referencias concretas excluye automáticamente imágenes sin
    # seguimiento, notas internas y resultados de trabajos anteriores.
    exportar(head, work / 'es', out / 'fuentes-es.zip')
    exportar(source_commit, work / 'en', out / 'fuentes-original-en.zip')
    detalle = preparar_ingles(work / 'en', meta)
    shim = work / 'bin'
    shim.mkdir()
    if os.name == 'nt':
        (shim / 'python3.cmd').write_text(f'@"{sys.executable}" %*\n', encoding='utf-8')
    env = os.environ.copy()
    env['PATH'] = str(shim) + os.pathsep + env['PATH']
    env['PYTHONIOENCODING'] = 'utf-8'
    env['QUARTO_PYTHON'] = sys.executable
    for lang in ('es', 'en'):
        command = [args.quarto, 'render'] + (['--profile', 'en'] if lang == 'en' else [])
        with (out / f'quarto-{lang}.log').open('w', encoding='utf-8') as log:
            result = subprocess.run(command, cwd=work / lang, env=env, stdout=log, stderr=subprocess.STDOUT)
        print(f'{lang}: Quarto termina con {result.returncode}', flush=True)
        if result.returncode:
            raise SystemExit(f'Revisar {out / ("quarto-" + lang + ".log")}')
    site = out / 'site'
    shutil.copytree(work / 'es/_book', site)
    enlaces_idioma(site, 'es', meta)
    shutil.copytree(work / 'en/_book', site / 'en')
    enlaces_idioma(site / 'en', 'en', meta)
    qr = {'es': redirecciones(site, 'es'), 'en': redirecciones(site / 'en', 'en')}
    print(f"Redirecciones QR: {qr['es']} (es), {qr['en']} (en)", flush=True)
    record = {'source_spanish_live': head, 'source_translation': source_commit,
              'source_doi': meta['source_doi'], 'translation': meta,
              'python': sys.version, 'quarto': subprocess.check_output([args.quarto, '--version'], encoding='utf-8').strip(),
              'translated_content': detalle, 'qr_redirects': qr, 'build_driver_sha256': digest(Path(__file__)),
              'shared_build_hashes': {p.name: digest(p) for p in (BOOK / 'bilingue').glob('*.py')},
              'translation_source_hashes': {str(p.relative_to(BOOK)).replace('\\', '/'): digest(p) for p in (BOOK / 'en').rglob('*') if p.is_file()},
              'output_hashes': {str(p.relative_to(site)).replace('\\', '/'): digest(p) for p in site.rglob('*') if p.is_file()}}
    (out / 'generacion.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with zipfile.ZipFile(out / 'bilingue-html.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in site.rglob('*'):
            if p.is_file():
                z.write(p, str(p.relative_to(site)))
    print(f'Edición inglesa: {site / "en/index.html"}', flush=True)


if __name__ == '__main__':
    main()
