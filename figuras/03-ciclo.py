"""Figura 3.1 del libro «Algoritmos genéticos, paso a paso»: el ciclo de un algoritmo genético.

Esquema propio. Sigue el orden del portal genetic-algorithms-lab («Así encajan en el algoritmo»):
antes del ciclo, representar el problema y crear la población inicial; en cada generación,
evaluar, seleccionar, cruzar, mutar y reemplazar, hasta cumplir el criterio de parada. Como en el
pseudocódigo del capítulo, la población inicial se evalúa una vez antes de entrar en el ciclo, cada
hijo se evalúa al crearse (antes de reemplazar) y el criterio de parada se comprueba al empezar
cada generación.

Uso: python3 03-ciclo.py   → escribe 03-ciclo.svg. Solo usa la biblioteca estándar de Python 3.
"""
from pathlib import Path

W, H = 780, 360
INK, INK2, MUTED = '#0b0b0b', '#52514e', '#7a7974'
AZUL, NARANJA = '#2a78d6', '#eb6834'
AZUL_CLARO, GRIS_CLARO = '#dbe8f9', '#f1f0ec'
FUENTE = "font-family=\"system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif\""

TITULO = 'El ciclo de un algoritmo genético'
DESCRIPCION = (
    'A la izquierda, lo que se hace una sola vez: representar el problema, crear la población inicial '
    'y evaluarla. Una flecha lleva a la pregunta ¿Parar? Si la respuesta es no, empieza una generación: '
    'seleccionar los padres, cruzarlos, mutar a los hijos, evaluar a los hijos y reemplazar, que forma la '
    'población siguiente y vuelve a la pregunta. Si la respuesta es sí, el algoritmo devuelve la mejor '
    'solución encontrada.')


def caja(x, y, w, h, nombre, pista, relleno, borde):
    cx = x + w / 2
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{relleno}" stroke="{borde}" '
            f'stroke-width="1.5"/>'
            f'<text x="{cx}" y="{y + h / 2 - 3}" text-anchor="middle" font-size="15" font-weight="600" '
            f'fill="{INK}">{nombre}</text>'
            f'<text x="{cx}" y="{y + h / 2 + 15}" text-anchor="middle" font-size="12" fill="{INK2}">{pista}</text>')


def flecha(x1, y1, x2, y2, color=INK2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.6" '
            f'marker-end="url(#punta)"/>')


def rotulo(x, y, texto, ancla='middle', color=MUTED, estilo='italic'):
    return (f'<text x="{x}" y="{y}" text-anchor="{ancla}" font-size="12" font-style="{estilo}" '
            f'fill="{color}">{texto}</text>')


def figura():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
         f'aria-labelledby="t1 d1" {FUENTE}>',
         f'<title id="t1">{TITULO}</title><desc id="d1">{DESCRIPCION}</desc>',
         '<defs><marker id="punta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK2}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>']

    # Antes del ciclo: una sola vez
    s.append(f'<text x="110" y="36" text-anchor="middle" font-size="13" font-weight="600" fill="{INK2}">'
             'Antes del ciclo · una vez</text>')
    s.append(caja(20, 54, 180, 48, 'Representar', 'define los cromosomas', GRIS_CLARO, INK2))
    s.append(flecha(110, 102, 110, 132))
    s.append(caja(20, 134, 180, 48, 'Crear P(0)', 'la población inicial', GRIS_CLARO, INK2))
    s.append(flecha(110, 182, 110, 212))
    s.append(caja(20, 214, 180, 48, 'Evaluar P(0)', 'mide su aptitud', GRIS_CLARO, INK2))

    # Una generación
    s.append(f'<rect x="250" y="48" width="520" height="236" rx="12" fill="none" stroke="{MUTED}" '
             'stroke-width="1.2" stroke-dasharray="6 5"/>')
    s.append(f'<text x="510" y="36" text-anchor="middle" font-size="13" font-weight="600" fill="{INK2}">'
             'En cada generación</text>')
    s.append(caja(260, 70, 150, 56, 'Seleccionar', 'elige los padres', AZUL_CLARO, AZUL))
    s.append(caja(435, 70, 150, 56, 'Cruzar', 'combina los genes', AZUL_CLARO, AZUL))
    s.append(caja(610, 70, 150, 56, 'Mutar', 'introduce cambios', AZUL_CLARO, AZUL))
    s.append(caja(610, 210, 150, 56, 'Evaluar', 'aptitud de los hijos', AZUL_CLARO, AZUL))
    s.append(caja(435, 210, 150, 56, 'Reemplazar', 'forma P(t + 1)', AZUL_CLARO, AZUL))
    s.append(flecha(410, 98, 433, 98))
    s.append(rotulo(422, 62, 'padres'))
    s.append(flecha(585, 98, 608, 98))
    s.append(rotulo(597, 62, 'hijos'))
    s.append(flecha(685, 126, 685, 208))
    s.append(rotulo(695, 172, 'hijos', ancla='start'))
    s.append(rotulo(695, 186, 'mutados', ancla='start'))
    s.append(flecha(610, 238, 587, 238))
    s.append(flecha(435, 238, 397, 238))

    # Criterio de parada
    s.append(f'<polygon points="335,204 395,238 335,272 275,238" fill="#ffffff" stroke="{NARANJA}" '
             'stroke-width="1.8"/>')
    s.append(f'<text x="335" y="243" text-anchor="middle" font-size="14" font-weight="600" fill="{INK}">'
             '¿Parar?</text>')
    s.append(flecha(200, 238, 273, 238))
    s.append(flecha(335, 204, 335, 128))
    s.append(rotulo(345, 170, 'no', ancla='start', color=INK2, estilo='normal'))
    s.append(flecha(335, 272, 335, 304))
    s.append(rotulo(345, 294, 'sí', ancla='start', color=INK2, estilo='normal'))
    s.append(caja(235, 306, 200, 46, 'Devolver', 'la mejor solución encontrada', '#ffffff', NARANJA))
    s.append('</svg>')
    return ''.join(s)


if __name__ == '__main__':
    destino = Path(__file__).with_name('03-ciclo.svg')
    destino.write_text(figura() + '\n', encoding='utf-8')
    print('Escrito', destino.name)
