'use strict';
// Generador de la edición PDF completa de «Evolución a la vista».
// Ruta: fuentes Quarto → HTML del libro (preparar.py) → adaptación temporal por archivo (adaptar.cjs)
//       → documento único con portada, créditos, índice y capítulos → PDF de Chromium (dos pasadas
//       para numerar el índice) → folios, cabeceras, marcadores y metadatos (posproceso.py).
//
// Uso: node libro.cjs --libro RUTA/_book --trabajo RUTA [--solo c10] [--cuerpo 10.5pt] [--chrome RUTA]
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const {execFileSync} = require('node:child_process');
let playwright;
try { playwright = require(process.env.PLAYWRIGHT_MODULE || 'playwright'); } catch { playwright = require('playwright-core'); }
const {adaptarArchivo} = require('./adaptar.cjs');

const arg = (name, def) => { const i = process.argv.indexOf('--' + name); return i > 0 ? process.argv[i + 1] : def; };
const BOOK = path.resolve(arg('libro'));
const WORK = path.resolve(arg('trabajo'));
const ONLY = arg('solo') ? arg('solo').split(',') : null;
const BODY = arg('cuerpo', '10.5pt');
const PYTHON = arg('python', process.platform === 'win32' ? 'python' : 'python3');
const HERE = __dirname;
const config = JSON.parse(fs.readFileSync(path.join(WORK, 'config.json'), 'utf8'));
const dictionary = JSON.parse(fs.readFileSync(path.join(WORK, 'silabeo.json'), 'utf8'));
const textos = JSON.parse(fs.readFileSync(path.join(HERE, 'textos-impresion.json'), 'utf8'));
const ajustes = JSON.parse(fs.readFileSync(path.join(HERE, 'ajustes.json'), 'utf8'));
let printCss = fs.readFileSync(path.join(HERE, 'impresion.css'), 'utf8') + '\n' + (ajustes.css || []).join('\n');

const mime = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf'};
const server = http.createServer((req, res) => {
  try {
    let p = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    let base = BOOK;
    if (p.startsWith('/pdf-assets/')) { base = HERE; p = p.slice('/pdf-assets'.length); }
    const file = path.resolve(base, '.' + p);
    if (!file.startsWith(base + path.sep) || !fs.existsSync(file)) throw Error();
    res.writeHead(200, {'Content-Type': mime[path.extname(file).toLowerCase()] || 'application/octet-stream'});
    fs.createReadStream(file).pipe(res);
  } catch { res.writeHead(404).end(); }
});

const files = config.files.filter(f => !ONLY || ONLY.includes(f.key));
const fileMap = Object.fromEntries(config.files.map(f => [f.file, f.key]));
// Sin el libro completo, las remisiones a archivos ausentes van a la web.
if (ONLY) for (const f of config.files) if (!ONLY.includes(f.key)) delete fileMap[f.file];
const replaced = ONLY ? {} : config.replaced;
const fecha = new Intl.DateTimeFormat('es-ES', {day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Europe/Madrid'}).format(new Date());

function esc(s) { return String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c])); }

function creditos() {
  const affs = [];
  const authors = config.authors.map(a => {
    const marks = a.affiliations.map(x => { let i = affs.indexOf(x); if (i < 0) { affs.push(x); i = affs.length - 1; } return i + 1; });
    return `<li>${esc(a.name)}<sup>${marks.join(',')}${a.corresponding ? ',*' : ''}</sup></li>`;
  }).join('');
  const short = config.commit.slice(0, 7);
  const sourceLabel = config.cambios_locales?.length ? `base ${short}, con cambios locales` : short;
  const notice = ajustes.borrador ? `<div class="pdf-notice"><p><strong>${esc(ajustes.borrador)}</strong></p><p>Generada el ${fecha} a partir de las fuentes del libro (commit ${short}). Las aplicaciones y la versión web no forman parte del archivo.</p></div>` : '';
  return `<section class="pdf-creditos" id="pdf-creditos">
  <h1>${esc(config.title)}</h1><p class="pdf-subtitulo">${esc(config.subtitle)}</p>
  <ul class="pdf-autores">${authors}</ul>
  <ol class="pdf-filiaciones">${affs.map((x, i) => `<li><sup>${i + 1}</sup> ${esc(x)}</li>`).join('')}</ol>
  ${notice}
  <div class="pdf-legal">
   <p><strong>Versión ${esc(config.version)}</strong>, revisada el ${esc(config.revision)}. Primera publicación en la web: ${new Intl.DateTimeFormat('es-ES', {day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'}).format(new Date(config.first_published))}. Edición en PDF generada el ${fecha} a partir de las mismas fuentes que la web (<a href="${esc(config.repo)}/commit/${config.commit}">${esc(sourceLabel)}</a>).</p>
   ${config.doi ? `<p>DOI de esta edición: <a href="https://doi.org/${esc(config.doi)}">${esc(config.doi)}</a>. ${config.portal_doi ? `Archivo del portal 1.0.0: <a href="https://doi.org/${esc(config.portal_doi)}">${esc(config.portal_doi)}</a>.` : ''}</p>` : ''}
   <p>Este libro se lee junto con el Laboratorio de algoritmos genéticos: los ejemplos y las actividades se hacen con aplicaciones web que el PDF no contiene. Sus enlaces necesitan conexión. Versión interactiva: <a href="${esc(config.site)}">${esc(config.site.replace(/^https:\/\//, '').replace(/\/$/, ''))}</a>. Fuentes: <a href="${esc(config.repo)}">${esc(config.repo.replace(/^https:\/\//, ''))}</a>.</p>
   <p>Texto, figuras propias y ejercicios: licencia <a href="https://creativecommons.org/licenses/by/4.0/deed.es">Creative Commons Atribución 4.0 Internacional (CC BY 4.0)</a>. Código del repositorio: MIT. Las imágenes de terceros, la biblioteca KaTeX, el estilo de citas y las herramientas enlazadas conservan su propia licencia; véase <a href="#avisos--licencia">«Agradecimientos y avisos»</a>. Tipografía: Noto Sans (SIL Open Font License 1.1).</p>
   <p>* Autor de correspondencia. Comentarios y contacto: <a href="#avisos--contacto">«Comentarios y contacto»</a>.</p>
  </div></section>`;
}

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const launch = {headless: true};
  if (arg('chrome')) launch.executablePath = arg('chrome');
  const browser = await playwright.chromium.launch(launch);
  const errors = [];
  try {
    // 1. Adaptación de cada archivo en su propia página (KaTeX y scripts de Quarto ya ejecutados).
    const parts = [];
    for (const f of files) {
      const page = await browser.newPage({viewport: {width: 1280, height: 900}, locale: 'es-ES'});
      page.on('pageerror', e => errors.push(`${f.file}: ${e}`));
      await page.goto(base + f.file, {waitUntil: 'networkidle'});
      await page.evaluate(() => document.fonts.ready);
      await page.waitForFunction(() => [...document.querySelectorAll('main .math')].every(m => m.querySelector('.katex')), null, {timeout: 20000});
      const part = await page.evaluate(adaptarArchivo, {key: f.key, file: f.file, fileMap, replaced, origin: config.site,
        substitutions: textos[f.file] || [], isChapter: /^c\d\d$/.test(f.key)});
      parts.push({...f, ...part});
      await page.close();
      console.log(`${f.file}: ${part.stats.solutionsMoved} soluciones, ${part.stats.resultsFlattened} desplegables, ${part.stats.paragraphsWrapped} párrafos normalizados`);
    }

    // 2. Documento único.
    const page = await browser.newPage({viewport: {width: 1280, height: 900}, locale: 'es-ES'});
    page.on('pageerror', e => errors.push(`libro: ${e}`));
    page.on('console', m => { if (m.type() === 'error') errors.push(`consola: ${m.text()}`); });
    await page.goto(base + 'index.html', {waitUntil: 'networkidle'});
    const leerFinal = textos.pdf_leer_final.replaceAll('{site}', config.site).replaceAll('{site_text}', config.site.replace(/^https:\/\//, '').replace(/\/$/, ''));
    const assembly = await page.evaluate(({parts, creditosHtml, leerFinal, full, dictionary, ajustes}) => {
      document.documentElement.lang = 'es';
      document.title = 'Evolución a la vista';
      document.body.className = 'pdf-body';
      // Quarto fija por guion márgenes y rellenos del cuerpo para su barra de navegación.
      document.body.removeAttribute('style'); document.documentElement.removeAttribute('style');
      document.body.innerHTML = '<main class="content pdf-libro" id="quarto-document-content"></main>';
      // index.html no carga KaTeX (no tiene fórmulas): se añade su hoja de estilo local.
      if (!document.querySelector('link[href*="katex.min.css"]')) {
        const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = 'vendor/katex/katex.min.css'; document.head.append(l);
      }
      const main = document.querySelector('main');
      let html = '';
      if (full) html += `<section class="pdf-portada" id="pdf-portada" aria-label="Portada"></section>` + creditosHtml +
        '<section class="pdf-indice pdf-front" id="pdf-indice"><h1>Índice</h1><ul class="pdf-toc"></ul></section>';
      for (const p of parts) {
        const anchors = p.headerIds.map(id => `<span id="${id}"></span>`).join('');
        const label = p.number ? `<p class="pdf-chapter-label">Capítulo ${p.number}</p>` : '';
        const extra = p.key === 'leer' ? leerFinal : '';
        html += `<section class="pdf-part${p.number ? ' pdf-chapter' : ''}" id="${p.key}" data-key="${p.key}" data-number="${p.number || ''}"><div class="pdf-chapter-head">${anchors}${label}<h1 class="pdf-h1">${p.title}</h1></div>${p.html}${extra}</section>`;
      }
      main.innerHTML = html;

      // Índice con páginas (los números se rellenan en la segunda pasada).
      const toc = main.querySelector('.pdf-toc');
      const entries = [], structure = [];
      const add = (cls, href, num, title, badge) => {
        const li = document.createElement('li'); li.className = cls;
        li.innerHTML = `<a href="#${href}"><span class="toc-num">${num || ''}</span><span class="toc-title"></span><span class="toc-fill"></span><span class="toc-page" data-target="${href}">000</span></a>`;
        li.querySelector('.toc-title').textContent = title;
        if (badge) li.querySelector('.toc-title').append(' ', badge);
        if (!num) li.querySelector('.toc-num').remove();
        toc?.append(li); entries.push(href);
      };
      for (const part of main.querySelectorAll('.pdf-part')) {
        const key = part.dataset.key, number = part.dataset.number;
        const title = part.querySelector('.pdf-h1').textContent.trim();
        const sections = [];
        const level2 = [...part.querySelectorAll('section.level2')].filter(s => s.querySelector(':scope > h2'));
        for (const s of level2) {
          const h2 = s.querySelector(':scope > h2').cloneNode(true);
          const num = h2.querySelector('.header-section-number')?.textContent.trim() || '';
          const nivel = h2.querySelector('.nivel'); let badge = null;
          if (nivel) { badge = nivel.cloneNode(true); badge.classList.add('solo-corto'); badge.querySelector('.largo')?.remove(); }
          h2.querySelectorAll('.header-section-number,.nivel').forEach(n => n.remove());
          sections.push({id: s.id, number: num, title: h2.textContent.replace(/\s+/g, ' ').trim(), level: nivel ? [...nivel.classList].find(c => ['basico', 'avanzado', 'saber-mas'].includes(c)) : null, badge});
        }
        structure.push({key, number, title, sections: sections.map(({badge, ...rest}) => rest)});
        if (!toc) continue;
        if (key === 'leer' || key === 'actividades' || key === 'avisos') { add(key === 'leer' ? 'toc-front' : 'toc-l1', key, '', title); continue; }
        add('toc-l1', key, number, title);
        for (const s of sections) add('toc-l2', s.id, s.number, s.title, s.badge);
      }

      // Silabeo con los puntos de Pyphen (piloto), excluyendo nombres, enlaces, fórmulas, tablas, títulos y referencias.
      const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
      const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
      let words = 0, hints = 0;
      nodes.forEach(node => {
        const parent = node.parentElement;
        if (!parent || !parent.closest('p,li') || parent.closest('a,code,pre,.katex,math,table,h1,h2,h3,h4,strong,summary,.pdf-notice,.csl-entry,.pdf-box-title,figcaption,.pdf-toc,.pdf-creditos,.pdf-chapter-head,.pdf-result-title')) return;
        node.textContent = node.textContent.replace(/\b[a-záéíóúüñ]{7,}\b/gu, w => {
          if (!dictionary[w]) return w; words++; hints += dictionary[w].split('­').length - 1; return dictionary[w];
        });
      });

      // Ajustes locales de figuras (alto máximo), declarados en ajustes.json.
      for (const [id, h] of Object.entries(ajustes.figuras || {})) {
        const fig = document.getElementById(id); if (!fig) throw Error('Figura sin destino en ajustes.json: ' + id);
        fig.querySelectorAll('img').forEach(i => { i.style.maxHeight = h; i.style.width = 'auto'; });
      }

      // Remisiones internas sin destino.
      const ids = new Set([...main.querySelectorAll('[id]')].map(e => e.id));
      const missing = [...main.querySelectorAll('a[href^="#"]')].map(a => decodeURIComponent(a.getAttribute('href').slice(1))).filter(h => !ids.has(h));
      const dup = [...main.querySelectorAll('[id]')].map(e => e.id).filter((id, i, all) => all.indexOf(id) !== i);
      return {entries, structure, hyphenation: {words, hints}, missing: [...new Set(missing)], duplicateIds: [...new Set(dup)]};
    }, {parts, creditosHtml: creditos(), leerFinal, full: !ONLY, dictionary, ajustes});
    if (assembly.missing.length) throw Error('Remisiones internas sin destino: ' + assembly.missing.slice(0, 20).join(', '));
    if (assembly.duplicateIds.length) throw Error('Identificadores duplicados: ' + assembly.duplicateIds.slice(0, 20).join(', '));

    await page.waitForFunction(() => [...document.styleSheets].some(s => (s.href || '').includes('katex.min.css')));
    await page.addStyleTag({content: printCss + `\n:root{--pdf-cuerpo:${BODY};}`});
    await page.emulateMedia({media: 'print'});
    // Anchura de la caja de texto de A4 (210 − 2 × 18 mm) para medir como en la impresión.
    await page.setViewportSize({width: Math.round(174 / 25.4 * 96), height: 990});
    await page.evaluate(() => document.fonts.ready);
    await page.waitForFunction(() => [...document.images].every(i => i.complete));

    // 3a. Tablas más anchas que la caja de texto: letra menor y, si aún no caben, corte de palabra.
    const wideTables = await page.evaluate(() => {
      const out = [];
      document.querySelectorAll('main table').forEach(t => {
        // Tablas cortas (hasta el 40 % de la caja de texto): no se parten; una fila suelta en otra página obliga a volver atrás.
        if (t.getBoundingClientRect().height <= 0.4 * (297 - 35) / 25.4 * 96) {
          t.classList.add('pdf-short-table');
          // Chromium no siempre respeta break-after:avoid ante una tabla que no se parte: se agrupan
          // la frase que la presenta (y el título que la precede, si lo hay) con la tabla.
          const prev = t.previousElementSibling;
          if (prev && prev.tagName === 'P' && prev.getBoundingClientRect().height < 120) {
            const group = document.createElement('div'); group.className = 'pdf-keep-group';
            t.before(group); group.append(prev, t);
          }
        }
        const box = (t.closest('.callout-body,.pdf-details,.pdf-solution,section') || t.parentElement).getBoundingClientRect().right;
        if (t.getBoundingClientRect().right <= box + 1) return;
        t.classList.add('pdf-wide');
        let fixed = t.getBoundingClientRect().right <= box + 1;
        if (!fixed) { t.classList.add('pdf-wide-break'); fixed = t.getBoundingClientRect().right <= box + 1; }
        out.push({id: t.closest('[id]')?.id, headers: [...t.querySelectorAll('thead th')].map(th => th.textContent.trim()).slice(0, 4), fixed});
      });
      return out;
    });
    if (wideTables.some(t => !t.fixed)) console.warn('Tablas que siguen desbordando:', JSON.stringify(wideTables.filter(t => !t.fixed)));

    // 3. Paginación de cajas: se mantienen enteras las que caben en una fracción de la página.
    const keep = await page.evaluate(({fractions, whole}) => {
      const pageHeight = (297 - 35) / 25.4 * 96;
      const out = [];
      document.querySelectorAll('main .callout').forEach(box => {
        const type = box.classList.contains('ejemplo') ? 'ejemplo' : box.classList.contains('pdf-solution') ? 'solucion'
          : box.classList.contains('ejercicio') ? 'ejercicio' : box.classList.contains('en-app') ? 'en-app' : box.classList.contains('objetivos') ? 'objetivos' : 'otra';
        const h = box.getBoundingClientRect().height / pageHeight;
        const limit = fractions[type] ?? fractions.otra;
        const kept = h <= limit || (whole.includes(box.id) && h <= 1);
        box.classList.toggle('pdf-keep', kept);
        // Las reglas fijas del piloto para estas cajas se sustituyen por la medida.
        if (!kept) box.style.setProperty('break-inside', 'auto', 'important');
        out.push({id: box.id, type, height: +h.toFixed(3), kept});
      });
      return out;
    }, {fractions: ajustes.mantener_enteras, whole: ajustes.cajas_enteras?.ids || []});

    const overflow = await page.evaluate(() => {
      const W = document.querySelector('main').getBoundingClientRect().right + 1;
      return {scrollWidth: document.documentElement.scrollWidth, wide: [...document.querySelectorAll('main *')].filter(e => e.getBoundingClientRect().right > W)
        .filter(e => !e.closest('.katex svg,.katex-mathml') && (!e.parentElement || e.parentElement.getBoundingClientRect().right <= W))
        .slice(0, 15).map(e => ({tag: e.tagName, cls: e.className?.baseVal ?? e.className, id: e.id || e.closest('[id]')?.id, w: Math.round(e.getBoundingClientRect().right), text: e.textContent.slice(0, 60)}))};
    });
    fs.writeFileSync(path.join(WORK, 'desbordes.json'), JSON.stringify(overflow, null, 1));
    if (overflow.wide.length) console.warn('Elementos más anchos que la caja de texto:', JSON.stringify(overflow.wide.slice(0, 6)));
    const geometry = await page.evaluate(() => ({
      fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => `${f.family} ${f.weight} ${f.style}`).filter((v, i, a) => a.indexOf(v) === i),
      bodyFont: getComputedStyle(document.querySelector('main p')).fontFamily,
      math: [...document.querySelectorAll('main .katex')].slice(0, 30).every(e => getComputedStyle(e).fontSize === getComputedStyle(e.parentElement).fontSize),
      displayMath: [...document.querySelectorAll('main .katex-display')].every(e => getComputedStyle(e).textAlign === 'center' && getComputedStyle(e).textAlignLast === 'center'),
      linkColors: [...new Set([...document.querySelectorAll('main a.abrir,main a.explorar,main a.configurar')].map(a => getComputedStyle(a).webkitTextFillColor))],
      images: [...document.querySelectorAll('main img')].map(i => ({src: i.getAttribute('src'), ok: i.complete && i.naturalWidth > 0})),
      counts: {examples: document.querySelectorAll('main .ejemplo').length, enApp: document.querySelectorAll('main .en-app').length,
        exercises: document.querySelectorAll('main .ejercicio').length, solutions: document.querySelectorAll('main .pdf-solution').length,
        forward: document.querySelectorAll('main .pdf-solution-link a').length, back: document.querySelectorAll('main .pdf-return a').length,
        figures: document.querySelectorAll('main figure').length, tables: document.querySelectorAll('main table').length,
        localUrls: [...document.querySelectorAll('main a[href]')].filter(a => /127\.0\.0\.1|localhost/.test(a.href) && !a.getAttribute('href').startsWith('#')).length},
    }));
    if (geometry.images.some(i => !i.ok)) throw Error('Imágenes sin cargar: ' + JSON.stringify(geometry.images.filter(i => !i.ok)));

    // 4. Dos pasadas: la primera fija las páginas; la segunda escribe los números del índice.
    const pdfOptions = {format: 'A4', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: false, tagged: true, outline: false};
    const targets = [...new Set([...assembly.entries, ...assembly.structure.map(p => p.key)])];
    fs.writeFileSync(path.join(WORK, 'destinos.json'), JSON.stringify(targets));
    const pagesOf = file => JSON.parse(execFileSync(PYTHON, [path.join(HERE, 'paginas.py'), file, path.join(WORK, 'destinos.json')], {encoding: 'utf8'}));
    let previous = null, pass = 0, pages;
    while (true) {
      pass++;
      const file = path.join(WORK, `pasada-${pass}.pdf`);
      await page.pdf({...pdfOptions, path: file});
      pages = pagesOf(file);
      if (pages.missing.length && !ONLY) throw Error('Destinos sin página: ' + pages.missing.slice(0, 20).join(', '));
      for (const m of pages.missing) pages.map[m] = 0;
      if (previous && JSON.stringify(previous.map) === JSON.stringify(pages.map) && previous.total === pages.total) break;
      if (pass >= 4) throw Error('La paginación no se estabiliza');
      previous = pages;
      const bodyStart = ONLY ? 0 : pages.map[assembly.structure.find(p => p.number)?.key];
      const label = i => {
        if (i >= bodyStart) return String(i - bodyStart + 1);
        const r = [['m', 1000], ['cm', 900], ['d', 500], ['cd', 400], ['c', 100], ['xc', 90], ['l', 50], ['xl', 40], ['x', 10], ['ix', 9], ['v', 5], ['iv', 4], ['i', 1]];
        let n = i + 1, s = ''; for (const [k, v] of r) while (n >= v) { s += k; n -= v; } return s;
      };
      await page.evaluate(labels => document.querySelectorAll('.pdf-toc .toc-page').forEach(e => { e.textContent = labels[e.dataset.target]; }),
        Object.fromEntries(Object.entries(pages.map).map(([id, i]) => [id, label(i)])));
    }
    const finalPass = path.join(WORK, `pasada-${pass}.pdf`);
    // Portada: página aparte, a sangre, que posproceso.py coloca sobre la primera página (en blanco).
    if (!ONLY) {
      const cover = await browser.newPage();
      await cover.setContent(`<!doctype html><html><head><style>@page{size:A4;margin:0}html,body{margin:0;background:#f6f5ef}
        body{width:210mm;height:297mm;overflow:hidden}img{display:block;height:297mm;width:auto}</style></head>
        <body><img src="${base}figuras/portada.svg" alt="Portada de Evolución a la vista. Algoritmos genéticos en un laboratorio interactivo."></body></html>`);
      await cover.waitForFunction(() => document.images[0].complete && document.images[0].naturalWidth > 0);
      await cover.pdf({path: path.join(WORK, 'portada.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true, tagged: true});
      await cover.close();
    }
    fs.writeFileSync(path.join(WORK, 'estructura.json'), JSON.stringify({pass, total: pages.total, map: pages.map, structure: assembly.structure, full: !ONLY, config}, null, 1));
    fs.writeFileSync(path.join(WORK, 'render.json'), JSON.stringify({browser: browser.version(), cuerpo: BODY, fecha, files: parts.map(p => p.stats),
      hyphenation: assembly.hyphenation, wideTables, keep, geometry, errors, pdf: finalPass, pasadas: pass, paginas: pages.total}, null, 1));
    fs.writeFileSync(path.join(WORK, 'impresion-aplicada.css'), printCss);
    console.log(JSON.stringify({browser: browser.version(), pdf: finalPass, paginas: pages.total, pasadas: pass, counts: geometry.counts, errors}));
    if (errors.length) console.warn('Avisos JavaScript:', errors.slice(0, 10));
  } finally { await browser.close(); await new Promise(r => server.close(r)); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
