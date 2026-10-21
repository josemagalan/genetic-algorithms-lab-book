"""Portada vectorial de «Evolución a la vista» y adaptación horizontal.

Uso: python figuras/portada.py
Solo biblioteca estándar. Los SVG se escriben junto a este archivo.
Ilustración editorial original: los controles y gráficos son esquemáticos,
no capturas de las herramientas ni resultados de un experimento.
Contenido: CC BY 4.0; código: MIT (licencias del repositorio).
"""

from html import escape
from pathlib import Path


INK = "#19362f"
MUTED = "#5a6d64"
GREEN = "#0f6e56"
PURPLE = "#4a3f9e"
PALE_GREEN = "#e3f2ec"
PALE_PURPLE = "#ecebf8"
PAPER = "#f6f5ef"
LINE = "#d5ded5"
TITLE = "Evolución a la vista. Algoritmos genéticos en un laboratorio interactivo"
AUTHORS = [
    "José Manuel Galán", "Silvia Díaz-de la Fuente", "Virginia Ahedo",
    "María Pereda", "José Ignacio Santos",
]


def text(x, y, value, size=24, fill=INK, weight=400, extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" {extra}>{escape(value)}</text>')


def rect(x, y, w, h, fill, radius=0, stroke="none", sw=1, extra=""):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def line(x1, y1, x2, y2, color=LINE, width=2, extra=""):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{width}" {extra}/>')


def path(d, color, width=2, fill="none", extra=""):
    return (f'<path d="{d}" stroke="{color}" stroke-width="{width}" '
            f'fill="{fill}" stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def circle(cx, cy, r, fill, stroke="none", sw=1):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def label(x, y, value, fill=MUTED, size=17):
    return text(x, y, value, size, fill, 600, 'letter-spacing="2"')


def genome(x, y, values, colors, changed=None):
    out = []
    for i, (v, c) in enumerate(zip(values, colors)):
        xx = x + i * 54
        out.append(rect(xx, y, 46, 48, c, 7))
        out.append(text(xx + 23, y + 33, str(v), 27, "#ffffff", 600,
                        'text-anchor="middle" font-family="Consolas, monospace"'))
        if changed == i:
            out.append(rect(xx - 5, y - 5, 56, 58, "none", 10, INK, 2))
            out.append(circle(xx + 45, y - 4, 6, INK))
    return "".join(out)


def slider(x, y, title, position, color):
    return "".join([
        text(x, y, title, 23, INK, 500),
        line(x, y + 31, x + 170, y + 31, LINE, 5),
        line(x, y + 31, x + position, y + 31, color, 5),
        circle(x + position, y + 31, 11, "#ffffff", color, 3),
    ])


def chart(x, y, title, first, second):
    out = [text(x, y, title, 22, INK, 500)]
    for yy in (y + 35, y + 76, y + 117):
        out.append(line(x, yy, x + 256, yy, "#e8ece7", 1))
    out.extend([
        line(x, y + 23, x, y + 134, LINE, 1.5),
        line(x, y + 134, x + 256, y + 134, LINE, 1.5),
        f'<g transform="translate({x} {y+24})">',
        path(first, GREEN, 3.5),
        path(second, PURPLE, 3.5, extra='stroke-dasharray="6 6"'),
        '</g>',
    ])
    return "".join(out)


def panel():
    """Instrumento esquemático; coordenadas locales de 1020 × 730."""
    out = [
        rect(6, 12, 1020, 730, "#e4e8df", 25),
        rect(0, 0, 1020, 730, "#ffffff", 25, LINE, 2),
        path("M 25 0 H 995 Q 1020 0 1020 25 V 72 H 0 V 25 Q 0 0 25 0", INK, 0, INK),
        circle(35, 36, 5, "#88c2ac"),
        label(56, 42, "LABORATORIO / ALGORITMOS GENÉTICOS", "#ffffff", 16),
        # Small geometric instrument mark.
        rect(934, 25, 8, 22, "#88c2ac", 3),
        rect(950, 17, 8, 30, "#b9b1ed", 3),
        rect(966, 30, 8, 17, "#ffffff", 3),
        rect(20, 92, 244, 616, "#f3f6f1", 14),
        label(43, 130, "01 / CONFIGURA", GREEN, 16),
        slider(43, 190, "Población", 104, GREEN),
        slider(43, 296, "Cruce", 133, PURPLE),
        slider(43, 402, "Mutación", 38, GREEN),
        rect(43, 493, 193, 58, GREEN, 9),
        path("M 63 511 L 63 533 L 80 522 Z", "none", 0, "#ffffff"),
        text(98, 531, "Prueba", 24, "#ffffff", 600),
        # A circular arrow suggests repetitions and experimentation.
        path("M 92 636 A 23 23 0 1 1 132 615", MUTED, 2),
        path("M 121 615 L 134 615 L 134 602", MUTED, 2),
        text(149, 630, "Repite", 20, MUTED),
        label(302, 130, "02 / EXPERIMENTA", PURPLE, 16),
        text(302, 172, "Combina y explora", 30, INK, 600),
        label(302, 215, "PADRES", MUTED, 13),
        genome(302, 234, "10110110", [GREEN] * 8),
        genome(302, 300, "01001001", [PURPLE] * 8),
        # The same three-bit cut is used in both children.
        line(460, 225, 460, 355, "#b7c7bf", 1.5, 'stroke-dasharray="4 5"'),
        path("M 773 258 H 801 Q 817 258 817 274 V 343 Q 817 359 833 359 H 865", PURPLE, 2.5),
        path("M 773 324 H 793 Q 803 324 803 335 V 389 Q 803 401 819 401 H 865", GREEN, 2.5),
        # Children are represented in a compact vertical pair at right.
        label(866, 217, "HIJOS", MUTED, 13),
    ]
    # Two small eight-cell vertical chromosomes; a literal one-point crossover
    # at index 3 and a single mutation in the second child, index 5.
    child_values = ("10101001", "01010010")
    for j in range(2):
        for i in range(8):
            xx, yy = 866 + j * 57, 234 + i * 22
            c = (GREEN if i < 3 else PURPLE) if j == 0 else (PURPLE if i < 3 else GREEN)
            if j == 1 and i == 5:
                # Parent-A suffix is 10110; child 01010110 -> 01010010.
                out.append(rect(xx - 3, yy - 3, 48, 24, "none", 5, INK, 1.5))
            out.append(rect(xx, yy, 42, 18, c, 3))
            out.append(text(xx + 21, yy + 14, child_values[j][i], 14, "#ffffff", 600,
                            'text-anchor="middle" font-family="Consolas, monospace"'))
    out.extend([
        line(302, 449, 975, 449, LINE, 1.5),
        label(302, 488, "03 / COMPARA", GREEN, 16),
        chart(302, 533, "Aptitud",
              "M 0 101 L 20 89 L 40 92 L 60 69 L 80 76 L 100 52 L 120 56 L 140 37 L 160 42 L 180 24 L 200 30 L 220 17 L 250 19",
              "M 0 101 L 20 96 L 40 84 L 60 87 L 80 72 L 100 78 L 120 65 L 140 68 L 160 51 L 180 57 L 200 44 L 220 50 L 250 38"),
        chart(650, 533, "Diversidad",
              "M 0 12 L 20 25 L 40 21 L 60 38 L 80 34 L 100 47 L 120 40 L 140 55 L 160 52 L 180 65 L 200 60 L 220 72 L 250 68",
              "M 0 12 L 20 28 L 40 34 L 60 31 L 80 47 L 100 51 L 120 61 L 140 58 L 160 75 L 180 78 L 200 89 L 220 86 L 250 98"),
        line(945, 483, 965, 483, GREEN, 3),
        line(979, 483, 999, 483, PURPLE, 3, 'stroke-dasharray="5 4"'),
    ])
    return "".join(out)


def svg_document(width, height, body, description):
    # Self-contained SVG, system fonts, editable text, no linked assets.
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="cover-title cover-desc">
<title id="cover-title">{escape(TITLE)}</title>
<desc id="cover-desc">{escape(description)}</desc>
<metadata>Ilustración editorial original elaborada con asistencia de Codex, 2026-10-21. Contenido CC BY 4.0. Controles y gráficas esquemáticos, sin datos experimentales. Texto editable; fuentes de sistema.</metadata>
<g font-family="Arial, Helvetica, sans-serif">{body}</g>
</svg>
'''


def portrait():
    out = [
        rect(0, 0, 1200, 1800, PAPER),
        rect(0, 0, 16, 1800, GREEN),
        label(90, 99, "EXPLORA · EXPERIMENTA · COMPARA", GREEN, 19),
        line(90, 134, 1110, 134, LINE, 2),
        text(83, 273, "Evolución", 132, INK, 700, 'letter-spacing="-6"'),
        text(83, 410, "a la vista.", 132, INK, 700, 'letter-spacing="-6"'),
        text(90, 508, "Algoritmos genéticos", 66, PURPLE, 600, 'letter-spacing="-2"'),
        text(90, 567, "en un laboratorio interactivo", 43, INK, 400, 'letter-spacing="-0.5"'),
        '<g transform="translate(90 654)">' + panel() + '</g>',
        # The connected line leads out of the instrument into the reader's act.
        line(90, 1451, 150, 1451, GREEN, 3),
        text(173, 1461, "Predice. Prueba. Comprende.", 34, INK, 500),
        line(90, 1545, 1110, 1545, LINE, 2),
        label(90, 1597, "AUTORES", MUTED, 16),
        text(90, 1648, "José Manuel Galán · Silvia Díaz-de la Fuente", 30, INK, 500),
        text(90, 1694, "Virginia Ahedo · María Pereda · José Ignacio Santos", 30, INK, 500),
        label(90, 1760, "LABORATORIO DE ALGORITMOS GENÉTICOS", GREEN, 16),
        # A small signature derived from the recombination motif.
        rect(1005, 1735, 28, 28, GREEN, 5),
        rect(1043, 1735, 28, 28, PURPLE, 5),
        rect(1081, 1735, 28, 28, PALE_PURPLE, 5),
    ]
    return svg_document(1200, 1800, "".join(out),
        "Portada con el título completo y los cinco autores. Un panel de laboratorio digital conecta controles de población, cruce y mutación, cadenas binarias y dos gráficas esquemáticas de aptitud y diversidad.")


def landscape():
    out = [
        rect(0, 0, 1800, 1000, PAPER),
        rect(0, 0, 16, 1000, GREEN),
        label(80, 96, "EXPLORA · EXPERIMENTA · COMPARA", GREEN, 17),
        text(74, 242, "Evolución", 100, INK, 700, 'letter-spacing="-4.5"'),
        text(74, 350, "a la vista.", 100, INK, 700, 'letter-spacing="-4.5"'),
        text(80, 435, "Algoritmos genéticos", 50, PURPLE, 600, 'letter-spacing="-1.5"'),
        text(80, 486, "en un laboratorio", 38, INK),
        text(80, 534, "interactivo", 38, INK),
        line(80, 624, 126, 624, GREEN, 3),
        text(149, 634, "Predice. Prueba. Comprende.", 26, INK, 500),
        '<g transform="translate(745 178) scale(0.94)">' + panel() + '</g>',
        line(80, 748, 650, 748, LINE, 2),
        text(80, 798, AUTHORS[0], 25, INK, 500),
        text(80, 837, AUTHORS[1], 25, INK, 500),
        text(80, 876, AUTHORS[2] + " · " + AUTHORS[3], 25, INK, 500),
        text(80, 915, AUTHORS[4], 25, INK, 500),
        label(745, 96, "LABORATORIO DE ALGORITMOS GENÉTICOS", GREEN, 16),
    ]
    return svg_document(1800, 1000, "".join(out),
        "Adaptación horizontal: título y autores a la izquierda; panel de experimentación digital a la derecha, con controles, recombinación de soluciones y comparación de resultados esquemáticos.")


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent
    for name, content in (("portada.svg", portrait()), ("portada-horizontal.svg", landscape())):
        target = folder / name
        target.write_text(content, encoding="utf-8", newline="\n")
        print(target)
