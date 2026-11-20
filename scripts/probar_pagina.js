const fs=require('fs'); const {JSDOM,VirtualConsole}=require('jsdom');
const html0=fs.readFileSync('salida/tienda.html','utf8').replace(/<script src="[^"]*three[^"]*"><\/script>/,'');
const three=fs.readFileSync('node_modules/three/build/three.js','utf8');
const errors=[]; const vc=new VirtualConsole(); vc.on('jsdomError',e=>errors.push('jsdomError: '+(e.detail&&e.detail.stack||e.message).split('\n').slice(0,3).join(' | '))); vc.on('error',e=>errors.push('console.error: '+e));
const dom=new JSDOM(html0,{runScripts:'outside-only',pretendToBeVisual:true,virtualConsole:vc,url:'http://localhost/'});
const w=dom.window;
const m2d=new Proxy({}, {get:(t,k)=> k==='createRadialGradient'||k==='createLinearGradient' ? ()=>({addColorStop(){}}) : (typeof k==='string'? (()=>{}) : undefined), set:()=>true});
w.HTMLCanvasElement.prototype.getContext=function(){return m2d;};
w.ResizeObserver=class{observe(){}}; w.matchMedia=()=>({addEventListener(){}});
w.addEventListener('error',e=>errors.push('window.error: '+e.message));
w.eval(three);
const renders=[]; 
w.THREE.WebGLRenderer=function(){ this.setPixelRatio=()=>{}; this.setSize=()=>{}; this.render=(s,c)=>{renders.push({p:c.position.clone(), y:c.rotation.y, x:c.rotation.x});}; };
w.THREE.TextureLoader=function(){ this.load=(u,cb)=>{ const t=new w.THREE.Texture(); return t; }; };
const scripts=[...w.document.querySelectorAll('script')].map(s=>s.textContent).filter(t=>t.includes('buildStore'));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const $=id=>w.document.getElementById(id);
const click=id=>$(id).dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
const key=(type,code)=>w.dispatchEvent(new w.KeyboardEvent(type,{code,bubbles:true}));
(async()=>{
  try { w.eval(scripts[0]); } catch(e){ errors.push('carga: '+e.stack.split('\n').slice(0,3).join(' | ')); }
  await sleep(400);
  console.log("renderizados tras la carga:",renders.length,"| lista válidos:",$('listValid').children.length,"| aprox:",$('listApprox').children.length);
  // ---- vuelo ----
  click('tFly'); await sleep(100);
  console.log("modo vuelo:",$('flyInfo').textContent.slice(0,30),"| HUD oculto:",$('hud').hidden);
  const n0=renders.length, p0=renders[renders.length-1].p.clone();
  key('keydown','KeyW'); await sleep(500); key('keyup','KeyW');
  const p1=renders[renders.length-1].p; console.log("avance con W:",Math.round(p0.distanceTo(p1)),"cm | cuadros nuevos:",renders.length-n0);
  const y0=p1.y; key('keydown','KeyE'); await sleep(400); key('keyup','KeyE'); await sleep(60);
  console.log("subida con E: altura",Math.round(y0),"→",Math.round(renders[renders.length-1].p.y),"| etiqueta:",$('fAltV').textContent);
  $('fAlt').value=500; $('fAlt').dispatchEvent(new w.Event('input')); await sleep(60);
  console.log("altura fijada a mano 5 m:",Math.round(renders[renders.length-1].p.y));
  // ---- recorrido ----
  click('rAdd'); key('keydown','KeyW'); await sleep(900); key('keyup','KeyW'); click('rAdd'); key('keydown','KeyD'); await sleep(700); key('keyup','KeyD'); click('rAdd');
  console.log("puntos:",$('rList').children.length,"|",$('rMsg').textContent);
  $('rDur').value=5; $('rFix').checked=true; $('rH').value=800; click('rPlay'); await sleep(250);
  console.log("durante el recorrido:",$('flyInfo').textContent,"| altura de cámara:",Math.round(renders[renders.length-1].p.y));
  await sleep(5600);
  console.log("al terminar:",$('flyInfo').textContent.slice(0,25),"|",$('rMsg').textContent);
  // ---- cielos a alturas distintas ----
  $('cSalaMode').value='aw'; $('cSalaMode').dispatchEvent(new w.Event('change'));
  $('cBodMode').value='ab'; $('cBodMode').dispatchEvent(new w.Event('change'));
  $('cBodH').value=330; $('cBodH').dispatchEvent(new w.Event('input'));
  console.log("sala:",$('cSalaV').textContent,"| bodega:",$('cBodV').textContent);
  $('cSalaMode').value='pn'; $('cSalaMode').dispatchEvent(new w.Event('change')); console.log("sala pintura negra:",$('cSalaV').textContent);
  // ---- noche ----
  click('tNight'); $('nLevel').value='0.6'; $('nLevel').dispatchEvent(new w.Event('change')); await sleep(80);
  console.log("noche: ganancia",$('nLevel').options[$('nLevel').selectedIndex].text);
  click('tFly'); await sleep(80); console.log("de vuelta a órbita:",$('flyInfo').textContent.slice(0,22));
  console.log("\nERRORES:",errors.length?errors:"ninguno");
  process.exit(0);
})();
