"""Página (índice desde 0) de cada destino interno de un PDF de Chromium."""
import json, sys
from pypdf import PdfReader
reader = PdfReader(sys.argv[1])
wanted = json.load(open(sys.argv[2], encoding='utf-8'))
names = reader.named_destinations
out, missing = {}, []
for w in wanted:
    d = names.get(w) or names.get('/' + w)
    if d is None: missing.append(w); continue
    out[w] = reader.get_destination_page_number(d)
print(json.dumps({'total': len(reader.pages), 'map': out, 'missing': missing}, ensure_ascii=False))
