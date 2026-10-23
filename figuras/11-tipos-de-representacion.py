"""Figura fig-tipos-representacion del capítulo 11 del libro «Evolución a la vista»: las cuatro
representaciones del libro, cada una con un cromosoma (arriba) y la solución que describe (abajo).

Los cuatro casos son los ejemplos del capítulo 3, con los mismos datos:
  - Binaria, mochila (sección 3.7): pesos 3 5 2 4 6 1, valores 4 6 3 5 7 2, W = 10; cromosoma 1 0 1 1 0 1
    → objetos 1, 3, 4 y 6, peso 10, valor 14 (el óptimo).
  - Entera, asignación (sección 3.4): 5 tareas y 3 máquinas con los tiempos de la tabla; cromosoma
    2 1 3 2 1 → cargas 7, 10 y 5, makespan 10.
  - Real, función de Himmelblau (sección 3.6): cromosoma (3; 2), uno de los cuatro mínimos, f = 0.
  - Permutación, viajante (sección 3.5): 6 ciudades de la semilla 3 de representation-ga
    (TSP.randomInstance(3, 6), commit 59ff580), cromosoma 1 3 5 2 6 4 → circuito de 327,4. Como en la
    herramienta, el eje vertical del mapa crece hacia abajo.
Todos los valores se recalculan aquí y se comprueban con assert.

Uso: python3 11-tipos-de-representacion.py   → escribe 11-tipos-de-representacion.svg.
Necesita matplotlib y NumPy, como 03-himmelblau.py.
"""

import math
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap
from matplotlib.patches import ConnectionPatch, FancyBboxPatch, Rectangle

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#7a7974', '#e4e3df'
AZUL, NARANJA = '#2a78d6', '#eb6834'
AZUL_OSCURO, AZUL_CLARO = '#123f78', '#dbe8f9'
MAQUINAS = [AZUL_OSCURO, AZUL, NARANJA]
FUENTE = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

# Datos de los ejemplos del capítulo 3
PESOS, VALORES, W = [3, 5, 2, 4, 6, 1], [4, 6, 3, 5, 7, 2], 10
MOCHILA = [1, 0, 1, 1, 0, 1]
TIEMPOS = [[4, 6, 3], [5, 2, 7], [3, 3, 5], [6, 4, 2], [2, 5, 6]]   # tarea × máquina
ASIGNACION = [2, 1, 3, 2, 1]
PUNTO = (3.0, 2.0)
CIUDADES = [(41.8, 8.2), (89.2, 15.1), (21.0, 25.9), (88.0, 37.2), (25.6, 87.0), (65.8, 63.6)]
CIRCUITO = [1, 3, 5, 2, 6, 4]
NIVELES = [0, 1, 2, 5, 10, 20, 50, 100, 200, 400, 900]   # los de 03-himmelblau.py


def coma(v, d=1):
    return f'{v:.{d}f}'.replace('.', ',').replace('-', '−')


def himmelblau(x, y):
    return (x * x + y - 11) ** 2 + (x + y * y - 7) ** 2


def longitud(circuito):
    """Como en representation-ga: cada tramo, la distancia euclídea redondeada a décimas."""
    tramos = zip(circuito, circuito[1:] + circuito[:1])
    return round(sum(round(math.dist(CIUDADES[a - 1], CIUDADES[b - 1]), 1) for a, b in tramos), 1)


def cargas():
    c = [0, 0, 0]
    for tarea, maquina in enumerate(ASIGNACION):
        c[maquina - 1] += TIEMPOS[tarea][maquina - 1]
    return c


def cromosoma(ax, genes, colores=None, ancho=1.0):
    """Tira de casillas, una por gen, centrada en el eje."""
    n = len(genes)
    for i, g in enumerate(genes):
        fondo = colores[i] if colores else 'white'
        ax.add_patch(Rectangle((i * ancho, 0), ancho, 1, facecolor=fondo, edgecolor=INK, linewidth=1.1))
        ax.text(i * ancho + ancho / 2, 0.5, g, ha='center', va='center', fontsize=11, fontweight='bold',
                color='white' if fondo != 'white' else INK)
    margen = (7.4 - n * ancho) / 2
    ax.set_xlim(-margen, n * ancho + margen)
    ax.set_ylim(-0.1, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')


def flecha(sub, arriba, abajo):
    sub.add_artist(ConnectionPatch(xyA=(0.5, -0.06), coordsA=arriba.transAxes, xyB=(0.5, 1.03),
                                   coordsB=abajo.transAxes, arrowstyle='-|>', mutation_scale=12,
                                   color=MUTED, linewidth=1.2))


def panel(sub, titulo, subtitulo, abajo=0.03):
    sub.text(0.5, 0.965, titulo, ha='center', va='top', fontsize=12, fontweight='bold', color=INK)
    sub.text(0.5, 0.885, subtitulo, ha='center', va='top', fontsize=9.5, color=INK2)
    gs = sub.add_gridspec(2, 1, height_ratios=[1, 3.3], hspace=0.32, top=0.80, bottom=abajo,
                          left=0.05, right=0.95)
    return sub.add_subplot(gs[0]), sub.add_subplot(gs[1])


def binaria(sub):
    g, s = panel(sub, 'Binaria', 'Pertenencia · la mochila')
    cromosoma(g, [str(b) for b in MOCHILA], [AZUL if b else 'white' for b in MOCHILA])
    # La mochila como una barra de capacidad W; cada objeto, tan ancho como su peso
    x0 = 0.8                                    # para centrar la mochila sobre la fila de los que quedan fuera
    x = x0
    for i, b in enumerate(MOCHILA):
        if b:
            s.add_patch(FancyBboxPatch((x + 0.06, 2.06), PESOS[i] - 0.12, 0.88, boxstyle='round,pad=0,rounding_size=0.12',
                                       facecolor=AZUL, edgecolor='none'))
            s.text(x + PESOS[i] / 2, 2.5, str(i + 1), ha='center', va='center', color='white',
                   fontweight='bold', fontsize=10.5)
            x += PESOS[i]
    s.add_patch(Rectangle((x0, 2), W, 1, facecolor='none', edgecolor=INK, linewidth=1.4))
    s.text(x0 + W / 2, 3.25, f'Mochila (W = {W})', ha='center', va='bottom', fontsize=9, color=INK2)
    x = 0.0
    for i, b in enumerate(MOCHILA):
        if not b:
            s.add_patch(FancyBboxPatch((x + 0.06, 0.66), PESOS[i] - 0.12, 0.88, boxstyle='round,pad=0,rounding_size=0.12',
                                       facecolor=GRID, edgecolor=MUTED, linewidth=0.8))
            s.text(x + PESOS[i] / 2, 1.1, str(i + 1), ha='center', va='center', color=MUTED,
                   fontweight='bold', fontsize=10.5)
            x += PESOS[i] + 0.6
    s.text(x0 + W / 2, 0.12, 'Fuera', ha='center', va='bottom', fontsize=9, color=MUTED)
    peso = sum(p for p, b in zip(PESOS, MOCHILA) if b)
    valor = sum(v for v, b in zip(VALORES, MOCHILA) if b)
    s.text(x0 + W / 2, -0.55, f'Peso {peso} de {W} · valor {valor}', ha='center', fontsize=9.5, color=INK)
    s.set_xlim(-0.6, W + 2.2), s.set_ylim(-0.8, 3.7)
    s.axis('off')
    flecha(sub, g, s)
    return peso, valor


def entera(sub):
    g, s = panel(sub, 'Entera', 'Asignación · tareas a máquinas')
    cromosoma(g, [str(m) for m in ASIGNACION], [MAQUINAS[m - 1] for m in ASIGNACION])
    c = cargas()
    for k in range(3):
        y = 2 - k
        s.text(-0.4, y + 0.4, f'Máquina {k + 1}', ha='right', va='center', fontsize=9.5,
               color=MAQUINAS[k], fontweight='bold')
        x = 0
        for tarea, maquina in enumerate(ASIGNACION):
            if maquina == k + 1:
                t = TIEMPOS[tarea][k]
                s.add_patch(FancyBboxPatch((x + 0.05, y + 0.1), t - 0.1, 0.6, boxstyle='round,pad=0,rounding_size=0.1',
                                           facecolor=MAQUINAS[k], edgecolor='none'))
                s.text(x + t / 2, y + 0.4, f'T{tarea + 1}', ha='center', va='center', color='white',
                       fontweight='bold', fontsize=9.5)
                x += t
    mk = max(c)
    s.plot([mk, mk], [-0.15, 3.0], color=INK, linewidth=1, linestyle=(0, (3, 2)))
    s.text(mk, 3.08, f'makespan {mk}', ha='center', va='bottom', fontsize=9, color=INK)
    s.plot([0, 0], [-0.15, 3.0], color=MUTED, linewidth=0.8)
    for t in range(0, 11, 2):
        s.text(t, -0.3, str(t), ha='center', va='top', fontsize=8, color=MUTED)
    s.text(5, -0.85, 'tiempo', ha='center', va='top', fontsize=8.5, color=MUTED)
    s.set_xlim(-4.2, 11.2), s.set_ylim(-1.3, 3.6)
    s.axis('off')
    flecha(sub, g, s)
    return c


def real(sub):
    g, s = panel(sub, 'Real', 'Optimización continua · la función de Himmelblau', abajo=0.1)
    cromosoma(g, [coma(PUNTO[0], 2), coma(PUNTO[1], 2)], ancho=2.2)
    colores = ['#123f78', AZUL, '#7fb0ea', '#dbe8f9', '#f6f5f1']
    cmap = LinearSegmentedColormap.from_list('himmelblau', colores)
    xs = np.linspace(-5, 5, 201)
    X, Y = np.meshgrid(xs, xs)
    Z = himmelblau(X, Y)
    s.contourf(X, Y, Z, levels=NIVELES, cmap=cmap, norm=BoundaryNorm(NIVELES, cmap.N)).set_rasterized(True)
    s.contour(X, Y, Z, levels=[1, 10, 50, 100, 200, 400], colors='white', linewidths=0.6)
    s.plot(*PUNTO, marker='o', ms=9, color=NARANJA, mec='white', mew=1.6)
    s.annotate(f'({coma(PUNTO[0], 0)}; {coma(PUNTO[1], 0)}), f = {coma(himmelblau(*PUNTO), 0)}', PUNTO,
               xytext=(-9, -4), textcoords='offset points', ha='right', va='top', fontsize=9, color=INK)
    s.set_aspect('equal'), s.set_xlim(-5, 5), s.set_ylim(-5, 5)
    s.set_xticks([-5, 0, 5]), s.set_yticks([-5, 0, 5])
    s.tick_params(labelsize=8, colors=INK2, length=2, pad=2)
    s.set_xlabel('x₁', fontsize=9, color=INK2, labelpad=1)
    s.set_ylabel('x₂', fontsize=9, color=INK2, labelpad=1, rotation=0)
    for lado in s.spines.values():
        lado.set_color(MUTED), lado.set_linewidth(0.8)
    flecha(sub, g, s)
    return himmelblau(*PUNTO)


def permutacion(sub):
    g, s = panel(sub, 'Permutación', 'Ordenación · el viajante')
    cromosoma(g, [str(c) for c in CIRCUITO])
    cerrado = CIRCUITO + CIRCUITO[:1]
    for a, b in zip(cerrado, cerrado[1:]):
        s.annotate('', xy=CIUDADES[b - 1], xytext=CIUDADES[a - 1],
                   arrowprops=dict(arrowstyle='-|>', color=AZUL, lw=1.6, shrinkA=10, shrinkB=10,
                                   mutation_scale=11))
    for c, (x, y) in enumerate(CIUDADES, start=1):
        s.plot(x, y, marker='o', ms=17, color='white', mec=INK, mew=1.3, zorder=3)
        s.text(x, y, str(c), ha='center', va='center', fontsize=9.5, fontweight='bold', zorder=4)
    L = longitud(CIRCUITO)
    s.text(55, 108, f'Longitud {coma(L)}', ha='center', va='top', fontsize=9.5, color=INK)
    s.set_xlim(5, 105), s.set_ylim(112, -2)     # el eje vertical crece hacia abajo, como en la herramienta
    s.set_aspect('equal')
    s.axis('off')
    flecha(sub, g, s)
    return L


def svg_accesible(ruta, titulo, desc):
    """Como en 03-himmelblau.py: fuente de las demás figuras, sin tamaño fijo, con título y descripción."""
    s = open(ruta, encoding='utf-8').read()
    s = re.sub(r"font-family:\s*'?DejaVu Sans'?(, sans-serif)?", f'font-family: {FUENTE}', s)
    s = re.sub(r'<svg ([^>]*?)width="[^"]*" height="[^"]*" ', r'<svg \1', s, count=1)
    s = re.sub(r'(<svg [^>]*?)>', r'\1 role="img" aria-labelledby="t1 d1">' +
               f'\n <title id="t1">{titulo}</title>\n <desc id="d1">{desc}</desc>', s, count=1)
    open(ruta, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    plt.rcParams.update({
        'svg.fonttype': 'none', 'svg.hashsalt': 'tipos-representacion',
        'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans'], 'font.size': 9.5,
        'text.color': INK, 'axes.unicode_minus': True,
    })
    fig = plt.figure(figsize=(7.6, 7.4))
    sub = fig.subfigures(2, 2, wspace=0.03, hspace=0.03)
    peso, valor = binaria(sub[0, 0])
    c = entera(sub[0, 1])
    f0 = real(sub[1, 0])
    L = permutacion(sub[1, 1])
    assert (peso, valor) == (10, 14)
    assert c == [7, 10, 5] and max(c) == 10
    assert f0 == 0
    assert L == 327.4 and longitud([1, 3, 5, 6, 4, 2]) == 239.6
    fig.savefig('11-tipos-de-representacion.svg', metadata={'Date': None}, dpi=200)
    svg_accesible('11-tipos-de-representacion.svg', 'Las cuatro representaciones del libro, del cromosoma a la solución',
                  'Cuatro paneles. Binaria: el cromosoma 1 0 1 1 0 1 mete en la mochila los objetos 1, 3, 4 y 6, '
                  'que pesan 10 de 10 y valen 14. Entera: el cromosoma 2 1 3 2 1 reparte cinco tareas entre tres '
                  'máquinas, con cargas 7, 10 y 5 y makespan 10. Real: el cromosoma (3,00; 2,00) es el punto (3; 2) '
                  'de la función de Himmelblau, uno de sus mínimos, con f = 0. Permutación: el cromosoma '
                  '1 3 5 2 6 4 es un circuito por seis ciudades que mide 327,4.')
    print('Mochila: peso', peso, 'valor', valor, '| Cargas', c, '| f', f0, '| Circuito', L)
