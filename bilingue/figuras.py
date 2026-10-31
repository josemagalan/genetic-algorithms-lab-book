"""Deriva SVG ingleses conservando geometría, estilos, metadatos y créditos."""
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def generar(originales: Path, destino: Path, diccionario: Path):
    mappings = json.loads(diccionario.read_text(encoding='utf-8'))
    resultados = {}
    for nombre, cambios in mappings.items():
        texto = (originales / nombre).read_text(encoding='utf-8')
        raiz = ET.fromstring(texto)
        usados = set()
        # Sustituir solo contenido de nodos, nunca atributos, trazados o estilos.
        def traducir(match):
            contenido = html.unescape(match[1])
            if contenido not in cambios:
                return match[0]
            usados.add(contenido)
            return '>' + html.escape(cambios[contenido], quote=False) + '<'
        nuevo = re.sub(r'>([^<>]+)<', traducir, texto)
        if usados != set(cambios):
            raise ValueError(f'Rótulos de figura no encontrados en {nombre}: {set(cambios) - usados}')
        traducida = ET.fromstring(nuevo)
        original_nodes, translated_nodes = list(raiz.iter()), list(traducida.iter())
        if [(n.tag, n.attrib) for n in original_nodes] != [(n.tag, n.attrib) for n in translated_nodes]:
            raise ValueError(f'Cambió la geometría o estructura de {nombre}')
        destino.mkdir(parents=True, exist_ok=True)
        (destino / nombre).write_text(nuevo, encoding='utf-8')
        resultados[nombre] = len(usados)
    return resultados
