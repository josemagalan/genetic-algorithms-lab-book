"""Genera la edición PDF de «Evolución a la vista» desde una copia limpia del repositorio.

Uso (desde cualquier carpeta):
    python pdf/generar.py TRABAJO SALIDA.pdf [--quarto RUTA] [--chrome RUTA] [--sin-render] [--contactos]

  TRABAJO      carpeta temporal (se crea): configuración, pasadas, informes y hojas de contacto
  SALIDA.pdf   PDF final
  --quarto     ejecutable de Quarto (por defecto, «quarto» del PATH)
  --chrome     navegador Chrome/Chromium que usará Playwright (por defecto, el de Playwright)
  --sin-render no vuelve a ejecutar «quarto render»: usa el _book/ existente
  --contactos  genera también hojas de contacto (12 páginas por hoja) para revisar la paginación

El libro que se imprime es el repositorio que contiene este guion. Debe estar limpio: verificar.py
falla si hay cambios en archivos con seguimiento. Los pasos y requisitos están en pdf/LEEME.md.
"""
from pathlib import Path
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent
args = sys.argv[1:]

def option(name, default=None):
    if name in args:
        i = args.index(name)
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default

def flag(name):
    if name in args:
        args.remove(name)
        return True
    return False

quarto = option('--quarto', 'quarto')
chrome = option('--chrome')
no_render = flag('--sin-render')
sheets = flag('--contactos')
if len(args) != 2:
    raise SystemExit(__doc__)
work, output = Path(args[0]).resolve(), Path(args[1]).resolve()
work.mkdir(parents=True, exist_ok=True)
output.parent.mkdir(parents=True, exist_ok=True)

env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
env['QUARTO_PYTHON'] = sys.executable
# El pre-render y el post-render de Quarto llaman a «python3»; en Windows ese nombre no siempre existe.
shim = work / 'bin'
shim.mkdir(exist_ok=True)
if os.name == 'nt':
    (shim / 'python3.cmd').write_text(f'@"{sys.executable}" %*\n', encoding='utf-8')
else:
    (shim / 'python3').write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n', encoding='utf-8')
    (shim / 'python3').chmod(0o755)
env['PATH'] = str(shim) + os.pathsep + env['PATH']
local_playwright = BOOK / 'comprobaciones/node_modules/playwright'
if 'PLAYWRIGHT_MODULE' not in env and local_playwright.exists():
    env['PLAYWRIGHT_MODULE'] = str(local_playwright)

def step(name, command):
    print(f'== {name}', flush=True)
    result = subprocess.run([str(c) for c in command], cwd=BOOK, env=env)
    if result.returncode:
        raise SystemExit(f'{name}: salida {result.returncode}')

python = [sys.executable, '-X', 'utf8']
step('preparar', [*python, HERE / 'preparar.py', BOOK, work, quarto, *(['--sin-render'] if no_render else [])])
step('imprimir', ['node', HERE / 'libro.cjs', '--libro', BOOK / '_book', '--trabajo', work, '--python', sys.executable,
                  *(['--chrome', chrome] if chrome else [])])
step('posproceso', [*python, HERE / 'posproceso.py', work, output])
step('verificar', [*python, HERE / 'verificar.py', BOOK, work, output])
if sheets:
    step('contactos', [*python, HERE / 'contactos.py', output, work / 'contactos', '45', '12'])
print(f'PDF: {output}')
