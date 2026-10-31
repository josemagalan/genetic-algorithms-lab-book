'use strict';
// Transformaciones de impresión por archivo, en el DOM temporal de Chromium.
// Generaliza adaptar.cjs y la parte de crear.cjs del cierre del piloto (capítulo 10) a todo el libro.
// Nunca modifica el HTML web ni los .qmd.

// Se ejecuta dentro de la página de cada archivo HTML del libro ya cargado (KaTeX renderizado).
function adaptarArchivo(args) {
  const {key, file, fileMap, replaced, origin, substitutions, isChapter} = args;
  const main = document.querySelector('main');
  const stats = {key, file};

  // 1. Sustituciones exclusivas del PDF (textos que describen la interfaz web).
  let html = main.innerHTML;
  stats.substitutions = 0;
  for (const s of substitutions || []) {
    const n = html.split(s.buscar).length - 1;
    if (n !== 1) throw Error(`${file}: «${s.buscar.slice(0, 60)}…» aparece ${n} veces; revisar textos-impresion.json`);
    html = html.replace(s.buscar, s.poner); stats.substitutions++;
  }
  if (stats.substitutions) main.innerHTML = html;

  // 2. Material exclusivo de la web: incrustaciones, ampliar figura, comentarios.
  stats.webOnlyRemoved = main.querySelectorAll('.incrustada').length;
  main.querySelectorAll('.incrustada,.ampliar-figura,.quarto-comment-link,.comentario-pagina,script,img.quarto-cover-image').forEach(n => {
    const p = n.parentElement; n.remove();
    if (p && p.tagName === 'P' && !p.textContent.trim() && !p.querySelector('img,svg')) p.remove();
  });
  main.querySelectorAll('a[href*="issues/new"]').forEach(a => { const p = a.closest('p'); if (p) p.remove(); else a.remove(); });
  main.querySelectorAll('iframe').forEach(f => { const a = document.createElement('a'); a.href = f.src; a.textContent = 'Abrir la aplicación en la web'; f.replaceWith(a); });

  // 3. Título: se sustituye el bloque de Quarto por una cabecera propia de capítulo.
  const header = main.querySelector('#title-block-header');
  const h1 = header?.querySelector('h1');
  const number = h1?.querySelector('.chapter-number')?.textContent.trim() || null;
  let title = h1?.querySelector('.chapter-title')?.textContent.trim() || h1?.textContent.trim() || '';
  const firstLevel1 = main.querySelector(':scope > section.level1');
  if (!number && firstLevel1?.querySelector(':scope > h1')) {
    title = firstLevel1.querySelector(':scope > h1').textContent.trim();
    firstLevel1.querySelector(':scope > h1').remove();
  }
  // Los identificadores del bloque de título (p. ej. #sec-ciclo) se conservan como anclas.
  const headerIds = header ? [...header.querySelectorAll('[id]')].map(e => e.id).filter(id => id !== 'title-block-header') : [];
  header?.remove();

  // 4. Desplegables: se abren y se rotulan como en el piloto.
  const rename = {'Ver el resultado': 'Resultado', 'Ver la solución': 'Solución', 'Ver los datos de la figura': 'Datos de la figura'};
  main.querySelectorAll('details').forEach(d => {
    d.open = true;
    const s = d.querySelector(':scope > summary');
    if (s) {
      const t = s.textContent.replace(/\s+/g, ' ').trim(); s.dataset.original = t;
      // «Ver el resultado» → «Resultado»; en general se quita el verbo de la interfaz web.
      const label = rename[t] || (/^Ver /.test(t) ? t.replace(/^Ver (el |la |los |las )?/, '') : null);
      if (label) s.textContent = label.charAt(0).toUpperCase() + label.slice(1);
    }
  });

  // 5. Cabeceras de cajas → rótulo explícito.
  main.querySelectorAll('.callout').forEach(box => {
    const head = box.querySelector(':scope > .callout-header');
    if (!head) return;
    const text = (head.querySelector('.callout-title-container') || head).cloneNode(true);
    text.querySelectorAll('.screen-reader-only,.visually-hidden,.callout-icon-container,.callout-icon,[aria-hidden="true"]').forEach(n => n.remove());
    const t = document.createElement('p'); t.className = 'pdf-box-title'; t.append(...text.childNodes); head.replaceWith(t);
  });

  // 6. Soluciones de los ejercicios al final del capítulo, con enlaces de ida y vuelta.
  stats.solutionsMoved = 0; stats.exercises = main.querySelectorAll('.ejercicio').length; stats.exercisesWithoutSolution = [];
  if (isChapter) {
    const appendix = document.createElement('section');
    appendix.id = 'soluciones-ejercicios'; appendix.className = 'level2 unnumbered pdf-solutions';
    appendix.innerHTML = '<h2 class="unnumbered">Soluciones de los ejercicios</h2><p>Intenta resolver cada ejercicio antes de consultar su solución. Los enlaces permiten volver al enunciado.</p>';
    let auto = 0;
    main.querySelectorAll('.ejercicio').forEach(box => {
      if (!box.id) box.id = 'ejercicio-auto-' + (++auto);
      const titleText = box.querySelector('.pdf-box-title')?.textContent || '';
      const number = titleText.match(/Ejercicio\s+(\d+\.\d+)/)?.[1];
      if (!number) throw Error(`${file}: ejercicio sin número (${box.id})`);
      const details = [...box.querySelectorAll('details')].find(d => d.querySelector(':scope > summary')?.dataset.original === 'Ver la solución');
      if (!details) { stats.exercisesWithoutSolution.push(number); return; }
      const id = 'pdf-solucion-' + box.id;
      const solved = document.createElement('div');
      solved.className = 'callout callout-note pdf-solution'; solved.id = id;
      const t = document.createElement('h3'); t.className = 'pdf-box-title'; t.textContent = 'Solución del ejercicio ' + number;
      solved.append(t);
      details.querySelector(':scope > summary')?.remove();
      solved.append(...details.childNodes);
      const back = document.createElement('p'); back.className = 'pdf-return';
      const a = document.createElement('a'); a.href = '#' + box.id; a.textContent = 'Volver al ejercicio ' + number;
      back.append(a); solved.append(back); appendix.append(solved);
      const fwd = document.createElement('p'); fwd.className = 'pdf-solution-link';
      const l = document.createElement('a'); l.href = '#' + id; l.textContent = 'Consultar la solución del ejercicio ' + number + ' al final del capítulo';
      fwd.append(l); details.replaceWith(fwd); stats.solutionsMoved++;
    });
    if (stats.solutionsMoved) {
      const refs = main.querySelector('#refs')?.closest('section') ||
        [...main.querySelectorAll(':scope > section')].find(s => /Referencias del capítulo/.test(s.querySelector('h2')?.textContent || ''));
      if (refs && refs !== main) refs.before(appendix); else main.append(appendix);
    }
  }

  // 7. details restantes → bloques ordinarios (Chromium no los fragmenta bien).
  stats.resultsFlattened = 0;
  main.querySelectorAll('details').forEach(d => {
    const block = document.createElement('div'); block.className = 'pdf-details'; if (d.id) block.id = d.id;
    const s = d.querySelector(':scope > summary');
    if (s) { const p = document.createElement('p'); p.className = 'pdf-result-title'; p.append(...s.childNodes); s.replaceWith(p); }
    block.append(...d.childNodes); d.replaceWith(block); stats.resultsFlattened++;
  });

  // 8. Texto suelto que Pandoc deja al final de <details> → párrafos (piloto).
  stats.paragraphsWrapped = 0;
  const blockTags = new Set(['P','UL','OL','TABLE','DIV','SECTION','H1','H2','H3','H4','FIGURE','DETAILS','BLOCKQUOTE','PRE']);
  main.querySelectorAll('.pdf-details,.pdf-solution').forEach(container => {
    let run = [];
    const flush = before => {
      if (run.some(n => n.textContent.trim())) {
        const p = document.createElement('p'); container.insertBefore(p, before); run.forEach(n => p.append(n)); stats.paragraphsWrapped++;
      }
      run = [];
    };
    [...container.childNodes].forEach(n => {
      if (n.nodeType === Node.ELEMENT_NODE && blockTags.has(n.tagName)) flush(n);
      else if (n.nodeType !== Node.COMMENT_NODE) run.push(n);
    });
    flush(null);
  });

  // 9. Fórmulas en línea cortas, enteras (heurística del piloto: hasta 35 caracteres de TeX).
  stats.shortMath = 0;
  main.querySelectorAll('.math.inline').forEach(m => {
    const tex = m.querySelector('annotation[encoding="application/x-tex"]')?.textContent || '';
    if (tex.length <= 35) { m.classList.add('pdf-short-math'); stats.shortMath++; }
  });

  // 10. Tablas: magnitudes a la derecha; identificadores centrados; anchos probados en el capítulo 10.
  stats.tables = [];
  main.querySelectorAll('table').forEach(table => {
    if (table.closest('.pdf-toc')) return;
    const headers = [...table.querySelectorAll('thead th')].map(th => th.textContent.trim());
    const rows = [...table.querySelectorAll('tbody tr')];
    const numeric = [], identifiers = [];
    headers.forEach((h, i) => {
      const cells = rows.map(r => r.children[i]).filter(Boolean);
      const values = cells.map(c => c.textContent.trim()).filter(v => v && v !== '—');
      const mark = cls => { cells.forEach(c => c.classList.add(cls)); table.querySelectorAll('thead tr').forEach(r => r.children[i]?.classList.add(cls)); };
      // Cadenas de bits (0101, 1 0 1 1…) son identificadores, no magnitudes: no se alinean a la derecha.
      if (/^(Cromosoma|Contendientes)$/.test(h) || (values.length && values.every(v => /^[01](\s?[01]){2,}$/.test(v)))) { identifiers.push(i); mark('pdf-id'); }
      else if (values.length && values.every(v => /^[+−\-\d\s.,()%/]+$/.test(v) || /^\d+ de \d+$/.test(v) || /^\d+ \(valor inicial\)$/.test(v))) { numeric.push(i); mark('pdf-num'); }
    });
    let widths;
    if (headers[0] === 'Cruce' && headers[1] === 'Mutación') widths = [29, 17, 22, 14, 18];
    else if (headers[0] === 'Configuración' && headers.length === 4) widths = [38, 24, 18, 20];
    else if (headers[0] === 'Configuración D') widths = [35, 25, 20, 20];
    // Los anchos de Quarto salen de los guiones de las tablas Markdown y no de su contenido
    // (p. ej., 35 % para la columna «Dónde» en 11.1): en papel se deja el reparto automático.
    if (!widths) { if (table.querySelector('colgroup')) stats.colgroupsRemoved = (stats.colgroupsRemoved || 0) + 1; table.querySelectorAll('colgroup').forEach(c => c.remove()); }
    if (widths && widths.length === headers.length) {
      table.querySelectorAll('colgroup').forEach(c => c.remove());
      const g = document.createElement('colgroup');
      widths.forEach(w => { const c = document.createElement('col'); c.style.width = w + '%'; g.append(c); });
      table.prepend(g); table.classList.add('pdf-fixed-table');
    }
    stats.tables.push({headers, numeric, identifiers, widths: widths || null});
  });

  // 11. Identificadores con prefijo del archivo y remisiones resueltas dentro del PDF.
  const pref = id => key + '--' + id;
  main.querySelectorAll('[id]').forEach(e => { e.id = pref(e.id); });
  ['aria-labelledby', 'aria-describedby', 'for', 'headers'].forEach(attr =>
    main.querySelectorAll(`[${attr}]`).forEach(e => e.setAttribute(attr, e.getAttribute(attr).split(/\s+/).map(pref).join(' '))));
  stats.links = {local: 0, crossFile: 0, externalized: 0, external: 0};
  const here = new URL(location.href);
  main.querySelectorAll('a[href]').forEach(a => {
    const href = a.getAttribute('href');
    if (href.startsWith('#')) { a.setAttribute('href', '#' + pref(decodeURIComponent(href.slice(1)))); stats.links.local++; return; }
    if (/^(mailto:|tel:|data:)/.test(href)) return;
    const target = new URL(href, here);
    let bookPath = null;
    if (target.origin === here.origin) bookPath = target.pathname.replace(/^\//, '');
    else if (target.href.startsWith(origin)) bookPath = target.href.slice(origin.length).split(/[?#]/)[0];
    if (bookPath === null) { stats.links.external++; return; }
    const name = bookPath.split('/').pop() || 'index.html';
    const hash = decodeURIComponent(target.hash.slice(1));
    if (name === file && hash) { a.setAttribute('href', '#' + pref(hash)); stats.links.local++; return; }
    if (fileMap[name]) { a.setAttribute('href', '#' + (hash ? fileMap[name] + '--' + hash : fileMap[name])); stats.links.crossFile++; return; }
    if (replaced[name]) { a.setAttribute('href', '#' + replaced[name]); stats.links.crossFile++; return; }
    a.href = origin + bookPath + target.search + target.hash; stats.links.externalized++;
  });
  main.querySelectorAll('a[target]').forEach(a => a.removeAttribute('target'));

  return {number, title, headerIds: headerIds.map(pref), html: main.innerHTML, stats};
}

module.exports = {adaptarArchivo};
