/*
 * «Enviar un comentario sobre esta página» (revisión beta, M06).
 * Abre el formulario de GitHub con la página, el capítulo y la versión ya rellenos
 * (.github/ISSUE_TEMPLATE/comentario.yml). Para quien no use GitHub, enlaza con los autores
 * (avisos.html#contacto). Sin peticiones externas al cargar la página.
 */
(function () {
  'use strict';
  var REPO = 'https://github.com/josemagalan/genetic-algorithms-lab-book';
  var meta = document.querySelector('meta[name="libro-version"]');
  var version = meta ? meta.content : '';
  var h1 = document.querySelector('h1.title');
  var capitulo = (h1 ? h1.textContent : document.title).replace(/\s+/g, ' ').trim();

  function urlFormulario() {
    var p = new URLSearchParams();
    p.set('template', 'comentario.yml');
    p.set('title', '[' + capitulo + '] ');
    p.set('pagina', location.origin + location.pathname + location.hash);
    p.set('capitulo', capitulo);
    p.set('version', version);
    return REPO + '/issues/new?' + p.toString();
  }

  function enlace(texto, href, clase) {
    var a = document.createElement('a');
    a.textContent = texto;
    a.href = href;
    if (clase) a.className = clase;
    return a;
  }

  function formulario(clase) {
    var a = enlace('Enviar un comentario sobre esta página', urlFormulario(), clase);
    a.target = '_blank';
    a.rel = 'noopener';
    // La sección visible puede cambiar: se recalcula al pulsar.
    a.addEventListener('click', function () { a.href = urlFormulario(); });
    return a;
  }

  // Junto a «Editar esta página»: en el índice lateral y, en pantallas pequeñas, al pie.
  document.querySelectorAll('.toc-actions ul').forEach(function (lista) {
    var li = document.createElement('li');
    var a = formulario('toc-action');
    var icono = document.createElement('i');
    icono.className = 'bi empty'; // mismo sangrado que «Ver el código»
    a.insertBefore(icono, a.firstChild);
    li.appendChild(a);
    lista.appendChild(li);
  });

  // Al final del contenido, también visible en pantallas pequeñas.
  var main = document.querySelector('main#quarto-document-content') || document.querySelector('main');
  if (main) {
    var p = document.createElement('p');
    p.className = 'comentario-pagina';
    p.appendChild(document.createTextNode('¿Has visto una errata o un resultado distinto? '));
    p.appendChild(formulario());
    p.appendChild(document.createTextNode(' (con una cuenta de GitHub) o '));
    p.appendChild(enlace('escribe a los autores', 'avisos.html#contacto'));
    p.appendChild(document.createTextNode('.'));
    main.appendChild(p);
  }
})();
