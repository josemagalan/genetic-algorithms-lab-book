"""Imágenes del capítulo 1 (Evolución y optimización).

No son figuras propias: son reproducciones de obras de dominio público o con
licencia CC BY 4.0, tomadas de Wikimedia Commons. Este guion parte de los
archivos originales, comprueba que son los publicados (SHA-256) y genera las
versiones para la web que usa el libro. La procedencia y la licencia de cada
una están en 01-imagenes.md.

Uso:
    python3 01-imagenes.py CARPETA_CON_LOS_ORIGINALES

Si un original no está en la carpeta, el guion intenta descargarlo de
Wikimedia Commons. Necesita Pillow (pip install pillow).
"""

import hashlib
import sys
import urllib.request
from pathlib import Path

from PIL import Image

COMMONS = "https://upload.wikimedia.org/wikipedia/commons/"
ORIGINALES = {
    "Darwins_first_tree.jpg": (
        COMMONS + "4/4b/Darwins_first_tree.jpg",
        "727da61c37a6d1a356d3096a279d7e65876ced812aa275f01988fecce81cdeb3",
    ),
    "Charles_Darwin_seated_crop.jpg": (
        COMMONS + "2/2e/Charles_Darwin_seated_crop.jpg",
        "08e67679abbeec69d81a5f70cc49d1422ecefde3e215b45f8e90c056368656a3",
    ),
    "Jean_Baptiste_Pierre_Antoine_de_Monet_Lamarck._Photogravure_Wellcome_V0003324.jpg": (
        COMMONS + "5/58/Jean_Baptiste_Pierre_Antoine_de_Monet_Lamarck._Photogravure_Wellcome_V0003324.jpg",
        "f792896e303246267af855a6b04365f147c35f52b9fbbdb3ca8c642a78960cb3",
    ),
    "Origin_of_Species_title_page.jpg": (
        COMMONS + "c/cd/Origin_of_Species_title_page.jpg",
        "6143dce553869357fa45a28d467660c08518d390e52bac20975daf7e9ffac78d",
    ),
}

AQUI = Path(__file__).resolve().parent


def original(carpeta, nombre):
    ruta = carpeta / nombre
    url, sha = ORIGINALES[nombre]
    if not ruta.exists():
        peticion = urllib.request.Request(url, headers={"User-Agent": "Libro-GA/1.0"})
        ruta.write_bytes(urllib.request.urlopen(peticion).read())
    resumen = hashlib.sha256(ruta.read_bytes()).hexdigest()
    if resumen != sha:
        sys.exit(f"{nombre}: el SHA-256 no coincide con el original publicado")
    return Image.open(ruta)


def guardar(imagen, nombre):
    imagen.convert("RGB").save(AQUI / nombre, "JPEG", quality=85, optimize=True, progressive=True)
    print(nombre, imagen.size)


def alto(imagen, h):
    return imagen.resize((round(imagen.width * h / imagen.height), h), Image.LANCZOS)


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / "originales"
    carpeta.mkdir(exist_ok=True)

    # Esbozo «I think» (1837): sin cambios de tamaño, solo recomprimido.
    guardar(original(carpeta, "Darwins_first_tree.jpg"), "01-darwin-esbozo-1837.jpg")

    # Retratos: Lamarck recortado al grabado (sin el margen del papel) y Darwin,
    # los dos a 520 px de alto, uno junto al otro con 16 px de separación.
    lamarck = original(
        carpeta, "Jean_Baptiste_Pierre_Antoine_de_Monet_Lamarck._Photogravure_Wellcome_V0003324.jpg"
    ).crop((366, 381, 1998, 2480))
    darwin = original(carpeta, "Charles_Darwin_seated_crop.jpg")
    lamarck, darwin = alto(lamarck.convert("RGB"), 520), alto(darwin.convert("RGB"), 520)
    lienzo = Image.new("RGB", (lamarck.width + 16 + darwin.width, 520), "white")
    lienzo.paste(lamarck, (0, 0))
    lienzo.paste(darwin, (lamarck.width + 16, 0))
    guardar(lienzo, "01-lamarck-darwin.jpg")

    # Portada de la primera edición (1859), a 520 px de ancho.
    portada = original(carpeta, "Origin_of_Species_title_page.jpg")
    portada = portada.resize((520, round(portada.height * 520 / portada.width)), Image.LANCZOS)
    guardar(portada, "01-origen-portada-1859.jpg")


if __name__ == "__main__":
    main()
