"""Quita la sigla de nivel duplicada de los extractos de búsqueda (revisión beta, M07).

Las etiquetas de nivel llevan el nombre largo y la sigla (Básico + B), y el CSS muestra uno u otro.
En search.json, Quarto concatena los dos («BásicoB»). Este script se ejecuta como «post-render»
y deja solo el nombre largo. No toca las páginas.
"""
import json
import os

CAMBIOS = (('BásicoB', 'Básico'), ('AvanzadoA', 'Avanzado'), ('Para saber más+', 'Para saber más'))


def limpiar(valor):
    if isinstance(valor, str):
        for antes, despues in CAMBIOS:
            valor = valor.replace(antes, despues)
        return valor
    if isinstance(valor, list):
        return [limpiar(v) for v in valor]
    if isinstance(valor, dict):
        return {k: limpiar(v) for k, v in valor.items()}
    return valor


def main():
    ruta = os.path.join(os.environ.get('QUARTO_PROJECT_OUTPUT_DIR', '_book'), 'search.json')
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding='utf-8') as fh:
        datos = json.load(fh)
    limpio = limpiar(datos)
    if limpio != datos:
        with open(ruta, 'w', encoding='utf-8') as fh:
            json.dump(limpio, fh, ensure_ascii=False)


if __name__ == '__main__':
    main()
