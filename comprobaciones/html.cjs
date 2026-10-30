#!/usr/bin/env node
'use strict';
// Comprueba el libro ya generado. Solo usa Node; no necesita conexión ni Playwright.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const book = path.join(root, '_book');
const pages = fs.readdirSync(root).filter(n => n.endsWith('.qmd')).map(n => n.replace(/\.qmd$/, '.html'));
const cache = new Map();
function read(name) {
  if (!cache.has(name)) {
    const html = fs.readFileSync(path.join(book, name), 'utf8');
    const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map(m => m[1]);
    assert.equal(new Set(ids).size, ids.length, `${name}: identificadores duplicados`);
    assert.ok(!/quarto-unresolved-ref|katex-error|\?@(?:sec|fig)-/.test(html), `${name}: referencia sin resolver`);
    cache.set(name, {html, ids: new Set(ids)});
  }
  return cache.get(name);
}
let links=0, resources=0, chapters=0, figures=0;
for (const name of pages) {
  const {html}=read(name);
  for (const match of html.matchAll(/<(a|img|script|link|iframe)\b[^>]*?\b(href|src)="([^"]+)"[^>]*>/g)) {
    const [,tag,,raw]=match;
    if (/^(?:[a-z]+:|\/\/|\/)/i.test(raw)) continue;
    const url=new URL(raw.replace(/&amp;/g,'&'),'https://libro.invalid/'+name);
    let filename=decodeURIComponent(url.pathname.slice(1));
    if (!filename || filename.endsWith('/')) filename+='index.html';
    const dest=path.resolve(book,filename);
    assert.ok(dest.startsWith(book+path.sep), `${name}: ruta fuera del libro: ${raw}`);
    assert.ok(fs.existsSync(dest),`${name}: falta ${raw}`);
    if (url.hash && filename.endsWith('.html')) assert.ok(read(filename).ids.has(decodeURIComponent(url.hash.slice(1))),`${name}: ancla ausente ${raw}`);
    if(tag==='a') links++; else resources++;
  }
  const main=(html.match(/<main\b[\s\S]*?<\/main>/)||[''])[0];
  for(const img of main.matchAll(/<img\b[^>]*>/g)) assert.ok(/\balt="[^"]+"/.test(img[0]),`${name}: imagen sin texto alternativo`);
  for(const frame of main.matchAll(/<iframe\b[^>]*>/g)) assert.ok(/\btitle="[^"]+"/.test(frame[0]),`${name}: iframe sin título`);
  for(const link of main.matchAll(/<a\b[^>]*class="[^"]*ampliar-figura[^>]*>/g)) {
    assert.ok(/href="figuras\/[^"#]+\.svg"/.test(link[0]),`${name}: ampliación sin SVG`);
    figures++;
  }
  if(!/^\d\d-/.test(name)) continue;
  chapters++;
  const summary=main.indexOf('id="resumen"');
  const optional=main.search(/class="nivel (?:avanzado|saber-mas)"/);
  assert.ok(summary>main.lastIndexOf('class="nivel basico"') && summary<optional,`${name}: resumen fuera del recorrido básico`);
  const continuation=main.match(/<p>(?:Para seguir el recorrido básico,|Aquí termina el recorrido básico)[\s\S]*?<\/p>/);
  assert.ok(continuation,`${name}: falta la continuación`);
  assert.ok(main.indexOf(continuation[0])>summary && main.indexOf(continuation[0])<optional,`${name}: continuación fuera del resumen básico`);
  assert.ok(!/href="[^"#]+#/.test(continuation[0]),`${name}: la continuación omite los objetivos`);
}
assert.equal(chapters,11);
assert.ok(figures>10,'Faltan enlaces para ampliar los esquemas');
console.log(JSON.stringify({pages:pages.length,links,resources,chapters,expandableFigures:figures,errors:0},null,2));
