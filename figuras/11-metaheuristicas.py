"""Figura fig-metaheuristicas del capítulo 11 del libro «Evolución a la vista»: un mapa de metaheurísticas.

Esquema propio a partir de la idea de Talbi (2009, figura 1.9, p. 24, y p. 25): en el diseño de una
metaheurística, la búsqueda al azar es el extremo de la exploración (diversificación) y la búsqueda local
que pasa al mejor vecino, el de la explotación (intensificación); en general, las metaheurísticas de
población tienden a explorar y las de una sola solución (de trayectoria), a explotar. La figura de Talbi
no se reproduce (D016): se rehace con los métodos que nombra el capítulo. La posición indica la tendencia
de cada familia, no ordena los métodos de dentro de cada caja.
Métodos: los de la sección «Otras metaheurísticas» del capítulo 11, que cita sus fuentes originales
(de población: Hansen y Ostermeier, 2001; Koza, 1992; Storn y Price, 1997; Mühlenbein y Paaß, 1996;
Dorigo et al., 1996; Kennedy y Eberhart, 1995; de trayectoria: Kirkpatrick et al., 1983; Glover, 1986;
Lourenço et al., 2003; Mladenović y Hansen, 1997; Feo y Resende, 1995; la clasificación, Blum y Roli, 2003).

Uso: python3 11-metaheuristicas.py   → escribe 11-metaheuristicas.svg. Solo usa la biblioteca estándar.
"""
from pathlib import Path

W, H = 720, 400
INK, INK2, MUTED = '#0b0b0b', '#52514e', '#7a7974'
AZUL, NARANJA = '#2a78d6', '#eb6834'
AZUL_CLARO, GRIS_CLARO = '#dbe8f9', '#f1f0ec'
FUENTE = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""

POBLACION = [
    ('Evolutivas', None),
    ('Algoritmos genéticos', 'destacado'),
    ('Estrategias evolutivas', ''),
    ('Programación genética', ''),
    ('Evolución diferencial', ''),
    ('Estimación de distribuciones', ''),
    ('De enjambre', None),
    ('Colonias de hormigas', ''),
    ('Enjambres de partículas', ''),
]
TRAYECTORIA = [
    ('Recocido simulado', ''),
    ('Búsqueda tabú', ''),
    ('Búsqueda local iterada', ''),
    ('Vecindario variable (VNS)', ''),
    ('GRASP', ''),
]

TITULO = 'Un mapa de metaheurísticas, entre explorar y explotar'
DESCRIPCION = (
    'Una flecha horizontal va de explorar, o diversificar, a la izquierda, a explotar, o intensificar, a la '
    'derecha. En el extremo izquierdo está la búsqueda al azar y en el derecho, la búsqueda local que pasa al '
    'mejor vecino. Entre ellas, dos cajas. La de la izquierda, metaheurísticas de población, tiende a explorar: '
    'evolutivas (algoritmos genéticos, destacados, estrategias evolutivas, programación genética, evolución '
    'diferencial y estimación de distribuciones) y de enjambre (colonias de hormigas y enjambres de '
    'partículas). La de la derecha, metaheurísticas de trayectoria, tiende a explotar: recocido simulado, '
    'búsqueda tabú, búsqueda local iterada, búsqueda de vecindario variable y GRASP. Una llave bajo las dos '
    'cajas indica que los métodos híbridos, como los algoritmos meméticos, combinan unas y otras.')


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def texto(x, y, t, ancla='middle', tam=13, color=INK, peso='normal', estilo='normal'):
    return (f'<text x="{x}" y="{y}" text-anchor="{ancla}" font-size="{tam}" font-weight="{peso}" '
            f'font-style="{estilo}" fill="{color}">{esc(t)}</text>')


def grupo(x, y, w, titulo, subtitulo, elementos, relleno, borde):
    alto = 58 + 21 * len(elementos) + 6
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{alto}" rx="10" fill="{relleno}" stroke="{borde}" '
         f'stroke-width="1.5"/>',
         texto(x + w / 2, y + 24, titulo, tam=15, peso='600'),
         texto(x + w / 2, y + 42, subtitulo, tam=12, color=INK2, estilo='italic')]
    yy = y + 66
    for nombre, tipo in elementos:
        if tipo is None:
            s.append(texto(x + 16, yy, nombre, ancla='start', tam=12, color=INK2, peso='600'))
        elif tipo == 'destacado':
            s.append(f'<rect x="{x + 22}" y="{yy - 14}" width="{w - 44}" height="20" rx="4" fill="{AZUL}"/>')
            s.append(texto(x + 30, yy + 1, nombre, ancla='start', tam=13, color='#ffffff', peso='600'))
        else:
            s.append(texto(x + 30, yy, nombre, ancla='start', tam=13))
        yy += 21
    return ''.join(s), alto


def figura():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
         f'aria-labelledby="t1 d1" {FUENTE}>',
         f'<title id="t1">{esc(TITULO)}</title><desc id="d1">{esc(DESCRIPCION)}</desc>',
         '<defs><marker id="punta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK2}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    y0 = 14
    pob, alto_p = grupo(120, y0, 250, 'De población', 'tienden a explorar', POBLACION, AZUL_CLARO, AZUL)
    tra, alto_t = grupo(386, y0, 214, 'De trayectoria', 'tienden a explotar', TRAYECTORIA, GRIS_CLARO, INK2)
    s += [pob, tra]
    # Los dos extremos
    for x, nombre1, nombre2 in [(10, 'Búsqueda', 'al azar'), (610, 'Búsqueda local', 'al mejor vecino')]:
        s.append(f'<rect x="{x}" y="{y0 + 70}" width="100" height="60" rx="10" fill="#ffffff" '
                 f'stroke="{MUTED}" stroke-width="1.3" stroke-dasharray="4 3"/>')
        s.append(texto(x + 50, y0 + 96, nombre1, tam=12.5, peso='600'))
        s.append(texto(x + 50, y0 + 114, nombre2, tam=12, color=INK2))
    # Híbridos: llave bajo las dos cajas
    yl = y0 + max(alto_p, alto_t) + 12
    s.append(f'<path d="M122,{yl} q0,12 12,12 L{360 - 12},{yl + 12} q12,0 12,12 q0,-12 12,-12 '
             f'L{598 - 12},{yl + 12} q12,0 12,-12" fill="none" stroke="{NARANJA}" stroke-width="1.6"/>')
    s.append(texto(360, yl + 44, 'Híbridos: combinan las dos, como los algoritmos meméticos', tam=13,
                   color=INK))
    # Eje
    ye = yl + 76
    s.append(f'<line x1="22" y1="{ye}" x2="{W - 22}" y2="{ye}" stroke="{INK2}" stroke-width="1.8" '
             'marker-start="url(#punta)" marker-end="url(#punta)"/>')
    s.append(texto(22, ye + 22, 'Explorar (diversificar)', ancla='start', tam=13, peso='600'))
    s.append(texto(W - 22, ye + 22, 'Explotar (intensificar)', ancla='end', tam=13, peso='600'))
    s.append('</svg>')
    assert ye + 30 <= H, ye
    return ''.join(s)


if __name__ == '__main__':
    destino = Path(__file__).with_name('11-metaheuristicas.svg')
    destino.write_text(figura() + '\n', encoding='utf-8')
    print('Escrito', destino.name)
