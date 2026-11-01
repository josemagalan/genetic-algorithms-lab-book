# Estilo de citas

- `apa.csl`: APA Style 7th edition, del repositorio oficial de estilos CSL
  (https://github.com/citation-style-language/styles), commit `0151fd1ed467ec54f4f2554d68fce9ccc6ff0118`
  (2026-10-07), copiado el 2026-10-08.
- Licencia: Creative Commons Attribution-ShareAlike 3.0 (indicada en el propio archivo).
- Cambios respecto al original (2026-10-08), permitidos por la licencia, que obliga a compartir igual:
  1. `default-locale="es-ES"`: en un libro de Quarto, citeproc no toma el `lang: es` del proyecto y saldría en inglés («In», «2nd ed.»).
  2. `and="text"` en lugar de `and="symbol"` (40 casos): «y» entre autores, como en las adaptaciones de APA al castellano, en lugar de «&».
  3. En el bloque de locale `es`, `page-range-delimiter` = «–» (raya corta), como en APA; el castellano de pandoc usa «-».
  4. (2026-11-02) Rama propia para `locator="chapter"` en la macro `label-locator`. Con pandoc, las condiciones originales omitían la etiqueta y `[@clave, capítulo 5]` salía «(Autor, año, 5)»; ahora sale «(Autor, año, capítulo 5)», en minúscula como «apartado».
- La variante inglesa `apa-en.csl` la crea `bilingue/generar.py`: revierte los cambios 1 y 2 y pone la etiqueta del cambio 4 con mayúscula inicial, «(Autor, año, Chapter 5)», como «Section 1.2».
- La conjunción «e» ante i-/hi- («Galán e Izquierdo») la pone `filtros/e-ante-i.py` después de generar el HTML.
