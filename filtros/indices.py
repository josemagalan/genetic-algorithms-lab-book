"""Genera los dos índices del libro a partir de los capítulos: indice.qmd y actividades.qmd.

- indice.qmd: índice general detallado (capítulos y secciones, con su nivel).
- actividades.qmd: ejemplos reproducibles, cajas «En la aplicación» y ejercicios,
  por herramienta y por capítulo.

Se ejecuta como «pre-render» del proyecto (_quarto.yml), así que los índices
siempre reflejan los capítulos tal como están. Solo reescribe un archivo si su
contenido cambia. También puede lanzarse a mano: python3 filtros/indices.py

Lee lo que ya marca cada capítulo y no necesita nada más:
  ## N.M Título [[…]{.largo}[…]{.corto}]{.nivel .basico|.avanzado|.saber-mas} {#ancla}
  ::: {.callout-tip .ejemplo #ejemplo-N-M title="Ejemplo reproducible N.M · …"}
  ::: {.callout-note .en-app title="En la aplicación · herramienta, «…»"}
  :::: {.callout-note .ejercicio #ejercicio-N-M title="Ejercicio N.M · …"}
"""
import os
import re
from collections import OrderedDict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NIVELES = {
    'basico': ('Básico', 'B'),
    'avanzado': ('Avanzado', 'A'),
    'saber-mas': ('Para saber más', '+'),
}
# Orden y nombre de las herramientas, como en el portal.
HERRAMIENTAS = OrderedDict([
    ('portal', 'Portal genetic-algorithms-lab'),
    ('representation-ga', 'representation-ga · Representación'),
    ('initialization-and-evaluation-ga', 'initialization-and-evaluation-ga · Inicialización y evaluación'),
    ('selection-ga', 'selection-ga · Selección'),
    ('crossover-ga', 'crossover-ga · Cruce'),
    ('mutation-ga', 'mutation-ga · Mutación'),
    ('evotraveller', 'EvoTraveller'),
    ('selectionmechanisms', 'SelectionMechanisms'),
])
NOMBRE_CORTO = {
    'portal': 'portal', 'evotraveller': 'EvoTraveller', 'selectionmechanisms': 'SelectionMechanisms',
}
TIPOS = {
    'ejemplo': 'Ejemplo reproducible',
    'en-app': 'En la aplicación',
    'ejercicio': 'Ejercicio',
}

CAPITULO = re.compile(r'^# (.+?)\s*\{[^}]*\}\s*$')
SECCION = re.compile(
    r'^## (\d+)\.(\d+) (.+?) \[\[[^\]]*\]\{\.largo\}\[[^\]]*\]\{\.corto\}\]'
    r'\{\.nivel \.([\w-]+)\}\s*\{#([\w-]+)\}\s*$')
CAJA = re.compile(r'^(:{3,}) \{\.callout-\w+ \.(ejemplo|en-app|ejercicio)(?: #([\w-]+))? title="([^"]*)"\}\s*$')
URL = re.compile(r'https?://[^\s)\]"\'>]+')


def herramientas_de(texto):
    """Herramientas a las que enlaza una caja (por las direcciones de sus botones)."""
    vistas = []
    for u in URL.findall(texto):
        m = re.match(r'https://josemagalan\.github\.io/([\w-]+)', u)
        clave = None
        if m:
            nombre = m.group(1)
            if nombre == 'genetic-algorithms-lab':
                clave = 'portal'
            elif nombre in HERRAMIENTAS:
                clave = nombre
        elif 'evotraveller.streamlit.app' in u:
            clave = 'evotraveller'
        elif 'SelectionMechanisms' in u:
            clave = 'selectionmechanisms'
        if clave and clave not in vistas:
            vistas.append(clave)
    return vistas


def capitulos():
    """Archivos de capítulo en el orden de _quarto.yml (los que empiezan por número)."""
    with open(os.path.join(RAIZ, '_quarto.yml'), encoding='utf-8') as fh:
        yml = fh.read()
    bloque = yml.split('chapters:', 1)[1]
    return [a for a in re.findall(r'^\s+-\s+([\w-]+\.qmd)', bloque, re.M) if re.match(r'\d\d-', a)]


def leer(archivo):
    with open(os.path.join(RAIZ, archivo), encoding='utf-8') as fh:
        lineas = fh.read().split('\n')
    cap = {'archivo': archivo, 'numero': int(archivo[:2]), 'titulo': None, 'secciones': [], 'cajas': []}
    seccion = None
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        if cap['titulo'] is None:
            m = CAPITULO.match(linea)
            if m:
                cap['titulo'] = m.group(1).strip()
        m = SECCION.match(linea)
        if m:
            seccion = {'num': f'{m.group(1)}.{m.group(2)}', 'titulo': m.group(3).strip(),
                       'nivel': m.group(4), 'ancla': m.group(5)}
            cap['secciones'].append(seccion)
        elif linea.startswith('## '):
            seccion = None          # Resumen, Referencias…
        m = CAJA.match(linea)
        if m:
            cierre = m.group(1)
            j = i + 1
            while j < len(lineas) and lineas[j].strip() != cierre:
                j += 1
            contenido = '\n'.join(lineas[i + 1:j])
            titulo = m.group(4)
            partes = titulo.split(' · ', 1)
            cabeza, nombre = partes[0], (partes[1] if len(partes) > 1 else '')
            numero = re.search(r'(\d+\.\d+)$', cabeza)
            cap['cajas'].append({
                'tipo': m.group(2), 'ancla': m.group(3), 'numero': numero.group(1) if numero else None,
                'nombre': nombre, 'seccion': seccion,
                'herramientas': herramientas_de(contenido),
            })
            i = j
        i += 1
    return cap


def insignia(nivel, larga=False):
    largo, corto = NIVELES[nivel]
    if larga:
        return f'[[{largo}]{{.largo}}[{corto}]{{.corto}}]{{.nivel .{nivel}}}'
    return f'[[{corto}]{{.corto}}]{{.nivel .{nivel} .solo-corto}}'


def celda(texto):
    return texto.replace('|', '\\|')


def enlace_caja(cap, caja):
    destino = caja['ancla'] or (caja['seccion']['ancla'] if caja['seccion'] else None)
    if caja['tipo'] == 'en-app':
        texto = TIPOS['en-app']
    else:
        texto = f"{'Ejemplo' if caja['tipo'] == 'ejemplo' else 'Ejercicio'} {caja['numero']}"
    return f"[{texto}]({cap['archivo']}#{destino})" if destino else texto


def nombre_caja(caja):
    nombre = caja['nombre']
    if caja['tipo'] == 'en-app':
        # «selection-ga, «Ruleta»» → «Ruleta»; sin subtítulo, la caja explora la sección
        m = re.match(r'^[^,«]+(?:,\s*(.*))?$', nombre)
        nombre = (m.group(1) or '').strip() if m else nombre
        if not nombre:
            nombre = 'Exploración libre'
    return nombre


def enlace_seccion(cap, s):
    return f"[{s['num']}]({cap['archivo']}#{s['ancla']})" if s else '—'


def nombres_herramientas(claves):
    return ', '.join(NOMBRE_CORTO.get(c, c) for c in claves) or '—'


AVISO = ('<!-- Archivo generado por filtros/indices.py en cada «quarto render» (pre-render). '
         'No lo edites a mano: los cambios se perderían. Para cambiar el contenido, '
         'cambia los capítulos; para cambiar el formato, cambia el script. -->')


def indice_general(caps):
    total = {k: 0 for k in NIVELES}
    cajas = {k: 0 for k in TIPOS}
    for c in caps:
        for s in c['secciones']:
            total[s['nivel']] += 1
        for b in c['cajas']:
            cajas[b['tipo']] += 1
    o = ['# Índice general {.unnumbered #sec-indice}', '', AVISO, '',
         f"El libro tiene {len(caps)} capítulos y {sum(total.values())} secciones: "
         f"{total['basico']} de nivel {insignia('basico', True)}, {total['avanzado']} de nivel "
         f"{insignia('avanzado', True)} y {total['saber-mas']} de nivel {insignia('saber-mas', True)}. "
         'El **recorrido básico** son las secciones azules: se leen seguidas, capítulo a capítulo, '
         'sin las demás. Las avanzadas amplían el recorrido básico y suelen apoyarse en él; '
         '«Para saber más» cierra cada capítulo con lecturas y temas que el libro no desarrolla.', '',
         f"Las actividades —{cajas['ejemplo']} ejemplos reproducibles, {cajas['en-app']} cajas "
         f"«En la aplicación» y {cajas['ejercicio']} ejercicios— están listadas en el "
         '[índice de actividades](actividades.qmd), por capítulo y por herramienta.', '',
         '## El libro de un vistazo {#vistazo}', '',
         '| Capítulo | B | A | + | Ejemplos | En la aplicación | Ejercicios |',
         '|---|:-:|:-:|:-:|:-:|:-:|:-:|']
    for c in caps:
        n = {k: sum(1 for s in c['secciones'] if s['nivel'] == k) for k in NIVELES}
        b = {k: sum(1 for x in c['cajas'] if x['tipo'] == k) for k in TIPOS}
        o.append(f"| [{c['numero']}. {celda(c['titulo'])}]({c['archivo']}) | {n['basico']} | {n['avanzado']} | "
                 f"{n['saber-mas']} | {b['ejemplo']} | {b['en-app']} | {b['ejercicio']} |")
    o.append(f"| **Total** | **{total['basico']}** | **{total['avanzado']}** | **{total['saber-mas']}** | "
             f"**{cajas['ejemplo']}** | **{cajas['en-app']}** | **{cajas['ejercicio']}** |")
    o.append('')
    for c in caps:
        o += [f"## {c['numero']}. {c['titulo']} {{#cap-{c['numero']}}}", '']
        for s in c['secciones']:
            o.append(f"- [{s['num']} {s['titulo']}]({c['archivo']}#{s['ancla']}) {insignia(s['nivel'])}")
        o.append('')
    return '\n'.join(o)


def indice_actividades(caps):
    o = ['# Índice de actividades {.unnumbered #sec-actividades}', '', AVISO, '',
         'Aquí están todas las cajas de trabajo del libro. Los **ejemplos reproducibles** abren '
         'la herramienta en un estado fijado, de modo que el resultado coincide con el del libro; '
         'las cajas **En la aplicación** proponen explorar sin resultados fijados; los **ejercicios** '
         'se resuelven con papel y lápiz. La primera parte las ordena por herramienta, para preparar '
         'una sesión con una aplicación concreta; la segunda, por capítulo. La columna de nivel es '
         'la de la sección en la que está la caja.', '']
    # --- Por herramienta
    o += ['## Por herramienta {#por-herramienta}', '']
    for clave, nombre in HERRAMIENTAS.items():
        filas = [(c, b) for c in caps for b in c['cajas'] if clave in b['herramientas']]
        if not filas:
            continue
        n_ej = sum(1 for _, b in filas if b['tipo'] == 'ejemplo')
        n_app = sum(1 for _, b in filas if b['tipo'] == 'en-app')
        n_ejer = sum(1 for _, b in filas if b['tipo'] == 'ejercicio')
        resumen = [texto for n, uno, varios in ((n_ej, 'ejemplo reproducible', 'ejemplos reproducibles'),
                                                (n_app, 'caja «En la aplicación»', 'cajas «En la aplicación»'),
                                                (n_ejer, 'ejercicio', 'ejercicios'))
                   if n for texto in [f'{n} {uno if n == 1 else varios}']]
        frase = resumen[0] if len(resumen) == 1 else ', '.join(resumen[:-1]) + ' y ' + resumen[-1]
        o += [f"### {nombre} {{#h-{clave}}}", '', frase[0].upper() + frase[1:] + '.', '',
              '| Actividad | Título | Sección | Nivel |', '|---|---|:-:|:-:|']
        for c, b in filas:
            nivel = insignia(b['seccion']['nivel']) if b['seccion'] else ''
            o.append(f"| {enlace_caja(c, b)} | {celda(nombre_caja(b))} | {enlace_seccion(c, b['seccion'])} | {nivel} |")
        o.append('')
    # --- Por capítulo
    o += ['## Por capítulo {#por-capitulo}', '']
    for c in caps:
        if not c['cajas']:
            continue
        o += [f"### {c['numero']}. {c['titulo']} {{#a-cap-{c['numero']}}}", '',
              '| Actividad | Título | Sección | Herramienta | Nivel |', '|---|---|:-:|---|:-:|']
        for b in c['cajas']:
            nivel = insignia(b['seccion']['nivel']) if b['seccion'] else ''
            o.append(f"| {enlace_caja(c, b)} | {celda(nombre_caja(b))} | {enlace_seccion(c, b['seccion'])} | "
                     f"{nombres_herramientas(b['herramientas'])} | {nivel} |")
        o.append('')
    return '\n'.join(o)


def escribir(nombre, texto):
    ruta = os.path.join(RAIZ, nombre)
    texto = texto.rstrip('\n') + '\n'
    try:
        with open(ruta, encoding='utf-8') as fh:
            if fh.read() == texto:
                return
    except FileNotFoundError:
        pass
    with open(ruta, 'w', encoding='utf-8') as fh:
        fh.write(texto)
    print(f'indices.py: {nombre} actualizado')


def main():
    caps = [leer(a) for a in capitulos()]
    escribir('indice.qmd', indice_general(caps))
    escribir('actividades.qmd', indice_actividades(caps))


if __name__ == '__main__':
    main()
