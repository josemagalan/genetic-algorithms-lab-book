# Edición en PDF

Estos guiones generan el PDF del libro a partir de las mismas fuentes que la web. No modifican ningún `.qmd`: Quarto produce el HTML del libro y las adaptaciones de impresión se hacen después, en una copia temporal del DOM.

## Qué hace

1. `preparar.py` ejecuta `quarto render` y registra la versión, el DOI, el commit y los autores leídos de `_quarto.yml`. Calcula además los puntos de corte de palabra con Pyphen (español, tres letras a cada lado).
2. `libro.cjs` y `adaptar.cjs` reúnen los capítulos en un documento único, con portada, créditos, índice con páginas, «Cómo leer» adaptado, índice de actividades y avisos. Abren los desplegables y trasladan las soluciones de los ejercicios al final de cada capítulo, con enlaces de ida y vuelta. Después imprimen el documento en Chromium con `impresion.css` y `textos-impresion.json`; hacen dos pasadas para numerar el índice.
3. `posproceso.py` añade folios, cabeceras, marcadores, etiquetas de página y metadatos.
4. `verificar.py` comprueba:
   - los enlaces internos y externos, los enlaces a las aplicaciones, los pares ida/vuelta y los marcadores;
   - el índice, las fuentes incrustadas y los metadatos, incluido el DOI;
   - que la web conserva las soluciones plegadas y que el commit no tiene cambios.

   Termina con error si algo falla y deja el informe en `TRABAJO/resultado.json`.

`ajustes.json` guarda los parámetros de paginación:

- las fracciones de página por debajo de las cuales una caja no se parte;
- las cajas que se mantienen completas;
- los altos máximos de figuras concretas.

Si cambia el contenido de un capítulo, conviene revisar esos valores con las hojas de contacto (`--contactos`, o `contactos.py` y `huecos.py`).

## Requisitos

- [Quarto](https://quarto.org) 1.10.19, la versión que usa la publicación web.
- Python 3.10 o posterior, con los paquetes de `requisitos.txt` (`pip install -r pdf/requisitos.txt`).
- Node 18 o posterior y Playwright. Basta con instalar las dependencias de las comprobaciones (`npm ci` en `comprobaciones/`); el generador las encuentra solo.
- Chrome o Chromium. Por defecto se usa el de Playwright; `--chrome` indica otro.
- Opcional: Poppler (`pdffonts`, `pdftotext`, `pdftoppm`). Acelera la verificación y hace falta para las hojas de contacto.

La tipografía del PDF, Noto Sans, va incluida en `fuentes/` (SIL Open Font License 1.1, `fuentes/OFL-NotoSans.txt`) y se incrusta en el PDF. Las figuras SVG declaran la fuente del sistema, de modo que en otro sistema operativo su texto puede cambiar ligeramente y, con él, algún salto de página.

## Uso

Desde una copia limpia del commit que se quiere imprimir (por ejemplo, un `git clone` de la etiqueta):

```bash
python pdf/generar.py ../trabajo-pdf ../evolucion-a-la-vista.pdf --contactos
```

En Windows, con un Quarto que no esté en el PATH:

```powershell
python pdf\generar.py ..\trabajo-pdf ..\evolucion-a-la-vista.pdf --quarto C:\ruta\quarto.exe --chrome "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

El guion crea en `TRABAJO/bin` un `python3` que apunta al Python con el que se ejecuta, porque los filtros de Quarto llaman a ese nombre.

Los créditos del PDF indican la versión, la fecha de revisión, el commit de origen y la fecha de generación. Una copia con cambios sin confirmar no supera `verificar.py`.

## Códigos QR (versión 1.1)

Desde la versión 1.1 (D100), `adaptar.cjs` añade un código QR junto a cada enlace a una aplicación y `qr.py` (segno) genera las imágenes. Las claves y sus destinos están en [`qr/claves.json`](../qr/claves.json), que también usa la web para publicar las redirecciones; las reglas, en [`qr/LEEME.md`](../qr/LEEME.md). Si el libro tiene enlaces nuevos, el generador se detiene: `--registrar-qr` los añade al registro, que hay que confirmar con un commit antes de generar el PDF definitivo. El manifiesto de cada generación queda en `TRABAJO/qr.json`.

Para comprobar los códigos, renderizar el PDF a 200 ppp (`pdftoppm`) y leerlos con zbar (`pyzbar`): deben coincidir uno a uno con el manifiesto.

## Edición inglesa

La traducción inglesa se imprime con el mismo generador:

```bash
python pdf/generar.py ../trabajo-pdf-en ../evolution-made-visible.pdf --edicion en --contactos
```

`--edicion en` ejecuta antes `bilingue/generar.py` en `TRABAJO/bilingue` (la misma copia que se publica en `/en/`: la etiqueta `v1.0` con las fuentes de `en/` superpuestas y el perfil `_quarto-en.yml`) e imprime su HTML inglés. Con `--sin-render` reutiliza esa copia si ya existe. El commit y los cambios locales se comprueban en este repositorio, no en la copia.

Los textos de cada edición están en `edicion.json` (español) y `en/edicion.json` (inglés): rótulos del índice, créditos, desplegables, soluciones, marcadores, metadatos, idioma del PDF y diccionario de Pyphen (`en_US` en inglés). Las sustituciones que describen la interfaz web están en `en/textos-impresion.json`, traducción de las aprobadas en D087, y la paginación en `en/ajustes.json`. El DOI de la traducción es el `libro-doi` de `en/_quarto-en.yml` (registro propio en Zenodo); el del original español aparece en los créditos y los metadatos como fuente, nunca como identificador de esta edición. Si el perfil no declarase un DOI propio, el PDF no tendría ninguno.

## Edición 1.0

El PDF de la edición 1.0 se generó con este código desde la etiqueta `v1.0`, en Windows, con Chrome 156 y Quarto 1.10.19. El registro de la generación, el entorno y los SHA-256 de los archivos depositados acompañan al depósito en Zenodo.
