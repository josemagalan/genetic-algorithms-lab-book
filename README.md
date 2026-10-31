# Evolución a la vista

*Algoritmos genéticos en un laboratorio interactivo*

> **Versión 1.0, revisada el 31 de octubre de 2026** (primera publicación: 7 de octubre de 2026). La versión y la fecha de revisión están en `_quarto.yml` (`libro-version` y `libro-revision`).

Libro para aprender algoritmos genéticos de forma práctica, con actividades sobre las herramientas interactivas del [Laboratorio de algoritmos genéticos](https://josemagalan.github.io/genetic-algorithms-lab/) (*genetic-algorithms-lab*). Está pensado para estudiantes de grado que empiezan.

**Versión para leer:** <https://josemagalan.github.io/genetic-algorithms-lab-book/>

## Cómo citar

Galán, J. M., Díaz-de la Fuente, S., Ahedo, V., Pereda, M., y Santos, J. I. (2026). *Evolución a la vista. Algoritmos genéticos en un laboratorio interactivo* (versión 1.0). Zenodo. DOI: [10.5281/zenodo.23835733](https://doi.org/10.5281/zenodo.23835733).

El DOI identifica esta edición; la web puede incorporar revisiones posteriores. Los metadatos de cita están en [`CITATION.cff`](CITATION.cff). El archivo independiente de la versión 1.0.0 del portal tiene el DOI [10.5281/zenodo.23834485](https://doi.org/10.5281/zenodo.23834485); contiene el portal y su inventario, con enlaces a las herramientas externas.

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

El libro está en español. / The book is in Spanish.
<!-- ga-series-links:end -->

## Qué hay ahora

| Capítulo | Estado |
|---|---|
| Cómo leer este libro | Revisado (31 de octubre de 2026) |
| Índice general | Generado (`filtros/indices.py`) |
| 1. Evolución y optimización | Revisado (20 de octubre de 2026) |
| 2. El ciclo y las decisiones de diseño | Revisado (21 de octubre de 2026) |
| 3. Representar soluciones | Revisado (22 de octubre de 2026) |
| 4. Inicializar y evaluar | Revisado (28 de octubre de 2026) |
| 5. Seleccionar a los padres | Revisado (28 de octubre de 2026) |
| 6. Cruzar | Revisado (28 de octubre de 2026) |
| 7. Mutar | Revisado (28 de octubre de 2026) |
| 8. Reemplazar y parar | Revisado (29 de octubre de 2026) |
| 9. Parámetros y aleatoriedad | Revisado (29 de octubre de 2026) |
| 10. El viajante de principio a fin | Revisado (29 de octubre de 2026) |
| 11. Recapitulación | Revisado (29 de octubre de 2026) |
| Índice de actividades | Generado (`filtros/indices.py`) |
| Agradecimientos y avisos | Texto aprobado |

Los once capítulos están completos y cuentan con la revisión del autor indicada en la tabla. El 29 de octubre se incorporó una revisión docente de precisión y coherencia; «Cómo leer este libro» se amplió el 31 de octubre.

## Cómo está hecho

- Libro de [Quarto](https://quarto.org) (`_quarto.yml`); cada capítulo es un archivo `.qmd`.
- Cada capítulo combina explicaciones, ejemplos reproducibles que abren la herramienta en un estado fijado, instrucciones para explorar en la aplicación y ejercicios. Las secciones se marcan por nivel: Básico, Avanzado y Para saber más.
- La numeración es automática. Quarto numera capítulos, secciones y figuras (`number-sections`), y las referencias se escriben con su identificador: `sección -@sec-cruce-ox`, `figura -@fig-mapa`, `capítulo -@sec-cruce`. Los ejemplos y ejercicios llevan el número de su sección (el ejemplo 5.3 está en la sección 5.3); en su título no se escribe el número, y se citan con un enlace vacío: `ejemplo [](#ejemplo-seleccion-ruleta)`. Para el número de capítulo de una sección concreta: `capítulo [](#sec-cruce-permutaciones){.capitulo}`. Los rellena `filtros/numeracion.lua` con los números que calcula `filtros/indices.py` en el *pre-render* (`_numeracion.json`, que no se versiona).
- `indice.qmd` (índice general) y `actividades.qmd` (índice de actividades) también los genera `filtros/indices.py` en cada `quarto render`, a partir de los encabezados de sección y de las cajas de los capítulos. No se editan a mano.
- Bibliografía en `referencias.bib`, con estilo APA en castellano (`vendor/csl/`).
- Sin dependencias externas en la página: KaTeX va en local (`vendor/katex/`).
- Al hacer *push* a `main`, GitHub Actions genera el libro y lo publica en GitHub Pages (`.github/workflows/publish.yml`).
- `comprobaciones/` guarda la versión revisada de cada herramienta y un guion que avisa si una herramienta cambia o si el libro pide un valor que sus controles no permiten; lo ejecuta `.github/workflows/comprobar.yml` en cada *push* y cada lunes (`comprobaciones/LEEME.md`).
- `.github/workflows/verificar-html.yml` comprueba además el HTML y una muestra de actividades en Chromium. Verifica la navegación del recorrido básico, el ciclo bilingüe, los enlaces al libro y resultados de selección, OX y siembra. Las instrucciones locales y los límites están en `comprobaciones/LEEME.md`.

Para generarlo en local hacen falta Quarto (≥ 1.10) y Python 3:

```bash
quarto render      # resultado en _book/
quarto preview     # vista previa que se actualiza al guardar
```

La edición en PDF se genera desde estas mismas fuentes con `pdf/generar.py`: la web se imprime en Chromium con una hoja de estilo de impresión que traslada las soluciones al final de cada capítulo, añade portada, créditos e índice con páginas y comprueba el resultado. Requisitos e instrucciones en [`pdf/LEEME.md`](pdf/LEEME.md).

Las figuras propias están en `figuras/`, junto al guion de Python que las genera. Los SVG se versionan, así que para generar el libro no hace falta ejecutar los guiones. Para regenerar una figura, se ejecuta su guion desde `figuras/` (por ejemplo, `python3 03-representacion.py`). Casi todos usan solo la biblioteca estándar; `03-himmelblau.py` necesita además matplotlib y NumPy.

La [portada vectorial](figuras/portada.svg) aparece en la página inicial del libro. Su [guion editable](figuras/portada.py) genera también una [adaptación horizontal](figuras/portada-horizontal.svg); la [ficha de la portada](figuras/portada.md) explica cómo regenerarla y su licencia.

## Comentarios

Cada página del libro tiene el enlace «Enviar un comentario sobre esta página», que abre un formulario de GitHub (`.github/ISSUE_TEMPLATE/comentario.yml`) con la página, el capítulo y la versión ya rellenos, y distingue errata, resultado distinto, problema de uso y sugerencia. Quien no use GitHub puede escribir a los autores a través de sus páginas (página «Agradecimientos y avisos», apartado «Comentarios y contacto»).

## Autores

- [José Manuel Galán](https://sites.google.com/site/josemagalan/)\*. ORCID: [0000-0003-3360-7602](https://orcid.org/0000-0003-3360-7602). Departamento de Ingeniería de Organización, Escuela Politécnica Superior, Universidad de Burgos. Edificio A1, Avda. Cantabria s/n, 09006 Burgos, España.
- [Silvia Díaz-de la Fuente](https://produccioncientifica.usal.es/investigadores/2300823/detalle). ORCID: [0000-0002-5961-3368](https://orcid.org/0000-0002-5961-3368). Departamento de Cartografía e Ingeniería del Terreno, Escuela Politécnica Superior de Ávila, Universidad de Salamanca. Hornos Caleros 50, 05003 Ávila, España.
- [Virginia Ahedo](https://investigacion.ubu.es/investigadores/34947/detalle). ORCID: [0000-0002-9812-388X](https://orcid.org/0000-0002-9812-388X). Departamento de Ingeniería de Organización, Escuela Politécnica Superior, Universidad de Burgos. Edificio A1, Avda. Cantabria s/n, 09006 Burgos, España.
- [María Pereda](https://portalcientifico.upm.es/es/ipublic/researcher/331932). ORCID: [0000-0002-6151-1176](https://orcid.org/0000-0002-6151-1176). Grupo de investigación Ingeniería de Organización y Logística (IOL), Escuela Técnica Superior de Ingenieros Industriales, Universidad Politécnica de Madrid. C/ José Gutiérrez Abascal 2, 28006 Madrid, España; y Grupo Interdisciplinar de Sistemas Complejos, Madrid, España.
- [José Ignacio Santos](https://investigacion.ubu.es/investigadores/35543/detalle). ORCID: [0000-0002-6653-043X](https://orcid.org/0000-0002-6653-043X). Departamento de Ingeniería de Organización, Escuela Politécnica Superior, Universidad de Burgos. Edificio A1, Avda. Cantabria s/n, 09006 Burgos, España.

\* Autor de correspondencia.

## Agradecimientos y uso de IA

Los autores agradecen el apoyo del plan Claude Team para científicos de Anthropic. En la elaboración de este material se han utilizado asistentes de inteligencia artificial; los contenidos originales son obra de los autores, que revisan, corrigen y verifican todos los materiales y son los responsables de la publicación. El texto completo está en la página «Agradecimientos y avisos» del libro.

## Licencia

- Texto, figuras propias y ejercicios: [CC BY 4.0](LICENSE-CONTENT.md).
- Código (guiones de `figuras/`, `filtros/`, `comprobaciones/`, `pdf/` y `comentarios.js`): [MIT](LICENSE).
- Los componentes de terceros conservan su licencia: las imágenes de terceros de `figuras/` (ficha en `figuras/01-imagenes.md`), KaTeX (MIT, `vendor/katex/LICENSE`), la tipografía Noto Sans del PDF (SIL OFL 1.1, `pdf/fuentes/OFL-NotoSans.txt`) y el estilo APA de CSL (CC BY-SA 3.0, `vendor/csl/LEEME.md`).
- La licencia del portal no se extiende al libro ni a las herramientas: cada recurso indica la suya.
