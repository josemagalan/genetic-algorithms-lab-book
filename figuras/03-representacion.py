"""Figuras fig-genotipo-fenotipo, fig-rejilla y fig-saltos-hamming del libro «Evolución a la vista»: genotipo y fenotipo, la rejilla de
puntos que puede escribir una cadena binaria y los saltos de Hamming entre enteros consecutivos.

Todo se calcula con las fórmulas del capítulo, sin usar la herramienta:
  - Función de Himmelblau f(x, y) = (x² + y − 11)² + (x + y² − 7)² en la caja [−5, 5]².
  - Cadena de 2k bits: k para cada variable, el primero el más significativo, z = Σ bⱼ 2^(k−1−j) y
    x = a + z (b − a)/(2^k − 1), como en representation-ga.
  - Código Gray reflejado: g₁ = b₁, gⱼ = bⱼ₋₁ ⊕ bⱼ.
Los valores que se citan en el texto (Δ, mejor punto de la rejilla y su valor) salen de este guion y
coinciden con los de la herramienta (memoria/verificaciones/2026-10-15-representacion.js).

Uso: python3 03-representacion.py   → escribe 03-genotipo-fenotipo.svg, 03-rejilla.svg y
03-saltos-hamming.svg, y muestra los datos. Solo usa la biblioteca estándar de Python 3.
"""

A, B = -5.0, 5.0
MINIMOS = [(3.0, 2.0), (-2.805118, 3.131312), (-3.77931, -3.283186), (3.584428, -1.848126)]
INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#7a7974', '#e4e3df'
AZUL, NARANJA = '#2a78d6', '#eb6834'
AZUL_CLARO = '#dbe8f9'
FUENTE = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""


def f(x, y):
    return (x * x + y - 11) ** 2 + (x + y * y - 7) ** 2


def coma(v, d=2):
    """Número con coma decimal y el signo menos tipográfico."""
    return f'{v:.{d}f}'.replace('.', ',').replace('-', '−')


def entero(bits):
    z = 0
    for b in bits:
        z = 2 * z + b
    return z


def a_bits(z, k):
    return [(z >> (k - 1 - j)) & 1 for j in range(k)]


def gray(bits):
    return [b if j == 0 else bits[j - 1] ^ b for j, b in enumerate(bits)]


def escala(z, k):
    return A + z * (B - A) / (2 ** k - 1)


def mejor_de_la_rejilla(k):
    n = 2 ** k
    mejor = None
    for z1 in range(n):
        for z2 in range(n):
            v = f(escala(z1, k), escala(z2, k))
            if mejor is None or v < mejor[0]:
                mejor = (v, escala(z1, k), escala(z2, k))
    return mejor


def abre(W, H, ident, titulo, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t{ident} d{ident}" {FUENTE}>',
            f'<title id="t{ident}">{titulo}</title>',
            f'<desc id="d{ident}">{desc}</desc>',
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>']


def texto(x, y, s, size=13, color=INK2, ancla='start', peso=None, extra=''):
    p = f' font-weight="{peso}"' if peso else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{ancla}"{p}{extra}>{s}</text>'


def flecha(x0, x1, y, color=INK2):
    return (f'<line x1="{x0}" y1="{y}" x2="{x1 - 8}" y2="{y}" stroke="{color}" stroke-width="2"/>'
            f'<polygon points="{x1},{y} {x1 - 10},{y - 5.5} {x1 - 10},{y + 5.5}" fill="{color}"/>')


def llave(x0, x1, y, color):
    """Llave horizontal bajo un grupo: una línea con dos remates hacia arriba."""
    return f'<path d="M{x0},{y - 6} V{y} H{x1} V{y - 6}" fill="none" stroke="{color}" stroke-width="2"/>'


# ----------------------------------------------------------------------------------------------
# fig-genotipo-fenotipo: genotipo y fenotipo
# ----------------------------------------------------------------------------------------------

def figura_genotipo_fenotipo():
    k = 4
    cromosoma = [1, 0, 1, 0, 0, 0, 1, 1]
    z1, z2 = entero(cromosoma[:k]), entero(cromosoma[k:])
    x1, x2 = escala(z1, k), escala(z2, k)
    fx = f(x1, x2)
    W, H = 760, 290
    o = abre(W, H, '1', 'Genotipo, fenotipo y aptitud de un individuo',
             f'Un cromosoma de 8 bits, 1010 0011, se decodifica en el punto (x₁, x₂) = ({coma(x1)}; {coma(x2)}), '
             f'y la función de aptitud lo evalúa: f = {coma(fx)}. El cruce y la mutación actúan sobre el '
             'cromosoma; la función de aptitud actúa sobre el punto decodificado.')
    # Etiquetas de columna
    o.append(texto(36, 44, 'Genotipo (cromosoma)', 14, INK, peso=600))
    o.append(texto(420, 44, 'Fenotipo (solución)', 14, INK, peso=600))
    o.append(texto(660, 44, 'Aptitud', 14, INK, peso=600))
    # Celdas del cromosoma
    cx0, cy, cw, ch, gap = 36, 74, 30, 36, 2
    for i, b in enumerate(cromosoma):
        x = cx0 + i * (cw + gap) + (6 if i >= k else 0)
        fill, stroke = (AZUL_CLARO, AZUL) if b else ('#ffffff', MUTED)
        o.append(f'<rect x="{x}" y="{cy}" width="{cw}" height="{ch}" rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        o.append(texto(x + cw / 2, cy + 24, str(b), 17, INK, 'middle', 600))
    gx = lambda i: cx0 + i * (cw + gap) + (6 if i >= k else 0)
    for g, (ini, fin, nombre, z) in enumerate([(0, k - 1, 'x₁', z1), (k, 2 * k - 1, 'x₂', z2)]):
        a, b = gx(ini), gx(fin) + cw
        o.append(llave(a, b, 130, MUTED))
        o.append(texto((a + b) / 2, 150, f'gen {nombre}: z = {z}', 13, INK2, 'middle'))
    # Flecha de decodificación
    o.append(flecha(310, 396, 92, INK2))
    o.append(texto(353, 78, 'decodificar', 13, INK, 'middle', 600))
    o.append(texto(353, 116, 'x = a + z · Δ', 13, INK2, 'middle'))
    # Fenotipo
    o.append(f'<rect x="410" y="62" width="170" height="64" rx="6" fill="#ffffff" stroke="{INK2}" stroke-width="1.5"/>')
    o.append(texto(495, 88, f'x₁ = {coma(x1)}', 16, INK, 'middle', 600))
    o.append(texto(495, 112, f'x₂ = {coma(x2)}', 16, INK, 'middle', 600))
    # Evaluación
    o.append(flecha(586, 654, 92, INK2))
    o.append(texto(620, 78, 'evaluar', 13, INK, 'middle', 600))
    o.append(f'<rect x="660" y="62" width="90" height="64" rx="6" fill="#ffffff" stroke="{INK2}" stroke-width="1.5"/>')
    o.append(texto(705, 100, f'f = {coma(fx)}', 14, INK, 'middle', 600))
    # Llaves con quién actúa dónde
    o.append(llave(36, 36 + 8 * (cw + gap) + 6 - gap, 226, NARANJA))
    o.append(texto(36, 252, 'Aquí actúan el cruce y la mutación', 14, INK))
    o.append(texto(36, 272, 'Operan sobre los bits, sin saber qué significan.', 13, INK2))
    o.append(llave(410, 750, 226, AZUL))
    o.append(texto(410, 252, 'Aquí actúa la función de aptitud', 14, INK))
    o.append(texto(410, 272, 'Evalúa la solución, sin ver los bits.', 13, INK2))
    o.append('</svg>')
    return '\n'.join(o) + '\n', dict(z=(z1, z2), x=(x1, x2), f=fx)


# ----------------------------------------------------------------------------------------------
# fig-rejilla: la rejilla de puntos representables
# ----------------------------------------------------------------------------------------------

def figura_rejilla(ks=(3, 4, 5)):
    W, H = 760, 372
    lado, top, izq, sep = 200, 62, 46, 38
    o = abre(W, H, '2', 'Puntos que puede representar una cadena binaria en la caja de Himmelblau',
             'Tres cuadrados con los puntos de la rejilla para k = 3, 4 y 5 bits por variable (64, 256 y 1024 '
             'puntos). Los cuatro mínimos globales de la función no caen sobre ningún punto de la rejilla. '
             'El mejor punto de cada rejilla se marca con un círculo azul y vale 1,50; 0,91 y 0,30.')
    datos = []
    X = lambda x, x0: x0 + (x - A) / (B - A) * lado
    Y = lambda y: top + lado - (y - A) / (B - A) * lado
    for p, k in enumerate(ks):
        x0 = izq + p * (lado + sep)
        n = 2 ** k
        v, bx, by = mejor_de_la_rejilla(k)
        delta = (B - A) / (n - 1)
        datos.append((k, n * n, delta, v, bx, by))
        o.append(texto(x0, 28, f'k = {k}: {n * n} puntos', 14, INK, peso=600))
        o.append(texto(x0, 46, f'Δ = {coma(delta)} · mejor f = {coma(v)}', 13, INK2))
        o.append(f'<rect x="{x0}" y="{top}" width="{lado}" height="{lado}" fill="#ffffff" stroke="{MUTED}" stroke-width="1"/>')
        r = 2.3 if k <= 4 else 1.6
        for z1 in range(n):
            for z2 in range(n):
                o.append(f'<circle cx="{X(escala(z1, k), x0):.1f}" cy="{Y(escala(z2, k)):.1f}" r="{r}" fill="{MUTED}"/>')
        for mx, my in MINIMOS:
            cx, cy = X(mx, x0), Y(my)
            o.append(f'<polygon points="{cx:.1f},{cy - 7:.1f} {cx + 7:.1f},{cy:.1f} {cx:.1f},{cy + 7:.1f} {cx - 7:.1f},{cy:.1f}" '
                     f'fill="{NARANJA}" stroke="#ffffff" stroke-width="2"/>')
        o.append(f'<circle cx="{X(bx, x0):.1f}" cy="{Y(by):.1f}" r="6" fill="none" stroke="#ffffff" stroke-width="5"/>')
        o.append(f'<circle cx="{X(bx, x0):.1f}" cy="{Y(by):.1f}" r="6" fill="none" stroke="{AZUL}" stroke-width="2.5"/>')
        for t in (-5, 0, 5):
            o.append(texto(X(t, x0), top + lado + 17, coma(t, 0), 12, INK2, 'middle'))
        if p == 0:
            for t in (-5, 0, 5):
                o.append(texto(x0 - 6, Y(t) + 4, coma(t, 0), 12, INK2, 'end'))
            o.append(texto(x0 + lado / 2, top + lado + 36, 'x₁', 13, INK2, 'middle'))
            o.append(texto(x0 - 34, top + lado / 2, 'x₂', 13, INK2, 'middle'))
    # Leyenda
    ly = H - 16
    o.append(f'<polygon points="{izq},{ly - 6} {izq + 6},{ly} {izq},{ly + 6} {izq - 6},{ly}" fill="{NARANJA}"/>')
    o.append(texto(izq + 14, ly + 4, 'Mínimos globales (f = 0)', 13, INK))
    o.append(f'<circle cx="{izq + 230}" cy="{ly}" r="6" fill="none" stroke="{AZUL}" stroke-width="2.5"/>')
    o.append(texto(izq + 244, ly + 4, 'Mejor punto de la rejilla', 13, INK))
    o.append(f'<circle cx="{izq + 440}" cy="{ly}" r="2.5" fill="{MUTED}"/>')
    o.append(texto(izq + 450, ly + 4, 'Puntos que se pueden escribir', 13, INK))
    o.append('</svg>')
    return '\n'.join(o) + '\n', datos


# ----------------------------------------------------------------------------------------------
# fig-saltos-hamming: saltos de Hamming entre enteros consecutivos
# ----------------------------------------------------------------------------------------------

def figura_saltos(k=4):
    estandar = [sum(p != q for p, q in zip(a_bits(z, k), a_bits(z + 1, k))) for z in range(2 ** k - 1)]
    grises = [sum(p != q for p, q in zip(gray(a_bits(z, k)), gray(a_bits(z + 1, k)))) for z in range(2 ** k - 1)]
    n = len(estandar)
    W, H = 760, 390
    x0, x1, y0, y1 = 64, 736, 316, 70
    X = lambda i: x0 + (x1 - x0) * i / n
    Y = lambda v: y0 - (y0 - y1) * v / k
    o = abre(W, H, '3', 'Bits que cambian al pasar de un entero al siguiente, en binario estándar y en código Gray',
             f'Gráfica de barras para los números de 0 a {2 ** k - 1} con {k} bits. En binario estándar, pasar de un '
             f'entero al siguiente cambia entre 1 y {k} bits; de 7 a 8 cambian los {k}. En código Gray, cambia '
             'siempre un solo bit.')
    for v in range(1, k + 1):
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(texto(x0 - 10, Y(v) + 4, str(v), 12, INK2, 'end'))
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{MUTED}" stroke-width="1"/>')
    paso = (x1 - x0) / n
    ancho = 13
    for i in range(n):
        cx = X(i) + paso / 2
        # Binaria estándar (naranja) a la izquierda; Gray (azul) a la derecha, con 2 px de hueco
        o.append(f'<rect x="{cx - ancho - 1:.1f}" y="{Y(estandar[i]):.1f}" width="{ancho}" height="{y0 - Y(estandar[i]):.1f}" rx="2" fill="{NARANJA}"/>')
        o.append(f'<rect x="{cx + 1:.1f}" y="{Y(grises[i]):.1f}" width="{ancho}" height="{y0 - Y(grises[i]):.1f}" rx="2" fill="{AZUL}"/>')
        o.append(texto(cx, y0 + 18, f'{i}→{i + 1}', 12, INK2, 'middle'))
    # Rótulo del salto de 7 a 8
    i = 7
    cx = X(i) + paso / 2
    o.append(texto(cx - ancho / 2 - 1, Y(estandar[i]) - 8, f'{estandar[i]} bits', 13, INK, 'middle', 600))
    o.append(texto((x0 + x1) / 2, y0 + 46, 'Paso de un entero al siguiente', 13, INK2, 'middle'))
    o.append(texto(18, (y0 + y1) / 2, 'Bits que cambian', 13, INK2, 'middle', extra=f' transform="rotate(-90 18 {(y0 + y1) / 2})"'))
    # Leyenda
    o.append(f'<rect x="{x0}" y="22" width="14" height="14" rx="2" fill="{NARANJA}"/>')
    o.append(texto(x0 + 22, 34, 'Binaria estándar', 13, INK))
    o.append(f'<rect x="{x0 + 170}" y="22" width="14" height="14" rx="2" fill="{AZUL}"/>')
    o.append(texto(x0 + 192, 34, 'Código Gray', 13, INK))
    o.append('</svg>')
    return '\n'.join(o) + '\n', (estandar, grises)


if __name__ == '__main__':
    svg1, d1 = figura_genotipo_fenotipo()
    with open('03-genotipo-fenotipo.svg', 'w', encoding='utf-8') as fh:
        fh.write(svg1)
    print('fig-genotipo-fenotipo: z =', d1['z'], '· x =', tuple(round(v, 4) for v in d1['x']), '· f =', round(d1['f'], 4))
    svg2, d2 = figura_rejilla()
    with open('03-rejilla.svg', 'w', encoding='utf-8') as fh:
        fh.write(svg2)
    print('fig-rejilla (k, puntos, Δ, mejor f, mejor punto):')
    for k, pts, delta, v, bx, by in d2:
        print(' ', k, pts, round(delta, 4), round(v, 4), (round(bx, 4), round(by, 4)))
    svg3, (est, gr) = figura_saltos()
    with open('03-saltos-hamming.svg', 'w', encoding='utf-8') as fh:
        fh.write(svg3)
    print('fig-saltos-hamming: bits que cambian de z a z + 1 (z = 0…14)')
    print('  estándar', est, 'suma', sum(est), 'media', round(sum(est) / len(est), 4))
    print('  Gray    ', gr, 'suma', sum(gr), 'media', round(sum(gr) / len(gr), 4))
