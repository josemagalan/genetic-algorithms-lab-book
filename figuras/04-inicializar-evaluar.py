"""Figuras 4.1 y 4.2 del libro «Algoritmos genéticos, paso a paso»: la aptitud penalizada de una población
de la mochila en función del peso λ y la cobertura de la caja con tres poblaciones de 8 individuos.

Figura 4.1. Mochila de 6 objetos (pesos 4 3 5 8 4 2, valores 5 4 9 4 7 4, capacidad 13) y la población
uniforme de 8 individuos del ejemplo 4.3 (initialization-and-evaluation-ga, s = 21, ps = 5). Penalización
lineal: F = valor − λ · e, con e = máx(0, peso − 13). Todo se calcula aquí a partir de los cromosomas.

Figura 4.2. Caja [−5, 5]² dividida en 8 franjas por eje y tres poblaciones de N = 8:
  - Uniforme e hipercubo latino: los puntos que da initialization-and-evaluation-ga (commit 49c1e2e) con
    la semilla de población 1, copiados de la herramienta (su generador de números aleatorios no se
    reproduce aquí).
  - Halton: se calcula aquí, u = (φ₂(i), φ₃(i)) para i = 1, …, 8 y x = −5 + 10 u redondeado a centésimas.

Uso: python3 04-inicializar-evaluar.py   → escribe 04-penalizacion.svg y 04-cobertura.svg, y muestra
los datos. Solo usa la biblioteca estándar de Python 3.
"""

from decimal import Decimal

INK, INK2, MUTED, GRID = '#0b0b0b', '#52514e', '#7a7974', '#e4e3df'
AZUL, NARANJA = '#2a78d6', '#eb6834'
NARANJA_CLARO = '#fbe3d8'
FUENTE = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""

PESOS = [4, 3, 5, 8, 4, 2]
VALORES = [5, 4, 9, 4, 7, 4]
W_CAP = 13
POBLACION = ['011011', '111101', '100000', '010010', '001011', '100100', '111110', '110110']

UNIFORME = [(-4.13, -2.23), (-0.46, -2.74), (4.80, 1.37), (4.68, -4.79),
            (-3.00, -0.89), (-4.74, -1.39), (3.83, 3.14), (-4.18, -0.98)]
HIPERCUBO = [(3.85, 0.50), (1.40, -1.17), (1.16, 1.67), (-1.07, 2.97),
             (3.09, 4.15), (-1.70, -1.29), (-3.57, -3.48), (-4.11, -4.74)]


def coma(v, d=2):
    """Número con coma decimal y el signo menos tipográfico."""
    return f'{v:.{d}f}'.replace('.', ',').replace('-', '−')


def abre(W, H, ident, titulo, desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
            f'aria-labelledby="t{ident} d{ident}" {FUENTE}>',
            f'<title id="t{ident}">{titulo}</title>',
            f'<desc id="d{ident}">{desc}</desc>',
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>']


def texto(x, y, s, size=13, color=INK2, ancla='start', peso=None):
    p = f' font-weight="{peso}"' if peso else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{ancla}"{p}>{s}</text>'


# ----------------------------------------------------------------------------------------------
# Figura 4.1: aptitud penalizada en función de λ
# ----------------------------------------------------------------------------------------------

def evaluar(c):
    x = [int(b) for b in c]
    peso = sum(w * b for w, b in zip(PESOS, x))
    valor = sum(v * b for v, b in zip(VALORES, x))
    return peso, valor, max(0, peso - W_CAP)


def figura_penalizacion():
    ind = [(f'I{i + 1}',) + evaluar(c) for i, c in enumerate(POBLACION)]
    B = max(v for _, p, v, e in ind if e == 0)
    lam_star = max((v - B) / e for _, p, v, e in ind if e > 0)
    W, H = 760, 400
    izq, der, top, base = 64, 640, 30, 340
    lmax, ymin, ymax = 5.0, -30.0, 30.0
    X = lambda l: izq + l / lmax * (der - izq)
    Y = lambda y: base - (y - ymin) / (ymax - ymin) * (base - top)
    o = abre(W, H, '51', 'Aptitud de cada individuo según el peso de la penalización',
             f'Rectas de aptitud F = valor − λ · e de los 8 individuos para λ entre 0 y 5. Los cuatro que caben '
             f'son horizontales; los cuatro que no caben bajan con pendiente igual a su exceso de peso. Por debajo '
             f'de λ* = {coma(lam_star, 0)}, el mejor es I1, que no cabe; por encima, I5, que cabe y vale {B}.')
    o.append(f'<defs><clipPath id="c51"><rect x="{izq}" y="{top}" width="{der - izq}" height="{base - top}"/></clipPath></defs>')
    for y in range(-30, 31, 10):
        o.append(f'<line x1="{izq}" y1="{Y(y):.1f}" x2="{der}" y2="{Y(y):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(texto(izq - 8, Y(y) + 4, coma(y, 0), 12, INK2, 'end'))
    o.append(f'<line x1="{izq}" y1="{Y(0):.1f}" x2="{der}" y2="{Y(0):.1f}" stroke="{MUTED}" stroke-width="1.2"/>')
    for l in range(0, 6):
        o.append(texto(X(l), base + 18, coma(l, 0), 12, INK2, 'middle'))
    o.append(texto((izq + der) / 2, base + 40, 'Peso λ', 13, INK2, 'middle'))
    o.append(texto(18, (top + base) / 2, 'Aptitud F', 13, INK2, 'middle').replace('<text ', f'<text transform="rotate(-90 18 {(top + base) / 2:.1f})" ', 1))
    # λ*
    o.append(f'<line x1="{X(lam_star):.1f}" y1="{top}" x2="{X(lam_star):.1f}" y2="{base}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    o.append(texto(X(lam_star) + 6, top + 14, f'λ* = {coma(lam_star, 0)}', 13, INK, peso=600))
    etiquetas = []
    for nombre, p, v, e in ind:
        destacado = nombre in ('I1', 'I5')
        color = AZUL if e == 0 else NARANJA
        ancho = 3.2 if destacado else 1.8
        y0, y1 = v, v - e * lmax
        o.append(f'<line x1="{X(0):.1f}" y1="{Y(y0):.1f}" x2="{X(lmax):.1f}" y2="{Y(y1):.1f}" stroke="{color}" '
                 f'stroke-width="{ancho}" clip-path="url(#c51)"/>')
        if e == 0:
            etiquetas.append((Y(v), f'{nombre} (cabe)', color, destacado))
        elif y1 >= ymin:
            etiquetas.append((Y(y1), f'{nombre} (exceso {e})', color, destacado))
        else:
            lc = (v - ymin) / e          # donde la recta sale por abajo
            o.append(texto(X(lc) + 4, base - 6, nombre, 12, color, 'start', 600 if destacado else None))
    etiquetas.sort()
    ultimo = -1e9
    for y, s, color, destacado in etiquetas:
        y = max(y, ultimo + 15)
        o.append(texto(der + 8, y + 4, s, 12, color, 'start', 600 if destacado else None))
        ultimo = y
    o.append('</svg>')
    datos = [(n, p, v, e, [v - e * l for l in (0, 1, 4, 5)]) for n, p, v, e in ind]
    return '\n'.join(o) + '\n', dict(B=B, lam_star=lam_star, datos=datos)


# ----------------------------------------------------------------------------------------------
# Figura 4.2: cobertura de la caja
# ----------------------------------------------------------------------------------------------

def inverso_radical(i, b):
    num, den = 0, 1
    while i > 0:
        i, d = divmod(i, b)
        num, den = num * b + d, den * b
    return num / den


def redondea(v):
    """Centésimas, como la herramienta (Math.round: medio hacia arriba)."""
    return float(Decimal(str(v)).quantize(Decimal('0.01'), rounding='ROUND_HALF_UP' if v >= 0 else 'ROUND_HALF_DOWN'))


def halton(n):
    return [(redondea(-5 + 10 * inverso_radical(i, 2)), redondea(-5 + 10 * inverso_radical(i, 3))) for i in range(1, n + 1)]


def franjas(puntos, n=8):
    col = {min(n - 1, int((x + 5) / 10 * n + 1e-9)) for x, _ in puntos}
    fil = {min(n - 1, int((y + 5) / 10 * n + 1e-9)) for _, y in puntos}
    return col, fil


def figura_cobertura():
    poblaciones = [('(a) Uniforme', UNIFORME), ('(b) Halton', halton(8)), ('(c) Hipercubo latino', HIPERCUBO)]
    W, H = 760, 330
    lado, top, izq, sep, n = 200, 52, 46, 38, 8
    o = abre(W, H, '52', 'Tres poblaciones de ocho individuos en la caja',
             'Tres cuadrados con la caja dividida en 8 franjas por eje. La población uniforme deja vacías 4 franjas '
             'verticales y 2 horizontales, sombreadas. Halton y el hipercubo latino tienen un individuo en cada '
             'franja de cada eje.')
    X = lambda x, x0: x0 + (x + 5) / 10 * lado
    Y = lambda y: top + lado - (y + 5) / 10 * lado
    datos = []
    for p, (nombre, pts) in enumerate(poblaciones):
        x0 = izq + p * (lado + sep)
        col, fil = franjas(pts, n)
        datos.append((nombre, pts, len(col), len(fil)))
        o.append(texto(x0, 22, nombre, 14, INK, peso=600))
        o.append(texto(x0, 40, f'Franjas ocupadas: {len(col)} en x₁ y {len(fil)} en x₂', 13, INK2))
        w = lado / n
        for k in range(n):
            if k not in col:
                o.append(f'<rect x="{x0 + k * w:.1f}" y="{top}" width="{w:.1f}" height="{lado}" fill="{NARANJA_CLARO}"/>')
            if k not in fil:
                o.append(f'<rect x="{x0}" y="{top + (n - 1 - k) * w:.1f}" width="{lado}" height="{w:.1f}" fill="{NARANJA_CLARO}" fill-opacity="0.8"/>')
        for k in range(1, n):
            o.append(f'<line x1="{x0 + k * w:.1f}" y1="{top}" x2="{x0 + k * w:.1f}" y2="{top + lado}" stroke="{GRID}" stroke-width="1"/>')
            o.append(f'<line x1="{x0}" y1="{top + k * w:.1f}" x2="{x0 + lado}" y2="{top + k * w:.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<rect x="{x0}" y="{top}" width="{lado}" height="{lado}" fill="none" stroke="{MUTED}" stroke-width="1"/>')
        for x, y in pts:
            o.append(f'<circle cx="{X(x, x0):.1f}" cy="{Y(y):.1f}" r="5" fill="{AZUL}" stroke="#ffffff" stroke-width="1.5"/>')
        for t in (-5, 0, 5):
            o.append(texto(X(t, x0), top + lado + 17, coma(t, 0), 12, INK2, 'middle'))
        if p == 0:
            for t in (-5, 0, 5):
                o.append(texto(x0 - 6, Y(t) + 4, coma(t, 0), 12, INK2, 'end'))
            o.append(texto(x0 + lado / 2, top + lado + 36, 'x₁', 13, INK2, 'middle'))
            o.append(texto(x0 - 34, top + lado / 2, 'x₂', 13, INK2, 'middle'))
    ly = H - 14
    o.append(f'<circle cx="{izq + 6}" cy="{ly - 4}" r="5" fill="{AZUL}"/>')
    o.append(texto(izq + 18, ly, 'Individuo', 13, INK))
    o.append(f'<rect x="{izq + 120}" y="{ly - 12}" width="16" height="14" fill="{NARANJA_CLARO}" stroke="{MUTED}" stroke-width="0.5"/>')
    o.append(texto(izq + 144, ly, 'Franja sin ningún individuo', 13, INK))
    o.append('</svg>')
    return '\n'.join(o) + '\n', datos


if __name__ == '__main__':
    import os
    aqui = os.path.dirname(os.path.abspath(__file__))
    svg, d = figura_penalizacion()
    with open(os.path.join(aqui, '04-penalizacion.svg'), 'w', encoding='utf-8') as fh:
        fh.write(svg)
    print(f"Figura 4.1: mejor factible B = {d['B']}, λ* = {d['lam_star']}")
    for n, p, v, e, f in d['datos']:
        print(f'  {n}: peso {p}, valor {v}, exceso {e}, F(λ = 0, 1, 4, 5) = {f}')
    svg, d = figura_cobertura()
    with open(os.path.join(aqui, '04-cobertura.svg'), 'w', encoding='utf-8') as fh:
        fh.write(svg)
    for nombre, pts, c, f in d:
        print(f'Figura 4.2 {nombre}: franjas {c} y {f}; puntos {pts}')
