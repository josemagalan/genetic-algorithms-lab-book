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
