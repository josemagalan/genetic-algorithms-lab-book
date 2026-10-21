# Evolución a la vista

*Algoritmos genéticos en un laboratorio interactivo*

> **Estado: versión 0.9 beta, revisada el 16 de octubre de 2026** (primera publicación: 7 de octubre de 2026). Los autores siguen revisando el texto y los ejemplos; el contenido, la estructura y el índice pueden cambiar. La versión y la fecha están en `_quarto.yml` (`libro-version` y `libro-revision`).

Libro para aprender algoritmos genéticos de forma práctica, con actividades sobre las herramientas interactivas del [Laboratorio de algoritmos genéticos](https://josemagalan.github.io/genetic-algorithms-lab/) (*genetic-algorithms-lab*). Está pensado para estudiantes de grado que empiezan.

**Versión para leer:** <https://josemagalan.github.io/genetic-algorithms-lab-book/>

<!-- ga-series-links:start -->
## Teaching resources / Materiales docentes

[Portal en español](https://josemagalan.github.io/genetic-algorithms-lab/?lang=es) · [Portal in English](https://josemagalan.github.io/genetic-algorithms-lab/?lang=en)

| Resource / Recurso | Use or read / Usar o leer | Repository / Repositorio |
| --- | --- | --- |
| Portal: Genetic Algorithms Lab / Laboratorio de algoritmos genéticos | [Open / Abrir](https://josemagalan.github.io/genetic-algorithms-lab/) | [GitHub](https://github.com/josemagalan/genetic-algorithms-lab) |
| Representation / Representación | [Open / Abrir](https://josemagalan.github.io/representation-ga/) | [GitHub](https://github.com/josemagalan/representation-ga) |
| Initialisation and evaluation / Inicialización y evaluación | [Open / Abrir](https://josemagalan.github.io/initialization-and-evaluation-ga/) | [GitHub](https://github.com/josemagalan/initialization-and-evaluation-ga) |
| Selection / Selección | [Open / Abrir](https://josemagalan.github.io/selection-ga/) | [GitHub](https://github.com/josemagalan/selection-ga) |
| Crossover / Cruce | [Open / Abrir](https://josemagalan.github.io/crossover-ga/) | [GitHub](https://github.com/josemagalan/crossover-ga) |
| Mutation / Mutación | [Open / Abrir](https://josemagalan.github.io/mutation-ga/) | [GitHub](https://github.com/josemagalan/mutation-ga) |
| EvoTraveller | [Open / Abrir](https://evotraveller.streamlit.app/) | [GitHub](https://github.com/jismartin/evotraveller) |
| SelectionMechanisms | [Open / Abrir](https://josemagalan.shinyapps.io/SelectionMechanisms/) | [GitHub](https://github.com/josemagalan/SelectionMechanisms) |
| Book / Libro: *Evolución a la vista* | [Read / Leer](https://josemagalan.github.io/genetic-algorithms-lab-book/) | [GitHub](https://github.com/josemagalan/genetic-algorithms-lab-book) |

El libro está en versión beta: su contenido y estructura pueden cambiar. / The book, in Spanish, is in beta: its content and structure may change.
<!-- ga-series-links:end -->

## Qué hay ahora

| Capítulo | Estado |
|---|---|
| Cómo leer este libro | Borrador |
| Índice general | Generado (`filtros/indices.py`) |
| 1. Evolución y optimización | Revisado (20 de octubre de 2026) |
| 2. El ciclo y las decisiones de diseño | Revisado (21 de octubre de 2026) |
| 3. Representar soluciones | Borrador completo, pendiente de revisión |
| 4. Inicializar y evaluar | Borrador completo, pendiente de revisión |
| 5. Seleccionar a los padres | Borrador completo, en revisión |
| 6. Cruzar | Borrador completo, en revisión |
| 7. Mutar | Borrador completo, en revisión |
| 8. Reemplazar y parar | Borrador completo, pendiente de revisión |
| 9. Parámetros y aleatoriedad | Borrador completo, pendiente de revisión |
| 10. El viajante de principio a fin | Borrador completo, pendiente de revisión |
| 11. Recapitulación | Borrador completo, pendiente de revisión |
| Índice de actividades | Generado (`filtros/indices.py`) |
| Agradecimientos y avisos | Texto aprobado |

El resto de capítulos está en preparación.

## Cómo está hecho

- Libro de [Quarto](https://quarto.org) (`_quarto.yml`); cada capítulo es un archivo `.qmd`.
- Cada capítulo combina explicaciones, ejemplos reproducibles que abren la herramienta en un estado fijado, instrucciones para explorar en la aplicación y ejercicios. Las secciones se marcan por nivel: Básico, Avanzado y Para saber más.
- La numeración es automática. Quarto numera capítulos, secciones y figuras (`number-sections`), y las referencias se escriben con su identificador: `sección -@sec-cruce-ox`, `figura -@fig-mapa`, `capítulo -@sec-cruce`. Los ejemplos y ejercicios llevan el número de su sección (el ejemplo 5.3 está en la sección 5.3); en su título no se escribe el número, y se citan con un enlace vacío: `ejemplo [](#ejemplo-seleccion-ruleta)`. Para el número de capítulo de una sección concreta: `capítulo [](#sec-cruce-permutaciones){.capitulo}`. Los rellena `filtros/numeracion.lua` con los números que calcula `filtros/indices.py` en el *pre-render* (`_numeracion.json`, que no se versiona).
- `indice.qmd` (índice general) y `actividades.qmd` (índice de actividades) también los genera `filtros/indices.py` en cada `quarto render`, a partir de los encabezados de sección y de las cajas de los capítulos. No se editan a mano.
- Bibliografía en `referencias.bib`, con estilo APA en castellano (`vendor/csl/`).
- Sin dependencias externas en la página: KaTeX va en local (`vendor/katex/`).
- Al hacer *push* a `main`, GitHub Actions genera el libro y lo publica en GitHub Pages (`.github/workflows/publish.yml`).
- `comprobaciones/` guarda la versión revisada de cada herramienta y un guion que avisa si una herramienta cambia o si el libro pide un valor que sus controles no permiten; lo ejecuta `.github/workflows/comprobar.yml` en cada *push* y cada lunes (`comprobaciones/LEEME.md`).

Para generarlo en local hacen falta Quarto (≥ 1.10) y Python 3:

```bash
quarto render      # resultado en _book/
quarto preview     # vista previa que se actualiza al guardar
```

Las figuras propias están en `figuras/`, junto al guion de Python que las genera. Los SVG se versionan, así que para generar el libro no hace falta ejecutar los guiones. Para regenerar una figura, se ejecuta su guion desde `figuras/` (por ejemplo, `python3 03-representacion.py`). Casi todos usan solo la biblioteca estándar; `03-himmelblau.py` necesita además matplotlib y NumPy.

## Comentarios

Cada página del libro tiene el enlace «Enviar un comentario sobre esta página», que abre un formulario de GitHub (`.github/ISSUE_TEMPLATE/comentario.yml`) con la página, el capítulo y la versión ya rellenos, y distingue errata, resultado distinto, problema de uso y sugerencia. Quien no use GitHub puede escribir a los autores a través de sus páginas (página «Agradecimientos y avisos», apartado «Comentarios y contacto»).

## Autores

- [José Manuel Galán](https://sites.google.com/site/josemagalan/), Universidad de Burgos.
- [Silvia Díaz-de la Fuente](https://produccioncientifica.usal.es/investigadores/2300823/detalle), Universidad de Salamanca.
- [Virginia Ahedo](https://investigacion.ubu.es/investigadores/34947/detalle), Universidad de Burgos.
- [María Pereda](https://portalcientifico.upm.es/es/ipublic/researcher/331932), Universidad Politécnica de Madrid.
- [José Ignacio Santos](https://investigacion.ubu.es/investigadores/35543/detalle), Universidad de Burgos.

## Agradecimientos y uso de IA

Los autores agradecen el apoyo del plan Claude Team para científicos de Anthropic. En la elaboración de este material se han utilizado asistentes de inteligencia artificial; los contenidos originales son obra de los autores, que revisan, corrigen y verifican todos los materiales y son los responsables de la publicación; en esta versión beta, esa revisión sigue en curso. El texto completo está en la página «Agradecimientos y avisos» del libro.

## Licencia

- Texto, figuras propias y ejercicios: [CC BY 4.0](LICENSE-CONTENT.md).
- Código (guiones de `figuras/`, `filtros/`, `comprobaciones/` y `comentarios.js`): [MIT](LICENSE).
- Los componentes de terceros conservan su licencia: las imágenes de terceros de `figuras/` (ficha en `figuras/01-imagenes.md`), KaTeX (MIT, `vendor/katex/LICENSE`) y el estilo APA de CSL (CC BY-SA 3.0, `vendor/csl/LEEME.md`).
- La licencia del portal no se extiende al libro ni a las herramientas: cada recurso indica la suya.
