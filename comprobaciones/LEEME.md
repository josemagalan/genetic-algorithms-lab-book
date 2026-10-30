# Comprobaciones del libro frente a las herramientas

Los ejemplos del libro dependen de las herramientas, que se actualizan por separado (revisión beta, M08). Aquí están:

- `herramientas.json`: el manifiesto. Para cada herramienta, el commit con el que se ejecutaron los ejemplos (`ejemplos`) y el último commit revisado (`revisado`): hasta ahí se ha comprobado que los cambios no alteran los ejemplos.
- `comprobar.cjs`: el guion de comprobación (Node 18 o posterior y git).

## Qué comprueba

1. **Versiones.** Descarga cada herramienta y la compara con `revisado`. Si han cambiado archivos que pueden alterar los ejemplos (operadores, interfaz, textos de los controles), falla y dice qué capítulos hay que volver a comprobar. Los cambios solo en README, pruebas, imágenes o «Acerca de» se anotan sin fallar.
2. **Controles.** Lee los enlaces del libro a selection-ga, crossover-ga y mutation-ga y comprueba en el código de cada herramienta que el operador y la variante existen y que cada parámetro cabe entre el mínimo y el máximo de su control; en el torneo, además, que *k* no supera la población. Las instrucciones del texto que piden un valor sin enlace se comprueban con una anotación invisible junto a ellas:

   ```html
   <!-- comprobar: https://josemagalan.github.io/selection-ga/#op=tournament&lang=es&k=4&f=1-2-3-4 -->
   ```

representation-ga, initialization-and-evaluation-ga, EvoTraveller y SelectionMechanisms solo tienen la comprobación de versiones: sus controles no siguen el mismo formato.

## Cuándo se ejecuta

`.github/workflows/comprobar.yml` lo ejecuta en cada *push* y *pull request*, cada lunes y a mano. No bloquea la publicación, que va en otro flujo (`publish.yml`); si falla, GitHub avisa por correo.

En local: `node comprobaciones/comprobar.cjs` (con `--sin-versiones`, solo los controles).

## Al volver a comprobar una herramienta

1. Repetir los ejemplos afectados con el código y en la interfaz publicada (guía para redactar un capítulo, apartado 8).
2. Actualizar en `herramientas.json` `revisado` (y `ejemplos`, si se han vuelto a ejecutar) y explicar en `comentario` qué ha cambiado.
3. Actualizar el comentario de comprobación de los capítulos afectados.

## HTML y muestra de interfaces

`html.cjs` comprueba el libro generado: archivos y anclas locales, identificadores duplicados, referencias sin resolver, textos alternativos, títulos de iframe y el recorrido básico con sus objetivos y resumen. Solo necesita Node 22:

```bash
quarto render
node comprobaciones/html.cjs
```

`interfaz.cjs` usa Playwright y Chromium para repetir una muestra: navegación básica, ampliación de una figura en móvil, ciclo del portal ES/EN, enlaces al capítulo en los cinco módulos, ruleta de Goldberg, OX clásico, siembra ES/EN y la comparación de selección. Lee las URL de los ejemplos del propio libro y contrasta los resultados visibles. No sustituye el repaso de todas las actividades ni las pruebas de Shiny o Streamlit.

```bash
cd comprobaciones
npm ci --ignore-scripts --no-audit --no-fund
npx playwright install chromium
cd ..
node comprobaciones/interfaz.cjs
```

El guion espera copias de los cinco módulos en `_herramientas/<nombre>/` y del portal en `_herramientas/portal/`. Se puede indicar otra carpeta con `GA_APPS_ROOT`. Sirve las copias y `_book/` en un servidor local temporal, y lo cierra al terminar. Usa los directorios completos de las herramientas, incluidos `vendor/`, imágenes y `.nojekyll`. `GA_CHROMIUM_PATH` permite usar un ejecutable de Chrome existente; si se omite, usa el Chromium de Playwright.

Los resultados y las capturas quedan en `comprobaciones/resultados/`, fuera del control de versiones. `GA_UI_OUTPUT` permite elegir otro destino. La salida es distinta de cero si falla una comprobación o aparece un error de JavaScript.

`.github/workflows/verificar-html.yml` genera el libro y ejecuta ambas comprobaciones en cada push, pull request, cada lunes y a mano. Descarga la cabecera actual de los módulos y del portal y guarda los resultados como artefacto. Es un flujo independiente de publicar: avisa de un fallo sin añadir una condición nueva al despliegue.

Al coordinar cambios entre repositorios, publica primero las herramientas y después actualiza el manifiesto del libro con sus commits comprobados. Las pruebas de siembra y del ciclo esperan la explicación coordinada del libro; si las herramientas siguen con los textos anteriores, el fallo señala esa falta de coordinación. No anotes un commit futuro ni declares verificada la versión publicada a partir de una prueba local.
