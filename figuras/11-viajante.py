"""Figuras 11.1 y 11.2 del libro «Algoritmos genéticos, paso a paso»: el mapa de seis lugares del capítulo 11
y la generación a mano de la sección 11.3.

El mapa es el que genera EvoTraveller (https://evotraveller.streamlit.app/) con Number of places = 6 y
Seed = 1111: el origen (0, 0) y cinco lugares en puntos enteros de una cuadrícula de 10 × 10. Las
coordenadas se obtuvieron con el código de la herramienta (repositorio jismartin/evotraveller, commit
41205ad: algorithm.set_seed(1111) y algorithm.places(10, 5)) y se copian aquí para no depender de él.

Una ruta se escribe como el orden de visita de los lugares 1–5 (el cromosoma); la ruta completa sale y
vuelve al origen. La longitud es la suma de las distancias euclídeas, como en EvoTraveller.

Uso: python3 11-viajante.py   → escribe 11-mapa.svg y 11-generacion.svg, y muestra la tabla de distancias,
las longitudes de las rutas del capítulo y la mejor ruta (por enumeración de las 120 permutaciones).
Solo usa la biblioteca estándar de Python 3.
"""
import itertools
import math
from pathlib import Path

LUGARES = {1: (7, 8), 2: (5, 6), 3: (1, 4), 4: (2, 8), 5: (4, 6)}
ORIGEN = (0, 0)

# Generación a mano de la sección 11.3
POBLACION = {'A': (5, 2, 1, 3, 4), 'B': (3, 1, 2, 4, 5), 'C': (2, 1, 3, 5, 4), 'D': (1, 5, 4, 2, 3)}
SIGUIENTE = {'B (élite)': (3, 1, 2, 4, 5), 'D (copia)': (1, 5, 4, 2, 3),
             'H1 (cruce)': (4, 1, 2, 5, 3), 'H2 (cruce y mutación)': (5, 2, 1, 4, 3)}

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#7a7974', '#e4e3df'
AZUL, NARANJA = '#2a78d6', '#eb6834'
FUENTE = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""


def punto(i):
    return ORIGEN if i == 0 else LUGARES[i]


def longitud(orden):
    ruta = [0] + list(orden) + [0]
    return sum(math.dist(punto(ruta[k]), punto(ruta[k + 1])) for k in range(len(ruta) - 1))


def coma(x, d=2):
    return f'{x:.{d}f}'.replace('.', ',')


def cabecera(w, h, titulo, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d" {FUENTE}>',
            f'<title id="t">{titulo}</title>', f'<desc id="d">{desc}</desc>',
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>']


def texto(x, y, s, size=12, color=INK2, ancla='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{ancla}"{extra}>{s}</text>'


def mapa(o, x0, y0, lado, orden=None, color=AZUL, etiquetas=True, rejilla=True, ancho=2.5, radio=9, fuente=12):
    """Dibuja la cuadrícula 0–9 con el origen y los lugares; si hay orden, la ruta completa."""
    paso = lado / 10
    X = lambda x: x0 + paso * (x + 0.5)
    Y = lambda y: y0 + lado - paso * (y + 0.5)
    o.append(f'<rect x="{x0}" y="{y0}" width="{lado}" height="{lado}" fill="#fbfbfa" stroke="{GRID}"/>')
    if rejilla:
        for v in range(10):
            o.append(f'<line x1="{X(v):.1f}" y1="{Y(0):.1f}" x2="{X(v):.1f}" y2="{Y(9):.1f}" stroke="{GRID}" stroke-width="0.8"/>')
            o.append(f'<line x1="{X(0):.1f}" y1="{Y(v):.1f}" x2="{X(9):.1f}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="0.8"/>')
    if orden is not None:
        ruta = [0] + list(orden) + [0]
        p = ' '.join(f'{X(punto(i)[0]):.1f},{Y(punto(i)[1]):.1f}' for i in ruta)
        o.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{ancho}" stroke-linejoin="round"/>')
    s = radio * 1.6
    o.append(f'<rect x="{X(0) - s / 2:.1f}" y="{Y(0) - s / 2:.1f}" width="{s:.1f}" height="{s:.1f}" fill="{INK}"/>')
    if etiquetas:
        o.append(texto(X(0) + s / 2 + 4, Y(0) - s / 2 - 2, 'O', fuente, INK, 'start', ' font-weight="600"'))
    for i, (x, y) in LUGARES.items():
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{radio}" fill="#ffffff" stroke="{INK}" stroke-width="1.6"/>')
        if etiquetas:
            o.append(texto(X(x), Y(y) + fuente * 0.36, str(i), fuente, INK, 'middle', ' font-weight="600"'))
    return X, Y


def fig_mapa(mejor):
    W, H = 720, 470
    lado = 400
    o = cabecera(W, H, 'Mapa de seis lugares del capítulo 11 y la mejor ruta',
                 'Cuadrícula de 10 por 10 con el origen O en (0, 0) y cinco lugares: 1 en (7, 8), 2 en (5, 6), 3 en (1, 4), '
                 f'4 en (2, 8) y 5 en (4, 6). La mejor ruta, O 3 4 1 2 5 O, mide {coma(longitud(mejor))}.')
    X, Y = mapa(o, 40, 30, lado, mejor, radio=11, fuente=13)
    for v in range(10):
        o.append(texto(X(v), 30 + lado + 18, str(v), 11, MUTED, 'middle'))
        o.append(texto(30, Y(v) + 4, str(v), 11, MUTED, 'end'))
    tx = 480
    o.append(texto(tx, 60, 'Lugares', 14, INK, 'start', ' font-weight="600"'))
    o.append(texto(tx, 84, 'O  (0, 0)  origen', 13, INK2))
    for k, (i, (x, y)) in enumerate(LUGARES.items()):
        o.append(texto(tx, 108 + 24 * k, f'{i}  ({x}, {y})', 13, INK2))
    o.append(texto(tx, 260, 'La mejor ruta', 14, INK, 'start', ' font-weight="600"'))
    o.append(f'<line x1="{tx}" y1="280" x2="{tx + 36}" y2="280" stroke="{AZUL}" stroke-width="3"/>')
    o.append(texto(tx + 44, 284, 'O 3 4 1 2 5 O', 13, INK2))
    o.append(texto(tx, 308, f'longitud {coma(longitud(mejor))}', 13, INK2))
    o.append(texto(tx, 332, '(o la misma al revés)', 13, INK2))
    o.append('</svg>')
    return '\n'.join(o) + '\n'


def fig_generacion():
    W, H = 760, 540
    lado, sep = 160, 24
    o = cabecera(W, H, 'Una generación a mano: población inicial y población siguiente',
                 'Arriba, las cuatro rutas de la población inicial con su longitud: A ' + coma(longitud(POBLACION['A'])) +
                 ', B ' + coma(longitud(POBLACION['B'])) + ', C ' + coma(longitud(POBLACION['C'])) + ' y D ' +
                 coma(longitud(POBLACION['D'])) + '. Abajo, la población siguiente: B, que pasa como élite; D, copiada; '
                 'H1, hijo del cruce de B y A, ' + coma(longitud(SIGUIENTE['H1 (cruce)'])) + '; y H2, hijo del cruce '
                 'mutado, ' + coma(longitud(SIGUIENTE['H2 (cruce y mutación)'])) + ', que es la mejor ruta posible.')
    filas = [('Población inicial', POBLACION, None), ('Población siguiente', SIGUIENTE, None)]
    for f, (nombre, pob, _) in enumerate(filas):
        y0 = 40 + f * 250
        o.append(texto(20, y0 - 14, nombre, 14, INK, 'start', ' font-weight="600"'))
        mejor = min(pob.values(), key=longitud)
        for c, (etq, orden) in enumerate(pob.items()):
            x0 = 20 + c * (lado + sep)
            color = NARANJA if orden == mejor else AZUL
            mapa(o, x0, y0, lado, orden, color, etiquetas=True, rejilla=False, ancho=2.2, radio=7, fuente=9)
            cad = ' '.join(map(str, orden))
            o.append(texto(x0, y0 + lado + 18, f'{etq}: {cad}', 12, INK, 'start'))
            o.append(texto(x0, y0 + lado + 34, f'longitud {coma(longitud(orden))}', 12, INK2, 'start'))
    o.append(f'<line x1="20" y1="{H - 18}" x2="52" y2="{H - 18}" stroke="{NARANJA}" stroke-width="3"/>')
    o.append(texto(60, H - 14, 'la ruta más corta de cada población', 12, INK2))
    o.append('</svg>')
    return '\n'.join(o) + '\n'


if __name__ == '__main__':
    aqui = Path(__file__).resolve().parent
    nodos = [0, 1, 2, 3, 4, 5]
    print('Distancias:')
    print('     ' + ''.join(f'{("O" if j == 0 else j):>7}' for j in nodos))
    for i in nodos:
        print(f'{("O" if i == 0 else i):>4} ' + ''.join(f'{coma(math.dist(punto(i), punto(j))):>7}' for j in nodos))
    rutas = sorted(itertools.permutations(LUGARES), key=longitud)
    mejor = rutas[0]
    print('Mejor ruta:', mejor, coma(longitud(mejor), 4), '| peor:', rutas[-1], coma(longitud(rutas[-1]), 4))
    print('Rutas distintas (contando cada una y su inversa una vez):', len({min(r, r[::-1]) for r in rutas}))
    for k, v in list(POBLACION.items()) + list(SIGUIENTE.items()):
        print(k, v, coma(longitud(v), 4), 'aptitud', f'{1 / longitud(v):.4f}')
    m0 = sum(map(longitud, POBLACION.values())) / 4
    m1 = sum(map(longitud, SIGUIENTE.values())) / 4
    print('Media inicial', coma(m0, 4), '| media siguiente', coma(m1, 4))
    (aqui / '11-mapa.svg').write_text(fig_mapa(mejor), encoding='utf-8')
    (aqui / '11-generacion.svg').write_text(fig_generacion(), encoding='utf-8')
