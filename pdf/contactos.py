"""Hojas de contacto para revisar todas las páginas: python3 contactos.py PDF CARPETA [ppp] [por_hoja]"""
import sys, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw
from pypdf import PdfReader
pdf, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 60
per = int(sys.argv[4]) if len(sys.argv) > 4 else 6
reader = PdfReader(pdf); labels = reader.page_labels
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', str(pdf), f'{tmp}/p'], check=True)
    pages = sorted(Path(tmp).glob('p-*.png'))
    cols = 6 if per >= 12 else (4 if per >= 8 else (3 if per >= 6 else 2))
    for s in range(0, len(pages), per):
        group = pages[s:s + per]; ims = [Image.open(p).convert('RGB') for p in group]
        w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * (w + 12) + 12, rows * (h + 26) + 12), '#d1d5db'); d = ImageDraw.Draw(sheet)
        for j, im in enumerate(ims):
            x = 12 + (j % cols) * (w + 12); y = 12 + (j // cols) * (h + 26)
            d.text((x, y), f'PDF {s + j + 1} · folio {labels[s + j]}', fill='black'); sheet.paste(im, (x, y + 14))
        sheet.save(out / f'hoja-{s + 1:03d}-{s + len(group):03d}.png')
print(len(pages), 'páginas;', len(list(out.glob('*.png'))), 'hojas')
