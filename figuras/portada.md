# Portada: laboratorio de experimentación

## Archivos y regeneración

- `portada.svg`: composición vertical, proporción 2:3, espacio de diseño de 1200 × 1800 unidades.
- `portada-horizontal.svg`: adaptación horizontal, 1800 × 1000 unidades.
- `portada.py`: fuente reproducible, solo con la biblioteca estándar de Python 3.

Desde la raíz del repositorio:

```sh
python figuras/portada.py
```

Los SVG son autónomos: sin imágenes enlazadas, JavaScript ni fuentes descargadas.
El texto permanece editable. Se utiliza Arial, con alternativas Helvetica y sans-serif;
los caracteres binarios emplean Consolas o monospace. La tipografía puede variar
si esas fuentes no están instaladas en el sistema que abre el SVG.

## Concepto y procedencia

La portada vertical se incorpora a la página inicial mediante `book.cover-image`
y `book.cover-image-alt` en `_quarto.yml`. Su tamaño adaptable se define con
`img.quarto-cover-image` en `estilos.css`. El título, autores y enlaces de contacto
del libro se mantienen también como texto HTML accesible.

Ilustración editorial original preparada con asistencia de Codex el 21 de octubre
de 2026, a partir de la orientación de José Manuel Galán: mostrar el laboratorio
interactivo como rasgo diferencial del libro.

La composición conecta tres acciones: configurar, experimentar y comparar.
Retoma el verde `#0f6e56` y el morado `#4a3f9e` utilizados en el libro. El título
completo y los cinco nombres proceden de los metadatos del libro, conservando
su orden. No se ha reproducido ninguna captura ni ilustración de terceros.

Los controles y gráficas son esquemáticos. Las curvas no representan datos,
una herramienta concreta ni una comparación real de parámetros o algoritmos.
El gráfico de cadenas sí representa un cruce coherente: padres `10110110` y
`01001001`, corte después de la tercera posición, hijos `10101001` y `01010110`;
en el segundo hijo se invierte el sexto bit para obtener `01010010`. El contorno
oscuro señala ese bit. La disposición y los controles no pretenden reproducir
exactamente la interfaz de ninguna herramienta.

## Licencia

La ilustración se ofrece bajo CC BY 4.0, como el contenido propio del libro
(`LICENSE-CONTENT.md`). El guion está bajo MIT, como el código del repositorio
(`LICENSE`). Las fuentes del sistema no se distribuyen con estos archivos.
