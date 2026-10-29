"""Figura fig-que-metodo del capítulo 11 del libro «Evolución a la vista»: ¿qué método uso?

Esquema propio, una orientación y no una regla. Las tres primeras preguntas son las de Mitchell (1998,
apartado 5.1): si el espacio es pequeño, se revisa entero; si es suave o tiene una sola cima, un método
que sube por la pendiente es más eficiente; si el problema se conoce bien, las heurísticas específicas
suelen dar mejores resultados. García-Martínez et al. (2025, p. 652) dan la misma idea: los algoritmos
genéticos convienen en espacios grandes, complejos y poco conocidos. La cuarta pregunta separa las
metaheurísticas de población de las de trayectoria: el rasgo propio del algoritmo genético es combinar
dos soluciones con el cruce, frente a explorar el vecindario de una sola (García-Martínez et al., 2025,
p. 629), y las de población tienden a explorar y las de trayectoria a explotar (Talbi, 2009, p. 25). El
pie de la figura remite al horizonte de la decisión (Talbi, 2009, pp. 33–34; sección 9.6 del libro).

Uso: python3 11-que-metodo.py   → escribe 11-que-metodo.svg. Solo usa la biblioteca estándar de Python 3.
"""
from pathlib import Path

W, H = 720, 590
INK, INK2, MUTED = '#0b0b0b', '#52514e', '#7a7974'
AZUL, NARANJA = '#2a78d6', '#eb6834'
AZUL_CLARO, GRIS_CLARO = '#dbe8f9', '#f1f0ec'
FUENTE = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""

TITULO = '¿Qué método uso? Una orientación en cuatro preguntas'
DESCRIPCION = (
    'Cuatro preguntas en cascada. Primera: ¿el espacio es pequeño? Si es así, se revisan todas las soluciones. '
    'Si no, segunda: ¿es suave y con una sola cima? Si es así, un método que sube por la pendiente. Si no, '
    'tercera: ¿hay heurísticas específicas, como en el viajante? Si es así, se usan, solas o dentro de una '
    'metaheurística. Si no, hace falta una metaheurística, y la cuarta pregunta elige cuál: ¿conviene combinar '
    'partes de buenas soluciones o buscar con muchas a la vez, por ejemplo con varias cimas o varios objetivos? '
    'Si es así, una de población, como el algoritmo genético; si no, una de trayectoria, como la búsqueda local, '
    'el recocido simulado o la búsqueda tabú. Las dos se pueden combinar en un algoritmo memético. Al final, '
    'en todos los casos, hay que fijar el presupuesto de evaluaciones según el horizonte de la decisión, '
    'estratégico, táctico u operativo, y ajustar con casos parecidos al real.')


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def caja(x, y, w, h, nombre, pista, relleno, borde, grueso=1.5, peso='600'):
    cx = x + w / 2
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="{relleno}" stroke="{borde}" '
         f'stroke-width="{grueso}"/>')
    if pista:
        s += (f'<text x="{cx}" y="{y + h / 2 - 4}" text-anchor="middle" font-size="15" font-weight="{peso}" '
              f'fill="{INK}">{esc(nombre)}</text>'
              f'<text x="{cx}" y="{y + h / 2 + 15}" text-anchor="middle" font-size="12.5" fill="{INK2}">'
              f'{esc(pista)}</text>')
    else:
        s += (f'<text x="{cx}" y="{y + h / 2 + 5}" text-anchor="middle" font-size="15" font-weight="{peso}" '
              f'fill="{INK}">{esc(nombre)}</text>')
    return s


def flecha(x1, y1, x2, y2, color=INK2, discontinua=False):
    d = ' stroke-dasharray="5 4"' if discontinua else ''
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.6"{d} '
            f'marker-end="url(#punta)"/>')


def rotulo(x, y, texto, ancla='start', color=INK2, tam=12.5, estilo='normal', peso='normal'):
    return (f'<text x="{x}" y="{y}" text-anchor="{ancla}" font-size="{tam}" font-style="{estilo}" '
            f'font-weight="{peso}" fill="{color}">{esc(texto)}</text>')


# Preguntas (izquierda) y respuestas cuando la respuesta es «sí» (derecha)
PREGUNTAS = [
    ('¿El espacio es pequeño?', 'se pueden revisar todas las soluciones',
     'Revisarlas todas', 'y quedarse con la mejor'),
    ('¿Es suave y con una sola cima?', 'el paisaje no tiene óptimos locales',
     'Subir por la pendiente', 'es mucho más eficiente'),
    ('¿Hay heurísticas específicas?', 'un problema muy estudiado, como el viajante',
     'Usarlas', 'solas o dentro de una metaheurística'),
]
QX, QW, QH = 20, 380, 62
RX, RW = 450, 250
Y0, PASO = 16, 92


def figura():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
         f'aria-labelledby="t1 d1" {FUENTE}>',
         f'<title id="t1">{esc(TITULO)}</title><desc id="d1">{esc(DESCRIPCION)}</desc>',
         '<defs><marker id="punta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK2}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    for i, (preg, pista, resp, rpista) in enumerate(PREGUNTAS):
        y = Y0 + i * PASO
        s.append(caja(QX, y, QW, QH, preg, pista, '#ffffff', NARANJA, grueso=1.8))
        s.append(flecha(QX + QW, y + QH / 2, RX - 2, y + QH / 2))
        s.append(rotulo((QX + QW + RX) / 2, y + QH / 2 - 7, 'sí', ancla='middle'))
        s.append(caja(RX, y, RW, QH, resp, rpista, GRIS_CLARO, INK2))
        s.append(flecha(QX + QW / 2, y + QH, QX + QW / 2, y + PASO - 2))
        s.append(rotulo(QX + QW / 2 + 10, y + QH + 19, 'no'))

    # Una metaheurística: ¿cuál?
    y4 = Y0 + 3 * PASO
    s.append(f'<rect x="10" y="{y4 - 6}" width="{W - 20}" height="232" rx="12" fill="none" '
             f'stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="6 5"/>')
    s.append(rotulo(W - 22, y4 + 14, 'Hace falta una metaheurística. ¿Cuál?', ancla='end',
                    color=INK2, tam=13, peso='600'))
    s.append(caja(QX, y4 + 24, QW, QH + 4, '¿Conviene combinar buenas soluciones?',
                  'o buscar con muchas a la vez: varias cimas u objetivos', '#ffffff', NARANJA, grueso=1.8))
    yq = y4 + 24 + QH + 4
    yh = yq + 56
    # «no» a la izquierda, «sí» a la derecha
    s.append(flecha(QX + 110, yq, 120, yh - 2))
    s.append(rotulo(QX + 92, yq + 26, 'no', ancla='end'))
    s.append(flecha(QX + QW - 60, yq, 520, yh - 2))
    s.append(rotulo(QX + QW - 18, yq + 26, 'sí'))
    s.append(caja(20, yh, 250, QH, 'De trayectoria', 'búsqueda local, recocido, tabú', GRIS_CLARO, INK2))
    s.append(caja(390, yh, 300, QH, 'De población', 'el algoritmo genético y otras', AZUL_CLARO, AZUL))
    s.append(f'<line x1="272" y1="{yh + QH / 2}" x2="388" y2="{yh + QH / 2}" stroke="{INK2}" '
             'stroke-width="1.4" stroke-dasharray="5 4" marker-start="url(#punta)" marker-end="url(#punta)"/>')
    s.append(rotulo(330, yh + QH / 2 - 8, 'combinarlas:', ancla='middle', tam=12, estilo='italic', color=MUTED))
    s.append(rotulo(330, yh + QH / 2 + 18, 'memético', ancla='middle', tam=12, estilo='italic', color=MUTED))

    # Después, en todos los casos
    yb = y4 + 238
    s.append(f'<rect x="10" y="{yb}" width="{W - 20}" height="52" rx="9" fill="{GRIS_CLARO}" stroke="none"/>')
    s.append(rotulo(W / 2, yb + 21, 'En todos los casos: fija el presupuesto de evaluaciones según el horizonte',
                    ancla='middle', color=INK, tam=13))
    s.append(rotulo(W / 2, yb + 40, '(estratégico, táctico u operativo) y ajusta con casos parecidos al real',
                    ancla='middle', color=INK, tam=13))
    s.append('</svg>')
    assert yb + 52 <= H, yb
    return ''.join(s)


if __name__ == '__main__':
    destino = Path(__file__).with_name('11-que-metodo.svg')
    destino.write_text(figura() + '\n', encoding='utf-8')
    print('Escrito', destino.name)
