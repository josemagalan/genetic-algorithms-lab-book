"""English cover derived from the approved Spanish vector design.

Run from the repository root: python en/figuras/portada.py
Uses the shared drawing primitives and panel in figuras/portada.py.
Content: CC BY 4.0; code: MIT. Python standard library only.
"""

from html import escape
import importlib.util
from pathlib import Path


BOOK = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("portada_original", BOOK / "figuras/portada.py")
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
text, rect, line, label = original.text, original.rect, original.line, original.label
INK, MUTED, GREEN, PURPLE = original.INK, original.MUTED, original.GREEN, original.PURPLE
PAPER, LINE, PALE_PURPLE = original.PAPER, original.LINE, original.PALE_PURPLE
AUTHORS = original.AUTHORS
TITLE = "Evolution Made Visible: Genetic Algorithms in an Interactive Laboratory"

PANEL_TEXT = {
    "LABORATORIO / ALGORITMOS GENÉTICOS": "LAB / GENETIC ALGORITHMS",
    "01 / CONFIGURA": "01 / CONFIGURE",
    "Población": "Population",
    "Cruce": "Crossover",
    "Mutación": "Mutation",
    "Prueba": "Run",
    "Repite": "Repeat",
    "02 / EXPERIMENTA": "02 / EXPERIMENT",
    "Combina y explora": "Combine and explore",
    "PADRES": "PARENTS",
    "HIJOS": "OFFSPRING",
    "03 / COMPARA": "03 / COMPARE",
    "Aptitud": "Fitness",
    "Diversidad": "Diversity",
}


def panel():
    """Preserve all geometry, chromosomes, colors, and schematic curves."""
    result = original.panel()
    for spanish, english in PANEL_TEXT.items():
        source = ">" + escape(spanish) + "<"
        if result.count(source) != 1:
            raise ValueError(f"Shared panel label has changed: {spanish}")
        result = result.replace(source, ">" + escape(english) + "<")
    return result


def svg_document(width, height, body, description):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xml:lang="en-US" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="cover-title cover-desc">
<title id="cover-title">{escape(TITLE)}</title>
<desc id="cover-desc">{escape(description)}</desc>
<metadata>English adaptation prepared with the assistance of Codex, 2026-10-31, from the Spanish cover designed with Codex, 2026-10-21. Content CC BY 4.0. Schematic controls and charts, not experimental data. Editable text; system fonts.</metadata>
<g font-family="Arial, Helvetica, sans-serif">{body}</g>
</svg>
'''


def portrait():
    out = [
        rect(0, 0, 1200, 1800, PAPER),
        rect(0, 0, 16, 1800, GREEN),
        label(90, 99, "EXPLORE · EXPERIMENT · COMPARE", GREEN, 19),
        line(90, 134, 1110, 134, LINE, 2),
        text(83, 273, "Evolution", 132, INK, 700, 'letter-spacing="-6"'),
        text(83, 410, "Made Visible", 132, INK, 700, 'letter-spacing="-6"'),
        text(90, 508, "Genetic Algorithms", 66, PURPLE, 600, 'letter-spacing="-2"'),
        text(90, 567, "in an Interactive Laboratory", 43, INK, 400, 'letter-spacing="-0.5"'),
        '<g transform="translate(90 654)">' + panel() + '</g>',
        line(90, 1451, 150, 1451, GREEN, 3),
        text(173, 1461, "Predict. Test. Understand.", 34, INK, 500),
        line(90, 1545, 1110, 1545, LINE, 2),
        label(90, 1597, "AUTHORS", MUTED, 16),
        text(90, 1648, AUTHORS[0] + " · " + AUTHORS[1], 30, INK, 500),
        text(90, 1694, " · ".join(AUTHORS[2:]), 30, INK, 500),
        label(90, 1760, "GENETIC ALGORITHMS LAB", GREEN, 16),
        rect(1005, 1735, 28, 28, GREEN, 5),
        rect(1043, 1735, 28, 28, PURPLE, 5),
        rect(1081, 1735, 28, 28, PALE_PURPLE, 5),
    ]
    return svg_document(1200, 1800, "".join(out),
        "Book cover with the full English title and five authors. A digital laboratory "
        "panel connects population, crossover, and mutation controls, binary chromosomes, "
        "and schematic fitness and diversity charts.")


def landscape():
    out = [
        rect(0, 0, 1800, 1000, PAPER),
        rect(0, 0, 16, 1000, GREEN),
        label(80, 96, "EXPLORE · EXPERIMENT · COMPARE", GREEN, 17),
        text(74, 242, "Evolution", 100, INK, 700, 'letter-spacing="-4.5"'),
        text(74, 350, "Made Visible", 100, INK, 700, 'letter-spacing="-4.5"'),
        text(80, 435, "Genetic Algorithms", 50, PURPLE, 600, 'letter-spacing="-1.5"'),
        text(80, 486, "in an Interactive", 38, INK),
        text(80, 534, "Laboratory", 38, INK),
        line(80, 624, 126, 624, GREEN, 3),
        text(149, 634, "Predict. Test. Understand.", 26, INK, 500),
        '<g transform="translate(745 178) scale(0.94)">' + panel() + '</g>',
        line(80, 748, 650, 748, LINE, 2),
        text(80, 798, AUTHORS[0], 25, INK, 500),
        text(80, 837, AUTHORS[1], 25, INK, 500),
        text(80, 876, AUTHORS[2] + " · " + AUTHORS[3], 25, INK, 500),
        text(80, 915, AUTHORS[4], 25, INK, 500),
        label(745, 96, "GENETIC ALGORITHMS LAB", GREEN, 16),
    ]
    return svg_document(1800, 1000, "".join(out),
        "Horizontal cover: the English title and authors on the left; a digital "
        "laboratory panel on the right, with controls, recombination, and schematic "
        "fitness and diversity comparisons.")


if __name__ == "__main__":
    folder = Path(__file__).resolve().parent
    for name, content in (("portada.svg", portrait()), ("portada-horizontal.svg", landscape())):
        target = folder / name
        target.write_text(content, encoding="utf-8", newline="\n")
        print(target)
