"""Conjunción «y» → «e» ante palabras que empiezan por el sonido /i/ (i-, hi-) en el HTML generado.

El estilo de citas (CSL) siempre escribe «y» («Galán y Izquierdo»), y en los libros de Quarto
las citas se resuelven al final, así que un filtro Lua no llega a verlas. Este script se ejecuta
como «post-render» del proyecto y solo toca el texto entre etiquetas, nunca atributos ni código.
No cambia «y» ante diptongo (hie-, hia-, io-…: «y hierro», «y Iowa»).
"""
import os
import re
import sys

PATRON = re.compile(r'(?<![\w-])y(\s+)(?=(?:[Hh])?[IiÍí](?![aeoáéóAEOÁÉÓ]))')
TROZO = re.compile(r'(<(script|style|pre|code)\b.*?</\2>)|(<[^>]*>)|([^<]+)', re.S | re.I)


def corregir(html):
    def f(m):
        if m.group(4) is None:
            return m.group(0)
        return PATRON.sub(lambda x: 'e' + x.group(1), m.group(4))
    return TROZO.sub(f, html)


def main():
    salida = os.environ.get('QUARTO_PROJECT_OUTPUT_DIR', '.')
    archivos = os.environ.get('QUARTO_PROJECT_OUTPUT_FILES', '').split('\n')
    archivos = [a for a in archivos if a.endswith('.html')] or sys.argv[1:]
    for a in archivos:
        ruta = a if os.path.isabs(a) or os.path.exists(a) else os.path.join(salida, a)
        with open(ruta, encoding='utf-8') as fh:
            antes = fh.read()
        despues = corregir(antes)
        if despues != antes:
            with open(ruta, 'w', encoding='utf-8') as fh:
                fh.write(despues)


if __name__ == '__main__':
    main()
