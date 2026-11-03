# Códigos QR del PDF

Desde la versión 1.1 (D100), el PDF lleva un código QR junto a cada enlace a una aplicación: los
«Abrir», «Abrir y configurar» y «Explorar», los enlaces del texto a una variante concreta y las
herramientas de la línea «Herramientas» de cada capítulo. Las portadas de las herramientas que
aparecen en el texto no llevan código.

Cada código contiene una dirección corta, `base + clave`, y la web la redirige a la aplicación:

- español: `https://josemagalan.github.io/genetic-algorithms-lab-book/a/<clave>`
- inglés: `https://josemagalan.github.io/genetic-algorithms-lab-book/en/a/<clave>`

La clave es el número de la sección (o del capítulo, para la línea «Herramientas») seguido de una
letra por enlace distinto: `4.6a`, `4.6b`, `4a`. Se omiten la i, la l y la o, que en papel se
confunden con 1 y 0.

## Registro

`claves.json` guarda, por edición, la base y el destino de cada clave. Es un registro acumulativo:

- **Una clave publicada no se borra ni cambia de destino**, aunque el enlace desaparezca del libro
  o se renumere su sección: puede haber ejemplares impresos con ella.
- Si un enlace sigue en la misma sección, el generador reutiliza su clave.
- Un enlace nuevo, o uno que cambia de destino o de sección, recibe la primera letra libre de su
  sección. `pdf/generar.py` se detiene si encuentra claves sin registrar; con `--registrar-qr` las
  añade a `claves.json`, que después se confirma con un commit antes de generar el PDF definitivo.
- Si una aplicación cambia sus direcciones, se corrige aquí el destino de la clave afectada: es la
  única excepción a la regla anterior, porque mantiene el sentido de la clave impresa.

`bilingue/generar.py` publica una página de redirección por clave en `site/a/` y `site/en/a/`, y
`bilingue/comprobar.py` comprueba que existen todas y que llevan a su destino.
