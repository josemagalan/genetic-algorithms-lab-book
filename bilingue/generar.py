"""Genera una vista bilingüe local en copias aisladas, sin modificar las fuentes.

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


def indices_ingles(module, caps, destino):
    niveles = {'basico': 'Basic', 'avanzado': 'Advanced', 'saber-mas': 'Further reading'}
    tipos = {'ejemplo': 'Example', 'ejercicio': 'Exercise', 'en-app': 'In the Application'}
    indice = ['# Contents {.unnumbered #sec-indice}', '',
              'Translated chapters in this local edition. Other chapter entries lead to the Spanish original.', '']
    actividades = ['# Activity Index {.unnumbered #sec-actividades}', '',
                   'Activities in the translated chapters. Reproducible examples use fixed data; application boxes invite exploration. Exercise solutions remain folded.', '',
                   '| Activity | Title | Section | Level | Tool |', '|---|---|:---:|---|---|']
    for c in caps:
        indice += [f"## {c['numero']}. {c['titulo']} {{.unnumbered}}", '']
        for s in c['secciones']:
            indice += [f"- [{s['num']} {s['titulo']}]({c['archivo']}#{s['ancla']}) · {niveles[s['nivel']]}"]
        indice += ['']
        for b in c['cajas']:
            sec = b['seccion']
            ancla = b['ancla'] or sec['ancla']
            nombre = tipos[b['tipo']] + (' ' + b['numero'] if b['numero'] else '')
            titulo = b['nombre'] or 'Explore the application'
            actividades.append(f"| [{nombre}]({c['archivo']}#{ancla}) | {module.celda(titulo)} | {sec['num']} | {niveles[sec['nivel']]} | {', '.join(b['herramientas'])} |")
    (destino / 'indice.qmd').write_text('\n'.join(indice) + '\n', encoding='utf-8')
    (destino / 'actividades.qmd').write_text('\n'.join(actividades) + '\n', encoding='utf-8')


def preparar_ingles(destino, meta):
    for fuente in (BOOK / 'en').glob('*.qmd'):
        shutil.copyfile(fuente, destino / fuente.name)
    spec = importlib.util.spec_from_file_location('figuras_ingles', BOOK / 'bilingue/figuras.py')
    figuras = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(figuras)
    variantes = figuras.generar(destino / 'figuras', destino / 'figuras', BOOK / 'en/figuras.json')
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
    # Versión inglesa del mismo CSL: se revierten los ajustes españoles
    # documentados en vendor/csl/LEEME.md. Se conserva su licencia CC BY-SA.
    csl = (destino / 'vendor/csl/apa.csl').read_text(encoding='utf-8')
    csl = csl.replace('default-locale="es-ES"', 'default-locale="en-US"').replace('and="text"', 'and="symbol"')
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
            'source_files': {c['archivo']: digest(BOOK / 'en' / c['archivo']) for c in traducidos}}


CSS = '''\n/* Navegación entre ediciones, añadida solo a la vista bilingüe. */
.ediciones {display:flex; flex-wrap:wrap; gap:.4rem 1rem; padding:.65rem 0;
border-bottom:1px solid #d9dde3; margin:0 0 1.2rem; font-size:.88rem;}
.ediciones a {text-decoration:none;} .ediciones [aria-current] {font-weight:700;}
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
    estilos.write_text(estilos.read_text(encoding='utf-8') + CSS, encoding='utf-8')
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
    record = {'source_spanish_live': head, 'source_translation': source_commit,
              'source_doi': meta['source_doi'], 'translation': meta,
              'python': sys.version, 'quarto': subprocess.check_output([args.quarto, '--version'], encoding='utf-8').strip(),
              'translated_content': detalle, 'build_driver_sha256': digest(Path(__file__)),
              'shared_build_hashes': {p.name: digest(p) for p in (BOOK / 'bilingue').glob('*.py')},
              'translation_source_hashes': {str(p.relative_to(BOOK)).replace('\\', '/'): digest(p) for p in (BOOK / 'en').rglob('*') if p.is_file()},
              'output_hashes': {str(p.relative_to(site)).replace('\\', '/'): digest(p) for p in site.rglob('*') if p.is_file()}}
    (out / 'generacion.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with zipfile.ZipFile(out / 'bilingue-html.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in site.rglob('*'):
            if p.is_file():
                z.write(p, str(p.relative_to(site)))
    print(f'Vista inglesa: {site / "en/index.html"}', flush=True)


if __name__ == '__main__':
    main()
