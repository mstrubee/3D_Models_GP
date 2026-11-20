import json, re
D = json.load(open("data.json"))
def r1(v): return round(v,1)
def clean(o):
    if isinstance(o, float): return r1(o)
    if isinstance(o, list): return [clean(i) for i in o]
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    return o
import math, base64
L=json.load(open("datos/luces.json"))
D['luz']=[dict(t=l['t'],x=l['x'],y=l['y'],a=l['ang']) for l in L['lum']]
hd=sorted(L['heads'],key=lambda h:(round(h['y']/50),h['x'])); rails=[]; used=set()
for i,h in enumerate(hd):
    if i in used: continue
    for j in range(i+1,len(hd)):
        if j not in used and abs(hd[j]['y']-h['y'])<30 and abs(hd[j]['x']-h['x'])<80:
            rails.append(dict(x=(h['x']+hd[j]['x'])/2,y=(h['y']+hd[j]['y'])/2)); used.update([i,j]); break
D['rails']=rails
SIGN=json.dumps({"sur":"data:image/png;base64,"+base64.b64encode(open("datos/sign_sur.png","rb").read()).decode(),"ori":"data:image/png;base64,"+base64.b64encode(open("datos/sign_ori.png","rb").read()).decode(),"logo":"data:image/png;base64,"+base64.b64encode(open("datos/logo_ori.png","rb").read()).decode(),"cenefaBat":"data:image/jpeg;base64,"+base64.b64encode(open("datos/cenefa_baterias.jpg","rb").read()).decode(),"swBody":"data:image/png;base64,"+base64.b64encode(open("datos/sw_body.png","rb").read()).decode(),"swTip":"data:image/png;base64,"+base64.b64encode(open("datos/sw_tip.png","rb").read()).decode()})
for p in D['ph']:
    if p['label']=="Bodega 120×60": p['label']="Tablero eléctrico (rack arriba)"
    if p['label']=="Cabecera repisas HP":
        c=[p['ang']+90,p['ang']-90]
        p['fa']=min(c,key=lambda a:(abs((a-0+180)%360-180), -math.sin(math.radians(a))))
DATA = json.dumps(clean({k: D[k] for k in ("contour","XB","step","bodega","sala","per","hp","gon","cab","mes","bat","ph","luz","rails")}), ensure_ascii=False, separators=(",",":"))
def block(path):
    s = open(f"biblioteca/{path}", encoding="utf8").read()
    return s.split("/*BUILD_START*/")[1].split("/*BUILD_END*/")[0]
comp = f'''
const C_hp  = (function(){{ {block("rack_repisas_hp_v0.html")}
  return {{SPEC, build: buildRack}}; }})();
const C_mes = (function(){{ {block("meson_atencion_v1.html")}
  return {{SPEC, build: buildMeson}}; }})();
const C_gon = (function(){{ {block("gondola_negra_v0.html")}
  return {{SPEC, build: buildGondola}}; }})();
const C_per = (function(){{ {block("perimetral_v1.html")}
  return {{SPEC, build: buildPerimetral}}; }})();
const C_neu = (function(){{ {block("rack_neumaticos_v0.html")}
  return {{SPEC, build: buildNeumaticos}}; }})();
const C_cabhp = (function(){{ {block("cabecera_repisas_hp_v1.html")}
  return {{SPEC, build: buildCabecera}}; }})();
const C_resp = (function(){{ {block("bodega_respel_v0.html")}
  return {{SPEC, build: buildRespel}}; }})();
const C_jaula = (function(){{ {block("jaula_cartones_plasticos_v1.html")}
  return {{SPEC, build: buildJaula}}; }})();
const C_pal = (function(){{ {block("rack_pallets_v1.html")}
  return {{SPEC, build: buildRackPallets}}; }})();
const C_bat = (function(){{ {block("rack_baterias_v2.html")}
  return {{SPEC, build: buildRack}}; }})();
'''
core = r'''
/*CORE_START*/
const OX = 14392, OY = 516;
const px = x => x - OX, pz = y => -(y - OY);
const rotY = fa => Math.atan2(Math.cos(fa * Math.PI / 180), -Math.sin(fa * Math.PI / 180));
const H_BOD = 387, H_SALA = 780, WALL_T = 12;
const LUZ_H = { L01: 270, L02: 400, L03: 360, L06: 400, F01: 400 };      // altura de cada tipo de luminaria (L02 y L06 a 4 m: dato; el resto supuesto)

function makeMats(THREE, tex) {
  const std = (c, o) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.6 }, o || {}));
  const M = {};
  M.black = std(0x34373a, { roughness: 0.55, metalness: 0.25 });
  M.orange = std(0xe4540c, { roughness: 0.5 });
  M.carbon = std(0x1d1e20, { roughness: 0.4, metalness: 0.3 });
  M.post = std(0xb3b9bd, { metalness: 0.55, roughness: 0.45 });
  M.board = std(0xc9a46c, { roughness: 0.85 });
  M.lip = std(0x9aa2a6, { metalness: 0.6, roughness: 0.4 });
  M.frame = std(0x2b2e31, { metalness: 0.3, roughness: 0.5 });
  M.deck = std(0x3a3d40, { metalness: 0.25, roughness: 0.55 });
  M.strip = std(0xf1f1ee);
  M.cabm = std(0x26282b, { roughness: 0.6 });
  M.pend = new THREE.MeshStandardMaterial({ color: 0xe0a030, roughness: 0.7, transparent: true, opacity: 0.55 });
  M.perfMat = std(0xffffff, { roughness: 0.6 });
  M.lamp = new THREE.MeshBasicMaterial({ color: 0xfff4cf });
  M.part = std(0xe7e9ea, { roughness: 0.9 }); M.door = std(0xb8956a, { roughness: 0.7 });
  M.cer = std(0xf3f4f5, { roughness: 0.35 }); M.steelb = std(0xaeb4b9, { metalness: 0.7, roughness: 0.35 });
  M.dark = std(0x2a2d30, { roughness: 0.5 }); M.wood = std(0xb48a5a, { roughness: 0.8 }); M.cabn = std(0xcdbfa4, { roughness: 0.8 });
  M.top = std(0x50555a, { roughness: 0.5 }); M.fridgeM = std(0xe4e7ea, { roughness: 0.4, metalness: 0.2 });
  M.blueM = std(0x2d6ea8, { roughness: 0.5 }); M.chairM = std(0x3b3e42, { roughness: 0.7 });
  M.locker = std(0x9fb0bd, { roughness: 0.6 }); M.lockdoor = std(0xb3c1cc, { roughness: 0.55 }); M.mirror = std(0xbfdbe8, { roughness: 0.1, metalness: 0.5 });
  if (tex && tex.dotTex) M.perfMat.map = tex.dotTex;
  M.wireMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6, side: THREE.DoubleSide, alphaTest: 0.5 });
  if (tex && tex.wireTex) M.wireMat.map = tex.wireTex;
  const perf = (w, h) => ({ isPerfToken: true, w, h });
  const panel = i => tex && tex.panelMats ? tex.panelMats[i] : [M.strip, M.strip, M.strip, M.strip, M.strip, M.strip];
  M.hp = { post: M.post, board: M.board, lip: M.lip };
  M.mesAtn = { orange: M.orange, black: M.black, perf };
  M.mesTal = { orange: M.carbon, black: M.black, perf };
  M.gon = { black: M.black, perf };
  M.per = { black: M.black, perf };
  M.bat = { frame: M.frame, deck: M.deck, strip: M.strip, panel };
  M.neu = { frame: M.frame };
  M.jaula = { frame: M.frame, wire: (w, h) => ({ isPerfToken: true, kind: 'wire', w, h, tw: 10, th: 10 }) };
  M.resp = { wall: std(0xa4a9ad, { roughness: 0.8 }), door: std(0x80868a, { roughness: 0.6, metalness: 0.2 }) };
  M.cabhp = { black: M.black, perf, header: tex && tex.headMats ? tex.headMats : [M.strip, M.strip, M.strip, M.strip, M.strip, M.strip] };
  // Fachada: ACM brillante, revestimiento acanalado, perfilería roja y vidrio
  M.acm = std(0xf2f3f4, { roughness: 0.28, metalness: 0.15 }); M.acmG = std(0xc7c8ca, { roughness: 0.3, metalness: 0.2 });
  M.acmD = std(0x6a6d72, { roughness: 0.3, metalness: 0.35 }); M.clad = std(0x3f4247, { roughness: 0.4, metalness: 0.55 });
  M.louv = std(0x25272b, { roughness: 0.35, metalness: 0.6 }); M.corn = std(0xfff0d2, { roughness: 0.35, metalness: 0.1 });
  M.redAl = std(0xd9202b, { roughness: 0.25, metalness: 0.55 }); M.backW = std(0x30343a, { roughness: 0.9 });
  M.adP = std(0xe6e7e9, { roughness: 0.4 }); M.adF = std(0x80848a, { roughness: 0.35, metalness: 0.5 });
  M.glassM = new THREE.MeshStandardMaterial({ color: 0xb4d4e2, transparent: true, opacity: 0.14, roughness: 0.1, metalness: 0, side: THREE.DoubleSide, depthWrite: false });   // sin reflejo de cielo: el vidrio deja ver lo que hay detrás
  M.struct = std(0x1b1d20, { roughness: 0.7, metalness: 0.2, emissive: 0x101215 });
  M.pal = { frame: std(0x33363b, { roughness: 0.5, metalness: 0.4 }), beam: std(0xe8501a, { roughness: 0.4, metalness: 0.3 }) };
  M.tileW = tex && tex.tileW || null; M.tileB = tex && tex.tileB || null; M.radial = tex && tex.radial || null;
  M.envMats = [M.acm, M.acmG, M.acmD, M.clad, M.louv, M.corn, M.redAl, M.adF, M.steelb];
  if (tex && tex.env) M.envMats.forEach(x => { x.envMap = tex.env; x.envMapIntensity = 0.9; });
  return M;
}

function mergeRoots(THREE, roots, MM) {
  const bucket = new Map(), loose = [], out = new THREE.Group();
  roots.forEach(r => r.updateMatrixWorld(true));
  roots.forEach(r => r.traverse(o => {
    if (!o.isMesh) return;
    const m = o.material;
    if (Array.isArray(m)) { loose.push(o); return; }
    const key = m.isPerfToken ? (m.kind || 'perf') : m.uuid;
    if (!bucket.has(key)) bucket.set(key, { mat: m.isPerfToken ? (m.kind === 'wire' ? MM.wireMat : MM.perfMat) : m, items: [] });
    bucket.get(key).items.push(o);
  }));
  bucket.forEach(b => {
    const pos = [], nor = [], uv = [], idx = []; let base = 0;
    b.items.forEach(o => {
      const g = o.geometry.clone(); g.applyMatrix4(o.matrixWorld);
      const p = g.attributes.position.array, n = g.attributes.normal.array, u = g.attributes.uv.array;
      const m = o.material, sx = m.isPerfToken ? m.w / (m.tw || 5) : 1, sy = m.isPerfToken ? m.h / (m.th || 5) : 1;
      for (let i = 0; i < p.length; i++) pos.push(p[i]);
      for (let i = 0; i < n.length; i++) nor.push(n[i]);
      for (let i = 0; i < u.length; i += 2) uv.push(u[i] * sx, u[i + 1] * sy);
      const ix = g.index.array;
      for (let i = 0; i < ix.length; i++) idx.push(ix[i] + base);
      base += p.length / 3; g.dispose();
    });
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    geo.setIndex(idx);
    out.add(new THREE.Mesh(geo, b.mat));
  });
  loose.forEach(o => { const c = new THREE.Mesh(o.geometry, o.material); c.applyMatrix4(o.matrixWorld); out.add(c); });
  return out;
}

function buildShell(THREE, DATA, texs) {
  const C = DATA.contour, XB = DATA.XB;
  const walls = new THREE.Group(), ceil = new THREE.Group(), floors = new THREE.Group(), facade = new THREE.Group();
  let area = 0;
  for (let i = 0; i < C.length; i++) { const a = C[i], b = C[(i + 1) % C.length]; area += a[0] * b[1] - b[0] * a[1]; }
  const ccw = area > 0;
  const wallMat = new THREE.MeshStandardMaterial({ color: 0xcfd3d0, transparent: true, opacity: 0.28, roughness: 0.9, side: THREE.DoubleSide, depthWrite: false });
  const edgeMat = new THREE.LineBasicMaterial({ color: 0x7f8a84 });
  for (let i = 0; i < C.length; i++) {
    const a = C[i], b = C[(i + 1) % C.length];
    const pieces = [];
    if ((a[0] - XB) * (b[0] - XB) < 0) {
      const t = (XB - a[0]) / (b[0] - a[0]), m = [XB, a[1] + t * (b[1] - a[1])];
      pieces.push([a, m], [m, b]);
    } else pieces.push([a, b]);
    pieces.forEach(([p0, p1]) => {
      const dx = p1[0] - p0[0], dy = p1[1] - p0[1], len = Math.hypot(dx, dy);
      if (len < 1) return;
      const isFacade = (Math.abs(p0[1] - OY) < 1 && Math.abs(p1[1] - OY) < 1) || (p0[0] > 17300 && p1[0] > 17300) || !!(DATA.open && DATA.open.includes(i));   // DATA.open: lados sin muro
      const h = isFacade ? 836 : (((p0[0] + p1[0]) / 2 < XB) ? H_BOD : H_SALA);
      if (isFacade) return;
      const nx = ccw ? dy / len : -dy / len, ny = ccw ? -dx / len : dx / len;
      const cx = (p0[0] + p1[0]) / 2 + nx * WALL_T / 2, cy = (p0[1] + p1[1]) / 2 + ny * WALL_T / 2;
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(len, h, WALL_T), wallMat);
      mesh.position.set(px(cx), h / 2, pz(cy));
      mesh.rotation.y = Math.atan2(dy, dx);
      mesh.add(new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry), edgeMat));
      walls.add(mesh);
    });
  }
  const shape = ring => new THREE.Shape(ring.map(p => new THREE.Vector2(px(p[0]), p[1] - OY)));
  const floorMat = c => new THREE.MeshStandardMaterial({ color: c, roughness: 0.95, side: THREE.DoubleSide });
  const ceilMat = new THREE.MeshStandardMaterial({ color: 0xdfe6ea, transparent: true, opacity: 0.35, side: THREE.DoubleSide, depthWrite: false });
  [[DATA.bodega, 0x8e9391, H_BOD], [DATA.sala, 0xa6aaa6, H_SALA]].forEach(([ring, col, h]) => {
    const f = new THREE.Mesh(new THREE.ShapeGeometry(shape(ring)), floorMat(col));
    f.rotation.x = -Math.PI / 2; floors.add(f);
    const c = new THREE.Mesh(new THREE.ShapeGeometry(shape(ring)), ceilMat);
    c.rotation.x = -Math.PI / 2; c.position.y = h; ceil.add(c);
  });
  const s = DATA.step, sh = H_SALA - H_BOD, sl = Math.abs(s[1][1] - s[0][1]);
  const step = new THREE.Mesh(new THREE.PlaneGeometry(sl, sh), new THREE.MeshStandardMaterial({ color: 0x9db8d6, transparent: true, opacity: 0.3, side: THREE.DoubleSide, depthWrite: false }));
  step.rotation.y = Math.PI / 2;
  step.position.set(px(DATA.XB), H_BOD + sh / 2, pz((s[0][1] + s[1][1]) / 2));
  ceil.add(step);
  return { walls, ceil, floors, facade };
}


function buildServicios(THREE, M, bump) {
  const g = new THREE.Group();
  const pb = (x0, x1, y0, y1, z0, z1, mat) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, z1 - z0, y1 - y0), mat);
    m.position.set(px((x0 + x1) / 2), (z0 + z1) / 2, pz((y0 + y1) / 2)); g.add(m); return m;
  };
  const cyl = (x, y, rx, ry, z0, z1, mat) => {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, z1 - z0, 20), mat);
    m.scale.set(rx, 1, ry); m.position.set(px(x), (z0 + z1) / 2, pz(y)); g.add(m); return m;
  };
  const HP = 240;   // altura supuesta de los tabiques
  // Tabiques (doble línea del plano)
  [[14420, 14483, 1539, 1551], [14563, 14802, 1539, 1551], [14887, 14948, 1539, 1551], [15043, 15057, 1539, 1551],
   [14732, 14742, 1551, 1771], [14887, 14898, 1539, 1771], [15047, 15057, 1551, 1771], [14742, 14807, 1642, 1651]]
    .forEach(w => pb(w[0], w[1], w[2], w[3], 0, HP, M.part));
  // Puertas cerradas con dintel: cocina (80), baño (75) y camarín (95)
  [[14483, 14563, 1539, 1551], [14807, 14882, 1642, 1651], [14948, 15043, 1539, 1551]].forEach(d => {
    const yc = (d[2] + d[3]) / 2;
    pb(d[0], d[1], d[2], d[3], 210, HP, M.part);
    pb(d[0], d[1], yc - 1.75, yc + 1.75, 0, 210, M.door);
    pb(d[1] - 8, d[1] - 5, yc - 3.5, yc + 3.5, 98, 102, M.steelb);
    bump('Servicios: puerta');
  });
  // ---- Cocina ----
  pb(14422, 14482, 1706, 1766, 0, 180, M.fridgeM); pb(14482, 14484, 1711, 1715, 70, 140, M.steelb);   // refrigerador y manilla
  pb(14420, 14480, 1550, 1701, 0, 85, M.cabn); pb(14420, 14480, 1550, 1701, 85, 88, M.top);          // mesón de cocina
  pb(14430, 14475, 1646, 1696, 88, 89, M.steelb); pb(14434, 14471, 1650, 1692, 89, 89.5, M.dark);   // lavaplatos
  cyl(14438, 1671, 1.5, 1.5, 89, 112, M.steelb); pb(14438, 14452, 1670, 1672, 110, 112, M.steelb);  // grifería
  pb(14426, 14466, 1602, 1642, 88, 128, M.fridgeM); pb(14466, 14467.5, 1615, 1630, 100, 115, M.blueM);   // máquina de agua
  pb(14431, 14461, 1558, 1598, 88, 116, M.dark); pb(14461, 14462, 1562, 1585, 92, 112, M.mirror); pb(14461, 14463, 1589, 1591, 95, 110, M.steelb);   // microondas
  // mesa de 120 × 70 y cuatro sillas
  pb(14612, 14732, 1623, 1693, 73, 75, M.wood);
  [[14615, 1626], [14725, 1626], [14615, 1686], [14725, 1686]].forEach(([x, y]) => pb(x, x + 4, y, y + 4, 0, 73, M.steelb));
  [[14625, 14660, 1601, 1631, 0], [14685, 14719, 1601, 1631, 0], [14625, 14660, 1686, 1716, 1], [14685, 14719, 1686, 1716, 1]].forEach(c => {
    pb(c[0], c[1], c[2], c[3], 43, 47, M.chairM);
    [[c[0] + 2, c[2] + 2], [c[1] - 5, c[2] + 2], [c[0] + 2, c[3] - 5], [c[1] - 5, c[3] - 5]].forEach(([x, y]) => pb(x, x + 3, y, y + 3, 0, 43, M.steelb));
    c[4] ? pb(c[0], c[1], c[3] - 3, c[3], 47, 88, M.chairM) : pb(c[0], c[1], c[2], c[2] + 3, 47, 88, M.chairM);
    bump('Servicios: silla');
  });
  // lockers: 6 columnas de 30 cm, dos puertas cada una
  for (let i = 0; i < 6; i++) {
    const x0 = 14586 + 30 * i;
    pb(x0 + 0.3, x0 + 29.7, 1494, 1539, 0, 180, M.locker);
    [[2, 88], [92, 178]].forEach(([z0, z1]) => {
      pb(x0 + 1, x0 + 29, 1493.2, 1494, z0, z1, M.lockdoor); pb(x0 + 24, x0 + 27, 1492.4, 1493.2, (z0 + z1) / 2 - 6, (z0 + z1) / 2 + 6, M.steelb);
      bump('Servicios: locker');
    });
  }
  // ---- Baño ----
  const wc = (cx, cy, dir, tank0, tank1) => {          // dir +1: taza hacia +x; -1: hacia -x
    cyl(cx, cy, 20, 13, 0, 32, M.cer); cyl(cx, cy, 26, 17, 32, 42, M.cer);
    pb(tank0, tank1, cy - 19, cy + 19, 32, 82, M.cer); cyl((tank0 + tank1) / 2, cy, 2, 2, 82, 83.5, M.steelb);
    bump('Servicios: WC');
  };
  wc(14784, 1742, 1, 14743, 14758);                                    // baño: contra el muro oeste
  wc(15010, 1744, -1, 15033, 15048);                                   // camarín: contra el muro este
  const lav = (x0, x1, y0, y1, wallX, dir) => {        // lavamanos con pedestal, grifería y espejo
    const yc = (y0 + y1) / 2;
    cyl(dir > 0 ? x0 + 9 : x1 - 9, yc, 6, 6, 0, 72, M.cer); pb(x0, x1, y0, y1, 72, 88, M.cer);
    cyl(dir > 0 ? x0 + 4 : x1 - 4, yc, 1.5, 1.5, 88, 100, M.steelb);
    pb(dir > 0 ? x0 + 4 : x1 - 12, dir > 0 ? x0 + 12 : x1 - 4, yc - 0.5, yc + 0.5, 98, 100, M.steelb);
    pb(wallX - (dir > 0 ? 0 : 2), wallX + (dir > 0 ? 2 : 0), y0 + 2, y1 - 2, 105, 165, M.mirror);
    bump('Servicios: lavamanos');
  };
  lav(14743, 14779, 1668, 1710, 14742, 1);
  lav(15011, 15047, 1562, 1604, 15047, -1);
  // lavamopa: receptáculo de piso con pretil de 30 cm y grifo en el muro
  pb(14746, 14800, 1558, 1632, 0, 25, M.cer); pb(14750, 14796, 1562, 1628, 25, 25.5, M.dark);
  pb(14800, 14807, 1552, 1642, 0, 30, M.part);
  cyl(14745, 1595, 1.5, 1.5, 90, 110, M.steelb); pb(14745, 14756, 1594, 1596, 108, 110, M.steelb);
  return g;
}

function ringVSpan(ring, x) {
  const ys = [];
  for (let i = 0; i < ring.length - 1; i++) {
    const a = ring[i], b = ring[i + 1];
    if (a[0] !== b[0] && (a[0] - x) * (b[0] - x) <= 0) ys.push(a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0]));
  }
  ys.sort((p, q) => p - q);
  return ys.length >= 2 ? [ys[0], ys[ys.length - 1]] : null;
}
function ringHSpan(ring, y) {
  const xs = [];
  for (let i = 0; i < ring.length - 1; i++) {
    const a = ring[i], b = ring[i + 1];
    if (a[1] !== b[1] && (a[1] - y) * (b[1] - y) <= 0) xs.push(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]));
  }
  xs.sort((p, q) => p - q);
  return xs.length >= 2 ? [xs[0], xs[xs.length - 1]] : null;
}

// Fachada con volumen, a partir de las cotas de las elevaciones Sur y Oriente
function buildFacade3D(THREE, M, sign) {
  const mkFrame = (ax, ay, phi) => { const g = new THREE.Group(); g.position.set(px(ax), 0, pz(ay)); g.rotation.y = phi; return g; };
  const mkBox = (g, clip) => (u0, u1, h0, h1, d0, d1, mat) => {
    u1 = Math.min(u1, clip);
    if (u1 - u0 < 0.05 || h1 - h0 < 0.05) return;
    const m = new THREE.Mesh(new THREE.BoxGeometry(u1 - u0, h1 - h0, d1 - d0), mat);
    m.position.set((u0 + u1) / 2, (h0 + h1) / 2, (d0 + d1) / 2); g.add(m);
  };
  const panels = (bx, cols, rows, mat) => {
    for (let i = 0; i < cols.length - 1; i++) for (let j = 0; j < rows.length - 1; j++)
      bx(cols[i] + 0.6, cols[i + 1] - 0.6, rows[j] + 0.6, rows[j + 1] - 0.6, 0, 3, mat);
  };
  const adFrame = (bx, u0, u1, h0, h1) => {
    const e = 6;
    bx(u0, u1, h0, h0 + e, 4, 8, M.adF); bx(u0, u1, h1 - e, h1, 4, 8, M.adF);
    bx(u0, u0 + e, h0 + e, h1 - e, 4, 8, M.adF); bx(u1 - e, u1, h0 + e, h1 - e, 4, 8, M.adF);
    bx(u0 + e, u1 - e, h0 + e, h1 - e, 4, 6, M.adP);
  };
  const signStack = (g, tex, u0, w, h0, hh) => {          // letras y bandas con relieve de unos 5 cm, en capas
    const front = new THREE.MeshBasicMaterial({ map: tex || null, transparent: true, alphaTest: 0.4 });
    const back = new THREE.MeshBasicMaterial({ map: tex || null, transparent: true, alphaTest: 0.4, color: 0x45474b });
    for (let k = 0; k < 6; k++) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, hh), k < 5 ? back : front);
      m.position.set(u0 + w / 2, h0 + hh / 2, 3.2 + k * 0.9); g.add(m);
    }
  };
  const halos = new THREE.Group();
  const halo = (g, u, h, w, hh, color, op) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, hh), new THREE.MeshBasicMaterial({ map: M.radial || null, color, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false }));
    m.position.set(u, h, 12); g.add(m);
  };

  // ---------- Fachada Sur (muro y = 516, de x = 14392 a 17370) ----------
  const LS = 2978, gS = mkFrame(14392, 516, 0), bs = mkBox(gS, LS);
  [[0, 1694], [1980, 2120], [2640, LS]].forEach(([a, b]) => bs(a, b, 0, 280, -8, 0, M.backW));
  bs(0, LS, 280, 836, -8, 0, M.backW);
  [[0, 153], [358, 1694], [2640, LS]].forEach(([a, b]) => bs(a, b, 0, 280, 0, 4, M.acmG));
  [[153, 358], [1980, 2120]].forEach(([a, b]) => {                      // puertas rojas
    bs(a, b, 0, 280, 0, 6, M.redAl); const c = (a + b) / 2;
    if (a === 153) { bs(c - 0.6, c + 0.6, 0, 280, 6, 6.6, M.louv); bs(c - 12, c - 8, 96, 112, 6, 9, M.steelb); bs(c + 8, c + 12, 96, 112, 6, 9, M.steelb); }   // solo la salida del oeste es puerta (dos hojas de 108 cm)
  });
  const bay = (u0, u1, n) => {                                          // vitrinas con perfilería roja y vidrio
    const w = (u1 - u0) / n;
    for (let i = 0; i <= n; i++) bs(u0 + i * w - 3, u0 + i * w + 3, 0, 280, 0, 8, M.redAl);
    [[0, 4], [90, 96], [274, 280]].forEach(([a, b]) => bs(u0, u1, a, b, 0, 8, M.redAl));
    for (let i = 0; i < n; i++) { bs(u0 + i * w + 3, u0 + (i + 1) * w - 3, 4, 90, 3, 4, M.glassM); bs(u0 + i * w + 3, u0 + (i + 1) * w - 3, 96, 274, 3, 4, M.glassM); }
  };
  bay(2120, 2640, 5);
  {   // Acceso principal (u 1694-1980): paño fijo, puerta doble vidriada de 168 cm (dos hojas de 84 cm) y paño superior
    const fixed = (a, b) => {
      bs(a, a + 6, 0, 280, 0, 8, M.redAl); bs(b - 6, b, 0, 280, 0, 8, M.redAl);
      [[0, 4], [90, 96], [274, 280]].forEach(([p, q]) => bs(a, b, p, q, 0, 8, M.redAl));
      bs(a + 6, b - 6, 4, 90, 3, 4, M.glassM); bs(a + 6, b - 6, 96, 274, 3, 4, M.glassM);
    };
    fixed(1694, 1801);
    const leaf = (a, b) => {
      bs(a, a + 6, 0, 210, 0, 8, M.redAl); bs(b - 6, b, 0, 210, 0, 8, M.redAl);
      [[0, 12], [85, 93], [204, 210]].forEach(([p, q]) => bs(a, b, p, q, 0, 8, M.redAl));
      bs(a + 6, b - 6, 12, 85, 3, 4, M.glassM); bs(a + 6, b - 6, 93, 204, 3, 4, M.glassM);
    };
    leaf(1801, 1885); leaf(1885, 1969);
    bs(1801, 1969, 210, 216, 0, 8, M.redAl); bs(1801, 1969, 274, 280, 0, 8, M.redAl); bs(1801, 1969, 216, 274, 3, 4, M.glassM);
    bs(1969, 1980, 0, 280, 0, 8, M.redAl);
    bs(1876, 1879, 90, 135, 8, 11, M.steelb); bs(1891, 1894, 90, 135, 8, 11, M.steelb);
  }
  [[456, 698], [877, 1117], [1298, 1538], [2734, 2974]].forEach(([a, b]) => adFrame(bs, a, b, 139, 263));
  panels(bs, [0, 205, 443, 685, 923, 1165, 1403, 1644, 1883, 1981], [280, 397], M.acm);        // franja blanca sobre la bodega
  panels(bs, [1981, 2124, 2363, 2604, 2843, LS], [280, 382, 502, 622, 742, 780], M.acm);       // paño blanco de la sala
  const pil = [[0, 20], [660, 680], [1320, 1340], [1961, 1981]];
  pil.forEach(([a, b]) => bs(a, b, 397, 780, 0, 14, M.acmD));                                  // pilastras
  for (let u = 22; u < 1960; u += 12) {                                                        // revestimiento acanalado
    if (pil.some(([a, b]) => u + 6 > a && u < b)) continue;
    bs(u, u + 6, 397, 780, 0, 4, M.clad);
  }
  for (let k = 0; k < 9; k++) {                                                                // rejillas de ventilación de 3,99 a 4,79 m
    const h0 = 399 + 10 * k; let u0 = 20;
    [[20, 660], [680, 1320], [1340, 1961]].forEach(([a, b]) => bs(a, b, h0, h0 + 7, 0, 12, M.louv));
  }
  bs(0, LS, 780, 836, 0, 26, M.corn);                                                          // cornisa de 56 cm
  signStack(gS, sign && sign.sur, 2060, 918, 509, 221);

  // ---------- Fachada Oriente (muro diagonal, de (17370, 516) a (17712, 1798)) ----------
  const LO = 1327, phi = Math.atan2(1282, 342), gO = mkFrame(17370, 516, phi), bo = mkBox(gO, LO);
  bo(0, LO, 0, 836, -8, 0, M.backW);
  bo(0, LO, 0, 281, 0, 4, M.acmG);
  [[109, 349], [525, 763], [939, 1177]].forEach(([a, b]) => adFrame(bo, a, b, 139, 263));
  panels(bo, [0, 171, 405, 643, 878, 1116, LO], [281, 385, 505, 625, 745, 780], M.acm);
  bo(0, LO, 780, 836, 0, 26, M.corn);
  signStack(gO, sign && sign.ori, 0, LO, 530, 187);

  // Resplandor nocturno del letrero: logo retroiluminado y franja LED sobre el naranjo
  const hS = mkFrame(14392, 516, 0), hO = mkFrame(17370, 516, phi);
  halo(hS, 2363, 619, 830, 375, 0xfff1dc, 0.5); halo(hS, 2822, 619, 405, 177, 0xff7a1a, 0.6);
  halo(hO, 644, 623, 805, 337, 0xfff1dc, 0.5); halo(hO, 172, 623, 414, 140, 0xff7a1a, 0.6); halo(hO, 1128, 623, 478, 140, 0xff7a1a, 0.6);
  halos.add(hS, hO); halos.visible = false;
  return { frames: [gS, gO], halos };
}

// Cielos de sala y bodega: americano blanco o negro, o pintura negra con la estructura a la vista
function buildCeilings(THREE, DATA, M) {
  const root = new THREE.Group(), Z = {};
  let nightOn = false;
  const shape = ring => new THREE.Shape(ring.map(p => new THREE.Vector2(px(p[0]), p[1] - OY)));
  const mkTile = (map, color) => new THREE.MeshBasicMaterial(map ? { map, side: THREE.DoubleSide } : { color, side: THREE.DoubleSide });
  const tileW = mkTile(M.tileW, 0xefeff0), tileB = mkTile(M.tileB, 0x1b1c1e);
  const stepMat = new THREE.MeshBasicMaterial({ color: 0xefeff0, side: THREE.DoubleSide });
  const deckMat = M.struct.clone(); deckMat.side = THREE.DoubleSide;
  const step = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), stepMat); step.visible = false; root.add(step);
  const zones = { sala: DATA.sala, bodega: DATA.bodega };
  Object.keys(zones).forEach(name => {
    const ring = zones[name], geo = new THREE.ShapeGeometry(shape(ring));
    const white = new THREE.Mesh(geo, tileW), black = new THREE.Mesh(geo, tileB);
    [white, black].forEach(x => { x.rotation.x = -Math.PI / 2; x.visible = false; root.add(x); });
    const structure = new THREE.Group(); structure.visible = false; root.add(structure);
    Z[name] = { ring, white, black, structure, mode: 'none', h: 0 };
  });
  // Muros negros: con cielo de pintura negra, los muros de la zona se pintan de negro desde una altura (por defecto, 10 cm sobre las luces)
  const paintRoot = new THREE.Group(), paintMat = new THREE.MeshStandardMaterial({ color: 0x17191b, roughness: 0.95, side: THREE.DoubleSide });
  const baseMat = new THREE.MeshStandardMaterial({ color: 0xc9cdca, roughness: 0.95, side: THREE.DoubleSide });
  const WALLH = { sala: H_SALA, bodega: H_BOD }, paintG = { sala: new THREE.Group(), bodega: new THREE.Group() };
  Object.keys(paintG).forEach(k => { paintG[k].visible = false; paintRoot.add(paintG[k]); });
  (() => {
    const Cn = DATA.contour; let ar = 0;
    for (let i = 0; i < Cn.length; i++) { const a = Cn[i], b = Cn[(i + 1) % Cn.length]; ar += a[0] * b[1] - b[0] * a[1]; }
    const sg = ar > 0 ? 1 : -1;
    for (let i = 0; i < Cn.length; i++) {
      const a = Cn[i], b = Cn[(i + 1) % Cn.length], pcs = [];
      if ((a[0] - DATA.XB) * (b[0] - DATA.XB) < 0) { const t = (DATA.XB - a[0]) / (b[0] - a[0]); pcs.push([a, [DATA.XB, a[1] + t * (b[1] - a[1])]], [[DATA.XB, a[1] + t * (b[1] - a[1])], b]); } else pcs.push([a, b]);
      pcs.forEach(([p0, p1]) => {
        const dx = p1[0] - p0[0], dy = p1[1] - p0[1], len = Math.hypot(dx, dy); if (len < 1) return;
        if (DATA.open && DATA.open.includes(i)) return;                      // lado sin muro
        const fac = (Math.abs(p0[1] - OY) < 1 && Math.abs(p1[1] - OY) < 1) || (p0[0] > 17300 && p1[0] > 17300);
        const off = fac ? 9.2 : 1.2, cx = (p0[0] + p1[0]) / 2 + (-sg * dy / len) * off, cy = (p0[1] + p1[1]) / 2 + (sg * dx / len) * off;
        const q = new THREE.Mesh(new THREE.PlaneGeometry(len, 1), paintMat);
        q.rotation.y = Math.atan2(dy, dx); q.position.x = px(cx); q.position.z = pz(cy); q.userData.facadeSkin = fac;
        const grp = paintG[(p0[0] + p1[0]) / 2 < DATA.XB ? 'bodega' : 'sala'];
        grp.add(q);
        const q2 = new THREE.Mesh(new THREE.PlaneGeometry(len, 1), baseMat);   // tramo de muro sin pintar entre el tope del muro y el negro
        q2.rotation.y = q.rotation.y; q2.position.x = q.position.x; q2.position.z = q.position.z; q2.userData.base = true; q2.userData.facadeSkin = fac; grp.add(q2);
      });
    }
    const sp = ringVSpan(DATA.sala, DATA.XB);                  // cara de la sala en el escalón entre alturas
    if (sp) { const q = new THREE.Mesh(new THREE.PlaneGeometry(sp[1] - sp[0], 1), paintMat); q.rotation.y = Math.PI / 2; q.position.set(px(DATA.XB) + 1.2, 0, pz((sp[0] + sp[1]) / 2)); q.userData.step = true; paintG.sala.add(q); }
  })();
  const refreshPaint = name => {
    const z = Z[name], on = !!z.pon && z.pw != null, g = paintG[name]; g.visible = on; if (!on) return;
    // sin cielo, el muro llega a su altura; con americano, hasta el cielo; con pintura negra, hasta la plancha de techo sobre las cerchas
    const top0 = z.mode === 'none' ? WALLH[name] : (z.mode === 'pn' ? z.h + 80 : z.h);
    g.children.forEach(q => {
      if (q.userData.base) { const lo = WALLH[name], on2 = z.mode === 'pn' && z.pw > lo + 0.5; q.visible = on2; if (on2) { q.scale.y = z.pw - lo; q.position.y = (lo + z.pw) / 2; } return; }
      const top = top0, y0 = q.userData.step ? Math.max(z.pw, H_BOD) : z.pw, hh = Math.max(1, top - y0); q.visible = top > y0; q.scale.y = hh; q.position.y = y0 + hh / 2; });
  };
  const buildStructure = (z, h) => {
    const g = z.structure; while (g.children.length) g.remove(g.children[0]);
    const box = (sx, sy, sz, x, y, zz) => { const mm = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), M.struct); mm.position.set(x, y, zz); g.add(mm); return mm; };
    const ys = z.ring.map(p => p[1]), ymin = Math.min(...ys), ymax = Math.max(...ys);
    [15052, 15712, 16372, 17040, 17545].forEach(ax => {            // cerchas sobre los ejes estructurales (indicativas)
      const sp = ringVSpan(z.ring, ax); if (!sp) return;
      const y0 = sp[0] + 8, y1 = sp[1] - 8, L = y1 - y0, X = px(ax), Zc = pz((y0 + y1) / 2);
      if (L < 60) return;
      box(14, 10, L, X, h + 5, Zc); box(14, 10, L, X, h + 65, Zc);
      const n = Math.max(1, Math.round(L / 120)), stp = L / n;
      for (let k = 0; k < n; k++) {
        const za = pz(y0 + k * stp), zb = pz(y0 + (k + 0.5) * stp), zc = pz(y0 + (k + 1) * stp);
        [[za, h + 10, zb, h + 60], [zb, h + 60, zc, h + 10]].forEach(([z0, hy0, z1, hy1]) => {
          const dz = z1 - z0, dy = hy1 - hy0, d = box(6, Math.hypot(dz, dy), 6, X, (hy0 + hy1) / 2, (z0 + z1) / 2);
          d.rotation.x = Math.atan2(dz, dy);
        });
      }
    });
    for (let y = ymin + 40; y < ymax; y += 160) {                   // correas
      const sp = ringHSpan(z.ring, y); if (!sp) continue;
      const x0 = sp[0] + 8, x1 = sp[1] - 8; if (x1 - x0 < 60) continue;
      box(x1 - x0, 8, 10, px((x0 + x1) / 2), h + 74, pz(y));
    }
    const deck = new THREE.Mesh(new THREE.ShapeGeometry(shape(z.ring)), deckMat);   // plancha de techo, visible desde abajo
    deck.rotation.x = -Math.PI / 2; deck.position.y = h + 80; g.add(deck);
  };
  const eff = z => z.mode === 'none' ? null : (z.mode === 'pn' ? z.h + 80 : z.h);
  const tint = () => {
    tileW.color.setScalar(nightOn ? 0.2 : 1);
    stepMat.color.setHex(stepMat.userData.white ? 0xefeff0 : 0x1b1c1e); if (nightOn) stepMat.color.multiplyScalar(0.2);
  };
  const updateStep = () => {                                       // si las alturas difieren, se unen con una cara vertical opaca
    const a = eff(Z.sala), b = eff(Z.bodega);
    if (a === null || b === null || Math.abs(a - b) < 1) { step.visible = false; return; }
    const sp = ringVSpan(Z.sala.ring, DATA.XB); if (!sp) { step.visible = false; return; }
    const hi = a > b ? Z.sala : Z.bodega, lo = Math.min(a, b), top = Math.max(a, b);
    stepMat.userData.white = hi.mode === 'aw'; tint();
    step.geometry.dispose(); step.geometry = new THREE.PlaneGeometry(sp[1] - sp[0], top - lo);
    step.position.set(px(DATA.XB), (lo + top) / 2, pz((sp[0] + sp[1]) / 2)); step.rotation.y = Math.PI / 2; step.visible = true;
  };
  const set = (name, mode, h) => {
    const z = Z[name]; z.mode = mode; z.h = h;
    z.white.visible = mode === 'aw'; z.black.visible = mode === 'ab';
    z.white.position.y = h; z.black.position.y = h;
    z.structure.visible = mode === 'pn';
    if (mode === 'pn') buildStructure(z, h);
    updateStep(); refreshPaint(name);
  };
  const top = name => Z[name].mode === 'none' ? null : Z[name].h;
  const night = on => { nightOn = on; tint(); };
  const paint = (name, on, y0) => { Z[name].pon = on; Z[name].pw = y0; refreshPaint(name); };
  return { root, set, top, night, paint, paintRoot };
}

// Iluminación nocturna: charcos de luz en el piso, resplandor de cada luminaria y luces puntuales, con ganancia regulable
function buildNightFx(THREE, DATA, M) {
  const g = new THREE.Group(), LH = { L02: 400, L03: 360, F01: 400 };
  const pos = [], uv = [], idx = [], glow = [], lights = [], glowMeta = [], lightMeta = [], THK = { L02: 6, L03: 9, F01: 5, L01: 6 };
  const quad = (x, y, s) => {
    const b = pos.length / 3, X = px(x), Zc = pz(y);
    pos.push(X - s / 2, 0.8, Zc - s / 2, X + s / 2, 0.8, Zc - s / 2, X + s / 2, 0.8, Zc + s / 2, X - s / 2, 0.8, Zc + s / 2);
    uv.push(0, 0, 1, 0, 1, 1, 0, 1); idx.push(b, b + 2, b + 1, b, b + 3, b + 2);
  };
  DATA.luz.forEach(l => { if (l.t === 'L01') return; if (!l.alt) quad(l.x, l.y, l.t === 'L02' ? 240 : (l.t === 'F01' ? 150 : 210)); glow.push(px(l.x), (l.h || LH[l.t]) + 3, pz(l.y)); glowMeta.push({ h0: l.h || LH[l.t], zone: l.x < DATA.XB ? 'b' : 's' }); });
  DATA.rails.forEach(r => { quad(r.x, r.y, 180); glow.push(px(r.x), 403, pz(r.y)); glowMeta.push({ h0: 400, zone: r.x < DATA.XB ? 'b' : 's' }); });
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); geo.setIndex(idx);
  const poolMat = new THREE.MeshBasicMaterial({ map: M.radial || null, color: 0xffe9c8, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide });
  g.add(new THREE.Mesh(geo, poolMat));
  const pg = new THREE.BufferGeometry(), glowAttr = new THREE.Float32BufferAttribute(glow, 3); pg.setAttribute('position', glowAttr);
  const glowMat = new THREE.PointsMaterial({ map: M.radial || null, color: 0xfff4e0, size: 60, sizeAttenuation: true, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false });
  g.add(new THREE.Points(pg, glowMat));
  // Cada foco apunta recto hacia abajo: haz de 100° (50° a cada lado) a plena luz y caída suave hasta 140° (70°); sobre el horizonte no emite
  const SP_ANG = 70 * Math.PI / 180, SP_PEN = 1 - 50 / 70;
  const addL = (x, y, h, base, dist, meta) => {
    const L = new THREE.SpotLight(0xfff1de, base, dist, SP_ANG, SP_PEN, 1.2);
    if (meta) lightMeta.push({ L, h0: meta.h0, off: meta.h0 - h, zone: x < DATA.XB ? 'b' : 's', thick: THK[meta.t] || 6 });
    L.userData.base = base; L.position.set(px(x), h, pz(y)); L.target.position.set(px(x), 0, pz(y));
    g.add(L); g.add(L.target); lights.push(L);
  };
  const nL02 = DATA.luz.filter(l => l.t === 'L02').length, stepL = nL02 > 100 ? 12 : 6;      // con muchas luminarias se muestrean menos focos, para no pasar el límite de luces del equipo
  DATA.luz.filter(l => l.t === 'L02' && l.x > DATA.XB).filter((l, i) => i % stepL === 0).forEach(l => addL(l.x, l.y, (l.h || 400) - 15, 1.5, 1100, { h0: l.h || 400, t: l.t }));
  DATA.luz.filter(l => l.t === 'F01').filter((l, i) => i % 15 === 0).forEach(l => addL(l.x, l.y, (l.h || 400) - 5, 0.9, 600, { h0: l.h || 400, t: l.t }));
  DATA.luz.filter(l => l.t === 'L03').filter((l, i) => i % 9 === 0).forEach(l => addL(l.x, l.y, 350, 1.0, 850, { h0: l.h || 360, t: l.t }));
  DATA.luz.filter(l => l.t === 'L01').filter((l, i) => i % 3 === 0).forEach(l => addL(l.x, l.y, 255, 0.8, 500, { h0: l.h || 270, t: l.t }));
  g.userData.setTops = (topS, topB) => {         // las luces nocturnas siguen a su luminaria cuando el cielo la baja
    const eff = (h0, thick, zone) => { const t = zone === 's' ? topS : topB; return (t !== null && h0 + thick > t) ? t - thick : h0; };
    glowMeta.forEach((mt, i) => { glowAttr.array[i * 3 + 1] = eff(mt.h0, 6, mt.zone) + 3; });
    glowAttr.needsUpdate = true;
    lightMeta.forEach(lm => { lm.L.position.y = eff(lm.h0, lm.thick, lm.zone) - lm.off; });
  };
  g.userData.setGain = k => {
    lights.forEach(L => { L.intensity = L.userData.base * k; });
    poolMat.opacity = Math.min(1, 0.3 + 0.26 * k); glowMat.opacity = Math.min(1, 0.45 + 0.3 * k);
  };
  g.userData.setGain(1.6);
  g.visible = false;
  return g;
}

function buildAdmin(THREE, M, bump) {
  const g = new THREE.Group();
  const pb = (x0, x1, y0, y1, z0, z1, mat) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, z1 - z0, y1 - y0), mat);
    m.position.set(px((x0 + x1) / 2), (z0 + z1) / 2, pz((y0 + y1) / 2)); g.add(m); return m;
  };
  const perf = M.per.perf, X0 = 15822, XP0 = 15887, XP1 = 15893, X1 = 15928, Y0 = 541, Y1 = 913, H = 240;
  const joints = [541, 665, 789, 913];
  // Perimetral de privacidad: panel perforado de 2,4 m con cornisa naranja y montantes en cada junta
  pb(XP0, XP1, Y0, Y1, 0, 119.8, perf(372, 120)); pb(XP0, XP1, Y0, Y1, 120.2, 232, perf(372, 112));
  pb(XP0 - 3, XP1 + 3, Y0, Y1, 232, H, M.orange);
  joints.forEach(y => pb(XP0 - 2, XP1 + 2, Math.max(Y0, y - 2), Math.min(Y1, y + 2), 0, 232, M.black));
  // Mesón de administración (lado de 65 cm): cubierta naranja, divisiones y cajas fuertes de 60 × 50 cm
  pb(X0, XP0, Y0, Y1, 85, 90, M.orange); pb(X0, X0 + 2.5, Y0, Y1, 78, 85, M.orange);
  joints.forEach(y => pb(X0 + 1, XP0, Math.max(Y0, y - 1.5), Math.min(Y1, y + 1.5), 0, 85, M.orange));
  pb(15827, 15887, 546, 596, 0, 55, M.dark); pb(15825, 15827, 566, 576, 25, 35, M.steelb);
  pb(15824, 15884, 856, 906, 0, 55, M.dark); pb(15822, 15824, 876, 886, 25, 35, M.steelb);
  bump('Admin: caja fuerte'); bump('Admin: caja fuerte');
  // Bajo la cubierta: un mueble de rejilla con dos puertas de malla y tres puertas negras con tirador redondo
  pb(15824, XP0, 600, 660, 4, 80, M.black);
  [[601.5, 630], [630.5, 658.5]].forEach(([a, b]) => {
    const w = b - a, q = new THREE.Mesh(new THREE.PlaneGeometry(w, 72), M.jaula.wire(w, 72));
    q.rotation.y = Math.PI / 2; q.position.set(px(15823.4), 42, pz((a + b) / 2)); g.add(q);
    pb(15822.4, 15824.6, a, a + 1.6, 6, 78, M.black); pb(15822.4, 15824.6, b - 1.6, b, 6, 78, M.black);
  });
  pb(15824, XP0, 666, 854, 4, 80, M.black);
  [[666.8, 727.5], [728.5, 790.5], [791.5, 853.2]].forEach(([a, b]) => {
    pb(15822.2, 15824.2, a, b, 5, 79, M.black); pb(15820.6, 15822.2, b - 8, b - 4.4, 62, 65.6, M.steelb);
  });
  // Línea de repisas a 2 m de altura, sobre el mesón
  pb(15857, XP0, Y0, Y1, 198.5, 200, M.black); pb(15857, 15858.2, Y0, Y1, 198.5, 204.5, M.black);
  joints.forEach(y => pb(15858, XP0, Math.max(Y0, y - 1), Math.min(Y1, y + 1), 193, 198.5, M.black));
  // Segunda línea de repisas a 1,4 m y gabinete alto negro con tirador, en el extremo más lejano al pasillo (el sur: el norte da al pasillo transversal)
  pb(15857, XP0, Y0, Y1, 139.5, 141, M.black); pb(15857, 15858.2, Y0, Y1, 139.5, 145.5, M.black);
  joints.forEach(y => pb(15858, XP0, Math.max(Y0, y - 1), Math.min(Y1, y + 1), 134, 139.5, M.black));
  pb(15852, XP0, 548, 608, 143, 192, M.black); pb(15850.4, 15852, 574, 577, 150, 158, M.steelb);
  // Lado de 35 cm hacia la sala: zócalo y dos repisas bajas
  pb(XP1, X1 - 3, Y0, Y1, 0, 12, M.black);
  [[20.5, 22], [62, 63.5]].forEach(([a, b]) => { pb(XP1, X1, Y0, Y1, a, b, M.black); pb(X1 - 1.2, X1, Y0, Y1, a, b + 4.5, M.black); });
  // Tapas de 2,4 m, a la altura del perimetral, que cierran los bordes y cortan la vista desde la sala
  [[Y0 - 4, Y0], [Y1, Y1 + 4]].forEach(([a, b]) => { pb(X0, X1, a, b, 0, 232, perf(106, 232)); pb(X0, X1, a, b, 232, H, M.orange); });
  bump('Admin: mueble');
  return g;
}

// Pintura interior de la sala: muros blancos con franjas roja y naranja de 1 m (de 2,7 a 3,7 m), con extremos curvos, y el logo frente a los mesones
function buildSalaPaint(THREE, M, logoTex, sw) {
  const g = new THREE.Group();
  const std = (c, o) => new THREE.MeshStandardMaterial(Object.assign({ color: c, roughness: 0.9, side: THREE.DoubleSide }, o || {}));
  const white = std(0xf3f3f1);
  const tex = t => new THREE.MeshStandardMaterial({ map: t || null, transparent: true, alphaTest: 0.4, roughness: 0.8, side: THREE.DoubleSide });
  const logoMat = tex(logoTex), bodyMat = tex(sw && sw.body), tipMat = tex(sw && sw.tip);
  const HB = 100, TIPW = 176;                                  // franja de 1 m; la punta mide 194 × 110 px del letrero, o 176 × 100 cm
  // franja: cuerpo estirado + punta curva en el extremo que corresponda (la punta izquierda es la derecha reflejada)
  const band = (fr, u0, u1, tipL, tipR) => {
    const a = tipL ? u0 + TIPW - 1 : u0, b = tipR ? u1 - TIPW + 1 : u1;
    if (b > a) { const q = new THREE.Mesh(new THREE.PlaneGeometry(b - a, HB), bodyMat); q.position.set((a + b) / 2, 320, 0.25); fr.add(q); }
    if (tipR) { const q = new THREE.Mesh(new THREE.PlaneGeometry(TIPW, HB), tipMat); q.position.set(u1 - TIPW / 2, 320, 0.3); fr.add(q); }
    if (tipL) { const q = new THREE.Mesh(new THREE.PlaneGeometry(TIPW, HB), tipMat); q.scale.x = -1; q.position.set(u0 + TIPW / 2, 320, 0.3); fr.add(q); }
  };
  // ox, oy: origen en el plano; (dx, dy): dirección de u; (nx, ny): normal hacia el interior; off: separación del muro
  const wall = (ox, oy, dx, dy, nx, ny, off, len, bands, logoAt, holes, isFac) => {
    const fr = new THREE.Group();
    fr.position.set(px(ox + nx * off), 0, pz(oy + ny * off)); fr.rotation.y = Math.atan2(dy, dx);
    const piece = (u0, u1, h0, h1) => { if (u1 - u0 < 0.1) return; const q = new THREE.Mesh(new THREE.PlaneGeometry(u1 - u0, h1 - h0), white); q.position.set((u0 + u1) / 2, (h0 + h1) / 2, 0); fr.add(q); };
    let uc = 0;                                                  // los vanos de vidrio no se tapan con el muro blanco
    (holes || []).forEach(h => { piece(uc, h[0], 0, 780); piece(h[0], h[1], h[2], 780); uc = h[1]; });
    piece(uc, len, 0, 780);
    bands.forEach(b2 => band(fr, b2[0], b2[1], b2[2], b2[3]));
    if (logoAt !== undefined) { const l = new THREE.Mesh(new THREE.PlaneGeometry(290, 290 / 4.65), logoMat); l.position.set(logoAt, 320, 0.6); fr.add(l); }
    if (isFac) fr.traverse(o => { if (o.isMesh) o.userData.facadeSkin = true; });      // revestimiento interior de la fachada: se vuelve semitransparente con ella
    g.add(fr);
  };
  const Lw = Math.hypot(342, 1282), ex = -342 / Lw, ey = -1282 / Lw;       // muro oriente, de norte a sur
  wall(16372, 1798, 1, 0, 0, -1, 0.4, 1340, [[0, 1340, true, false]]);                 // norte: de oeste a este
  wall(17370, 516, -1, 0, 0, 1, 8.4, 998, [[0, 998, false, true]], undefined, [[338, 858, 270]], true);   // sur: de este a oeste, con el vano de las vitrinas
  wall(17712, 1798, ex, ey, -1282 / Lw, 342 / Lw, 8.4, Lw, [[0, Lw / 2 - 190, false, true], [Lw / 2 + 190, Lw, true, false]], Lw / 2, undefined, true);   // oriente, con el logo
  return g;
}

function buildIslaOfertas(THREE, M, L, D, H) {
  // Isla de ofertas "Súper precios" (foto de referencia): mueble amarillo de unos 90 cm, con dos caras abiertas (repisas negras con bidones) y dos paneles amarillos con el logo
  const mk = (k, f) => M[k] || (M[k] = f());
  const std = (c, r) => new THREE.MeshStandardMaterial({ color: c, roughness: r });
  const canvasMat = (w, h, draw, fallback) => {
    try { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); draw(x, w, h); const t = new THREE.CanvasTexture(c); return new THREE.MeshStandardMaterial({ map: t, roughness: 0.6 }); } catch (e) { return fallback; }
  };
  const yel = mk('isY', () => std(0xf2c200, 0.6)), blk = mk('isK', () => std(0x1b1c1e, 0.8)), jug = mk('isJ', () => std(0x5fa3c4, 0.35)), cap = mk('isC', () => std(0x111214, 0.7)), lab = mk('isL', () => std(0xe8861a, 0.6));
  const strip = mk('isS', () => canvasMat(512, 64, (x, w, h) => { x.fillStyle = '#f2c200'; x.fillRect(0, 0, w, h); x.fillStyle = '#16181a'; x.font = 'bold 40px sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('SÚPER PRECIOS', w / 2, h / 2 + 2); }, yel));
  const side = mk('isP', () => canvasMat(256, 256, (x, w, h) => { x.fillStyle = '#f2c200'; x.fillRect(0, 0, w, h); x.strokeStyle = '#16181a'; x.lineWidth = 14; x.beginPath(); x.arc(w / 2, h * 0.38, 62, 0, Math.PI * 2); x.stroke(); x.fillStyle = '#16181a'; x.font = 'bold 84px sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('$', w / 2, h * 0.39); x.font = 'bold 30px sans-serif'; x.fillText('SÚPER PRECIOS', w / 2, h * 0.82); }, yel));
  const g = new THREE.Group();
  const bx = (x0, x1, y0, y1, z0, z1, mat) => { const m2 = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), mat); m2.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); g.add(m2); };
  const pl = (w, h, x, y, z, ry, mat) => { const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); p.position.set(x, y, z); p.rotation.y = ry; g.add(p); };
  bx(0, L, 0, 8, 0, D, blk);                                              // zócalo negro
  bx(0, 2.5, 8, H, 0, D, yel); bx(L - 2.5, L, 8, H, 0, D, yel);            // paneles laterales amarillos
  pl(D - 2, H - 12, -0.05, H / 2 + 2, D / 2, -Math.PI / 2, side); pl(D - 2, H - 12, L + 0.05, H / 2 + 2, D / 2, Math.PI / 2, side);   // logo sobre los paneles
  bx(2.5, L - 2.5, H - 2, H, 0, D, blk);                                  // tapa superior
  const mid = 8 + (H - 10) / 2;
  bx(2.5, L - 2.5, mid - 1, mid + 1, 2, D - 2, blk);                      // repisa intermedia
  bx(2.5, L - 2.5, 8, 10, 2, D - 2, blk);                                 // repisa inferior
  bx(2.5, L - 2.5, 8, H - 2, D / 2 - 1, D / 2 + 1, blk);                   // fondo central: las dos caras abiertas quedan espalda con espalda
  [0, D].forEach(z => {                                                     // franjas amarillas "SÚPER PRECIOS" al frente de cada nivel
    const s = z === 0 ? -0.3 : D + 0.3, ry = z === 0 ? Math.PI : 0;
    pl(L - 5, 9, L / 2, H - 6, s, ry, strip); pl(L - 5, 9, L / 2, 14, s, ry, strip); pl(L - 5, 9, L / 2, mid + 8, s, ry, strip);
  });
  const nJ = 3, jw = (L - 9) / nJ - 2;                                      // bidones de 4 L: 3 por fila, a cada lado
  [[10, mid - 1], [mid + 1, H - 2]].forEach(([y0, y1]) => [0, 1].forEach(side2 => {
    for (let i = 0; i < nJ; i++) {
      const x0 = 4.5 + i * (jw + 2) + 1, z0 = side2 ? D / 2 + 2 : 2, zd = D / 2 - 4, jh = Math.min(29, y1 - y0 - 4);
      bx(x0, x0 + jw, y0, y0 + jh, z0, z0 + zd, jug); bx(x0 + jw * 0.3, x0 + jw * 0.7, y0 + jh, y0 + jh + 3, z0 + zd * 0.3, z0 + zd * 0.7, cap);
      const zf = side2 ? z0 + zd : z0; bx(x0 + 1, x0 + jw - 1, y0 + jh * 0.25, y0 + jh * 0.75, side2 ? zf : zf - 0.4, side2 ? zf + 0.4 : zf, lab);
    }
  }));
  return g;
}
function buildCabGondola(THREE, M, L, D, H) {
  // Cabecera de góndola (fotos de referencia): las repisas de la góndola (con labio: base + 3) miran hacia el pasillo, el respaldo perforado se apoya en el extremo de la isla
  // y los costados llevan panel de rejilla; sin productos. El frente (las repisas) mira hacia +x.
  const mk = (k, f) => M[k] || (M[k] = f());
  const gris = mk('cgG', () => new THREE.MeshStandardMaterial({ color: 0x3a3d41, roughness: 0.8 }));
  const SPINE = 3, POST_W = 4, KICK_H = 12, KICK_IN = 3, SHELF_T = 1.5, LIP_H = 4.5, LIP_T = 0.6, CAP_H = 1.5, SIDE_T = 1.2, k = H / 150;
  const SHELF_Y = [22, 55, 88, 121].map(y => y * k), ph = H - KICK_H;
  const g = new THREE.Group();
  const bx = (x0, x1, y0, y1, z0, z1, mat) => { const m2 = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), mat); m2.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); g.add(m2); };
  bx(SPINE / 2 - 0.3, SPINE / 2 + 0.3, KICK_H, H, 0, D, M.gon.perf(D, ph));                    // respaldo perforado, contra la isla
  bx(0, SPINE, H - CAP_H, H, 0, D, M.gon.black);                                                // remate superior
  [0, D - POST_W].forEach(z => bx(0, SPINE, KICK_H, H, z, z + POST_W, M.gon.black));             // montantes
  bx(SPINE, L - KICK_IN, 0, KICK_H, POST_W, D - POST_W, M.gon.black);                            // zócalo retranqueado
  SHELF_Y.forEach(yT => {                                                                       // repisas hacia el pasillo, con labio frontal
    bx(SPINE, L, yT - SHELF_T, yT, POST_W / 2, D - POST_W / 2, M.gon.black);
    bx(L - LIP_T, L, yT + 1 - LIP_H, yT + 1, POST_W / 2, D - POST_W / 2, M.gon.black);
  });
  bx(SPINE, L, H - CAP_H, H, 0, D, M.gon.black);                                                // cubierta superior
  [[0, 1], [D - SIDE_T, -1]].forEach(([z0, dir]) => {                                           // costados: fondo gris con rejilla de alambre
    bx(SPINE, L, KICK_H, H - CAP_H, z0, z0 + SIDE_T, gris);
    const wr = new THREE.Mesh(new THREE.PlaneGeometry(L - SPINE - 2, ph - CAP_H - 2), M.jaula.wire(L - SPINE - 2, ph - CAP_H - 2));
    wr.position.set(SPINE + (L - SPINE) / 2, KICK_H + (ph - CAP_H) / 2, dir === 1 ? -0.4 : D + 0.4); g.add(wr);
  });
  return g;
}
function buildStore(THREE, DATA, M, texs) {
  const layers = { valid: [], pend: [], cab: [], luz: [], fac: [] };
  const cabs = [];
  const fps = [], stats = {};
  const bump = k => stats[k] = (stats[k] || 0) + 1;
  function put(layer, comp, Lt, D, x, y, fa, tag, hy) {
    const wrap = new THREE.Group();
    comp.position.set(-Lt / 2, 0, -D / 2);
    wrap.add(comp);
    wrap.position.set(px(x), hy || 0, pz(y));
    wrap.rotation.y = rotY(fa);
    wrap.updateMatrixWorld(true);
    layers[layer].push(wrap);
    const pts = [[0, 0], [Lt, 0], [Lt, D], [0, D]].map(([a, b]) => {
      const v = new THREE.Vector3(a - Lt / 2, 0, b - D / 2).applyMatrix4(wrap.matrixWorld);
      return [v.x + OX, -v.z + OY];
    });
    fps.push({ tag, pts }); bump(tag);
    return wrap;
  }
  const boxComp = (L, D, h, mat) => {
    const g = new THREE.Group(), m = new THREE.Mesh(new THREE.BoxGeometry(L, h, D), mat);
    m.position.set(L / 2, h / 2, D / 2); g.add(m); return g;
  };
  DATA.hp.forEach(h => {
    const depth = h.D > 45 ? 60 : 30;
    put('valid', C_hp.build(THREE, { depth, modules: 1 }, M.hp), C_hp.SPEC.W, depth, h.x, h.y, h.ang - 90, 'Rack HP');
  });
  DATA.per.forEach((p, i) => {
    const depth = Math.round(p.D);
    put('valid', C_per.build(THREE, { depth, modules: 1, seed: 11 + i * 7 }, M.per), C_per.SPEC.W, depth, p.x, p.y, p.fa, 'Perimetral ' + p.kind);
  });
  DATA.gon.forEach(g => put('valid', C_gon.build(THREE, { modules: 1 }, M.gon), C_gon.SPEC.L, 90, g.x, g.y, g.ang - 90, 'Góndola negra'));
  // El cliente de cada mesón mira hacia las góndolas más cercanas (hilera norte–sur: 180 = cliente al este, 0 = al oeste)
  const mesFa = mm => {
    let best = null, bd = 1e9; DATA.gon.forEach(g => { const d = Math.hypot(g.x - mm.x, g.y - mm.y); if (d < bd) { bd = d; best = g; } });
    const al = mm.a === undefined ? 90 : mm.a, r = Math.PI / 180;
    if (!best) return al - 90 + 180;
    // el cliente mira hacia la góndola más cercana: sin giro mira a al + 90, con giro de 180° mira a al - 90
    const dot = ang => Math.cos(ang * r) * (best.x - mm.x) + Math.sin(ang * r) * (best.y - mm.y);
    return al - 90 + (dot(al - 90) >= dot(al + 90) ? 180 : 0);
  };
  DATA.mes.forEach(m => { const mc = C_mes.build(THREE, { modules: 1 }, m.v === 'tal' ? M.mesTal : M.mesAtn); const Lt = m.L || C_mes.SPEC.L; if (m.L) mc.scale.x = m.L / C_mes.SPEC.L; put('valid', mc, Lt, 90, m.x, m.y, mesFa(m), m.L ? 'Mesón de accesorios' : (m.v === 'tal' ? 'Mesón talleres' : 'Mesón atención')); });
  // Cenefa estándar de 3 cuerpos: la gráfica "Conoce tu batería" ocupa los tres paneles, un tercio de la imagen por cuerpo
  const cenT = texs && texs.sign && texs.sign.cen, cenMats = cenT ? cenT.map(t => new THREE.MeshStandardMaterial({ map: t, roughness: 0.7 })) : null;
  DATA.bat.forEach(b => put('valid', C_bat.build(THREE, { modules: 3, cenefa: true }, cenMats ? Object.assign({}, M.bat, { panel: i => cenMats[i % 3] }) : M.bat), C_bat.SPEC.W * 3, C_bat.SPEC.D, b.x, b.y, b.fa, 'Rack baterías (3) con cenefa'));
  DATA.cab.forEach(c => {
    if (c.D > 80) {       // cabecera de góndola: el frente mira hacia afuera de la isla (lejos de la góndola más cercana)
      let best = null, bd = 1e9; DATA.gon.forEach(g => { const d = Math.hypot(g.x - c.x, g.y - c.y); if (d < bd) { bd = d; best = g; } });
      const ar = c.ang * Math.PI / 180, out = best ? (c.x - best.x) * Math.cos(ar) + (c.y - best.y) * Math.sin(ar) : 1;
      put('cab', buildCabGondola(THREE, M, c.L, c.D, c.h), c.L, c.D, c.x, c.y, c.ang - 90 + (out < 0 ? 180 : 0), 'Cabecera de góndola (aprox.)');
    } else put('cab', boxComp(c.L, c.D, c.h, M.cabm), c.L, c.D, c.x, c.y, c.ang - 90, 'Cabecera de fila HP (aprox.)');
  });
  DATA.ph.forEach(p => {
    if (p.label === 'Rack neumáticos (bodega)') put('cab', C_neu.build(THREE, { modules: 1 }, M.neu), C_neu.SPEC.L, C_neu.SPEC.D, p.x, p.y, p.ang - 90, 'Rack neumáticos (aprox.)');
    else if (p.label === 'Bodega cartones/basura 120×60') put('valid', C_jaula.build(THREE, { open: 0 }, M.jaula), C_jaula.SPEC.W, C_jaula.SPEC.D, p.x, p.y, 0, 'Jaula cartones y plásticos');
    else if (p.label === 'Rack pallets 120×220') put('valid', C_pal.build(THREE, { pallets: 2, levels: 3 }, M.pal), C_pal.SPEC.SPACE * 2 + 2 * C_pal.SPEC.UP_W, C_pal.SPEC.D, p.x, p.y, p.ang - 90, 'Rack pallets');
    else if (p.label === 'Bodega residuos peligrosos') put('valid', C_resp.build(THREE, {}, M.resp), C_resp.SPEC.L, C_resp.SPEC.D, p.x, p.y, 180, 'Bodega RESPEL');
    else if (p.label === 'Cabecera repisas HP') put('cab', C_cabhp.build(THREE, { graphic: p.x > 15500 }, M.cabhp), C_cabhp.SPEC.W, C_cabhp.SPEC.D, p.x, p.y, p.fa, p.x > 15500 ? 'Cabecera repisas HP con gráfica (aprox.)' : 'Cabecera repisas HP solo repisas (aprox.)');
    else if (/Isla/.test(p.label) && /Ofertas/.test(p.label)) put('valid', buildIslaOfertas(THREE, M, p.L, p.D, 90), p.L, p.D, p.x, p.y, p.ang - 90, 'Isla de ofertas');
    else put('pend', boxComp(p.L, p.D, p.h, M.pend), p.L, p.D, p.x, p.y, p.ang - 90, 'Pendiente: ' + p.label);
  });
  // Luminarias del plano eléctrico: L02 y L06 colgadas a 4 m (dato tuyo); L03 y L01 con altura supuesta
  const LH = { L02: 400, L03: 360, L01: 270, F01: 400 }, LD = { L02: [120, 7.5, 6], L03: [130, 14, 9], L01: [120, 8, 6], F01: [14, 14, 5] };   // F01: foco embutido redondo; cada luminaria puede traer su altura (l.h)
  const lamps = [];      // cada luminaria sube o baja según el cielo: si queda sobre él, se fija a su cara inferior; el resto no se toca
  const regLamp = (wrap, h0, thick, x) => { lamps.push({ obj: wrap, h0, thick, zone: x < DATA.XB ? 'b' : 's', eff: h0 }); return lamps.length - 1; };
  const addCab = (x, y, h0, kind, lamp) => cabs.push({ x, y, h0, zone: x < DATA.XB ? 'b' : 's', kind, lamp });
  DATA.luz.forEach(l => {
    const d = LD[l.t], g = new THREE.Group(), mm = new THREE.Mesh(l.t === 'F01' ? new THREE.CylinderGeometry(d[0] / 2, d[0] / 2, d[2], 16) : new THREE.BoxGeometry(d[0], d[2], d[1]), M.lamp);
    mm.position.set(d[0] / 2, d[2] / 2, d[1] / 2); g.add(mm);
    const wl = put('luz', g, d[0], d[1], l.x, l.y, l.a - 90, 'Luminaria ' + l.t, l.h || LH[l.t]), li = regLamp(wl, l.h || LH[l.t], d[2], l.x);
    if (l.t === 'L02' || l.t === 'L03') { const a = l.a * Math.PI / 180, s0 = l.t === 'L02' ? 45 : 50; [-s0, s0].forEach(s => addCab(l.x + s * Math.cos(a), l.y + s * Math.sin(a), (l.h || LH[l.t]) + d[2], l.t, li)); }
  });
  DATA.rails.forEach(r => {
    const g = new THREE.Group();
    const rail = new THREE.Mesh(new THREE.BoxGeometry(120, 3, 3), M.black); rail.position.set(60, 1.5, 1.5); g.add(rail);
    [30, 90].forEach(x => { const h = new THREE.Mesh(new THREE.BoxGeometry(12, 6, 6), M.black); h.position.set(x, -3, 1.5); g.add(h); });
    const wr = put('luz', g, 120, 3, r.x, r.y, -90, 'Riel L06 (2 cabezales)', LH.L02), ri = regLamp(wr, LH.L02, 3, r.x);
    [-55, 55].forEach(s => addCab(r.x + s, r.y, LH.L02 + 3, 'L06', ri));
  });
  const cabArr = new Float32Array(cabs.length * 6);
  const cables = new THREE.LineSegments(new THREE.BufferGeometry().setAttribute('position', new THREE.BufferAttribute(cabArr, 3)), new THREE.LineBasicMaterial({ color: 0x8a8f94 }));
  let nightFx = null;
  const cutU = { value: new THREE.Vector3(1e6, 1e6, px(DATA.XB)) };       // altura de corte de los muebles: sala, bodega y x del límite entre zonas
  // El cielo marca el final (si existe): las luminarias que quedarían sobre él se fijan a su cara inferior, los tirantes terminan bajo el cielo
  // y los muebles que lo sobrepasarían se cortan 10 cm más abajo.
  const setCableTops = (topS, topB) => {
    lamps.forEach(L => { const t = L.zone === 's' ? topS : topB; L.eff = (t !== null && L.h0 + L.thick > t) ? t - L.thick : L.h0; L.obj.position.y = L.eff; });
    cabs.forEach((c, i) => {
      const h0 = c.lamp !== undefined ? lamps[c.lamp].eff + lamps[c.lamp].thick : c.h0;
      let top = c.zone === 's' ? (topS === null ? (c.kind === 'L03' ? null : H_SALA) : topS) : topB;
      if (top === null || top <= h0 + 2) top = h0;
      const o = i * 6; cabArr[o] = px(c.x); cabArr[o + 1] = h0; cabArr[o + 2] = pz(c.y); cabArr[o + 3] = px(c.x); cabArr[o + 4] = top; cabArr[o + 5] = pz(c.y);
    });
    cables.geometry.attributes.position.needsUpdate = true;
    cutU.value.set(topS === null ? 1e6 : topS - 10, topB === null ? 1e6 : topB - 10, px(DATA.XB));
    if (nightFx) nightFx.userData.setTops(topS, topB);
  };
  setCableTops(null, null);
  layers.valid.push(buildServicios(THREE, M, bump));
  layers.valid.push(buildAdmin(THREE, M, bump));
  const fac = buildFacade3D(THREE, M, texs && texs.sign);
  layers.fac = fac.frames;
  // Cajas de colisión (cm, mundo): cada parte de mueble, de la fachada y del altillo. La cámara se acerca hasta 25 cm de ellas; el vidrio no cuenta (se puede entrar por la puerta)
  const boxes = [], cbb = new THREE.Box3();
  ['valid', 'cab', 'pend', 'fac'].forEach(k => layers[k].forEach(root => { root.updateMatrixWorld(true); root.traverse(o => {
    if (!o.isMesh) return; const mt = Array.isArray(o.material) ? o.material[0] : o.material; if (mt && mt.transparent && mt.opacity < 0.3) return;
    if (!o.geometry.boundingBox) o.geometry.computeBoundingBox(); cbb.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); boxes.push(cbb.min.x, cbb.min.y, cbb.min.z, cbb.max.x, cbb.max.y, cbb.max.z);
  }); }));
  const wallSegs = [];                                                       // muros que no son fachada: segmentos en el plano (mundo)
  for (let i = 0; i < DATA.contour.length; i++) {
    const a = DATA.contour[i], b = DATA.contour[(i + 1) % DATA.contour.length];
    const fac = (Math.abs(a[1] - OY) < 1 && Math.abs(b[1] - OY) < 1) || (a[0] > 17300 && b[0] > 17300 && OX > 0) || !!(DATA.open && DATA.open.includes(i));
    if (!fac && Math.hypot(b[0] - a[0], b[1] - a[1]) > 15) wallSegs.push([px(a[0]), pz(a[1]), px(b[0]), pz(b[1])]);
  }
  const colliders = { boxes: new Float32Array(boxes), walls: wallSegs, wallH: H_SALA };
  const merged = {};
  const lampWraps = layers.luz; layers.luz = [];                         // las luminarias quedan sueltas para poder moverlas
  Object.keys(layers).forEach(k => merged[k] = mergeRoots(THREE, layers[k], M));
  lampWraps.forEach(w => merged.luz.add(w));
  // corte de muebles sobre el cielo: se descarta lo que queda por encima de la altura de corte de su zona
  const cutShader = shader => {
    shader.uniforms.uCut = cutU;
    shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vCutP;').replace('#include <begin_vertex>', '#include <begin_vertex>\nvCutP = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    shader.fragmentShader = shader.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vCutP;\nuniform vec3 uCut;').replace('void main() {', 'void main() {\n  if (vCutP.y > (vCutP.x < uCut.z ? uCut.y : uCut.x)) discard;');
  };
  ['valid', 'cab', 'pend'].forEach(k => merged[k].traverse(o => {
    if (!o.isMesh) return;
    const arr = Array.isArray(o.material); const cl = (arr ? o.material : [o.material]).map(mt => { const c = mt.clone(); c.onBeforeCompile = cutShader; return c; });
    o.material = arr ? cl : cl[0];
  }));
  const ceilings = buildCeilings(THREE, DATA, M);
  nightFx = buildNightFx(THREE, DATA, M);
  return { merged, fps, stats, cables, setCableTops, fac, ceil: ceilings, night: nightFx, colliders, shell: (() => { const s = buildShell(THREE, DATA, texs); s.walls.add(buildSalaPaint(THREE, M, texs && texs.sign && texs.sign.logo, texs && texs.sign && texs.sign.sw)); s.walls.add(ceilings.paintRoot); return s; })() };
}
/*CORE_END*/
'''
css = open("biblioteca/perimetral_v1.html", encoding="utf8").read().split("<style>")[1].split("</style>")[0]
css += '''
  .controls { gap: 6px 8px; padding: 8px 12px; }
  .controls .sep { width: 1px; height: 22px; background: var(--line); margin: 0 4px; }
  button { padding: 8px 10px; min-height: 38px; font-size: 13.5px; }
  .ceilrow { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 10px; margin: 6px 0 10px; }
  .ceilrow .zn { width: 52px; font-weight: 600; }
  .ceilrow select { font: inherit; font-size: 14px; padding: 8px; border-radius: 8px; background: var(--btn); color: var(--ink); border: 1px solid var(--line); min-height: 40px; }
  .ceilrow input[type=range] { flex: 1 1 140px; min-width: 120px; accent-color: var(--accent); }
  .ceilrow label { display: inline-flex; align-items: center; gap: 6px; min-height: 40px; }
  .gal { display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: 6px; margin: 6px 0; }
  .gal figure { margin: 0; position: relative; } .gal img { width: 100%; border-radius: 6px; display: block; }
  .gal button { position: absolute; top: 2px; right: 2px; min-height: 28px; padding: 0 8px; }
  .saved { padding-left: 18px; margin: 6px 0; } .saved li { margin: 4px 0; }
  #vgName { flex: 1 1 140px; min-height: 40px; }
  #cv { touch-action: none; }
  .ceilrow output { min-width: 150px; font-size: 13px; color: var(--muted); }
  .note { margin: 0 0 10px; font-size: 12.5px; color: var(--muted); }
  .controls select { font: inherit; font-size: 13.5px; padding: 6px 8px; border-radius: 8px; background: var(--btn); color: var(--ink); border: 1px solid var(--line); min-height: 38px; }
  #hud { position: absolute; inset: 0; pointer-events: none; }
  #joy { position: absolute; left: 16px; bottom: 16px; width: 120px; height: 120px; border-radius: 50%; background: rgba(255,255,255,.14); border: 2px solid rgba(255,255,255,.4); pointer-events: auto; touch-action: none; }
  #knob { position: absolute; left: 36px; top: 36px; width: 44px; height: 44px; border-radius: 50%; background: rgba(255,255,255,.6); }
  #vert { position: absolute; right: 16px; bottom: 16px; display: flex; flex-direction: column; gap: 10px; pointer-events: auto; }
  #vert button { width: 58px; height: 58px; border-radius: 50%; font-size: 20px; background: rgba(255,255,255,.6); color: #111; touch-action: none; }
  #rList { margin: 4px 0 8px; padding-left: 20px; font-size: 13px; } #rList input { width: 70px; } #rList button { min-height: 30px; padding: 2px 8px; }
  #rJson { width: 100%; font: inherit; font-size: 12px; background: var(--btn); color: var(--ink); border: 1px solid var(--line); border-radius: 8px; padding: 6px; box-sizing: border-box; }
  #rVid { width: 100%; margin-top: 8px; border-radius: 8px; } #rLink { display: block; margin: 8px 0 12px; color: var(--accent); font-weight: 600; }
  input[type=number] { width: 74px; font: inherit; font-size: 14px; padding: 6px; border-radius: 8px; background: var(--btn); color: var(--ink); border: 1px solid var(--line); }
'''
browser = 'if (typeof window !== \'undefined\') {\n  const $ = id => document.getElementById(id);\n  const cv = $(\'cv\'), stage = $(\'stage\');\n  const renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true });\n  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));\n  const scene = new THREE.Scene();\n  const camera = new THREE.PerspectiveCamera(42, 1, 10, 30000);\n  const hemi = new THREE.HemisphereLight(0xffffff, 0x8a8f8c, 1.0); scene.add(hemi);\n  const sun = new THREE.DirectionalLight(0xffffff, 0.3); sun.position.set(1500, 3000, 1500); scene.add(sun);\n  const sun2 = new THREE.DirectionalLight(0xffffff, 0.2); sun2.position.set(-1500, 1800, -900); scene.add(sun2);\n  let dirty = true, night = false, gain = 1.6, mode = \'orbit\', recording = false;\n  const FOV_EXT = 42; let fovInt = 70;                                 // apertura vertical: exterior fija, interior regulable\n\n  const canvasTex = (w, h, draw) => { const c = document.createElement(\'canvas\'); c.width = w; c.height = h; draw(c.getContext(\'2d\'), w, h); return new THREE.CanvasTexture(c); };\n  const dotTex = canvasTex(64, 64, x => {\n    x.fillStyle = \'#26282b\'; x.fillRect(0, 0, 64, 64); x.fillStyle = \'#5b6065\';\n    [[16, 16], [48, 48]].forEach(([a, b]) => { x.beginPath(); x.arc(a, b, 4.2, 0, Math.PI * 2); x.fill(); });\n  }); dotTex.wrapS = dotTex.wrapT = THREE.RepeatWrapping;\n  const wireTex = canvasTex(64, 64, x => { x.fillStyle = \'#16181a\'; x.fillRect(0, 0, 3, 64); x.fillRect(32, 0, 3, 64); x.fillRect(0, 0, 64, 3); });\n  wireTex.wrapS = wireTex.wrapT = THREE.RepeatWrapping;\n  const panelTex = i => canvasTex(384, 384, x => {\n    x.fillStyle = \'#f4f4f2\'; x.fillRect(0, 0, 384, 384); x.fillStyle = \'#d3242b\'; x.fillRect(0, 0, 384, 65);\n    if (i === 2) x.fillRect(0, 65, 384, 319);\n    else if (i === 0) { x.fillStyle = \'#25282b\'; x.fillRect(35, 150, 170, 135); }\n    else { x.strokeStyle = \'#b9bdc0\'; x.lineWidth = 2; for (let r = 0; r < 6; r++) x.strokeRect(20, 85 + r * 45, 344, 45); }\n  });\n  const panelMats = [0, 1, 2].map(i => {\n    const side = new THREE.MeshStandardMaterial({ color: 0xe9e9e6, roughness: 0.8 });\n    return [side, side, side, side, new THREE.MeshStandardMaterial({ map: panelTex(i), roughness: 0.7 }), side];\n  });\n  const hs = new THREE.MeshStandardMaterial({ color: 0xe9e9e6, roughness: 0.8 });\n  const headMats = [hs, hs, hs, hs, new THREE.MeshStandardMaterial({ map: canvasTex(335, 500, x => {\n    x.fillStyle = \'#f6f6f4\'; x.fillRect(0, 0, 335, 500); x.fillStyle = \'#d3242b\'; x.fillRect(0, 0, 335, 70); x.fillStyle = \'#c9ccce\'; x.fillRect(18, 170, 299, 220);\n  }), roughness: 0.7 }), hs];\n  const radial = canvasTex(128, 128, (x, w, h) => {\n    const g = x.createRadialGradient(64, 64, 0, 64, 64, 64);\n    g.addColorStop(0, \'rgba(255,255,255,1)\'); g.addColorStop(0.35, \'rgba(255,255,255,0.45)\'); g.addColorStop(1, \'rgba(255,255,255,0)\');\n    x.fillStyle = g; x.fillRect(0, 0, w, h);\n  });\n  const tileTex = (tile, line) => {\n    const t = canvasTex(64, 64, x => { x.fillStyle = tile; x.fillRect(0, 0, 64, 64); x.strokeStyle = line; x.lineWidth = 3; x.strokeRect(0, 0, 64, 64); });\n    t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1 / 60, 1 / 60); return t;     // baldosa de 60 × 60 cm\n  };\n  const tileW = tileTex(\'#efeff0\', \'#c4c5c8\'), tileB = tileTex(\'#1b1c1e\', \'#434549\');\n  const env = (() => {\n    const mk = (top, bot) => { const c = document.createElement(\'canvas\'); c.width = c.height = 64; const x = c.getContext(\'2d\'); const g = x.createLinearGradient(0, 0, 0, 64); g.addColorStop(0, top); g.addColorStop(0.5, \'#e9eef2\'); g.addColorStop(1, bot); x.fillStyle = g; x.fillRect(0, 0, 64, 64); return c; };\n    const side = mk(\'#8db3d8\', \'#5c6064\'), topF = mk(\'#a7c8ea\', \'#cfe2f3\'), botF = mk(\'#4d5054\', \'#3b3e41\');\n    const t = new THREE.CubeTexture([side, side, topF, botF, side, side]); t.needsUpdate = true; return t;\n  })();\n  const loader = new THREE.TextureLoader();\n  const sign = { sur: loader.load(SIGN.sur, () => { dirty = true; }), ori: loader.load(SIGN.ori, () => { dirty = true; }), logo: loader.load(SIGN.logo, () => { dirty = true; }),\n    sw: { body: loader.load(SIGN.swBody, () => { dirty = true; }), tip: loader.load(SIGN.swTip, () => { dirty = true; }) },\n    cen: [0, 1, 2].map(i => { const t = loader.load(SIGN.cenefaBat, () => { dirty = true; }); t.repeat.set(1 / 3, 1); t.offset.set(i / 3, 0); return t; }) };\n  const M = makeMats(THREE, { dotTex, panelMats, headMats, wireTex, env, tileW, tileB, radial });\n  const built = buildStore(THREE, DATA, M, { sign });\n  scene.add(built.shell.floors, built.shell.walls, built.merged.valid, built.merged.cab, built.merged.pend, built.merged.luz, built.merged.fac, built.fac.halos, built.cables, built.ceil.root, built.night);\n\n  const S = built.stats;\n  const li = (id, items) => $(id).innerHTML = items.map(t => \'<li>\' + t + \'</li>\').join(\'\');\n  li(\'listValid\', [\n    \'Racks HP: \' + (S[\'Rack HP\'] || 0) + \' módulos de 122 × 30 o 122 × 60 cm y 3 m de alto\',\n    \'Perimetrales: \' + (S[\'Perimetral RV1\'] || 0) + \' RV1, \' + (S[\'Perimetral RV2\'] || 0) + \' RV2 y \' + (S[\'Perimetral RN\'] || 0) + \' RN, de 2,4 m\',\n    \'Góndolas negras: \' + (S[\'Góndola negra\'] || 0) + \' módulos dobles de 124 × 90 × 150 cm\',\n    \'Mesones: \' + (S[\'Mesón atención\'] || 0) + \' de atención y \' + (S[\'Mesón talleres\'] || 0) + \' de talleres\',\n    \'Racks de baterías: 3, de 2,4 m, con su cenefa de 1,5 m traslapada (3,0 m en total)\',\n    \'Luminarias del plano eléctrico: \' + (S[\'Luminaria L02\'] || 0) + \' L02 de 1,2 m a 4 m, \' + (S[\'Riel L06 (2 cabezales)\'] || 0) + \' rieles L06 a 4 m y \' + (S[\'Luminaria L03\'] || 0) + \' canoas L03 de 1,3 m en la bodega\',\n    \'Fachada Sur y Oriente en volumen, con las medidas de las elevaciones: paneles de ACM de 240 × 120 cm con juntas, pilastras, revestimiento acanalado y rejillas de ventilación sobre la bodega, vitrinas de vidrio con perfilería roja, marcos publicitarios y cornisa de 56 cm\',\n    \'Acceso principal: puerta doble vidriada de 168 cm (dos hojas de 84 cm) con marcos de aluminio rojo, paño fijo y paño superior; la salida del oeste es una puerta doble roja de 216 cm\',\n    \'Letrero de ACM: logo y bandas completas en capas con unos 5 cm de relieve, sin el rectángulo del dibujo; retroiluminado con franja LED de 4000 K en modo Noche\',\n    \'Racks de pallets (\' + (S[\'Rack pallets\'] || 0) + \'): de 2 pallets de ancho y 3 de alto, con pilares de 2,5 m y travesaños a 1 y 2 m; 6 posiciones cada uno, que con 3 pallets en piso suman los 15 del cuadro de bodegaje\',\n    \'Pintura de los muros de la sala: franjas roja y naranja de 1 m, de 2,7 a 3,7 m, con extremos curvos tomados del letrero, y el logo en el muro oriente frente a los mesones\',\n    \'Jaulas de cartones y plásticos: \' + (S[\'Jaula cartones y plásticos\'] || 0) + \' de 120 × 60 × 150 cm, de malla negra\',\n    \'Bodega RESPEL: \' + (S[\'Bodega RESPEL\'] || 0) + \' de 300 × 160 × 230 cm, gris, con 2 puertas dobles\'\n  ]);\n  li(\'listApprox\', [\n    \'Cabeceras de góndola: \' + (S[\'Cabecera de góndola (aprox.)\'] || 0) + \' volúmenes de 53 × 95 × 150 cm\',\n    \'Racks de neumáticos: \' + (S[\'Rack neumáticos (aprox.)\'] || 0) + \' de 210 × 60 × 350 cm, con 4 pisos\',\n    \'Cabeceras de repisas HP: \' + (S[\'Cabecera repisas HP con gráfica (aprox.)\'] || 0) + \' con gráfica detrás de los mesones y \' + (S[\'Cabecera repisas HP solo repisas (aprox.)\'] || 0) + \' solo con repisas en la bodega, de 67 × 44 × 300 cm\',\n    \'Baños y cocina: 3 recintos con \' + (S[\'Servicios: WC\'] || 0) + \' WC, \' + (S[\'Servicios: lavamanos\'] || 0) + \' lavamanos, lavamopa, refrigerador, mesón con lavaplatos, máquina de agua, microondas, mesa con \' + (S[\'Servicios: silla\'] || 0) + \' sillas, \' + (S[\'Servicios: locker\'] || 0) + \' lockers y \' + (S[\'Servicios: puerta\'] || 0) + \' puertas\',\n    \'Mueble Admin (\' + (S[\'Admin: mueble\'] || 0) + \'): mesón naranjo de 372 × 106 cm con mueble de rejilla y puertas negras con tirador, perimetral perforado de 2,4 m con dos líneas de repisas (1,4 y 2 m) y gabinete alto, tapas de 2,4 m en los dos bordes y \' + (S[\'Admin: caja fuerte\'] || 0) + \' cajas fuertes de 60 × 50 cm\',\n    \'Cielos de sala y bodega: americano blanco o negro, o pintura negra con cerchas indicativas, a alturas distintas unidas con una cara opaca (panel Cielos)\'\n  ]);\n  const pend = {}; Object.keys(S).filter(k => k.startsWith(\'Pendiente: \')).forEach(k => pend[k.slice(11)] = S[k]);\n  li(\'listPend\', Object.keys(pend).map(k => k + \': \' + pend[k]));\n  const total = Object.values(S).reduce((a, b) => a + b, 0);\n  $(\'readout\').textContent = \'402 m² · bodega 253 m² a 3,87 m · sala de ventas 150 m² a 7,8 m · \' + total + \' piezas colocadas\';\n\n  // ---------- Cielos y luz nocturna ----------\n  const selS = $(\'cSalaMode\'), selB = $(\'cBodMode\'), rngS = $(\'cSalaH\'), rngB = $(\'cBodH\'), outS = $(\'cSalaV\'), outB = $(\'cBodV\');\n  const rwS = $(\'cSalaW\'), rwB = $(\'cBodW\'), owS = $(\'cSalaWV\'), owB = $(\'cBodWV\'), wcS = $(\'cSalaWOn\'), wcB = $(\'cBodWOn\');\n  const DEF = { aw: { sala: 450, bodega: 387 }, ab: { sala: 450, bodega: 387 }, pn: { sala: 780, bodega: 387 } };\n  const luzTop = zone => { let h = 0; const en = x => (x < DATA.XB) === (zone === \'bodega\'); DATA.luz.forEach(l => { if (en(l.x)) h = Math.max(h, LUZ_H[l.t] || 0); }); DATA.rails.forEach(r => { if (en(r.x)) h = Math.max(h, LUZ_H.L06); }); return h; };\n  const DEFW = { sala: luzTop(\'sala\') + 10, bodega: luzTop(\'bodega\') + 10 };      // muros negros desde 10 cm sobre la luz más alta de cada zona\n  const fmt = v => (v / 100).toFixed(2).replace(\'.\', \',\') + \' m\';\n  function applyCeil(zone, byMode) {\n    const sel = zone === \'sala\' ? selS : selB, rng = zone === \'sala\' ? rngS : rngB, out = zone === \'sala\' ? outS : outB;\n    if (byMode && DEF[sel.value]) rng.value = DEF[sel.value][zone];\n    rng.disabled = sel.value === \'none\'; out.textContent = sel.value === \'none\' ? \'\' : (sel.value === \'pn\' ? \'libre bajo cerchas: \' : \'cielo a \') + fmt(+rng.value);\n    const rw = zone === \'sala\' ? rwS : rwB, ow = zone === \'sala\' ? owS : owB, wc = zone === \'sala\' ? wcS : wcB;\n    if (byMode) { rw.value = DEFW[zone]; wc.checked = sel.value === \'pn\' || sel.value === \'ab\'; }      // pintura negra y americano negro pintan los muros; con otro cielo, tú decides\n    const lim = sel.value === \'none\' ? (zone === \'sala\' ? 780 : 387) : (sel.value === \'pn\' ? +rng.value + 80 : +rng.value);\n    rw.disabled = !wc.checked; ow.textContent = wc.checked ? \'desde \' + fmt(+rw.value) + (+rw.value >= lim ? \' (sobre el cielo: no se ve)\' : \'\') : \'\';\n    built.ceil.set(zone, sel.value, +rng.value); built.ceil.paint(zone, wc.checked, +rw.value);\n    built.setCableTops(built.ceil.top(\'sala\'), built.ceil.top(\'bodega\'));\n    dirty = true;\n  }\n  selS.onchange = () => applyCeil(\'sala\', true); rngS.oninput = () => applyCeil(\'sala\', false);\n  selB.onchange = () => applyCeil(\'bodega\', true); rngB.oninput = () => applyCeil(\'bodega\', false);\n  rwS.oninput = () => applyCeil(\'sala\', false); rwB.oninput = () => applyCeil(\'bodega\', false);\n  wcS.onchange = () => applyCeil(\'sala\', false); wcB.onchange = () => applyCeil(\'bodega\', false);\n  function applyNight() {\n    hemi.intensity = night ? 0.35 * gain : 1.0; sun.intensity = night ? 0.12 * gain : 0.3; sun2.intensity = night ? 0.08 * gain : 0.2;\n    hemi.groundColor.setHex(night ? 0x14161a : 0x8a8f8c);      // de noche nada rebota hacia el techo\n    built.night.visible = night; built.night.userData.setGain(gain);\n    built.fac.halos.visible = night && built.merged.fac.visible;\n    M.envMats.forEach(x => { x.envMapIntensity = night ? 0.15 : 0.9; });\n    built.ceil.night(night); applyTheme();\n  }\n  $(\'nLevel\').onchange = () => { gain = +$(\'nLevel\').value; applyNight(); dirty = true; };      // luz débil 0,6 · media 1,0 · alta 1,6\n\n  // ---------- Cámara: órbita, vuelo tipo dron y recorrido ----------\n  const target = new THREE.Vector3(1660, 100, -640);\n  let th = -0.45, ph = 0.95, radius = 3800;\n  const fly = { pos: new THREE.Vector3(2300, 300, 300), yaw: 0, pitch: -0.2, speed: 500 };\n  const V = {\n    planta: [1660, 0, -640, 0.0, 0.03, 4300], aerea: [1660, 100, -640, -0.45, 0.95, 3800], fachada: [2300, 350, -250, 0.7, 1.3, 3300],\n    sala: [2600, 120, -640, -0.5, 1.0, 1700], bodega: [1000, 120, -640, -0.5, 1.0, 2000],\n    ojosSala: [2300, 165, -640, Math.PI / 2, 1.5, 520], ojosBodega: [1000, 165, -640, Math.PI / 2, 1.5, 520]\n  };\n  // Vistas interiores: a la altura de los ojos, en modo vuelo, mirando un poco hacia arriba para que se vea el cielo\n  const FLYV = { ojosSala: [2050, 165, -640, -Math.PI / 2, 0.2], ojosBodega: [1750, 165, -640, Math.PI / 2, 0.2] };\n  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));\n  const orbitPos = () => new THREE.Vector3(target.x + radius * Math.sin(ph) * Math.sin(th), target.y + radius * Math.cos(ph), target.z + radius * Math.sin(ph) * Math.cos(th));\n  const updateAlt = () => { $(\'fAlt\').value = clamp(Math.round(fly.pos.y), 50, 3000); $(\'fAltV\').textContent = fmt(fly.pos.y); };\n  function flyFromOrbit() {\n    const p = orbitPos(); fly.pos.copy(p);\n    const d = new THREE.Vector3().subVectors(target, p).normalize();\n    fly.yaw = Math.atan2(-d.x, -d.z); fly.pitch = Math.asin(clamp(d.y, -1, 1)); updateAlt();\n  }\n  function orbitFromFly() {\n    const d = new THREE.Vector3(-Math.sin(fly.yaw) * Math.cos(fly.pitch), Math.sin(fly.pitch), -Math.cos(fly.yaw) * Math.cos(fly.pitch));\n    target.copy(fly.pos).addScaledVector(d, 1200); if (target.y < 0) target.y = 0;\n    const v = new THREE.Vector3().subVectors(fly.pos, target); radius = Math.max(150, v.length());\n    ph = Math.acos(clamp(v.y / radius, -1, 1)); th = Math.atan2(v.x, v.z);\n  }\n  const setView = n => {\n    if (FLYV[n]) { const f = FLYV[n]; setMode(\'fly\'); fly.pos.set(f[0], f[1], f[2]); fly.yaw = f[3]; fly.pitch = f[4]; updateAlt(); dirty = true; return; }\n    const v = V[n]; target.set(v[0], v[1], v[2]); th = v[3]; ph = v[4]; radius = v[5]; if (mode !== \'orbit\') flyFromOrbit(); dirty = true;\n  };\n  document.querySelectorAll(\'[data-view]\').forEach(b => b.onclick = () => { if (mode === \'tour\') return; setView(b.dataset.view); });\n  function applyCam() {\n    if (mode === \'orbit\') { camera.position.copy(orbitPos()); camera.lookAt(target); }\n    else { camera.position.copy(fly.pos); camera.rotation.order = \'YXZ\'; camera.rotation.set(fly.pitch, fly.yaw, 0); }\n    camera.updateMatrixWorld();\n  }\n  const setMode = (m2) => {\n    if (m2 === mode) return;\n    if (mode === \'orbit\') flyFromOrbit(); else if (m2 === \'orbit\') orbitFromFly();\n    mode = m2; $(\'hud\').hidden = mode !== \'fly\'; dirty = true;\n    camera.fov = mode === \'orbit\' ? FOV_EXT : fovInt; camera.updateProjectionMatrix();\n    $(\'tFly\').setAttribute(\'aria-pressed\', mode === \'fly\');\n    $(\'flyInfo\').textContent = mode === \'fly\' ? \'Vuelo: arrastra para mirar (hacia arriba para ver el cielo) · palanca para avanzar · ▲▼ para subir o bajar\' : (mode === \'tour\' ? \'Reproduciendo el recorrido…\' : \'Arrastra para girar · pellizca o rueda para acercar\');\n  };\n  const tog = (id, fn) => { const b = $(id); b.onclick = () => { const on = b.getAttribute(\'aria-pressed\') !== \'true\'; b.setAttribute(\'aria-pressed\', on); fn(on); dirty = true; }; };\n  const cssVar = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();\n  const applyTheme = () => { scene.background = new THREE.Color(night ? \'#090c11\' : cssVar(\'--bg\')); dirty = true; };\n  tog(\'tWalls\', on => built.shell.walls.visible = on);\n  tog(\'tPend\', on => built.merged.pend.visible = on);\n  tog(\'tFac\', on => { built.merged.fac.visible = on; built.fac.halos.visible = on && night; });\n  // Fachada semitransparente: copia propia de los materiales de la fachada y del revestimiento interior de sus muros, para no afectar al resto\n  const facSkin = [];\n  const addSkin = o => { if (!o.isMesh) return; const arr = Array.isArray(o.material); const cl = (arr ? o.material : [o.material]).map(mt => { const c = mt.clone(); facSkin.push({ c, t: c.transparent, o: c.opacity, d: c.depthWrite }); return c; }); o.material = arr ? cl : cl[0]; };\n  built.merged.fac.traverse(addSkin); built.shell.walls.traverse(o => { if (o.userData && o.userData.facadeSkin) addSkin(o); });\n  const applyFacT = on => { const k = +$(\'fFacOp\').value / 100; facSkin.forEach(s => { if (on && !(s.t && s.o < 0.3)) { s.c.transparent = true; s.c.opacity = k; s.c.depthWrite = false; } else { s.c.transparent = s.t; s.c.opacity = s.o; s.c.depthWrite = s.d; } s.c.needsUpdate = true; }); dirty = true; };\n  tog(\'tFacT\', applyFacT);\n  $(\'fFacOp\').oninput = () => { $(\'fFacOpV\').textContent = $(\'fFacOp\').value + \' %\'; if ($(\'tFacT\').getAttribute(\'aria-pressed\') === \'true\') applyFacT(true); };\n  tog(\'tLuz\', on => { built.merged.luz.visible = on; built.cables.visible = on; });\n  tog(\'tCiel\', on => built.ceil.root.visible = on);\n  tog(\'tNight\', on => { night = on; applyNight(); });\n  tog(\'tFly\', on => { if (mode === \'tour\') return; setMode(on ? \'fly\' : \'orbit\'); });\n  window.matchMedia(\'(prefers-color-scheme: dark)\').addEventListener(\'change\', applyTheme);\n\n  // Vuelo: palanca, botones de altura y teclado\n  const keys = {}; let jx = 0, jy = 0, vy = 0, joyId = null;\n  const joy = $(\'joy\'), knob = $(\'knob\');\n  const moveJoy = e => { const r = joy.getBoundingClientRect(); let x = e.clientX - r.left - r.width / 2, y = e.clientY - r.top - r.height / 2; const R = r.width / 2 - 20, l = Math.hypot(x, y); if (l > R) { x *= R / l; y *= R / l; } knob.style.transform = \'translate(\' + x + \'px,\' + y + \'px)\'; jx = x / R; jy = y / R; };\n  joy.addEventListener(\'pointerdown\', e => { joyId = e.pointerId; joy.setPointerCapture(e.pointerId); moveJoy(e); });\n  joy.addEventListener(\'pointermove\', e => { if (e.pointerId === joyId) moveJoy(e); });\n  const endJoy = e => { if (e.pointerId === joyId) { joyId = null; jx = jy = 0; knob.style.transform = \'translate(0,0)\'; } };\n  joy.addEventListener(\'pointerup\', endJoy); joy.addEventListener(\'pointercancel\', endJoy);\n  [[\'vUp\', 1], [\'vDown\', -1]].forEach(([id, s]) => { const b = $(id); b.addEventListener(\'pointerdown\', e => { b.setPointerCapture(e.pointerId); vy = s; }); const end = () => { vy = 0; }; b.addEventListener(\'pointerup\', end); b.addEventListener(\'pointercancel\', end); });\n  window.addEventListener(\'keydown\', e => { if (mode !== \'fly\' || /INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) return; keys[e.code] = true; if (e.code === \'Space\') e.preventDefault(); });\n  window.addEventListener(\'keyup\', e => { keys[e.code] = false; });\n  $(\'fAlt\').oninput = () => { fly.pos.y = +$(\'fAlt\').value; $(\'fAltV\').textContent = fmt(fly.pos.y); dirty = true; };\n  $(\'fFov\').oninput = () => { fovInt = +$(\'fFov\').value; $(\'fFovV\').textContent = fovInt + \'°\'; if (mode !== \'orbit\') { camera.fov = fovInt; camera.updateProjectionMatrix(); dirty = true; } };\n  $(\'fSpd\').oninput = () => { fly.speed = +$(\'fSpd\').value; $(\'fSpdV\').textContent = (fly.speed / 100).toFixed(0) + \' m/s\'; };\n\n  // Recorrido: puntos fijados a mano, trayectoria suave y grabación de video\n  const tour = { pts: [], t: 0, dur: 30, seg: [], curve: null, prev: \'orbit\' };\n  const msg = t => { $(\'rMsg\').textContent = t; };\n  function renderList() {\n    $(\'rList\').innerHTML = tour.pts.map((p, i) => \'<li>punto \' + (i + 1) + \' · x \' + Math.round(p.x) + \', y \' + Math.round(-p.z) + \' · altura <input type="number" data-i="\' + i + \'" value="\' + Math.round(p.y) + \'" min="20" max="1500"> cm <button data-d="\' + i + \'" aria-label="Quitar punto \' + (i + 1) + \'">✕</button></li>\').join(\'\');\n  }\n  $(\'rList\').addEventListener(\'input\', e => { const i = e.target.dataset.i; if (i !== undefined) tour.pts[+i].y = +e.target.value || tour.pts[+i].y; });\n  $(\'rList\').addEventListener(\'click\', e => { const d = e.target.dataset.d; if (d !== undefined) { tour.pts.splice(+d, 1); renderList(); } });\n  $(\'rAdd\').onclick = () => {\n    applyCam(); const p = camera.position.clone(), d = new THREE.Vector3(); camera.getWorldDirection(d);\n    tour.pts.push({ x: p.x, y: p.y, z: p.z, yaw: Math.atan2(-d.x, -d.z), pitch: Math.asin(clamp(d.y, -1, 1)) });\n    renderList(); msg(\'Punto \' + tour.pts.length + \' agregado desde la vista actual.\');\n  };\n  $(\'rClear\').onclick = () => { tour.pts = []; renderList(); msg(\'Recorrido borrado.\'); };\n  $(\'rExp\').onclick = () => { $(\'rJson\').value = JSON.stringify({ pts: tour.pts, dur: +$(\'rDur\').value, fix: $(\'rFix\').checked, h: +$(\'rH\').value }); msg(\'Recorrido copiado en el cuadro; guárdalo para reusarlo.\'); };\n  $(\'rImp\').onclick = () => { try { const o = JSON.parse($(\'rJson\').value); tour.pts = o.pts || []; $(\'rDur\').value = o.dur || 30; $(\'rFix\').checked = !!o.fix; $(\'rH\').value = o.h || 300; renderList(); msg(\'Recorrido importado.\'); } catch (err) { msg(\'El texto no es un recorrido válido.\'); } };\n  let rec = null, chunks = [];\n  function startRec() {\n    if (!cv.captureStream || typeof MediaRecorder === \'undefined\') { msg(\'Este navegador no graba video desde la página: usa la grabación de pantalla mientras se reproduce.\'); return false; }\n    const mt = [\'video/mp4;codecs=avc1\', \'video/webm;codecs=vp9\', \'video/webm;codecs=vp8\', \'video/webm\'].find(t => MediaRecorder.isTypeSupported(t)) || \'\';\n    rec = new MediaRecorder(cv.captureStream(30), mt ? { mimeType: mt, videoBitsPerSecond: 8000000 } : {});\n    chunks = []; rec.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data); };\n    rec.onstop = () => {\n      const type = rec.mimeType || \'video/webm\', blob = new Blob(chunks, { type }), url = URL.createObjectURL(blob), ext = type.indexOf(\'mp4\') >= 0 ? \'mp4\' : \'webm\';\n      $(\'rVid\').src = url; $(\'rVid\').hidden = false; $(\'rLink\').href = url; $(\'rLink\').download = \'recorrido.\' + ext; $(\'rLink\').hidden = false; $(\'rLink\').textContent = \'Descargar video (\' + ext + \')\';\n      recording = false; addVideo(blob, ext, url); msg(\'Video listo: reprodúcelo abajo o descárgalo.\');\n    };\n    rec.start(); recording = true; return true;\n  }\n  function startTour(record) {\n    if (tour.pts.length < 2) { msg(\'Agrega al menos 2 puntos.\'); return; }\n    tour.dur = Math.max(5, +$(\'rDur\').value || 30);\n    const fix = $(\'rFix\').checked, h = +$(\'rH\').value || 300;\n    const P = tour.pts.map(p => new THREE.Vector3(p.x, fix ? h : p.y, p.z));\n    tour.curve = new THREE.CatmullRomCurve3(P, false, \'centripetal\');\n    const L = []; for (let i = 0; i < P.length - 1; i++) L.push(P[i].distanceTo(P[i + 1]) + 50);\n    const T = L.reduce((a, b) => a + b, 0); tour.seg = L.map(l => l / T * tour.dur);\n    tour.fixH = fix ? h : null; tour.t = 0; tour.prev = mode === \'tour\' ? \'orbit\' : mode;\n    $(\'rVid\').hidden = true; $(\'rLink\').hidden = true;\n    if (record && !startRec()) return;\n    setMode(\'tour\'); msg(record ? \'Grabando…\' : \'Reproduciendo…\');\n  }\n  function stopTour() {\n    if (mode !== \'tour\') return;\n    if (recording && rec && rec.state !== \'inactive\') rec.stop();\n    setMode(tour.prev); if (!recording) msg(\'Recorrido detenido.\');\n  }\n  function tourStep(dt) {\n    tour.t += dt; let t = tour.t, i = 0;\n    while (i < tour.seg.length - 1 && t > tour.seg[i]) { t -= tour.seg[i]; i++; }\n    const s = clamp(t / tour.seg[i], 0, 1), k = s * s * (3 - 2 * s), n = tour.pts.length;\n    fly.pos.copy(tour.curve.getPoint((i + s) / (n - 1)));\n    const a = tour.pts[i], b = tour.pts[i + 1]; let dy = b.yaw - a.yaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy));\n    fly.yaw = a.yaw + dy * k; fly.pitch = a.pitch + (b.pitch - a.pitch) * k; dirty = true;\n    if (tour.t >= tour.dur) stopTour();\n  }\n  $(\'rPlay\').onclick = () => startTour(false); $(\'rRec\').onclick = () => startTour(true); $(\'rStop\').onclick = stopTour;\n\n  // Vistas guardadas, imágenes en el almacenamiento local, videos y exportación del HTML con todo adentro\n  const SK = \'ap3d:\' + document.title, estado = (() => { try { return JSON.parse($(\'estado\').textContent) || {}; } catch (e) { return {}; } })();\n  const ls = { get: k => { try { return JSON.parse(localStorage.getItem(SK + \':\' + k)) || []; } catch (e) { return []; } }, set: (k, v) => { try { localStorage.setItem(SK + \':\' + k, JSON.stringify(v)); return true; } catch (e) { return false; } } };\n  const uniq = (a, b, key) => { const out = a.slice(); b.forEach(x => { if (!out.some(y => y[key] === x[key])) out.push(x); }); return out; };\n  const saved = { views: uniq(estado.views || [], ls.get(\'vistas\'), \'n\'), imgs: uniq(estado.imgs || [], ls.get(\'imgs\'), \'d\'), vids: (estado.vids || []).slice() };\n  const arMsg = t => { $(\'arMsg\').textContent = t; };\n  const camState = () => mode === \'orbit\' ? { m: \'o\', t: [target.x, target.y, target.z], th, ph, r: radius } : { m: \'f\', p: [fly.pos.x, fly.pos.y, fly.pos.z], yaw: fly.yaw, pitch: fly.pitch };\n  function goView(v) {\n    if (mode === \'tour\') return;\n    if (v.m === \'o\') { if (mode !== \'orbit\') setMode(\'orbit\'); target.set(v.t[0], v.t[1], v.t[2]); th = v.th; ph = v.ph; radius = v.r; }\n    else { if (mode !== \'fly\') setMode(\'fly\'); fly.pos.set(v.p[0], v.p[1], v.p[2]); fly.yaw = v.yaw; fly.pitch = v.pitch; updateAlt(); }\n    dirty = true;\n  }\n  function renderViews() {\n    $(\'vgList\').innerHTML = saved.views.map((v, i) => \'<li><button data-vg="\' + i + \'">\' + v.n.replace(/</g, \'&lt;\') + \'</button> <button data-vx="\' + i + \'" aria-label="Borrar la vista \' + (i + 1) + \'">✕</button></li>\').join(\'\') || \'<li>Aún no hay vistas guardadas. Además de las predeterminadas, guarda aquí las tuyas.</li>\';\n  }\n  $(\'vgList\').addEventListener(\'click\', e => { const g = e.target.dataset.vg, x = e.target.dataset.vx; if (g !== undefined) goView(saved.views[+g]); if (x !== undefined) { saved.views.splice(+x, 1); ls.set(\'vistas\', saved.views); renderViews(); } });\n  $(\'vgSave\').onclick = () => {\n    if (mode === \'tour\') { arMsg(\'Detén el recorrido para guardar una vista.\'); return; }\n    const n = $(\'vgName\').value.trim() || (\'Vista \' + (saved.views.length + 1)), v = Object.assign({ n }, camState());\n    const i = saved.views.findIndex(q => q.n === n); if (i >= 0) saved.views[i] = v; else saved.views.push(v);\n    ls.set(\'vistas\', saved.views); $(\'vgName\').value = \'\'; renderViews(); arMsg(\'Vista "\' + n + \'" guardada.\');\n  };\n  function renderImgs() {\n    $(\'imGal\').innerHTML = saved.imgs.map((im, i) => \'<figure><a href="\' + im.d + \'" download="imagen-\' + (i + 1) + \'.jpg"><img src="\' + im.d + \'" alt="Imagen guardada \' + (i + 1) + \'"></a><button data-ix="\' + i + \'" aria-label="Borrar la imagen \' + (i + 1) + \'">✕</button></figure>\').join(\'\');\n  }\n  $(\'imGal\').addEventListener(\'click\', e => { const x = e.target.dataset.ix; if (x !== undefined) { saved.imgs.splice(+x, 1); ls.set(\'imgs\', saved.imgs); renderImgs(); } });\n  $(\'imSave\').onclick = () => {\n    applyCam(); renderer.render(scene, camera);\n    const w = Math.min(1280, cv.width), c2 = document.createElement(\'canvas\'); c2.width = w; c2.height = Math.round(cv.height * w / cv.width);\n    c2.getContext(\'2d\').drawImage(cv, 0, 0, c2.width, c2.height);\n    const d = c2.toDataURL(\'image/jpeg\', 0.82); saved.imgs.push({ d, t: Date.now() });\n    if (!ls.set(\'imgs\', saved.imgs)) { saved.imgs.pop(); arMsg(\'El almacenamiento del navegador está lleno: descarga o borra imágenes y vuelve a intentar.\'); return; }\n    renderImgs(); arMsg(\'Imagen guardada (\' + saved.imgs.length + \'). Toca una miniatura para descargarla.\');\n  };\n  $(\'imClear\').onclick = () => { saved.imgs = []; ls.set(\'imgs\', saved.imgs); renderImgs(); arMsg(\'Imágenes borradas.\'); };\n  function renderVids() {\n    $(\'vidList\').innerHTML = saved.vids.map((v, i) => \'<li>Video \' + (i + 1) + \' (\' + v.ext + (v.mb ? \', \' + v.mb + \' MB\' : \'\') + \') <button data-vv="\' + i + \'">Ver</button> <a href="\' + (v.url || \'#\') + \'" download="video-\' + (i + 1) + \'.\' + v.ext + \'">Descargar</a> <button data-vq="\' + i + \'" aria-label="Quitar el video \' + (i + 1) + \'">✕</button></li>\').join(\'\');\n  }\n  $(\'vidList\').addEventListener(\'click\', e => { const v = e.target.dataset.vv, q = e.target.dataset.vq; if (v !== undefined) { const it = saved.vids[+v]; $(\'rVid\').src = it.url; $(\'rVid\').hidden = false; } if (q !== undefined) { saved.vids.splice(+q, 1); renderVids(); } });\n  function addVideo(blob, ext, url) { saved.vids.push({ ext, url, blob, mb: (blob.size / 1048576).toFixed(1) }); renderVids(); }\n  const toDataUrl = blob => new Promise(res => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(blob); });\n  const pressed0 = {}; document.querySelectorAll(\'button[aria-pressed]\').forEach(b => { pressed0[b.id] = b.getAttribute(\'aria-pressed\'); });\n  $(\'exHtml\').onclick = async () => {\n    arMsg(\'Preparando el archivo…\');\n    const vids = []; for (const v of saved.vids) vids.push({ ext: v.ext, mb: v.mb, url: v.blob ? await toDataUrl(v.blob) : v.url });\n    const est = { views: saved.views, imgs: saved.imgs, vids, tour: { pts: tour.pts, dur: +$(\'rDur\').value, fix: $(\'rFix\').checked, h: +$(\'rH\').value }, facOp: +$(\'fFacOp\').value };\n    const clone = document.documentElement.cloneNode(true);\n    clone.querySelector(\'#estado\').textContent = JSON.stringify(est).replace(/</g, \'\\\\u003c\');\n    clone.querySelectorAll(\'button[aria-pressed]\').forEach(b => { if (pressed0[b.id] !== undefined) b.setAttribute(\'aria-pressed\', pressed0[b.id]); });\n    clone.querySelectorAll(\'details\').forEach(d => d.removeAttribute(\'open\'));                      // el archivo se abre con los paneles cerrados\n    [\'imGal\', \'vidList\', \'vgList\'].forEach(id => { const el = clone.querySelector(\'#\' + id); if (el) el.innerHTML = \'\'; });   // se vuelven a dibujar al abrir\n    const rv = clone.querySelector(\'#rVid\'); if (rv) { rv.removeAttribute(\'src\'); rv.setAttribute(\'hidden\', \'\'); }\n    const rl = clone.querySelector(\'#rLink\'); if (rl) { rl.removeAttribute(\'href\'); rl.setAttribute(\'hidden\', \'\'); }\n    [\'rMsg\', \'arMsg\'].forEach(id => { const el = clone.querySelector(\'#\' + id); if (el && id === \'rMsg\') el.textContent = \'\'; });\n    const html = \'<!doctype html>\\n\' + clone.outerHTML, blob = new Blob([html], { type: \'text/html\' }), a = document.createElement(\'a\');\n    a.href = URL.createObjectURL(blob); a.download = (document.title.replace(/[^\\w\\-]+/g, \'-\').replace(/-+/g, \'-\') || \'modelo\') + \'-exportado.html\'; document.body.appendChild(a); a.click(); a.remove();\n    arMsg(\'Archivo exportado (\' + (blob.size / 1048576).toFixed(1) + \' MB) con \' + saved.views.length + \' vistas, \' + saved.imgs.length + \' imágenes y \' + vids.length + \' videos.\');\n  };\n  if (estado.tour && estado.tour.pts && estado.tour.pts.length) { tour.pts = estado.tour.pts; $(\'rDur\').value = estado.tour.dur || 30; $(\'rFix\').checked = !!estado.tour.fix; $(\'rH\').value = estado.tour.h || 300; renderList(); }\n  if (estado.facOp) { $(\'fFacOp\').value = estado.facOp; $(\'fFacOpV\').textContent = estado.facOp + \' %\'; }\n  renderViews(); renderImgs(); renderVids();\n\n  // Zoom orbital hacia el punto bajo el cursor (o entre los dedos): el centro de giro se acerca a ese punto en la misma proporción que el radio,\n  // de modo que lo que está bajo el cursor se queda en su lugar de la pantalla. Sin la casilla, el zoom va al centro de giro, como antes.\n  const zRay = new THREE.Raycaster(), zPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), zNdc = new THREE.Vector2(), zHit = new THREE.Vector3(); let zCache = null;\n  function pickPoint(cx, cy) {\n    const t = performance.now();\n    if (zCache && t - zCache.t < 400 && Math.hypot(zCache.x - cx, zCache.y - cy) < 2) { zCache.t = t; return zCache.p; }\n    const r = cv.getBoundingClientRect(); zNdc.set(((cx - r.left) / r.width) * 2 - 1, -((cy - r.top) / r.height) * 2 + 1);\n    applyCam(); camera.updateMatrixWorld(); zRay.setFromCamera(zNdc, camera);\n    const hits = zRay.intersectObjects(Object.values(built.merged).filter(g => g.visible), true); let p = null;\n    if (hits.length) p = hits[0].point.clone(); else if (zRay.ray.intersectPlane(zPlane, zHit)) p = zHit.clone();\n    zCache = p ? { x: cx, y: cy, t, p } : null; return p;\n  }\n  // Acercarse de verdad (no es un zoom): la cámara avanza hacia el punto bajo el cursor o entre los dedos, sin tope de distancia, y se detiene a 25 cm de cualquier\n  // objeto, del suelo o de un muro. El centro de giro queda a la profundidad de ese punto. Con la casilla desmarcada avanza hacia el centro de la pantalla.\n  const COL = built.colliders, NEAR = 25;\n  function clearance(x, y, z) {\n    let d = Math.min(NEAR, y); const b = COL.boxes;\n    for (let i = 0; i < b.length; i += 6) {\n      const dx = Math.max(b[i] - x, 0, x - b[i + 3]); if (dx >= d) continue;\n      const dy = Math.max(b[i + 1] - y, 0, y - b[i + 4]); if (dy >= d) continue;\n      const dz = Math.max(b[i + 2] - z, 0, z - b[i + 5]); if (dz >= d) continue;\n      const r = Math.sqrt(dx * dx + dy * dy + dz * dz); if (r < d) d = r;\n    }\n    if (y < COL.wallH + NEAR) COL.walls.forEach(w => {\n      const vx = w[2] - w[0], vz = w[3] - w[1], t = clamp(((x - w[0]) * vx + (z - w[1]) * vz) / (vx * vx + vz * vz), 0, 1);\n      const r = Math.hypot(x - (w[0] + t * vx), z - (w[1] + t * vz)) - 6; if (r < d) d = Math.max(r, 0);\n    });\n    return d;\n  }\n  const canMove = (from, to) => { const n = clearance(to.x, to.y, to.z); return n >= NEAR || n >= clearance(from.x, from.y, from.z) - 0.01; };   // desde una posición ya pegada a algo se puede salir\n  function dollyBy(f, cx, cy) {                      // f < 1 se acerca, f > 1 se aleja\n    const C = orbitPos(), fwd = new THREE.Vector3().subVectors(target, C).normalize();\n    let P = $(\'zCur\').checked ? pickPoint(cx, cy) : null; if (!P) P = C.clone().addScaledVector(fwd, radius);\n    const full = P.clone().sub(C); let t = 1 - f, C2 = null;\n    for (let k = 0; k < 8; k++) { const c2 = C.clone().addScaledVector(full, t); if (t < 0 || canMove(C, c2)) { C2 = c2; break; } t *= 0.5; }\n    if (!C2 || C2.distanceTo(C) < 0.05 || C2.length() > 20000) return;\n    const depth = clamp(P.clone().sub(C2).dot(fwd), 40, 9000);\n    radius = depth; target.copy(C2).addScaledVector(fwd, depth);\n  }\n  function panBy(dx, dy) {                           // desplaza la cámara paralelo a la pantalla; el contenido sigue al dedo\n    if (!dx && !dy) return;\n    const k = 2 * radius * Math.tan(camera.fov * Math.PI / 360) / cv.clientHeight; camera.updateMatrixWorld();\n    const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);\n    const mv = right.multiplyScalar(-dx * k).addScaledVector(up, dy * k), C = orbitPos();\n    for (let s = 1, i = 0; i < 6; i++, s *= 0.5) { if (canMove(C, C.clone().addScaledVector(mv, s))) { target.addScaledVector(mv, s); return; } }\n  }\n  function lowFix() { const c = orbitPos(); if (c.y < NEAR) ph = Math.acos(clamp((NEAR - target.y) / radius, -1, 1)); }   // la cámara no baja del suelo\n\n  // Entrada del lienzo: órbita o mirada de vuelo\n  const pts = new Map(); let lastDist = 0;\n  let lastMid = null;\n  cv.addEventListener(\'contextmenu\', e => e.preventDefault());\n  cv.addEventListener(\'pointerdown\', e => { if (mode === \'tour\') return; try { cv.setPointerCapture(e.pointerId); } catch (err) {} pts.set(e.pointerId, { x: e.clientX, y: e.clientY }); lastDist = 0; lastMid = null; });\n  cv.addEventListener(\'pointermove\', e => {\n    const p = pts.get(e.pointerId); if (!p || mode === \'tour\') return;\n    const dx = e.clientX - p.x, dy = e.clientY - p.y; p.x = e.clientX; p.y = e.clientY;\n    if (mode === \'fly\') { if (pts.size === 1) { fly.yaw -= dx * 0.005; fly.pitch = clamp(fly.pitch - dy * 0.005, -1.5, 1.5); } }\n    else if (pts.size === 1) { if (e.pointerType === \'mouse\' && ((e.buttons & 2) || e.shiftKey)) panBy(dx, dy); else { th -= dx * 0.007; ph = clamp(ph - dy * 0.007, 0.02, 1.9); lowFix(); } }\n    else if (pts.size === 2) { const [a, b] = [...pts.values()], d = Math.hypot(a.x - b.x, a.y - b.y), mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2; if (lastDist && lastMid) { dollyBy(lastDist / d, mx, my); panBy(mx - lastMid.x, my - lastMid.y); } lastDist = d; lastMid = { x: mx, y: my }; }\n    dirty = true;\n  });\n  const up = e => { pts.delete(e.pointerId); lastDist = 0; lastMid = null; };\n  cv.addEventListener(\'pointerup\', up); cv.addEventListener(\'pointercancel\', up);\n  cv.addEventListener(\'wheel\', e => {\n    e.preventDefault(); if (mode === \'tour\') return;\n    if (mode === \'fly\') { const s = -e.deltaY * 0.6, sy = Math.sin(fly.yaw), cy = Math.cos(fly.yaw); fly.pos.x += -sy * s; fly.pos.z += -cy * s; }\n    else dollyBy(Math.exp(e.deltaY * 0.001), e.clientX, e.clientY);\n    dirty = true;\n  }, { passive: false });\n  function resize() { const w = stage.clientWidth, h = stage.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); dirty = true; }\n  new ResizeObserver(resize).observe(stage);\n  applyNight(); applyTheme(); resize(); updateAlt();\n  let last = performance.now();\n  (function loop(now) {\n    const dt = Math.min(0.05, (now - last) / 1000); last = now;\n    if (mode === \'fly\') {\n      const sp = fly.speed * (keys.ShiftLeft || keys.ShiftRight ? 2.5 : 1);\n      const f = -jy + (keys.KeyW ? 1 : 0) - (keys.KeyS ? 1 : 0), s = jx + (keys.KeyD ? 1 : 0) - (keys.KeyA ? 1 : 0);\n      const v = vy + ((keys.KeyE || keys.Space) ? 1 : 0) - ((keys.KeyQ || keys.ControlLeft) ? 1 : 0);\n      if (f || s || v) {\n        const sy = Math.sin(fly.yaw), cy = Math.cos(fly.yaw);\n        fly.pos.x += (-sy * f + cy * s) * sp * dt; fly.pos.z += (-cy * f - sy * s) * sp * dt;\n        fly.pos.y = clamp(fly.pos.y + v * sp * 0.6 * dt, 20, 5000); updateAlt(); dirty = true;\n      }\n    } else if (mode === \'tour\') tourStep(dt);\n    if (dirty) { applyCam(); renderer.render(scene, camera); dirty = false; }\n    requestAnimationFrame(loop);\n  })(last);\n}\n'
html = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Tienda Talca · modelo v39</title>
<style>{css}</style>
</head>
<body>
<header>
  <h1>Autoplanet Talca · modelo 3D v39</h1>
  <p id="readout"></p>
</header>
<div id="stage">
  <canvas id="cv" aria-label="Modelo 3D de la tienda. Arrastra para girar, pellizca para acercar."></canvas>
  <div class="hint" id="flyInfo">Arrastra para girar · pellizca o rueda para acercar</div>
  <div id="hud" hidden><div id="joy" aria-label="Palanca de avance"><div id="knob"></div></div><div id="vert"><button id="vUp" aria-label="Subir">▲</button><button id="vDown" aria-label="Bajar">▼</button></div></div>
</div>
<div class="controls">
  <button data-view="planta">Planta</button>
  <button data-view="aerea">Aérea</button>
  <button data-view="fachada">Fachada</button>
  <button data-view="sala">Sala</button>
  <button data-view="bodega">Bodega</button>
  <button data-view="ojosSala">Ojos sala</button>
  <button data-view="ojosBodega">Ojos bodega</button>
  <span class="sep"></span>
  <button id="tWalls" aria-pressed="true">Muros</button>
  <button id="tPend" aria-pressed="true">Pendientes</button>
  <button id="tFac" aria-pressed="true">Fachada</button>
  <button id="tFacT" aria-pressed="false">Fachada transp.</button>
  <button id="tFly" aria-pressed="false">Vuelo</button>
  <button id="tLuz" aria-pressed="true">Luces</button>
  <button id="tCiel" aria-pressed="true">Cielos</button>
  <button id="tNight" aria-pressed="false">Noche</button>
  <select id="nLevel" aria-label="Intensidad de la luz nocturna"><option value="0.6">Luz débil</option><option value="1.0">Luz media</option><option value="1.6" selected>Luz alta</option></select>
</div>
<details id="vuelo">
  <summary>Vuelo y recorrido en video</summary>
  <div class="ceilrow"><span class="zn">Altura</span><input type="range" id="fAlt" min="50" max="3000" step="5" value="300" aria-label="Altura de vuelo"><output id="fAltV">3,00 m</output></div>
  <div class="ceilrow"><span class="zn">Apertura</span><input type="range" id="fFov" min="40" max="100" step="1" value="70" aria-label="Apertura de la cámara en vuelo"><output id="fFovV">70°</output></div>
  <div class="ceilrow"><span class="zn">Velocidad</span><input type="range" id="fSpd" min="100" max="1500" step="50" value="500" aria-label="Velocidad de vuelo"><output id="fSpdV">5 m/s</output></div>
  <p class="note">Con el botón "Vuelo": arrastra para mirar, usa la palanca para avanzar y ▲▼ para subir o bajar. En computador: W A S D para moverte, Q y E para bajar y subir, Mayús para ir más rápido.</p>
  <div class="ceilrow"><button id="rAdd">Agregar punto</button><button id="rPlay">Reproducir</button><button id="rRec">Grabar video</button><button id="rStop">Detener</button><button id="rClear">Borrar</button></div>
  <div class="ceilrow"><span class="zn">Duración</span><input type="number" id="rDur" value="30" min="5" max="300" aria-label="Duración en segundos"> s
    <label><input type="checkbox" id="rFix"> altura fija</label><input type="number" id="rH" value="300" min="50" max="1500" aria-label="Altura fija del recorrido"> cm</div>
  <p class="note">Vuela hasta cada lugar, mira hacia donde quieras y pulsa "Agregar punto". El recorrido une los puntos con una trayectoria suave. Con "altura fija" todo el recorrido vuela a esa altura.</p>
  <ol id="rList"></ol>
  <p class="note" id="rMsg"></p>
  <textarea id="rJson" rows="3" placeholder="Recorrido en texto, para guardar o pegar"></textarea>
  <div class="ceilrow"><button id="rExp">Exportar</button><button id="rImp">Importar</button></div>
  <video id="rVid" controls hidden playsinline></video><a id="rLink" hidden>Descargar video</a>
</details>
<details id="archivo">
  <summary>Vistas, imágenes y exportar</summary>
  <div class="ceilrow"><label><input type="checkbox" id="zCur" checked> Acercarse hacia el cursor o los dedos</label></div>
  <div class="ceilrow"><span class="zn">Fachada</span><input type="range" id="fFacOp" min="5" max="60" step="1" value="22" aria-label="Opacidad de la fachada semitransparente"><output id="fFacOpV">22 %</output></div>
  <p class="note">El botón "Fachada transp." deja la fachada (y el revestimiento interior de sus muros) semitransparente, para ver el interior desde afuera. El vidrio no cambia.</p>
  <div class="ceilrow"><input type="text" id="vgName" placeholder="Nombre de la vista" aria-label="Nombre de la vista"><button id="vgSave">Guardar vista</button></div>
  <ul id="vgList" class="saved"></ul>
  <div class="ceilrow"><button id="imSave">Guardar imagen</button><button id="imClear">Borrar imágenes</button></div>
  <div id="imGal" class="gal"></div>
  <ul id="vidList" class="saved"></ul>
  <div class="ceilrow"><button id="exHtml">Exportar HTML</button></div>
  <p class="note" id="arMsg">Las vistas y las imágenes se guardan en este navegador. Los videos viven mientras la página esté abierta: "Exportar HTML" los lleva dentro del archivo, junto con las vistas, las imágenes y el recorrido.</p>
</details>
<details id="cielos">
  <summary>Cielos</summary>
  <div class="ceilrow"><span class="zn">Sala</span>
    <select id="cSalaMode" aria-label="Cielo de la sala"><option value="none">Sin cielo</option><option value="aw">Americano blanco</option><option value="ab">Americano negro</option><option value="pn">Pintura negra, estructura a la vista</option></select>
    <input type="range" id="cSalaH" min="250" max="800" step="5" value="450" disabled aria-label="Altura del cielo de la sala"><output id="cSalaV"></output></div>
  <div class="ceilrow"><span class="zn">Muros</span><label><input type="checkbox" id="cSalaWOn"> Negros</label><input type="range" id="cSalaW" min="300" max="800" step="5" value="410" disabled aria-label="Altura desde la que se pintan de negro los muros de la sala"><output id="cSalaWV"></output></div>
  <div class="ceilrow"><span class="zn">Bodega</span>
    <select id="cBodMode" aria-label="Cielo de la bodega"><option value="none">Sin cielo</option><option value="aw">Americano blanco</option><option value="ab">Americano negro</option><option value="pn">Pintura negra, estructura a la vista</option></select>
    <input type="range" id="cBodH" min="250" max="800" step="5" value="387" disabled aria-label="Altura del cielo de la bodega"><output id="cBodV"></output></div>
  <div class="ceilrow"><span class="zn">Muros</span><label><input type="checkbox" id="cBodWOn"> Negros</label><input type="range" id="cBodW" min="300" max="800" step="5" value="410" disabled aria-label="Altura desde la que se pintan de negro los muros de la bodega"><output id="cBodWV"></output></div>
  <p class="note">Para ver el cielo desde adentro, usa "Ojos sala" u "Ojos bodega" o activa "Vuelo" y arrastra hacia arriba. Sala y bodega se configuran por separado: puedes dejarlas iguales, pero es una decisión tuya. El cielo de cada zona solo cubre esa zona. Con pintura negra o americano negro, los muros de esa zona también se pintan de negro desde la altura de la barra Muros, que parte 10 cm sobre la luz más alta de la zona (4,10 m en la sala y en la bodega). La casilla Negros permite pintarlos también sin cielo, o desmarcarlos.</p>
  <p class="note">El americano usa baldosas de 60 × 60 cm. En "Pintura negra" la altura es la de la parte baja de las cerchas, que van sobre los ejes estructurales: son indicativas, y no incluyo ductos ni bandejas.</p>
</details>
<details>
  <summary>Qué incluye este modelo</summary>
  <h2>Con componentes ya validados</h2>
  <ul id="listValid"></ul>
  <h2>Aproximado</h2>
  <ul id="listApprox"></ul>
  <h2>Pendiente (volúmenes ámbar, de 100 cm de alto supuesto, salvo cabeceras HP de 300 cm)</h2>
  <ul id="listPend" class="pending"></ul>
  <h2>No incluido todavía</h2>
  <ul class="pending">
    <li>Salidas de emergencia, kits, interruptores, tableros y bandejas del plano eléctrico.</li>
    <li>Franja LED del letrero en volumen: el resplandor del modo Noche es una aproximación de tu foto. Herrajes de las puertas rojas de salida, y los P.O.S., cajas fuertes y mesas de venta.</li>
    <li>Ductos y bandejas del cielo, neumáticos y productos.</li>
  </ul>
  <h2>Supuestos del conjunto</h2>
  <ul class="pending">
    <li>El cambio de alturas (bodega 3,87 m, sala 7,8 m) está en x = 16372 del plano, un eje estructural. Es una inferencia mía.</li>
    <li>Muros de 12 cm de espesor hacia afuera del contorno; no hay muro entre bodega y sala.</li>
    <li>Baños y cocina: tabiques de 2,4 m (supuesto) con las dos puertas y la del camarín cerradas; alturas de artefactos estándar, lockers de 1,8 m, y espejos y grifería agregados por mí. Los colores son supuestos.</li>
    <li>Luz nocturna: cada luminaria alumbra solo hacia abajo, con haz de 100° (dato tuyo) y caída suave hasta 140° (supuesto mío); el cielo y las cerchas casi no reciben luz.</li>
    <li>Alturas de luminarias supuestas: canoas L03 a 3,6 m y L01 a 2,7 m. Las L02 y L06 van a 4 m, como dijiste, con tirantes hasta el cielo.</li>
    <li>Hay 14 luminarias L02 en x entre 16063 y 16282, a 4 m: quedarían sobre un cielo de 3,87 m si el límite de alturas está en x = 16372. El límite puede estar más al oeste.</li>
    <li>Muros negros: la altura inicial es la de la luz más alta de la zona más 10 cm. En la bodega hay L02 a 4 m, así que parte en 4,10 m, sobre su cielo de 3,87 m: el negro solo se ve con pintura negra, sobre las cerchas. La barra Muros parte en 3 m para no tapar los vidrios (llegan a 2,8 m). Sin cielo, el muro negro llega a la altura del muro (7,8 m en la sala, 3,87 m en la bodega).</li>
    <li>Cielos: americano de 60 × 60 cm; alturas iniciales de 4,5 m en la sala y 3,87 m en la bodega. En pintura negra la altura es la libre bajo las cerchas (7,8 m y 3,87 m por defecto) y las cerchas, correas y plancha de techo son indicativas, sobre los ejes estructurales.</li>
    <li>Fachada: alturas, paños y posiciones tomados de las elevaciones, con una precisión de unos 10 cm; el espesor, el relieve y los colores son supuestos. Las pilastras, las rejillas y el revestimiento acanalado de la bodega siguen la foto de otra tienda.</li>
    <li>Mueble Admin: la altura del mesón (90 cm), la profundidad de las repisas (30 cm), la altura de la repisa baja (1,4 m), el gabinete alto (de 60 × 35 × 49 cm; va en el extremo más lejano al pasillo, el sur, porque el norte da al pasillo transversal de 90 cm) y el reparto de puertas y mallas bajo la cubierta se estiman de tu foto; las repisas bajas del lado de la sala son supuestos. Puse una tapa en cada borde porque no sé en cuál va.</li>
    <li>Racks de pallets: el grosor de los pilares y las vigas es estimado; no están los pallets. El cuadro de bodegaje da 15 pallets: 12 en estos racks y 3 en piso.</li>
    <li>Pintura de la sala: el tamaño del logo (290 cm de ancho), el reparto de rojo y naranja y la forma de las puntas salen del letrero del plano, escalado a 1 m de alto. Los muros de la sala se pintan en blanco.</li>
    <li>Vistas interiores ("Ojos sala" y "Ojos bodega"): se abren en modo vuelo, a 1,65 m, mirando unos 11° hacia arriba y con 70° de apertura; la apertura se regula en el panel de vuelo.</li>
    <li>Luz nocturna: débil se parece a la versión anterior, media queda al medio y alta es la actual.</li>
    <li>Puertas de acceso: las hojas van cerradas; el paño superior y el paño fijo repiten el mismo marco de aluminio rojo de 6 cm. La puerta doble es de 168 cm porque así la dibuja el arco del plano.</li>
    <li>Recorrido en video: el navegador graba lo que se ve en pantalla; si no puede grabar, usa la grabación de pantalla del teléfono mientras se reproduce.</li>
    <li>Noche: las luces puntuales, los charcos de luz y el resplandor son aproximaciones visuales, no un cálculo de iluminación.</li>
    <li>Pilares y cruceta "a eliminar por el desarrollador" no se dibujan.</li>
    <li>Los módulos de 120 cm del plano se modelan con 122 cm, así que pueden solaparse 2 cm.</li>
    <li>En piezas simétricas la orientación del frente es arbitraria. En los mesones, el lado cliente (45 cm) mira a la sala, al este, y las cabeceras altas quedan detrás.</li>
    <li>Las 2 cabeceras HP de la bodega miran hacia el norte del plano: no tengo su orientación real.</li>
    <li>Cada perimetral tiene 3 o 4 repisas al azar; las de tipo RN van con 70 cm de fondo, según el plano.</li>
  </ul>
</details>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script id="estado" type="application/json">{{}}</script>
<script>
const DATA = {DATA};
const SIGN = {SIGN};
{comp}
{core}
{browser}
</script>
</body>
</html>
'''
open("salida/tienda.html","w",encoding="utf8").write(html)
print("escrito", len(html)//1024, "KB")
