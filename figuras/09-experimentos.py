"""Figuras 9.1 a 9.4 del libro «Evolución a la vista»: varias ejecuciones, comparación de
valores de la probabilidad de mutación, tamaño del problema e interacción con el torneo.

Algoritmo genético mínimo para el viajante (TSP), con el mismo diseño que EvoTraveller (representación
por permutación, torneo con contendientes distintos, cruce OX con probabilidad Pc, intercambio de dos
genes con probabilidad pm por individuo, reemplazo generacional con élite) pero con su propio
generador de números aleatorios: no reproduce número a número las ejecuciones de esa herramienta.
Los mapas son puntos enteros distintos de una cuadrícula de 10 × 10; el origen es (0, 0). Un mapa de n destinos
tiene n puntos más el origen, donde empieza y acaba la ruta: n + 1 ciudades y n + 1 aristas.

Ejecuciones: el generador de cada réplica es random.Random(semilla), con semillas 1–30 (REPLICAS).
Cada comparación usa el mismo mapa y las mismas semillas para todas las configuraciones.

Uso: python3 09-experimentos.py   → escribe 09-replicas.svg, 09-comparar-pm.svg, 09-tamano.svg y
09-interaccion.svg, y muestra los datos y los resúmenes, también los que se citan en el texto sin figura
(efecto de Pc, diversidad, élite, mutación por inversión, escalador, localidad de los operadores y
tipo de cruce). Solo usa la biblioteca estándar de Python 3. Las cifras del libro se obtuvieron con Python 3.12;
con Python 3.10 algunas ejecuciones dan valores algo distintos (comprobado el 2026-10-16).
"""
import math
import random
import statistics as st

REPLICAS = 30
MAPA = 7                      # semilla del mapa de 20 destinos (más el origen) de las figuras 9.1, 9.2 y 9.4
N, G, K, PC, E = 30, 100, 3, 0.6, 1   # población, generaciones, torneo, Pc y tamaño de la élite
PM_BASE = 0.05


def mapa(n, semilla, malla=10):
    r = random.Random(semilla)
    puntos = []
    while len(puntos) < n:
        p = (r.randrange(malla), r.randrange(malla))
        if p != (0, 0) and p not in puntos:
            puntos.append(p)
    return puntos


def longitud(orden, pts):
    ruta = [(0, 0)] + [pts[i] for i in orden] + [(0, 0)]
    return sum(math.dist(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1))


def ox(p1, p2, r):
    n = len(p1)
    a, b = sorted(r.sample(range(n), 2))

    def hijo(x, y):
        c = [None] * n
        c[a:b] = x[a:b]
        usados = set(x[a:b])
        resto = [g for g in y[b:] + y[:b] if g not in usados]
        for i, g in zip(list(range(b, n)) + list(range(a)), resto):
            c[i] = g
        return c
    return hijo(p1, p2), hijo(p2, p1)


def pmx(p1, p2, r):
    """PMX: el hijo copia un tramo de un padre y coloca los genes del otro padre siguiendo la correspondencia."""
    n = len(p1)
    a, b = sorted(r.sample(range(n), 2))

    def hijo(x, y):
        c = [None] * n
        c[a:b] = x[a:b]
        tramo = set(x[a:b])
        for i in range(a, b):
            g = y[i]
            if g in tramo:
                continue
            pos = i
            while a <= pos < b:
                pos = y.index(x[pos])
            c[pos] = g
        return [y[i] if g is None else g for i, g in enumerate(c)]
    return hijo(p1, p2), hijo(p2, p1)


def cx(p1, p2, r):
    """CX: cada gen conserva la posición que tenía en uno de los padres, por ciclos alternos."""
    n = len(p1)
    ciclo = [None] * n
    num = 0
    for inicio in range(n):
        if ciclo[inicio] is None:
            i = inicio
            while ciclo[i] is None:
                ciclo[i] = num
                i = p1.index(p2[i])
            num += 1
    h1 = [p1[i] if ciclo[i] % 2 == 0 else p2[i] for i in range(n)]
    h2 = [p2[i] if ciclo[i] % 2 == 0 else p1[i] for i in range(n)]
    return h1, h2


def erx(p1, p2, r):
    """ERX (Whitley y otros, 1989): el hijo intenta usar solo aristas de los padres. La ruta completa incluye
    el origen, que se trata como una ciudad más (-1) y se quita al final."""
    def hijo():
        vecinos = {}
        for padre in (p1, p2):
            ciclo = [-1] + list(padre)
            m = len(ciclo)
            for i, g in enumerate(ciclo):
                vecinos.setdefault(g, set()).update((ciclo[i - 1], ciclo[(i + 1) % m]))
        actual, ruta = -1, []
        pendientes = set(p1)
        while pendientes:
            for v in vecinos.values():
                v.discard(actual)
            candidatos = [g for g in vecinos.pop(actual) if g in pendientes]
            if candidatos:
                menor = min(len(vecinos[g]) for g in candidatos)
                actual = r.choice(sorted(g for g in candidatos if len(vecinos[g]) == menor))
            else:
                actual = r.choice(sorted(pendientes))
            ruta.append(actual)
            pendientes.discard(actual)
        return ruta
    return hijo(), hijo()


CRUCES = {'OX': ox, 'PMX': pmx, 'CX': cx, 'ERX': erx}


def aristas(orden):
    """Aristas (pares de ciudades vecinas, sin sentido) de la ruta completa, con el origen como -1."""
    c = [-1] + list(orden) + [-1]
    return {frozenset((c[i], c[i + 1])) for i in range(len(c) - 1)}


def busqueda_local(t, pts):
    """Aplica inversiones de tramo mientras alguna acorte la ruta (2-opt); devuelve la ruta y su longitud."""
    n = len(t)
    ft = longitud(t, pts)
    mejora = True
    while mejora:
        mejora = False
        for i in range(n - 1):
            for j in range(i + 1, n):
                u = t[:i] + t[i:j + 1][::-1] + t[j + 1:]
                fu = longitud(u, pts)
                if fu < ft - 1e-9:
                    t, ft, mejora = u, fu, True
    return t, ft


def ejecutar(pts, semilla, pm=PM_BASE, k=K, pc=PC, n_pob=N, gens=G, elite=E, oper='intercambio', distintos=None, cruce='OX'):
    """Devuelve la longitud de la mejor ruta en cada generación (0..gens).

    oper: 'intercambio' (dos posiciones) o 'inversion' (invierte el tramo entre dos posiciones).
    cruce: 'OX', 'PMX', 'CX' o 'ERX'.
    distintos: si es una lista, se le añade el número de rutas distintas de la población en cada generación."""
    r = random.Random(semilla)
    n = len(pts)
    pob = [r.sample(range(n), n) for _ in range(n_pob)]
    f = lambda s: longitud(s, pts)
    mejor = []

    def mutar(s):
        i, j = r.sample(range(n), 2)
        if oper == 'intercambio':
            s[i], s[j] = s[j], s[i]
        else:
            i, j = min(i, j), max(i, j)
            s[i:j + 1] = s[i:j + 1][::-1]

    for _ in range(gens):
        pob.sort(key=f)
        mejor.append(f(pob[0]))
        if distintos is not None:
            distintos.append(len({tuple(x) for x in pob}))
        sig = [list(s) for s in pob[:elite]]
        sel = [list(min(r.sample(pob, k), key=f)) for _ in range(n_pob)]
        r.shuffle(sel)
        nc = int(pc * n_pob)
        nc += nc % 2
        nc = min(nc, n_pob - elite - ((n_pob - elite) % 2))
        while len(sig) < n_pob - nc:
            s = sel.pop()
            if r.random() < pm:
                mutar(s)
            sig.append(s)
        while len(sig) < n_pob:
            for c in CRUCES[cruce](sel.pop(), sel.pop(), r):
                if r.random() < pm:
                    mutar(c)
                sig.append(c)
        pob = sig[:n_pob]
    pob.sort(key=f)
    mejor.append(f(pob[0]))
    return mejor


# ---------------------------------------------------------------- dibujo
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#7a7974', '#e4e3df'
AZUL, NARANJA, AQUA = '#2a78d6', '#eb6834', '#1baf7a'
FUENTE = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""


def cabecera(w, h, titulo, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" {FUENTE}>',
            f'<title id="t">{titulo}</title>', f'<desc id="d">{desc}</desc>',
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>']


def texto(x, y, s, size=12, color=INK2, ancla='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{ancla}"{extra}>{s}</text>'


def ejes(o, x0, x1, y0, y1, vmin, vmax, marcas_y, marcas_x, X, Y, etq_x, etq_y, dec=0):
    for v in marcas_y:
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(texto(x0 - 8, Y(v) + 4, f'{v:.{dec}f}'.replace('.', ','), 12, INK2, 'end'))
    for v, s in marcas_x:
        o.append(texto(X(v), y0 + 20, s, 12, INK2, 'middle'))
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{MUTED}" stroke-width="1"/>')
    o.append(texto((x0 + x1) / 2, y0 + 44, etq_x, 13, INK2, 'middle'))
    cy = (y0 + y1) / 2
    o.append(texto(18, cy, etq_y, 13, INK2, 'middle', f' transform="rotate(-90 18 {cy})"'))


def linea(pts, color, ancho=2, guiones='', halo=True, opac=1):
    p = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    h = f'<polyline points="{p}" fill="none" stroke="#ffffff" stroke-width="{ancho + 3}" stroke-linejoin="round"/>' if halo else ''
    d = f' stroke-dasharray="{guiones}"' if guiones else ''
    return (h + f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{ancho}" '
            f'stroke-linejoin="round" stroke-opacity="{opac}"{d}/>')


def coma(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',')


def fig_replicas(datos):
    """datos: lista de 30 series (mejor longitud por generación)."""
    W, H = 720, 430
    x0, x1, y0, y1 = 64, 560, 360, 64
    vmin, vmax = 40, 150
    X = lambda g: x0 + (x1 - x0) * g / G
    Y = lambda v: y0 - (y0 - y1) * (v - vmin) / (vmax - vmin)
    fin = [s[-1] for s in datos]
    media = [st.mean(s[g] for s in datos) for g in range(G + 1)]
    ib, iw = fin.index(min(fin)), fin.index(max(fin))
    o = cabecera(W, H, 'Mejor longitud de ruta por generación en 30 ejecuciones del mismo algoritmo',
                 f'Viajante con 20 destinos más el origen, población de 30, pm = 0,05 y 30 ejecuciones con semillas distintas. Las curvas '
                 f'terminan entre {coma(min(fin))} y {coma(max(fin))}; la media final es {coma(st.mean(fin))}.')
    ejes(o, x0, x1, y0, y1, vmin, vmax, range(40, 151, 20), [(g, str(g)) for g in range(0, G + 1, 20)], X, Y,
         'Generación', 'Longitud de la mejor ruta (menos es mejor)')
    for s in datos:
        o.append(linea([(X(g), Y(v)) for g, v in enumerate(s)], MUTED, 1, halo=False, opac=0.35))
    o.append(linea([(X(g), Y(v)) for g, v in enumerate(datos[ib])], AZUL, 2))
    o.append(linea([(X(g), Y(v)) for g, v in enumerate(datos[iw])], NARANJA, 2))
    o.append(linea([(X(g), Y(v)) for g, v in enumerate(media)], INK, 3, '7 4'))
    for serie, color, nombre in ((datos[ib], AZUL, f'La mejor: {coma(min(fin))}'),
                                 (datos[iw], NARANJA, f'La peor: {coma(max(fin))}'),
                                 (media, INK, f'Media: {coma(st.mean(fin))}')):
        o.append(f'<circle cx="{X(G):.1f}" cy="{Y(serie[-1]):.1f}" r="4" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
        o.append(texto(x1 + 12, Y(serie[-1]) + 4, nombre, 12, INK))
    o.append(texto(x1 + 12, Y(datos[0][0]) - 18, 'Gris: las otras', 12, INK2))
    o.append(texto(x1 + 12, Y(datos[0][0]) - 4, '27 ejecuciones', 12, INK2))
    o.append('</svg>')
    return '\n'.join(o) + '\n'


def fig_comparar(res, pms, colores):
    """res[pm] = lista de 30 longitudes finales."""
    W, H = 720, 430
    x0, x1, y0, y1 = 64, 700, 360, 64
    vmin, vmax = 35, 100
    Y = lambda v: y0 - (y0 - y1) * (v - vmin) / (vmax - vmin)
    ancho = (x1 - x0) / len(pms)
    cx = lambda i: x0 + ancho * (i + 0.5)
    o = cabecera(W, H, 'Longitud final de la mejor ruta en 30 ejecuciones para tres valores de pm',
                 'Cada punto es una ejecución. Medias: ' + ', '.join(f'pm = {coma(pm, 2)}: {coma(st.mean(res[pm]))}' for pm in pms)
                 + '. Las nubes de puntos de pm = 0,05 y pm = 0,2 se solapan.')
    for v in range(40, 101, 10):
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(texto(x0 - 8, Y(v) + 4, str(v), 12, INK2, 'end'))
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{MUTED}" stroke-width="1"/>')
    o.append(texto((x0 + x1) / 2, y0 + 44, 'Probabilidad de mutación pm', 13, INK2, 'middle'))
    o.append(texto(18, (y0 + y1) / 2, 'Longitud final (menos es mejor)', 13, INK2, 'middle',
                   f' transform="rotate(-90 18 {(y0 + y1) / 2})"'))
    for i, pm in enumerate(pms):
        v = res[pm]
        m, s = st.mean(v), st.stdev(v)
        r = random.Random(100 + i)
        o.append(texto(cx(i), y0 + 20, coma(pm, 2).rstrip('0').rstrip(',') if pm else '0', 12, INK2, 'middle'))
        for y in v:
            o.append(f'<circle cx="{cx(i) + r.uniform(-60, 60):.1f}" cy="{Y(y):.1f}" r="4" fill="{colores[i]}" '
                     f'fill-opacity="0.55" stroke="#ffffff" stroke-width="1.5"/>')
        o.append(f'<line x1="{cx(i) + 72:.1f}" y1="{Y(m - s):.1f}" x2="{cx(i) + 72:.1f}" y2="{Y(m + s):.1f}" stroke="{INK}" stroke-width="2"/>')
        o.append(f'<line x1="{cx(i) - 80:.1f}" y1="{Y(m):.1f}" x2="{cx(i) + 80:.1f}" y2="{Y(m):.1f}" stroke="{INK}" stroke-width="2.5"/>')
        o.append(texto(cx(i), y1 - 22, f'media {coma(m)}', 13, INK, 'middle', ' font-weight="600"'))
        o.append(texto(cx(i), y1 - 6, f'desv. típica {coma(s)}', 12, INK2, 'middle'))
    o.append('</svg>')
    return '\n'.join(o) + '\n'


def fig_tamano(tabla, pms, tamanos, colores):
    """tabla[n][pm] = media final. Eje y: % por encima de la mejor media de ese tamaño."""
    W, H = 720, 430
    x0, x1, y0, y1 = 64, 560, 360, 64
    X = lambda i: x0 + (x1 - x0) * (i + 0.5) / len(pms)
    vmax = 70
    Y = lambda v: y0 - (y0 - y1) * v / vmax
    o = cabecera(W, H, 'Cuánto empeora cada valor de pm respecto al mejor, según el tamaño del problema',
                 'pm = 0,05 queda un ' + ', '.join(f'{100 * (tabla[n][0.05] / min(tabla[n].values()) - 1):.0f} % por encima del mejor con {n} destinos'
                                                    for n in tamanos) + '. El mejor valor probado es el mismo en los tres tamaños, 0,5.')
    for v in range(0, 71, 10):
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(texto(x0 - 8, Y(v) + 4, f'{v} %', 12, INK2, 'end'))
    for i, pm in enumerate(pms):
        o.append(texto(X(i), y0 + 20, coma(pm, 2).rstrip('0').rstrip(',') if pm else '0', 12, INK2, 'middle'))
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{MUTED}" stroke-width="1"/>')
    o.append(texto((x0 + x1) / 2, y0 + 44, 'Probabilidad de mutación pm', 13, INK2, 'middle'))
    o.append(texto(18, (y0 + y1) / 2, 'Por encima de la mejor media del mismo tamaño', 13, INK2, 'middle',
                   f' transform="rotate(-90 18 {(y0 + y1) / 2})"'))
    etiquetas = []
    for n, c in zip(tamanos, colores):
        mejor = min(tabla[n].values())
        pts = [(X(i), Y(100 * (tabla[n][pm] / mejor - 1))) for i, pm in enumerate(pms)]
        o.append(linea(pts, c, 2.5))
        for x, y in pts:
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{c}" stroke="#ffffff" stroke-width="2"/>')
        etiquetas.append(texto(pts[0][0] + 12, pts[0][1] - 10, f'{n} destinos', 12, INK, extra=' stroke="#ffffff" stroke-width="4" paint-order="stroke"'))
    o.extend(etiquetas)
    o.append('</svg>')
    return '\n'.join(o) + '\n'


def fig_interaccion(tabla, pms, ks, colores):
    """tabla[k][pm] = (media, error típico)."""
    W, H = 720, 430
    x0, x1, y0, y1 = 64, 560, 360, 64
    X = lambda i: x0 + (x1 - x0) * (i + 0.5) / len(pms)
    vmin, vmax = 40, 100
    Y = lambda v: y0 - (y0 - y1) * (v - vmin) / (vmax - vmin)
    o = cabecera(W, H, 'Longitud media final según pm para dos tamaños de torneo',
                 f'Con torneo de 2, pm = 1 da {coma(tabla[2][1.0][0])} y pm = 0,2 da {coma(tabla[2][0.2][0])}: subir pm empeora. '
                 f'Con torneo de 10, pm = 1 da {coma(tabla[10][1.0][0])} y pm = 0,2 da {coma(tabla[10][0.2][0])}: subir pm mejora.')
    ejes(o, x0, x1, y0, y1, vmin, vmax, range(40, 101, 10), [(i, coma(pm, 2).rstrip('0').rstrip(',') if pm else '0') for i, pm in enumerate(pms)],
         X, Y, 'Probabilidad de mutación pm', 'Longitud media final (menos es mejor)')
    trazos = {k: [(X(i), Y(tabla[k][pm][0])) for i, pm in enumerate(pms)] for k in ks}
    for k, c in zip(ks, colores):
        o.append(linea(trazos[k], c, 2.5))
    for k, c in zip(ks, colores):
        for i, pm in enumerate(pms):
            m, e = tabla[k][pm]
            o.append(f'<line x1="{X(i):.1f}" y1="{Y(m - 2 * e):.1f}" x2="{X(i):.1f}" y2="{Y(m + 2 * e):.1f}" stroke="{c}" stroke-width="1.5"/>')
    for k, c in zip(ks, colores):
        mejor = min(range(len(pms)), key=lambda i: tabla[k][pms[i]][0])
        for i, (x, y) in enumerate(trazos[k]):
            r = 4.5 if i != mejor else 7
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" stroke="#ffffff" stroke-width="2"/>')
        o.append(texto(x1 + 12, trazos[k][-1][1] + 4, f'torneo de {k}', 12, INK))
    o.append(texto(x0 + 4, y1 - 12, 'Punto grande: el mejor de los cinco valores. Barras: ± 2 errores típicos.', 12, INK2))
    o.append('</svg>')
    return '\n'.join(o) + '\n'


if __name__ == '__main__':
    semillas = range(1, REPLICAS + 1)
    # --- 10.1 y 10.2: mapa de 20 destinos
    pts20 = mapa(20, MAPA)
    series = [ejecutar(pts20, s) for s in semillas]
    fin = [s[-1] for s in series]
    with open('09-replicas.svg', 'w', encoding='utf-8') as fh:
        fh.write(fig_replicas(series))
    print('FIGURA 9.1: 20 destinos, N=30, G=100, torneo 3, Pc=0,6, pm=0,05, élite 1; semillas 1-30')
    print('  finales ordenados:', [round(x, 1) for x in sorted(fin)])
    print(f'  media {st.mean(fin):.2f}  desv. típica {st.stdev(fin):.2f}  mín {min(fin):.2f} (semilla {fin.index(min(fin)) + 1})  '
          f'máx {max(fin):.2f} (semilla {fin.index(max(fin)) + 1})  mediana {st.median(fin):.2f}')
    print('  semilla 1:', round(fin[0], 2), '| semillas 1-5:', [round(x, 2) for x in fin[:5]])
    c5 = fin[:5]
    print(f'  semillas 1-5: media {st.mean(c5):.2f}, desv. típica {st.stdev(c5):.2f}')
    ee = st.stdev(fin) / math.sqrt(len(fin))
    print(f'  error típico {ee:.2f}; intervalo del 95 % de la media: {st.mean(fin) - 1.96 * ee:.1f} a {st.mean(fin) + 1.96 * ee:.1f}')
    print('  inicial (gen 0) media', round(st.mean(s[0] for s in series), 1), '| gen 50 media', round(st.mean(s[50] for s in series), 1))
    pms = [0, 0.05, 0.2]
    res = {pm: [ejecutar(pts20, s, pm=pm)[-1] for s in semillas] for pm in pms}
    with open('09-comparar-pm.svg', 'w', encoding='utf-8') as fh:
        fh.write(fig_comparar(res, pms, [AZUL, NARANJA, AQUA]))
    print('FIGURA 9.2')
    for pm in pms:
        v = res[pm]
        print(f'  pm={pm}: media {st.mean(v):.2f} desv. típica {st.stdev(v):.2f} error típico {st.stdev(v) / math.sqrt(len(v)):.2f} '
              f'mín {min(v):.2f} máx {max(v):.2f}')
    for a, b in ((0.05, 0.2), (0.0, 0.05)):
        # probabilidad de que una sola ejecución de la configuración peor gane a una de la mejor (todas las parejas)
        gana = sum(1 for x in res[a] for y in res[b] if x < y) / (len(res[a]) * len(res[b]))
        mismas = sum(1 for s in range(REPLICAS) if res[a][s] < res[b][s])
        print(f'  una ejecución de pm={a} supera a una de pm={b} en el {100 * gana:.1f} % de las 900 parejas '
              f'y en {mismas} de 30 semillas emparejadas')
    for a, b in ((0.05, 0.2), (0.0, 0.05)):
        n_gana = sum(1 for x in res[a] for y in res[b] if x < y)
        print(f'  parejas (pm={a} gana a pm={b}): {n_gana} de {len(res[a]) * len(res[b])}')
    dif = st.mean(res[0.05]) - st.mean(res[0.2])
    eed = math.sqrt(st.variance(res[0.05]) / 30 + st.variance(res[0.2]) / 30)
    print(f'  diferencia de medias pm 0,05 - pm 0,2: {dif:.2f}, error típico {eed:.2f}, intervalo del 95 %: {dif - 1.96 * eed:.1f} a {dif + 1.96 * eed:.1f}')
    d = [res[0.05][s] - res[0.2][s] for s in range(REPLICAS)]
    print(f'  diferencia emparejada pm 0,05 - pm 0,2: media {st.mean(d):.2f}, desv. típica {st.stdev(d):.2f}, '
          f'error típico {st.stdev(d) / math.sqrt(30):.2f}')
    # --- 10.3: tamaño del problema
    pms3 = [0, 0.01, 0.05, 0.2, 0.5]
    tam = [10, 20, 30]
    tabla3 = {}
    for n in tam:
        p = mapa(n, MAPA)
        tabla3[n] = {pm: st.mean(ejecutar(p, s, pm=pm)[-1] for s in semillas) for pm in pms3}
    with open('09-tamano.svg', 'w', encoding='utf-8') as fh:
        fh.write(fig_tamano(tabla3, pms3, tam, [AZUL, NARANJA, AQUA]))
    print('FIGURA 9.3: media de 30 ejecuciones (mapa de cada tamaño con semilla 7)')
    for n in tam:
        mejor = min(tabla3[n].values())
        print(f'  {n} destinos:', {pm: (round(tabla3[n][pm], 1), f'+{100 * (tabla3[n][pm] / mejor - 1):.0f} %') for pm in pms3})
    # --- 10.4: interacción torneo x pm
    pms4 = [0, 0.05, 0.2, 0.5, 1.0]
    ks = [2, 10]
    tabla4 = {}
    for k in ks:
        tabla4[k] = {}
        for pm in pms4:
            v = [ejecutar(pts20, s, pm=pm, k=k)[-1] for s in semillas]
            tabla4[k][pm] = (st.mean(v), st.stdev(v) / math.sqrt(len(v)))
    with open('09-interaccion.svg', 'w', encoding='utf-8') as fh:
        fh.write(fig_interaccion(tabla4, pms4, ks, [AZUL, NARANJA]))
    print('FIGURA 9.4: 20 destinos, media (error típico) de 30 ejecuciones')
    for k in ks:
        print(f'  torneo {k}:', {pm: f'{tabla4[k][pm][0]:.1f} ({tabla4[k][pm][1]:.1f})' for pm in pms4})
    # --- efecto de Pc (solo se muestra; no hay figura)
    print('EFECTO DE Pc: 20 destinos, media (error típico) de 30 ejecuciones')
    for pm in (0.05, 0.5):
        fila = {}
        for pc in (0.0, 0.6, 0.9):
            v = [ejecutar(pts20, s, pm=pm, pc=pc)[-1] for s in semillas]
            fila[pc] = f'{st.mean(v):.1f} ({st.stdev(v) / math.sqrt(len(v)):.1f})'
        print(f'  pm={pm}:', fila)
    # --- por qué sale tan alto el mejor pm (datos que se citan en el texto; no hay figura)
    print('POR QUÉ UN pm ALTO: 20 destinos, torneo 3, media de 30 ejecuciones')
    for pm in (0.05, 0.5):
        cuentas = []
        for s in semillas:
            d = []
            ejecutar(pts20, s, pm=pm, distintos=d)
            cuentas.append(d)
        print(f'  pm={pm}: rutas distintas en la población (de 30), generaciones 0, 10, 20 y 99:',
              [round(st.mean(c[g] for c in cuentas), 1) for g in (0, 10, 20, 99)])
    for el in (1, 0):
        print(f'  élite {el}:', {pm: round(st.mean(ejecutar(pts20, s, pm=pm, elite=el)[-1] for s in semillas), 1)
                                 for pm in (0.05, 0.2, 0.5, 1.0)})
    for k in (2, 10):
        cuentas = []
        for s in semillas:
            d = []
            ejecutar(pts20, s, pm=1.0, k=k, distintos=d)
            cuentas.append(d)
        print(f'  pm=1, torneo {k}: rutas distintas, generaciones 5, 20 y 99:',
              [round(st.mean(c[g] for c in cuentas), 1) for g in (5, 20, 99)])
    print('  mutación por inversión de un tramo:',
          {pm: round(st.mean(ejecutar(pts20, s, pm=pm, oper='inversion')[-1] for s in semillas), 1)
           for pm in (0.01, 0.05, 0.2, 0.5, 1.0)})

    def escalador(pts, semilla, oper='intercambio', vecinos=N - 1, gens=G):
        """Parte de la mejor de N rutas al azar y, en cada generación, prueba `vecinos` mutaciones de la mejor
        ruta y se queda con la mejor si no empeora: el mismo número de evaluaciones que el algoritmo genético."""
        r = random.Random(semilla)
        n = len(pts)
        mejor = min((r.sample(range(n), n) for _ in range(N)), key=lambda s: longitud(s, pts))
        for _ in range(gens):
            cand = []
            for _ in range(vecinos):
                s = list(mejor)
                i, j = sorted(r.sample(range(n), 2))
                if oper == 'intercambio':
                    s[i], s[j] = s[j], s[i]
                else:
                    s[i:j + 1] = s[i:j + 1][::-1]
                cand.append(s)
            c = min(cand, key=lambda s: longitud(s, pts))
            if longitud(c, pts) <= longitud(mejor, pts):
                mejor = c
        return longitud(mejor, pts)
    for oper in ('intercambio', 'inversion'):
        print(f'  escalador con {oper}:', round(st.mean(escalador(pts20, s, oper) for s in semillas), 1))

    # mejor ruta conocida del mapa de 20 destinos: búsqueda local con inversiones desde 300 rutas al azar
    mejor_conocida = min(busqueda_local(random.Random(s).sample(range(20), 20), pts20)[1] for s in range(300))
    print(f'  mejor ruta encontrada (búsqueda local con inversiones, 300 inicios): {mejor_conocida:.2f}')

    # --- localidad de los operadores: qué conservan de una buena ruta (sección 9.10)
    print('LOCALIDAD: 20 destinos; rutas buenas = 60 óptimos locales distintos de la búsqueda local con inversiones')
    r = random.Random(1)
    azar = [r.sample(range(20), 20) for _ in range(60)]
    buenas, vistas = [], set()
    while len(buenas) < 60:
        t = busqueda_local(r.sample(range(20), 20), pts20)[0]
        if frozenset(aristas(t)) not in vistas:
            vistas.add(frozenset(aristas(t)))
            buenas.append(t)
    print(f'  longitud media: rutas al azar {st.mean(longitud(t, pts20) for t in azar):.1f}, '
          f'rutas buenas {st.mean(longitud(t, pts20) for t in buenas):.1f}')
    for nombre, rutas in (('al azar', azar), ('buenas', buenas)):
        for op in ('intercambio', 'inversion'):
            cambio, conservadas = [], []
            for t in rutas:
                lt = longitud(t, pts20)
                for _ in range(50):
                    u = list(t)
                    i, j = sorted(r.sample(range(20), 2))
                    if op == 'intercambio':
                        u[i], u[j] = u[j], u[i]
                    else:
                        u[i:j + 1] = u[i:j + 1][::-1]
                    cambio.append(100 * abs(longitud(u, pts20) - lt) / lt)
                    conservadas.append(len(aristas(u) & aristas(t)))
            print(f'  mutación {op}, rutas {nombre}: la longitud cambia un {st.mean(cambio):.1f} % de media; '
                  f'conserva {st.mean(conservadas):.1f} de 21 aristas')
    for nombre, rutas in (('al azar', azar), ('buenas', buenas)):
        for cr, fn in CRUCES.items():
            heredadas, sobre = [], []
            for k in range(0, 60, 2):
                a, b = rutas[k], rutas[k + 1]
                de_padres = aristas(a) | aristas(b)
                mejor_padre = min(longitud(a, pts20), longitud(b, pts20))
                for _ in range(20):
                    for h in fn(a, b, r):
                        heredadas.append(100 * len(aristas(h) & de_padres) / 21)
                        sobre.append(100 * (longitud(h, pts20) / mejor_padre - 1))
            print(f'  cruce {cr}, padres {nombre}: el hijo hereda el {st.mean(heredadas):.0f} % de sus aristas de los padres '
                  f'y es un {st.mean(sobre):+.0f} % más largo que el mejor padre')

    # --- tipo de cruce y de mutación en el algoritmo genético (sección 9.10)
    print('CRUCE x MUTACIÓN: 20 destinos, torneo 3, élite 1, media (error típico) de 30 ejecuciones; Pc = 0,6 salvo «sin cruce»')
    for op in ('intercambio', 'inversion'):
        for pm in (0.05, 0.2, 0.5, 1.0):
            fila = {}
            for cr, pc in (('sin cruce', 0.0), ('OX', PC), ('PMX', PC), ('CX', PC), ('ERX', PC)):
                v = [ejecutar(pts20, s, pm=pm, pc=pc, oper=op, cruce='OX' if cr == 'sin cruce' else cr)[-1] for s in semillas]
                fila[cr] = f'{st.mean(v):.1f} ({st.stdev(v) / math.sqrt(len(v)):.1f})'
            print(f'  {op}, pm={pm}:', fila)
