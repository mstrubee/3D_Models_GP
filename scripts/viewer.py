import re
BASE = open("/mnt/user-data/outputs/gondola_negra_v0.html", encoding="utf8").read()
CSS = BASE.split("<style>")[1].split("</style>")[0]
def make_viewer(path, title, block, build_call, mats_js, readout_js, details_html, max_mod=None, view=(3.4, 1.1), extra_ctrl='', extra_js=''):
    ctrl_mod = '''
  <div class="group" role="group" aria-label="Módulos en hilera">
    <span>Módulos</span>
    <button id="less" aria-label="Quitar un módulo">−</button>
    <span id="count">1</span>
    <button id="more" aria-label="Agregar un módulo">+</button>
  </div>''' if max_mod else ''
    mod_js = f'''
  document.getElementById('less').onclick = () => {{ state.modules = Math.max(1, state.modules - 1); rebuild(true); }};
  document.getElementById('more').onclick = () => {{ state.modules = Math.min({max_mod or 1}, state.modules + 1); rebuild(true); }};''' if max_mod else ''
    count_js = "document.getElementById('count').textContent = state.modules;" if max_mod else ""
    th0, ph0 = view
    html = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <p id="readout"></p>
</header>
<div id="stage">
  <canvas id="cv" aria-label="Vista 3D de {title}. Arrastra para girar, pellizca para acercar."></canvas>
  <div class="hint">Arrastra para girar · pellizca o rueda para acercar</div>
</div>
<div class="controls">{ctrl_mod}{extra_ctrl}
  <button id="reset">Vista inicial</button>
</div>
{details_html}
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/*BUILD_START*/{block}/*BUILD_END*/

if (typeof window !== 'undefined') {{
  const cv = document.getElementById('cv'), stage = document.getElementById('stage');
  const renderer = new THREE.WebGLRenderer({{ canvas: cv, antialias: true }});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 5, 5000);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f8c, 1.0));
  const sun = new THREE.DirectionalLight(0xffffff, 0.8); sun.position.set(300, 600, 500); scene.add(sun);
  const sun2 = new THREE.DirectionalLight(0xffffff, 0.6); sun2.position.set(-250, 350, 500); scene.add(sun2);
  const dotTex = (() => {{
    const c = document.createElement('canvas'); c.width = 64; c.height = 64;
    const x = c.getContext('2d');
    x.fillStyle = '#26282b'; x.fillRect(0, 0, 64, 64); x.fillStyle = '#5b6065';
    [[16, 16], [48, 48]].forEach(([a, b]) => {{ x.beginPath(); x.arc(a, b, 4.2, 0, Math.PI * 2); x.fill(); }});
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t;
  }})();
  {mats_js}
  let state = {{ modules: 1, open: 0 }};
  let model = null, grid = null;
  let target = new THREE.Vector3(), th = {th0}, ph = {ph0}, radius = 400;
  const cssVar = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  function applyTheme() {{
    scene.background = new THREE.Color(cssVar('--bg'));
    if (grid) {{ scene.remove(grid); grid.geometry.dispose(); }}
    grid = new THREE.GridHelper(1400, 140, new THREE.Color(cssVar('--grid')), new THREE.Color(cssVar('--grid')));
    grid.position.set(target.x, -0.05, target.z); scene.add(grid);
  }}
  function fit() {{
    const u = model.userData;
    target.set(u.length / 2, u.height * 0.5, u.depth / 2);
    radius = Math.max(u.height * 2.2, u.length * 1.5, 220);
    th = {th0}; ph = {ph0};
    if (grid) grid.position.set(target.x, -0.05, target.z);
  }}
  function rebuild(resetView) {{
    if (model) {{ scene.remove(model); model.traverse(n => {{ if (n.geometry) n.geometry.dispose(); }}); }}
    model = {build_call};
    scene.add(model);
    if (resetView) fit();
    const u = model.userData;
    document.getElementById('readout').textContent = {readout_js};
    {count_js}
  }}
  {mod_js}
  {extra_js}
  document.getElementById('reset').onclick = () => fit();
  const pts = new Map(); let lastDist = 0;
  cv.addEventListener('pointerdown', e => {{ cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, {{ x: e.clientX, y: e.clientY }}); lastDist = 0; }});
  cv.addEventListener('pointermove', e => {{
    const p = pts.get(e.pointerId); if (!p) return;
    const dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY;
    if (pts.size === 1) {{ th -= dx * 0.007; ph = Math.min(1.53, Math.max(0.12, ph - dy * 0.007)); }}
    else if (pts.size === 2) {{ const [a, b] = [...pts.values()], d = Math.hypot(a.x - b.x, a.y - b.y); if (lastDist) radius = Math.min(2500, Math.max(90, radius * lastDist / d)); lastDist = d; }}
  }});
  const up = e => {{ pts.delete(e.pointerId); lastDist = 0; }};
  cv.addEventListener('pointerup', up); cv.addEventListener('pointercancel', up);
  cv.addEventListener('wheel', e => {{ e.preventDefault(); radius = Math.min(2500, Math.max(90, radius * Math.exp(e.deltaY * 0.001))); }}, {{ passive: false }});
  function resize() {{ const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }}
  new ResizeObserver(resize).observe(stage);
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
  rebuild(true); applyTheme(); resize();
  (function loop() {{
    camera.position.set(target.x + radius * Math.sin(ph) * Math.sin(th), target.y + radius * Math.cos(ph), target.z + radius * Math.sin(ph) * Math.cos(th));
    camera.lookAt(target); renderer.render(scene, camera); requestAnimationFrame(loop);
  }})();
}}
</script>
</body>
</html>
'''
    open(path, "w", encoding="utf8").write(html)
