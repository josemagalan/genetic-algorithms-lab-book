"""Figuras propias del capítulo 1 del libro «Evolución a la vista»: un paisaje con un óptimo
local y uno global, y el cubo de las cadenas de 3 bits del ejercicio «Subir por los vecinos».

  - Paisaje: 21 soluciones, x = 0, 1, …, 20, vecinas si se diferencian en 1. Se maximiza
    f(x) = 1 + 6 exp(−(x − 5)²/8) + 9 exp(−(x − 15)²/10), que tiene una cima local en x = 5 y la global
    en x = 15. Dos búsquedas que pasan siempre al mejor vecino, mientras sea mejor, salen de x = 1 y de
    x = 11.
  - Cubo: los valores de f son los de la tabla del ejercicio; dos cadenas son vecinas si se diferencian
    en un bit. De cada cadena sale una flecha hacia su mejor vecino, si es mejor que ella.
Las paradas de las búsquedas y las cuencas se calculan aquí y se comprueban con assert; coinciden con la
solución del ejercicio.

Uso: python3 01-evolucion.py   → escribe 01-paisaje.svg y 01-cubo-vecinos.svg, y muestra los datos.
Solo usa la biblioteca estándar de Python 3.
"""

from math import exp

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#7a7974', '#e4e3df'
AZUL, NARANJA = '#2a78d6', '#eb6834'
AZUL_CLARO, NARANJA_CLARO = '#dbe8f9', '#fbe1d6'
FUENTE = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""


def coma(v, d=1):
    """Número con coma decimal y el signo menos tipográfico."""
    return f'{v:.{d}f}'.replace('.', ',').replace('-', '−')


def abre(W, H, ident, titulo, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t{ident} d{ident}" {FUENTE}>',
            f'<title id="t{ident}">{titulo}</title>',
            f'<desc id="d{ident}">{desc}</desc>',
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>']


def texto(x, y, s, size=13, color=INK2, ancla='start', peso=None, extra=''):
    p = f' font-weight="{peso}"' if peso else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{ancla}"{p}{extra}>{s}</text>'


def punta(x, y, ux, uy, color, largo=10, ancho=5.5):
    """Punta de flecha en (x, y) que apunta en la dirección unitaria (ux, uy)."""
    bx, by = x - largo * ux, y - largo * uy
    return (f'<polygon points="{x:.1f},{y:.1f} {bx - ancho * uy:.1f},{by + ancho * ux:.1f} '
            f'{bx + ancho * uy:.1f},{by - ancho * ux:.1f}" fill="{color}"/>')


def mejor_vecino(s, vecinos, f):
    """El mejor vecino de s, o None si ninguno es mejor que s (s es un óptimo local)."""
    v = max(vecinos(s), key=f)
    return v if f(v) > f(s) else None


def sube(s, vecinos, f):
    camino = [s]
    while (v := mejor_vecino(camino[-1], vecinos, f)) is not None:
        camino.append(v)
    return camino


# ----------------------------------------------------------------------------------------------
# fig-optimos-locales: óptimos locales en un paisaje de una dimensión
# ----------------------------------------------------------------------------------------------

N = 21
INICIOS = (1, 11)


def f_paisaje(x):
    return 1 + 6 * exp(-(x - 5) ** 2 / 8) + 9 * exp(-(x - 15) ** 2 / 10)


def vecinos_paisaje(x):
    return [v for v in (x - 1, x + 1) if 0 <= v < N]


def figura_paisaje():
    caminos = [sube(s, vecinos_paisaje, f_paisaje) for s in INICIOS]
    optimos = [x for x in range(N) if mejor_vecino(x, vecinos_paisaje, f_paisaje) is None]
    assert optimos == [5, 15] and caminos[0][-1] == 5 and caminos[1][-1] == 15
    W, H = 760, 400
    izq, der, arr, aba = 64, 730, 84, 338
    ymax = 11
    X = lambda x: izq + x * (der - izq) / (N - 1)
    Y = lambda y: aba - y * (aba - arr) / ymax
    o = abre(W, H, '1', 'Dos búsquedas que pasan siempre al mejor vecino, en un paisaje con dos cimas',
             f'Valor de la función objetivo, que se quiere maximizar, para 21 soluciones, de x = 0 a x = 20. '
             f'Cada solución es vecina de las que tiene al lado. Hay dos cimas: un óptimo local en x = 5, con '
             f'f = {coma(f_paisaje(5))}, y el óptimo global en x = 15, con f = {coma(f_paisaje(15))}. Una búsqueda '
             f'que empieza en x = 1 sube hasta x = 5 y se para, porque ningún vecino es mejor. Otra que empieza '
             f'en x = 11 sube hasta x = 15, el óptimo global.')
    # Rejilla y ejes
    for t in range(0, ymax, 2):
        o.append(f'<line x1="{izq}" y1="{Y(t):.1f}" x2="{der}" y2="{Y(t):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(texto(izq - 10, Y(t) + 4, str(t), 12, INK2, 'end'))
    o.append(f'<line x1="{izq}" y1="{aba}" x2="{der}" y2="{aba}" stroke="{MUTED}" stroke-width="1"/>')
    for x in range(0, N, 5):
        o.append(texto(X(x), aba + 20, str(x), 12, INK2, 'middle'))
    o.append(texto((izq + der) / 2, aba + 44, 'Solución x', 13, INK2, 'middle'))
    o.append(texto(izq - 46, (arr + aba) / 2, 'f(x)', 13, INK2, 'middle'))
    # Paisaje: puntos unidos por una línea fina
    puntos = ' '.join(f'{X(x):.1f},{Y(f_paisaje(x)):.1f}' for x in range(N))
    o.append(f'<polyline points="{puntos}" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')
    for x in range(N):
        o.append(f'<circle cx="{X(x):.1f}" cy="{Y(f_paisaje(x)):.1f}" r="4" fill="#ffffff" stroke="{INK2}" stroke-width="1.5"/>')
    # Caminos: arcos sobre los puntos, de cada solución a la siguiente
    for camino, color in zip(caminos, (NARANJA, AZUL)):
        for a, b in zip(camino, camino[1:]):
            x0, y0, x1, y1 = X(a), Y(f_paisaje(a)) - 10, X(b), Y(f_paisaje(b)) - 10
            cx, cy = (x0 + x1) / 2, min(y0, y1) - 12
            o.append(f'<path d="M{x0:.1f},{y0:.1f} Q{cx:.1f},{cy:.1f} {x1:.1f},{y1:.1f}" fill="none" '
                     f'stroke="{color}" stroke-width="2"/>')
            dx, dy = x1 - cx, y1 - cy
            n = (dx * dx + dy * dy) ** 0.5
            o.append(punta(x1, y1, dx / n, dy / n, color, 8, 4.5))
        s, e = camino[0], camino[-1]
        o.append(f'<circle cx="{X(s):.1f}" cy="{Y(f_paisaje(s)):.1f}" r="6" fill="{color}"/>')
        o.append(f'<circle cx="{X(e):.1f}" cy="{Y(f_paisaje(e)):.1f}" r="7" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
        o.append(texto(X(s), Y(f_paisaje(s)) + 24, 'inicio', 12, color, 'middle', 600))
    # Etiquetas de las cimas
    o.append(texto(X(5), Y(f_paisaje(5)) - 40, 'óptimo local', 13, INK, 'middle', 600))
    o.append(texto(X(15), Y(f_paisaje(15)) - 40, 'óptimo global', 13, INK, 'middle', 600))
    # Leyenda
    ly = 24
    o.append(f'<circle cx="{izq + 6}" cy="{ly - 4}" r="6" fill="{NARANJA}"/>')
    o.append(texto(izq + 18, ly, 'Empieza en x = 1 y se para en el óptimo local', 13, INK))
    o.append(f'<circle cx="{izq + 376}" cy="{ly - 4}" r="6" fill="{AZUL}"/>')
    o.append(texto(izq + 388, ly, 'Empieza en x = 11 y llega al global', 13, INK))
    o.append('</svg>')
    return '\n'.join(o) + '\n', dict(caminos=caminos, optimos=optimos,
                                      f={x: round(f_paisaje(x), 3) for x in range(N)})


# ----------------------------------------------------------------------------------------------
# fig-cubo-vecinos: el cubo de las cadenas de 3 bits
# ----------------------------------------------------------------------------------------------

F_CUBO = {'000': 3, '001': 1, '010': 2, '011': 5, '100': 4, '101': 0, '110': 6, '111': 2}


def vecinos_cubo(s):
    return [s[:i] + ('1' if s[i] == '0' else '0') + s[i + 1:] for i in range(3)]


def figura_cubo():
    f = F_CUBO.get
    flecha_de = {s: mejor_vecino(s, vecinos_cubo, f) for s in F_CUBO}
    final = {s: sube(s, vecinos_cubo, f)[-1] for s in F_CUBO}
    assert [s for s, v in flecha_de.items() if v is None] == ['011', '110']
    assert final['001'] == '011' and final['010'] == '110'
    assert sorted(s for s in F_CUBO if final[s] == '011') == ['001', '011']
    W, H = 760, 430
    # Proyección: el primer bit desplaza a la derecha, el segundo hacia arriba y el tercero en diagonal
    pos = {s: (175 + 290 * int(s[0]) + 120 * int(s[2]), 340 - 200 * int(s[1]) - 90 * int(s[2])) for s in F_CUBO}
    R = 31
    o = abre(W, H, '2', 'Las ocho cadenas de 3 bits como vértices de un cubo, con una flecha hacia el mejor vecino',
             'Cada vértice es una cadena con su valor de f; las aristas unen las cadenas que se diferencian en un '
             'bit. De cada cadena sale una flecha hacia su mejor vecino, si es mejor que ella: 000 va a 100; 001, '
             'a 011; 010, a 110; 100, a 110; 101, a 100, y 111, a 110. De 011 y de 110 no sale ninguna flecha: '
             'son óptimos locales, y 110, con f = 6, es el global. Siguiendo las flechas, desde 001 se llega a '
             '011; desde las otras cinco cadenas, a 110.')
    # Aristas
    for s in F_CUBO:
        for v in vecinos_cubo(s):
            if s < v:
                (x0, y0), (x1, y1) = pos[s], pos[v]
                o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{GRID}" stroke-width="3"/>')
    # Flechas hacia el mejor vecino
    for s, v in flecha_de.items():
        if v is None:
            continue
        (x0, y0), (x1, y1) = pos[s], pos[v]
        dx, dy = x1 - x0, y1 - y0
        n = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / n, dy / n
        color = AZUL if final[s] == '110' else NARANJA
        a = (x0 + (R + 4) * ux, y0 + (R + 4) * uy)
        b = (x1 - (R + 5) * ux, y1 - (R + 5) * uy)
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0] - 8 * ux:.1f}" y2="{b[1] - 8 * uy:.1f}" '
                 f'stroke="{color}" stroke-width="3"/>')
        o.append(punta(b[0], b[1], ux, uy, color, 13, 7))
    # Vértices
    for s, (x, y) in pos.items():
        azul = final[s] == '110'
        fill, stroke = (AZUL_CLARO, AZUL) if azul else (NARANJA_CLARO, NARANJA)
        ancho = 3.5 if flecha_de[s] is None else 1.5
        o.append(f'<circle cx="{x}" cy="{y}" r="{R}" fill="{fill}" stroke="{stroke}" stroke-width="{ancho}"/>')
        o.append(texto(x, y - 2, s, 16, INK, 'middle', 600, ' font-family="ui-monospace, Menlo, Consolas, monospace"'))
        o.append(texto(x, y + 17, f'f = {F_CUBO[s]}', 13, INK2, 'middle'))
    # Etiquetas de los óptimos
    x, y = pos['110']
    o.append(texto(x + R + 8, y + 5, 'óptimo global', 13, INK, 'start', 600))
    x, y = pos['011']
    o.append(texto(x - R - 8, y - 22, 'óptimo local', 13, INK, 'end', 600))
    # Leyenda
    ly = H - 18
    o.append(f'<circle cx="40" cy="{ly - 4}" r="7" fill="{AZUL_CLARO}" stroke="{AZUL}" stroke-width="1.5"/>')
    o.append(texto(54, ly, 'Siguiendo las flechas se llega a 110', 13, INK))
    o.append(f'<circle cx="340" cy="{ly - 4}" r="7" fill="{NARANJA_CLARO}" stroke="{NARANJA}" stroke-width="1.5"/>')
    o.append(texto(354, ly, 'Se llega a 011', 13, INK))
    o.append(texto(500, ly, 'Borde grueso: ningún vecino es mejor', 13, INK2))
    o.append('</svg>')
    return '\n'.join(o) + '\n', dict(flecha=flecha_de, final=final)


if __name__ == '__main__':
    svg1, d1 = figura_paisaje()
    with open('01-paisaje.svg', 'w', encoding='utf-8') as fh:
        fh.write(svg1)
    print('fig-optimos-locales: óptimos locales', d1['optimos'])
    for c in d1['caminos']:
        print('  camino', c)
    print('  f(x):', d1['f'])
    svg2, d2 = figura_cubo()
    with open('01-cubo-vecinos.svg', 'w', encoding='utf-8') as fh:
        fh.write(svg2)
    print('fig-cubo-vecinos: mejor vecino', d2['flecha'])
    print('  final', d2['final'])
