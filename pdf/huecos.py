"""Fracción de la caja de texto que queda en blanco al pie de cada página.
Uso: python3 huecos.py PDF → JSON (lista por página). Usa Poppler (pdftotext -bbox) para no cargar
todo el documento en memoria; las figuras sin texto se detectan aparte en la revisión visual."""
import json, re, subprocess, sys
top, bottom = 17 / 25.4 * 72, (297 - 18) / 25.4 * 72
html = subprocess.run(['pdftotext', '-bbox', sys.argv[1], '-'], capture_output=True, text=True, check=True).stdout
res = []
for page in re.findall(r'<page[^>]*>(.*?)</page>', html, re.S):
    ys = [float(y) for y in re.findall(r'<word [^>]*yMax="([\d.]+)"', page)]
    ys = [y for y in ys if top - 1 < y < bottom - 2]
    res.append(round((bottom - (max(ys) if ys else top)) / (bottom - top), 3))
print(json.dumps(res))
