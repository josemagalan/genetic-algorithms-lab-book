# Sitio bilingüe

Generación local y publicación de las ediciones española e inglesa.
Fuentes inglesas en `en/`; español 1.0 como original fijo de la traducción.

Desde la raíz del repositorio:

```text
python bilingue/generar.py --quarto RUTA_AL_EJECUTABLE --salida CARPETA_NUEVA
```

Requiere Python 3 y Quarto 1.10.19; no necesita paquetes Python adicionales.
La salida debe ser nueva: ninguna ejecución previa se borra ni se sobrescribe.

Antes de publicar, comprobar el cotejo y el sitio generado:

```text
python bilingue/verificar.py --informe cotejo-ingles.json
python bilingue/comprobar.py --site CARPETA_NUEVA/site --informe CARPETA_NUEVA/comprobacion.json
```

GitHub Pages ejecuta estos pasos y publica `site/`, con el español en raíz y el
inglés bajo `/en/`. El checkout de CI incluye las etiquetas para poder exportar
la edición española original `v1.0`.

- Exporta HEAD para la vista española y `v1.0` para la base de la traducción.
- Superpone los `.qmd` ingleses en una copia temporal y aplica el perfil inglés.
- Calcula la numeración completa antes de preparar páginas de acceso al español
  para los capítulos aún no traducidos. `en/traduccion.json` declara los incluidos.
- Deriva variantes inglesas de los SVG desde los originales y `en/figuras.json`:
  sustituye solo texto y comprueba que geometría, atributos y estructura coinciden.
- Superpone las portadas inglesas de `en/figuras/` únicamente en la copia inglesa.
  Se regeneran con `python en/figuras/portada.py`; su ficha documenta procedencia,
  licencia y conservación del panel de la portada española.
- Genera índices ingleses solo para las actividades traducidas, localiza las
  plantillas y los comentarios y crea una variante inglesa del CSL compartido.
- Toma `referencias.bib` y `vendor/csl/apa.csl` de la copia de trabajo, no de la
  etiqueta fuente, para que sus correcciones lleguen a la edición inglesa. En la
  copia inglesa, el número de artículo «Artículo 72» del `.bib` pasa a «Article 72».
- Ensambla `site/` (español) y `site/en/` (traducción), con selector de edición
  estático y conservación del ancla cuando existe el capítulo equivalente.
- Guarda fuentes de partida, registros de Quarto, versiones, hashes y ZIP HTML.

Abrir `site/en/index.html` o servir `site/` con un servidor HTTP local.
Los directorios `trabajo/` son derivados, nunca una segunda fuente editorial.

El autor valoró favorablemente el piloto y encargó continuar con una pasada de
naturalidad por capítulo. Después del pulido, ejecutar el cotejo:

```text
python bilingue/verificar.py --informe RUTA_AL_INFORME_JSON
```

La revisión del asistente no sustituye una revisión humana independiente. La
traducción conserva sus avisos de IA y de revisión pendiente al publicarse en HTML.
Los enlaces del portal ofrecen ambas ediciones. No se asigna un DOI propio
ni se usa el DOI español como si identificara la traducción.
