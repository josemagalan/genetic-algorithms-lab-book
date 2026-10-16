#!/usr/bin/env node
/*
 * Comprobaciones del libro frente a las herramientas (revisión beta, M08).
 *
 * 1. Versiones: compara la versión actual de cada herramienta con la última revisada
 *    (herramientas.json). Si han cambiado archivos que pueden alterar los ejemplos, falla y dice
 *    qué capítulos hay que volver a comprobar. Los cambios en README, pruebas, imágenes o la
 *    pantalla «Acerca de» solo se anotan.
 * 2. Controles: comprueba que los valores que piden los enlaces del libro, y los que se anotan con
 *    <!-- comprobar: URL -->, caben en los controles de selection-ga, crossover-ga y mutation-ga
 *    (mínimo y máximo de cada parámetro, operador y variante existentes, k ≤ N en el torneo).
 *
 * Uso: node comprobaciones/comprobar.cjs        (necesita git y conexión)
 *      node comprobaciones/comprobar.cjs --sin-versiones   (solo los controles)
 * Salida: anotaciones de GitHub Actions (::error:: / ::warning:: / ::notice::) y un resumen.
 */
'use strict';
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');

const RAIZ = path.resolve(__dirname, '..');
const MANIFIESTO = JSON.parse(fs.readFileSync(path.join(__dirname, 'herramientas.json'), 'utf8'));
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'herramientas-'));
const resumen = [];
let errores = 0;

function anotar(nivel, texto, archivo, linea) {
  const donde = archivo ? ` file=${archivo}${linea ? ',line=' + linea : ''}` : '';
  console.log(`::${nivel}${donde}::${texto}`);
  resumen.push(`- **${nivel}**: ${texto}${archivo ? ` (${archivo}${linea ? ':' + linea : ''})` : ''}`);
  if (nivel === 'error') errores++;
}

function git(args, cwd) {
  return execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}

function clonar(nombre, repo) {
  const destino = path.join(TMP, nombre);
  git(['clone', '--quiet', '--filter=blob:none', `https://github.com/${repo}.git`, destino]);
  return destino;
}

// Capítulos del libro y enlaces a cada herramienta
const capitulos = fs.readdirSync(RAIZ).filter((f) => /^\d\d-.*\.qmd$/.test(f)).sort();
const textos = Object.fromEntries(capitulos.map((f) => [f, fs.readFileSync(path.join(RAIZ, f), 'utf8')]));

function capitulosQueUsan(nombre, h) {
  const marcas = h.marcas || [h.url];
  return capitulos.filter((f) => marcas.some((m) => textos[f].includes(m)));
}

function ignorado(archivo, h) {
  const ignorar = MANIFIESTO.ignorar.concat(h.ignorar || []);
  return ignorar.some((p) => (p.endsWith('/') ? archivo.startsWith(p) : archivo === p));
}

// ---------- 1. Versiones ----------
const clones = {};
if (!process.argv.includes('--sin-versiones')) {
  for (const [nombre, h] of Object.entries(MANIFIESTO.herramientas)) {
    const dir = clonar(nombre, h.repositorio);
    clones[nombre] = dir;
    const actual = git(['rev-parse', 'HEAD'], dir);
    const caps = capitulosQueUsan(nombre, h);
    if (actual.startsWith(h.revisado)) {
      resumen.push(`- ${nombre}: sin cambios desde ${h.revisado} (capítulos ${caps.join(', ') || '—'}).`);
      continue;
    }
    let cambiados;
    try {
      cambiados = git(['diff', '--name-only', h.revisado, actual], dir).split('\n').filter(Boolean);
    } catch (e) {
      anotar('error', `${nombre}: no se encuentra el commit revisado ${h.revisado} en ${h.repositorio}.`);
      continue;
    }
    const relevantes = cambiados.filter((a) => !ignorado(a, h));
    const corto = actual.slice(0, 7);
    if (relevantes.length) {
      anotar('error', `${nombre} ha cambiado (${h.revisado} → ${corto}) en ${relevantes.join(', ')}. ` +
        `Vuelve a comprobar los ejemplos de ${caps.join(', ') || 'ningún capítulo'} y actualiza «revisado» en comprobaciones/herramientas.json.`);
    } else {
      anotar('notice', `${nombre} ha cambiado (${h.revisado} → ${corto}) solo en ${cambiados.join(', ')}; no afecta a los ejemplos. ` +
        `Puedes actualizar «revisado» a ${corto}.`);
    }
  }
}

// ---------- 2. Controles ----------
const CON_CONTROLES = ['selection-ga', 'crossover-ga', 'mutation-ga'];
const especificaciones = {};
for (const nombre of CON_CONTROLES) {
  const dir = clones[nombre] || clonar(nombre, MANIFIESTO.herramientas[nombre].repositorio);
  const ops = path.join(dir, 'js', 'operators');
  especificaciones[nombre] = {};
  for (const f of fs.readdirSync(ops)) {
    let m;
    try { m = require(path.join(ops, f)); } catch (e) { continue; }
    if (m && m.spec && m.spec.id) especificaciones[nombre][m.spec.id] = m.spec;
  }
}

function numero(v) {
  const x = Number(String(v).replace(',', '.'));
  return Number.isFinite(x) ? x : null;
}

function comprobarUrl(url, archivo, linea) {
  const m = url.match(/^https:\/\/josemagalan\.github\.io\/([a-z-]+)\/#(.*)$/);
  if (!m || !especificaciones[m[1]]) return 0;
  const herramienta = m[1];
  const specs = especificaciones[herramienta];
  const q = new URLSearchParams(m[2]);
  const op = q.get('op') || q.get('from');
  let candidatos;
  if (op) {
    if (!specs[op]) {
      anotar('error', `${herramienta} no tiene el operador «${op}»: ${url}`, archivo, linea);
      return 1;
    }
    candidatos = [specs[op]];
    const v = q.get('v');
    const variantes = specs[op].variants;
    if (v && Array.isArray(variantes) && !variantes.includes(v)) {
      anotar('error', `${herramienta}, ${op}: no existe la variante «${v}» (hay ${variantes.join(', ')}): ${url}`, archivo, linea);
    }
  } else {
    candidatos = Object.values(specs); // pantallas de comparación: vale si cabe en algún operador
  }
  for (const [clave, valor] of q) {
    const conParam = candidatos.filter((s) => (s.params || []).some((p) => p.id === clave));
    if (!conParam.length) continue;
    const x = numero(valor);
    if (x === null) continue;
    const cabe = conParam.some((s) => {
      const p = s.params.find((pp) => pp.id === clave);
      return x >= p.min - 1e-9 && x <= p.max + 1e-9;
    });
    if (!cabe) {
      const rangos = conParam.map((s) => { const p = s.params.find((pp) => pp.id === clave); return `${s.id}: ${p.min}–${p.max}`; });
      anotar('error', `${herramienta}: ${clave}=${valor} está fuera del control (${rangos.join('; ')}): ${url}`, archivo, linea);
    }
  }
  // selection-ga limita k al tamaño de la población (js/app.js)
  if (herramienta === 'selection-ga' && op === 'tournament' && q.get('k') && q.get('f')) {
    const n = q.get('f').split('-').length;
    if (numero(q.get('k')) > n) anotar('error', `selection-ga: k=${q.get('k')} es mayor que la población (${n}); el control no lo permite: ${url}`, archivo, linea);
  }
  return 1;
}

let revisados = 0;
const ENLACE = /https:\/\/josemagalan\.github\.io\/(?:selection-ga|crossover-ga|mutation-ga)\/#[^)\s"'<>]+/g;
const ANOTACION = /<!--\s*comprobar:\s*(\S+)\s*-->/g;
for (const f of capitulos) {
  const lineas = textos[f].split(/\r?\n/);
  lineas.forEach((l, i) => {
    for (const a of l.matchAll(ANOTACION)) revisados += comprobarUrl(a[1], f, i + 1);
    for (const u of l.replace(ANOTACION, '').match(ENLACE) || []) revisados += comprobarUrl(u.replace(/&amp;/g, '&'), f, i + 1);
  });
}
resumen.unshift(`Enlaces y anotaciones comprobados en los controles: ${revisados}.`);

const texto = '## Comprobaciones del libro frente a las herramientas\n\n' + resumen.join('\n') + '\n';
if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, texto);
console.log('\n' + texto);
fs.rmSync(TMP, { recursive: true, force: true });
process.exit(errores ? 1 : 0);
