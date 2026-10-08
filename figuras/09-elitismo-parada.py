"""Figura 9.1 del libro «Algoritmos genéticos, paso a paso»: el elitismo a lo largo de una ejecución
y dónde pararía cada criterio de parada.

Algoritmo genético mínimo sobre OneMax (maximizar el número de unos de una cadena de 40 bits):
población de 20, torneo binario con reemplazo, cruce en un punto con Pc = 0,8, inversión de bits
con pm = 1/40 y reemplazo generacional, sin élite (e = 0) o con un individuo de élite (e = 1),
que ocupa el lugar del peor hijo, como en selection-ga. Las dos ejecuciones parten de la misma
población inicial (misma semilla), pero desde la primera generación consumen los números
aleatorios de forma distinta.

Uso: python3 09-elitismo-parada.py   → escribe 09-elitismo-parada.svg y muestra los datos y el
resumen de 30 semillas. Solo usa la biblioteca estándar de Python 3.
"""
import random
import statistics

L, N, G, PC = 40, 20, 100, 0.8
PM = 1 / L
SEMILLA = 3          # ejecución que se dibuja
REPLICAS = 30        # semillas 1–30 para el resumen


def ejecutar(semilla, elite):
    rng = random.Random(semilla)
    pob = [[rng.randint(0, 1) for _ in range(L)] for _ in range(N)]
    mejor = []
    for g in range(G + 1):
        apt = [sum(x) for x in pob]
        mejor.append(max(apt))
        if g == G:
            break

        def torneo():
            a, b = rng.randrange(N), rng.randrange(N)
            return pob[a] if apt[a] >= apt[b] else pob[b]

        hijos = []
        while len(hijos) < N:
            p1, p2 = torneo()[:], torneo()[:]
            if rng.random() < PC:
                c = rng.randint(1, L - 1)
                p1, p2 = p1[:c] + p2[c:], p2[:c] + p1[c:]
            for h in (p1, p2):
                hijos.append([1 - b if rng.random() < PM else b for b in h])
        hijos = hijos[:N]
        if elite:
            mejores = sorted(range(N), key=lambda i: apt[i], reverse=True)[:elite]
            apt_h = [sum(h) for h in hijos]
            peores = sorted(range(N), key=lambda i: apt_h[i])[:elite]
            for m, p in zip(mejores, peores):
                hijos[p] = pob[m][:]
        pob = hijos
    return mejor


def parada_sin_mejora(mejor, k):
    """Generación en la que se cumplen k generaciones sin mejorar la mejor solución encontrada."""
    record, ultima = mejor[0], 0
    for g in range(1, len(mejor)):
        if mejor[g] > record:
            record, ultima = mejor[g], g
        if g - ultima >= k:
            return g, record
    return None, record


def primera(mejor, valor):
    return next((g for g, v in enumerate(mejor) if v >= valor), None)


def svg(sin, con, marcas):
    W, H = 720, 420
    x0, x1, y0, y1 = 64, 600, 352, 72          # área de dibujo
    vmin, vmax = 26, 41
    X = lambda g: x0 + (x1 - x0) * g / G
    Y = lambda v: y0 - (y0 - y1) * (v - vmin) / (vmax - vmin)
    ink, ink2, muted, grid = '#0b0b0b', '#52514e', '#7a7974', '#e4e3df'
    azul, naranja = '#2a78d6', '#eb6834'
    f = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
         f'aria-labelledby="t d" {f}>',
         '<title id="t">Mejor aptitud de la población en cada generación, con y sin elitismo</title>',
         '<desc id="d">OneMax de 40 bits, población de 20. Con un individuo de élite, la mejor aptitud '
         'nunca baja y llega al óptimo, 40, en la generación 42. Sin élite, sube y baja y no llega '
         'al óptimo en 100 generaciones. Se marcan las generaciones 38 y 62, en las que pararían los '
         'criterios de 10 y de 20 generaciones sin mejora en la ejecución con élite.</desc>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    for v in range(28, 41, 4):
        o.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{grid}" stroke-width="1"/>')
        o.append(f'<text x="{x0 - 8}" y="{Y(v) + 4:.1f}" font-size="12" fill="{ink2}" text-anchor="end">{v}</text>')
    for g in range(0, G + 1, 20):
        o.append(f'<text x="{X(g):.1f}" y="{y0 + 20}" font-size="12" fill="{ink2}" text-anchor="middle">{g}</text>')
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{muted}" stroke-width="1"/>')
    o.append(f'<text x="{(x0 + x1) / 2}" y="{y0 + 44}" font-size="13" fill="{ink2}" text-anchor="middle">Generación</text>')
    o.append(f'<text x="18" y="{(y0 + y1) / 2}" font-size="13" fill="{ink2}" text-anchor="middle" '
             f'transform="rotate(-90 18 {(y0 + y1) / 2})">Mejor aptitud (número de unos)</text>')
    # óptimo
    o.append(f'<line x1="{x0}" y1="{Y(40):.1f}" x2="{x1}" y2="{Y(40):.1f}" stroke="{ink2}" stroke-width="1" stroke-dasharray="2 4"/>')
    o.append(f'<text x="{x0 + 4}" y="{Y(40) - 6:.1f}" font-size="12" fill="{ink2}">Óptimo: 40</text>')
    # marcas de parada (ejecución con élite): línea vertical, punto sobre la curva y rótulo arriba
    for k, (g, txt, ancla) in enumerate(marcas):
        ty = y1 - 34 + 16 * (k % 2)
        tx = X(g) - 4 if ancla == 'end' else X(g) + 4
        o.append(f'<line x1="{X(g):.1f}" y1="{ty + 4}" x2="{X(g):.1f}" y2="{y0}" stroke="{muted}" stroke-width="1" stroke-dasharray="4 3"/>')
        o.append(f'<text x="{tx:.1f}" y="{ty}" font-size="12" fill="{ink2}" text-anchor="{ancla}">{txt}</text>')
    def linea(serie, color, guiones=''):
        pts = ' '.join(f'{X(g):.1f},{Y(v):.1f}' for g, v in enumerate(serie))
        d = f' stroke-dasharray="{guiones}"' if guiones else ''
        return (f'<polyline points="{pts}" fill="none" stroke="#ffffff" stroke-width="5" stroke-linejoin="round"/>'
                f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"{d}/>')
    o.append(linea(sin, naranja, '6 3'))
    o.append(linea(con, azul))
    # etiquetas directas al final de cada línea
    o.append(f'<text x="{x1 + 8}" y="{Y(con[-1]) + 4:.1f}" font-size="12" fill="{ink}">Con élite (e = 1)</text>')
    o.append(f'<text x="{x1 + 8}" y="{Y(sin[-1]) + 4:.1f}" font-size="12" fill="{ink}">Sin élite (e = 0)</text>')
    o.append(f'<line x1="{x1 + 2}" y1="{Y(con[-1]):.1f}" x2="{x1 + 6}" y2="{Y(con[-1]):.1f}" stroke="{azul}" stroke-width="2"/>')
    o.append(f'<line x1="{x1 + 2}" y1="{Y(sin[-1]):.1f}" x2="{x1 + 6}" y2="{Y(sin[-1]):.1f}" stroke="{naranja}" stroke-width="2"/>')
    for g, _, _ in marcas:
        o.append(f'<circle cx="{X(g):.1f}" cy="{Y(con[g]):.1f}" r="4.5" fill="{azul}" stroke="#ffffff" stroke-width="2"/>')
    o.append('</svg>')
    return '\n'.join(o) + '\n'


if __name__ == '__main__':
    sin, con = ejecutar(SEMILLA, 0), ejecutar(SEMILLA, 1)
    g10, r10 = parada_sin_mejora(con, 10)
    g20, r20 = parada_sin_mejora(con, 20)
    gopt = primera(con, L)
    marcas = [(g10, f'10 sin mejora (gen. {g10})', 'end'), (gopt, f'óptimo alcanzado (gen. {gopt})', 'start'),
              (g20, f'20 sin mejora (gen. {g20})', 'start')]
    with open('09-elitismo-parada.svg', 'w', encoding='utf-8') as fh:
        fh.write(svg(sin, con, marcas))
    print('Semilla', SEMILLA)
    print('con élite: óptimo en la generación', gopt, '| 10 sin mejora →', (g10, r10), '| 20 sin mejora →', (g20, r20))
    print('sin élite: máximo', max(sin), 'en la generación', primera(sin, max(sin)), '| final', sin[-1],
          '| 10 sin mejora →', parada_sin_mejora(sin, 10), '| 20 sin mejora →', parada_sin_mejora(sin, 20))
    print('bajadas de la mejor aptitud sin élite:', sum(1 for g in range(1, G + 1) if sin[g] < sin[g - 1]))
    print('Generación | sin élite | con élite')
    for g in list(range(0, 61, 5)) + [g10, gopt, g20, 80, 100]:
        print(g, sin[g], con[g])
    for e in (0, 1):
        llegadas = [primera(ejecutar(s, e), L) for s in range(1, REPLICAS + 1)]
        ok = [x for x in llegadas if x is not None]
        print(f'e = {e}: llegan al óptimo {len(ok)} de {REPLICAS}; generación mediana {statistics.median(ok)}, '
              f'mínima {min(ok)}, máxima {max(ok)}')
