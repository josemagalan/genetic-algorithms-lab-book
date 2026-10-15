"""Figura de la función de Himmelblau del capítulo 3 del libro «Evolución a la vista»:
la superficie en 3D y el mapa de curvas de nivel en la caja [−5, 5]².

  - f(x₁, x₂) = (x₁² + x₂ − 11)² + (x₁ + x₂² − 7)², la misma de 03-representacion.py.
  - La altura de la superficie es f, en escala lineal. El color, en los dos paneles, sigue los mismos
    niveles, espaciados de forma aproximadamente logarítmica: así se distinguen los cuatro valles, que
    en escala lineal quedan aplastados frente al valor de las esquinas (890 en (5, 5)).
  - Los rombos son los cuatro mínimos globales, con los mismos valores que en 03-representacion.py.
Los datos que se citan en el texto (máximo local, valor de las esquinas) salen de este guion y se
comprueban con assert.

Uso: python3 03-himmelblau.py   → escribe 03-himmelblau.svg y muestra los datos.
A diferencia de los demás guiones, necesita matplotlib y NumPy.
"""

import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap

A, B = -5.0, 5.0
MINIMOS = [(3.0, 2.0), (-2.805118, 3.131312), (-3.77931, -3.283186), (3.584428, -1.848126)]
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#7a7974', '#e4e3df'
AZUL, NARANJA = '#2a78d6', '#eb6834'
FUENTE = "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
NIVELES = [0, 1, 2, 5, 10, 20, 50, 100, 200, 400, 900]
LINEAS = [1, 10, 50, 100, 200, 400]
VISTA = (50, -60)


def coma(v, d=2):
    return f'{v:.{d}f}'.replace('.', ',').replace('-', '−')


def f(x, y):
    return (x * x + y - 11) ** 2 + (x + y * y - 7) ** 2


def maximo_local():
    """Máximo local del centro, por ascenso de gradiente desde (0, 0)."""
    x, y = 0.0, 0.0
    for _ in range(20000):
        gx = 4 * x * (x * x + y - 11) + 2 * (x + y * y - 7)
        gy = 2 * (x * x + y - 11) + 4 * y * (x + y * y - 7)
        x, y = x + 1e-3 * gx, y + 1e-3 * gy
    return x, y, f(x, y)


def configura():
    plt.rcParams.update({
        'svg.fonttype': 'none', 'svg.hashsalt': 'himmelblau',
        'font.family': 'sans-serif', 'font.sans-serif': ['DejaVu Sans'], 'font.size': 9.5,
        'text.color': INK, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
        'axes.edgecolor': MUTED, 'axes.unicode_minus': True,
    })
    colores = ['#123f78', AZUL, '#7fb0ea', '#dbe8f9', '#f6f5f1']
    cmap = LinearSegmentedColormap.from_list('himmelblau', colores)
    return cmap, BoundaryNorm(NIVELES, cmap.N)


def cmap_continuo(t):
    """La misma escala de colores, en continuo, para t = log(1 + f)/log(901) entre 0 y 1."""
    colores = ['#123f78', AZUL, '#7fb0ea', '#dbe8f9', '#e9e6dd']
    return LinearSegmentedColormap.from_list('continuo', colores)(t)


def figura():
    cmap, norm = configura()
    xs = np.linspace(A, B, 201)
    X, Y = np.meshgrid(xs, xs)
    Z = f(X, Y)
    fig = plt.figure(figsize=(7.6, 3.5))

    # Panel izquierdo: superficie
    ax = fig.add_axes([0.0, 0.02, 0.5, 0.96], projection='3d')
    ax.computed_zorder = False
    t = np.log1p(Z) / np.log1p(900)              # color continuo con la misma escala que los niveles
    ax.plot_surface(X, Y, Z, facecolors=cmap_continuo(t), rstride=2, cstride=2, linewidth=0,
                    antialiased=False, shade=False, rasterized=True, zorder=1)
    ax.plot_wireframe(X, Y, Z, rstride=20, cstride=20, color=INK2, linewidth=0.35, alpha=0.45, zorder=2)
    for mx, my in MINIMOS:
        ax.scatter([mx], [my], [0], marker='D', s=34, color=NARANJA, edgecolors='white', linewidths=1,
                   depthshade=False, zorder=3)
    ax.view_init(elev=VISTA[0], azim=VISTA[1])
    ax.set_xlim(A, B), ax.set_ylim(A, B), ax.set_zlim(0, 900)
    ax.set_xticks([-5, 0, 5]), ax.set_yticks([0, 5]), ax.set_zticks([0, 300, 600, 900])
    ax.set_xlabel('x₁', labelpad=-4), ax.set_ylabel('x₂', labelpad=-4)
    ax.set_zlabel('f', labelpad=-2)
    ax.tick_params(pad=-2, labelsize=8.5)
    for eje in (ax.xaxis, ax.yaxis, ax.zaxis):
        eje.set_pane_color((1, 1, 1, 0))
        eje._axinfo['grid'].update(color=GRID, linewidth=0.6)
    ax.set_box_aspect(None, zoom=0.9)
    fig.text(0.07, 0.9, 'Superficie', fontsize=10.5, fontweight='bold', color=INK)

    # Panel derecho: curvas de nivel
    bx = fig.add_axes([0.575, 0.19, 0.30, 0.30 * 7.6 / 3.5 * 0.97])
    bx.contourf(X, Y, Z, levels=NIVELES, cmap=cmap, norm=norm, extend='neither').set_rasterized(True)
    bx.contour(X, Y, Z, levels=LINEAS, colors='white', linewidths=0.7)
    for mx, my in MINIMOS:
        bx.plot(mx, my, marker='D', ms=7.5, color=NARANJA, mec='white', mew=1.4)
    bx.set_aspect('equal'), bx.set_xlim(A, B), bx.set_ylim(A, B)
    bx.set_xticks([-5, 0, 5]), bx.set_yticks([-5, 0, 5])
    bx.set_xlabel('x₁', labelpad=2), bx.set_ylabel('x₂', labelpad=0)
    for lado in bx.spines.values():
        lado.set_color(MUTED), lado.set_linewidth(0.8)
    fig.text(0.575, 0.9, 'Curvas de nivel', fontsize=10.5, fontweight='bold', color=INK)

    # Escala de colores, común a los dos paneles
    cx = fig.add_axes([0.905, 0.19, 0.018, bx.get_position().height])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cx, ticks=[0, 1, 10, 100, 900],
                      spacing='uniform')
    cb.outline.set_edgecolor(MUTED), cb.outline.set_linewidth(0.6)
    cb.ax.tick_params(labelsize=8.5, length=2)
    cb.ax.set_title('f', fontsize=9.5, color=INK2, pad=4)
    return fig


def svg_accesible(ruta, titulo, desc):
    """Cambia la fuente por la de las demás figuras y añade el título y la descripción del SVG."""
    s = open(ruta, encoding='utf-8').read()
    s = re.sub(r"font-family:\s*'?DejaVu Sans'?(, sans-serif)?", f'font-family: {FUENTE}', s)
    s = re.sub(r'<svg ([^>]*?)width="[^"]*" height="[^"]*" ', r'<svg \1', s, count=1)
    s = re.sub(r'(<svg [^>]*?)>', r'\1 role="img" aria-labelledby="t1 d1">' +
               f'\n <title id="t1">{titulo}</title>\n <desc id="d1">{desc}</desc>', s, count=1)
    open(ruta, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    mx, my, mf = maximo_local()
    esquinas = {(x, y): f(x, y) for x in (A, B) for y in (A, B)}
    assert abs(mx + 0.270845) < 1e-4 and abs(my + 0.923039) < 1e-4 and abs(mf - 181.617) < 1e-3
    assert max(esquinas.values()) == 890 and all(f(x, y) < 1e-9 for x, y in MINIMOS[:1])
    assert all(f(x, y) < 1e-8 for x, y in MINIMOS)
    figura().savefig('03-himmelblau.svg', dpi=200, metadata={'Date': None})
    svg_accesible('03-himmelblau.svg', 'La función de Himmelblau en la caja de −5 a 5',
                  'A la izquierda, la superficie de f en tres dimensiones; a la derecha, sus curvas de nivel. '
                  'La función tiene cuatro mínimos globales, con f = 0, marcados con rombos, cada uno en su '
                  f'valle; en el centro hay un máximo local, cerca de ({coma(mx, 2)}; {coma(my, 2)}), con f ≈ '
                  f'{coma(mf, 1)}, y la función crece hacia las esquinas, hasta 890 en (5; 5).')
    print('Máximo local:', round(mx, 6), round(my, 6), round(mf, 3))
    print('Esquinas:', esquinas)
