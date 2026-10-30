#!/usr/bin/env node
'use strict';
// Muestra estable de actividades: mismo HTML y mismos módulos que usa el lector.
// GA_APPS_ROOT admite copias locales; en CI se descargan en _herramientas/.
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const apps=path.resolve(process.env.GA_APPS_ROOT||path.join(root,'_herramientas'));
const output=path.resolve(process.env.GA_UI_OUTPUT||path.join(__dirname,'resultados'));
fs.mkdirSync(output,{recursive:true});
const modules=['representation-ga','initialization-and-evaluation-ga','selection-ga','crossover-ga','mutation-ga'];
const routes={book:path.join(root,'_book'),portal:path.join(apps,'portal'),...Object.fromEntries(modules.map(n=>[n,path.join(apps,n)]))};
for(const [name,dir] of Object.entries(routes)) assert.ok(fs.existsSync(path.join(dir,'index.html')),`Falta ${name}: ${dir}. Consulta comprobaciones/LEEME.md.`);
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.svg':'image/svg+xml','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.woff2':'font/woff2','.woff':'font/woff','.ttf':'font/ttf'};
const server=http.createServer((req,res)=>{
  try {
    const [group,...rest]=decodeURIComponent(new URL(req.url,'http://localhost').pathname).split('/').filter(Boolean);
    const base=routes[group];
    if(!base) {res.writeHead(404).end();return;}
    let file=path.resolve(base,rest.join('/')||'index.html');
    if(!file.startsWith(base+path.sep)) {res.writeHead(403).end();return;}
    if(fs.statSync(file).isDirectory()) file=path.join(file,'index.html');
    res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream'});
    fs.createReadStream(file).pipe(res);
  } catch {res.writeHead(404).end();}
});
function example(file,id) {
  const source=fs.readFileSync(path.join(root,file),'utf8');
  const declaration=new RegExp('^:{3,} \\{[^\\n]*#'+id+'\\b','m').exec(source);
  assert.ok(declaration,`${id}: falta la caja del ejemplo`);
  const box=source.slice(declaration.index);
  const match=box.match(/\[Abrir[^\]]*\]\((https:\/\/josemagalan.github.io\/[^)]+)\)/);
  assert.ok(match,`${id}: no se encuentra el botón Abrir`);
  return new URL(match[1]);
}
async function lastStep(page) {
  const next=page.locator('#btnNext');
  await next.waitFor({state:'visible'});
  for(let i=0;i<80;i++) {
    if(await next.isDisabled()) return;
    await next.click();
  }
  throw new Error('La animación no termina en 80 pasos');
}
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const base='http://127.0.0.1:'+server.address().port;
  const browser=await chromium.launch({headless:true,...(process.env.GA_CHROMIUM_PATH?{executablePath:process.env.GA_CHROMIUM_PATH}:{})});
  const results=[];
  async function check(name,fn,viewport={width:1280,height:900}) {
    const page=await browser.newPage({viewport,locale:'es-ES'});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    try {
      await fn(page);
      assert.deepEqual(errors,[],`Errores de JavaScript en ${name}`);
      results.push({name,ok:true});
    } catch(error) {
      await page.screenshot({path:path.join(output,name+'-error.png'),fullPage:true});
      results.push({name,ok:false,error:String(error)});
      throw error;
    } finally {await page.close();}
  }
  try {
    await check('recorrido-basico',async page=>{
      await page.goto(base+'/book/08-reemplazo.html');
      await page.getByRole('link',{name:'capítulo «Parámetros y aleatoriedad»',exact:true}).click();
      await page.waitForURL('**/09-experimentos.html');
      assert.equal(new URL(page.url()).hash,'');
      assert.ok(await page.locator('.objetivos').isVisible());
      assert.ok((await page.locator('#resumen').boundingBox()).y<(await page.locator('#sec-experimentos-numero-replicas').boundingBox()).y);
    });
    await check('figura-movil',async page=>{
      await page.goto(base+'/book/11-recapitulacion.html#fig-que-metodo');
      const figure=page.locator('#fig-que-metodo');
      await figure.waitFor({state:'visible'});
      const link=figure.locator('xpath=following-sibling::p[1]').locator('a.ampliar-figura');
      assert.ok((await link.getAttribute('href')).endsWith('11-que-metodo.svg'));
      assert.ok((await page.request.get(new URL(await link.getAttribute('href'),page.url()).href)).ok());
      await link.scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(output,'figura-movil.png')});
    },{width:390,height:844});
    await check('ciclo-portal',async page=>{
      await page.goto(base+'/portal/?lang=es');
      assert.equal(await page.locator('.preparation-flow > li').count(),3);
      assert.deepEqual(await page.locator('.cycle .cycle-label').allTextContents(),['Seleccionar','Cruzar','Mutar','Evaluar a los hijos','Reemplazar']);
      await page.getByRole('button',{name:'English',exact:true}).click();
      assert.deepEqual(await page.locator('.cycle .cycle-label').allTextContents(),['Select','Cross over','Mutate','Evaluate offspring','Replace']);
      await page.locator('#algorithm').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(output,'ciclo-portal.png')});
    });
    await check('enlaces-capitulos',async page=>{
      for(let i=0;i<modules.length;i++) {
        await page.goto(base+'/'+modules[i]+'/#lang=es');
        assert.ok((await page.locator('#bookLink').getAttribute('href')).includes('/0'+(i+3)+'-'));
        await page.getByRole('button',{name:'EN',exact:true}).click();
        assert.match(await page.locator('#bookLink').innerText(),/Spanish/);
      }
    });
    await check('goldberg',async page=>{
      const url=example('02-ciclo.qmd','ejemplo-ciclo-seleccionar');
      await page.goto(base+url.pathname+url.hash);
      await lastStep(page);
      assert.match(await page.locator('#narration').innerText(),/padres son A B B D/);
      assert.match(await page.locator('#narration').innerText(),/420,5/);
    });
    await check('ox-clasico',async page=>{
      const url=example('06-cruce.qmd','ejemplo-cruce-ox');
      await page.goto(base+url.pathname+url.hash);
      await lastStep(page);
      const genes=await page.locator('#viz .children text.gene-num').allTextContents();
      assert.deepEqual(genes.slice(0,9),['2','3','8','4','5','6','7','1','9']);
      assert.deepEqual(genes.slice(9),['4','5','7','2','6','3','8','9','1']);
    });
    await check('siembra-es-en',async page=>{
      const url=example('04-inicializar-evaluar.qmd','ejemplo-inicializar-evaluar-sembrar');
      for(const lang of ['es','en']) {
        await page.goto(base+url.pathname+url.hash.replace('lang=es','lang='+lang));
        await page.locator('#narration').waitFor({state:'visible'});
        assert.match(await page.locator('#narration').innerText(),lang==='es'?/aproximación determinista/:/deterministic approximation/);
        assert.match(await page.locator('#explainBody').innerText(),lang==='es'?/12,2 %/:/12.2%/);
      }
    });
    await check('comparacion-seleccion',async page=>{
      const url=example('05-seleccion.qmd','ejemplo-seleccion-truncamiento');
      await page.goto(base+url.pathname+url.hash);
      const rows=page.locator('tr').filter({hasText:/truncamiento/i});
      await rows.first().waitFor();
      await page.waitForFunction(()=>[...document.querySelectorAll('tr')].some(r=>r.textContent.toLowerCase().includes('truncamiento')&&r.textContent.includes('2,2')));
      const data=(await rows.allTextContents()).join(' ');
      assert.match(data,/2,2/);
      assert.match(data,/24/);
    });
  } finally {
    fs.writeFileSync(path.join(output,'interfaz.json'),JSON.stringify(results,null,2)+'\n');
    console.log(JSON.stringify(results,null,2));
    await browser.close();
    await new Promise(resolve=>server.close(resolve));
  }
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
