# Algoritmos genéticos, paso a paso

> **Estado: en construcción (work in progress).** Borrador de trabajo de los autores, todavía sin revisar. El contenido, la estructura y el índice pueden cambiar.

Libro para aprender algoritmos genéticos de forma práctica, con actividades sobre las herramientas interactivas del portal [genetic-algorithms-lab](https://josemagalan.github.io/genetic-algorithms-lab/). Está pensado para estudiantes de grado que empiezan.

**Versión para leer:** <https://josemagalan.github.io/genetic-algorithms-lab-book/>

## Qué hay ahora

| Capítulo | Estado |
|---|---|
| Cómo leer este libro | Borrador |
| 6. Seleccionar a los padres | Borrador completo, en revisión |
| Agradecimientos y avisos | Texto aprobado |

El resto de capítulos está en preparación.

## Cómo está hecho

- Libro de [Quarto](https://quarto.org) (`_quarto.yml`); cada capítulo es un archivo `.qmd`.
- Cada capítulo combina explicaciones, ejemplos reproducibles que abren la herramienta en un estado fijado, instrucciones para explorar en la aplicación y ejercicios. Las secciones se marcan por nivel: Básico, Avanzado y Para saber más.
- Bibliografía en `referencias.bib`, con estilo APA en castellano (`vendor/csl/`).
- Sin dependencias externas en la página: KaTeX va en local (`vendor/katex/`).
- Al hacer *push* a `main`, GitHub Actions genera el libro y lo publica en GitHub Pages (`.github/workflows/publish.yml`).

Para generarlo en local hacen falta Quarto (≥ 1.10) y Python 3:

```bash
quarto render      # resultado en _book/
quarto preview     # vista previa que se actualiza al guardar
```

## Comentarios

Cada página del libro tiene enlaces «Informar sobre problema» y «Editar esta página». Los comentarios sobre el texto pueden abrirse como *issues*.

## Autores

José Manuel Galán, Silvia Díaz-de la Fuente, Virginia Ahedo, María Pereda y José Ignacio Santos.

## Agradecimientos y uso de IA

Los autores agradecen el apoyo del plan Claude Team para científicos de Anthropic. En la elaboración de este material se han utilizado asistentes de inteligencia artificial; los contenidos originales son obra de los autores, que han revisado, corregido y verificado todos los materiales y son los responsables de la publicación. El texto completo está en la página «Agradecimientos y avisos» del libro.

## Licencia

Pendiente de decidir. Los componentes de terceros conservan su licencia: KaTeX (MIT, `vendor/katex/LICENSE`) y el estilo APA de CSL (CC BY-SA 3.0, `vendor/csl/LEEME.md`).
