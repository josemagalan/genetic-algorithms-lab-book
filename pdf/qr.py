"""Genera los códigos QR del PDF (edición 1.1) a partir del manifiesto que escribe libro.cjs.

Uso: python qr.py TRABAJO/qr.json TRABAJO/qr

Cada código contiene la dirección corta base + clave (p. ej. …/a/4.6b), no la dirección completa de la
aplicación: así es más pequeño y la redirección se puede corregir en la web sin reimprimir el libro.
Corrección de errores M; SVG vectorial sin margen (el margen lo pone la hoja de estilo).
"""
import json
import sys
from pathlib import Path

import segno

manifest, out = Path(sys.argv[1]), Path(sys.argv[2])
data = json.loads(manifest.read_text(encoding='utf-8'))
out.mkdir(parents=True, exist_ok=True)
versions = {}
for c in data['codigos']:
    q = segno.make(c['url'], error='m', micro=False)
    # SVG con viewBox, sin tamaño fijo: la hoja de estilo fija el lado en milímetros.
    q.save(out / f"{c['clave']}.svg", kind='svg', scale=1, border=0, dark='#000', xmldecl=False, svgns=True,
           omitsize=True)
    versions[q.version] = versions.get(q.version, 0) + 1
print('QR por versión:', dict(sorted(versions.items())))
