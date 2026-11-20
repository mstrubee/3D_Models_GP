"""Genera el visor de Autoplanet Chillán Vivo reutilizando el visor de Talca (make_html.py) y los datos leídos del PDF."""
import json, math, re, base64, ast
src = open("/home/claude/build/make_html.py", encoding="utf8").read()
def rp(a, b, cnt=1):
    global src
    assert src.count(a) == cnt, (a[:90], src.count(a)); src = src.replace(a, b)

# ---------- 1) datos: del PDF al formato del kit ----------
head_end = src.index("def block(path):")
new_head = '''import json, re, math, base64
def r1(v): return round(v,1)
def clean(o):
    if isinstance(o, float): return r1(o)
    if isinstance(o, list): return [clean(i) for i in o]
    if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
    return o
D = json.load(open("/home/claude/chillan/chillan_data.json"))
W, DEPTH = D["meta"]["W"], D["meta"]["D"]
D["contour"] = [[0, 0], [W, 0], [W, DEPTH], [0, DEPTH]]
D["XB"] = 2; D["step"] = [[2, 0], [2, DEPTH]]                       # una sola zona: la bodega es una astilla de 2 cm hasta confirmar el límite
D["bodega"] = [[0, DEPTH - 2], [2, DEPTH - 2], [2, DEPTH], [0, DEPTH]]; D["sala"] = [[0, 0], [W, 0], [W, DEPTH], [0, DEPTH]]
D["mes"] = []; D["rails"] = []
ALT_H = (D.get("altillo") or {}).get("h", 260)
luces = json.load(open("/home/claude/chillan/luces_chillan.json")); D["luz"] = []
for l in luces:
    if not l["alt"] and not (0 < l["x"] < W and 0 < l["y"] < DEPTH): continue          # focos exteriores del acceso: fuera del local
    h = ALT_H + 240 if l["alt"] else (240 if (l["t"] == "F01" and l["x"] > 1179 and l["y"] > 2047) else 400)   # baños y cocina: bajo la losa del altillo
    D["luz"].append(dict(t=l["t"], x=l["x"], y=l["y"], a=l["a"], h=h, alt=1 if l["alt"] else 0))
nuevos_ph = []
for p in D["ph"]:
    if p["cls"] == "pend" and p["label"].startswith("P.O.S"):                 # 250 x 90 = dos módulos de mesón de atención de 124 cm
        for sg in (-1, 1): D["mes"].append(dict(v="atn", x=p["x"], y=p["y"] + sg * 62.4))
    elif p["cls"] == "pend" and p["label"].startswith("Mesón Acc"):            # 175 x 90: un módulo estirado a 175 cm
        D["mes"].append(dict(v="atn", x=p["x"], y=p["y"], L=175))
    elif p["cls"] == "pend" and 535 < p["x"] < 610 and p["y"] < 400:           # caja fuerte y rack del mueble de administración: van dentro del mueble
        continue
    else: nuevos_ph.append(p)
D["ph"] = nuevos_ph
bats = D["bat"]
if bats: D["bat"] = [dict(x=sum(b["x"] for b in bats) / len(bats), y=sum(b["y"] for b in bats) / len(bats), fa=-90)]   # tres racks de 150 cm juntos = un conjunto de 3 módulos
def b64(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
SIGN = json.dumps({"sur": b64("/home/claude/chillan/sign_sur.png"), "ori": b64("/home/claude/chillan/sign_sur.png"), "logo": b64("/home/claude/pdfs/logo_ori.png"), "cenefaBat": b64("/home/claude/pdfs/cenefa_baterias.jpg"), "swBody": b64("/home/claude/pdfs/sw_body.png"), "swTip": b64("/home/claude/pdfs/sw_tip.png")})
DATA = json.dumps(clean({k: D[k] for k in ("contour","XB","step","bodega","sala","per","hp","gon","cab","mes","bat","ph","luz","rails","altillo")}), ensure_ascii=False, separators=(",",":"))
FACW = round(W)
'''
src = new_head + src[head_end:]
rp('open("/mnt/user-data/outputs/tienda_talca_v39.html"', 'open("/mnt/user-data/outputs/tienda_chillan_v0.html"')

# ---------- 2) núcleo: origen, alturas y funciones propias de Talca ----------
rp("const OX = 14392, OY = 516;", "const OX = 0, OY = 0;")
rp("const H_BOD = 387, H_SALA = 780, WALL_T = 12;", "const H_BOD = 1096, H_SALA = 1097, WALL_T = 12;\nconst FACW = ''' + str(FACW) + r''', FACH = 1097;      // ancho del local y alto del galpón medido en la elevación")
rp("function buildServicios(THREE, M, bump) {", '''function buildServicios(THREE, M, bump) {
  // Baños y cocina de Chillán Vivo: tabiques, puertas y artefactos ubicados con las líneas y símbolos del plano (cm del local)
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
  [[1179, 1191, 2108, 2352], [1315, 1327, 2108, 2352], [1476, 1488, 2047, 2352], [1266, 1315, 2108, 2120], [1327, 1382, 2108, 2120],
   [1476, 1496, 2047, 2059], [1563, 1768, 2047, 2059], [1611, 1768, 2087, 2099], [1710, 1771, 1854, 1864]].forEach(w => pb(w[0], w[1], w[2], w[3], 0, HP, M.part));
  // puertas cerradas con dintel: baño 1 (P3, 70), baño 2 (P4, 90) y cocina (P3, 70)
  [[1191, 1266, 2108, 2120], [1382, 1476, 2108, 2120], [1496, 1563, 2047, 2059]].forEach(d => {
    const yc = (d[2] + d[3]) / 2;
    pb(d[0], d[1], d[2], d[3], 210, HP, M.part);
    pb(d[0], d[1], yc - 1.75, yc + 1.75, 0, 210, M.door);
    pb(d[1] - 8, d[1] - 5, yc - 3.5, yc + 3.5, 98, 102, M.steelb);
    bump('Servicios: puerta');
  });
  // ---- Baños ----
  const wcN = (cx, yW) => {                                // WC con el estanque contra el muro norte
    const cy = yW - 40;
    cyl(cx, cy, 13, 20, 0, 32, M.cer); cyl(cx, cy, 17, 26, 32, 42, M.cer);
    pb(cx - 19, cx + 19, yW - 15, yW, 32, 82, M.cer); cyl(cx, yW - 7, 2, 2, 82, 83.5, M.steelb);
    bump('Servicios: WC');
  };
  wcN(1285, 2341); wcN(1433, 2341);
  const lavN = (x0, x1, yW) => {                           // lavamanos con pedestal, grifería y espejo contra el muro norte
    const xc = (x0 + x1) / 2, y0 = yW - 40;
    cyl(xc, yW - 12, 6, 6, 0, 72, M.cer); pb(x0, x1, y0, yW, 72, 88, M.cer);
    cyl(xc, yW - 5, 1.5, 1.5, 88, 100, M.steelb); pb(xc - 0.5, xc + 0.5, yW - 13, yW - 4, 98, 100, M.steelb);
    pb(x0 + 2, x1 - 2, yW - 0.1, yW + 1.9, 105, 165, M.mirror);
    bump('Servicios: lavamanos');
  };
  lavN(1208, 1252, 2341);
  const lavW = (x0, x1, y0, y1, wallX) => {                // lavamanos contra el muro oeste (baño 2)
    const yc = (y0 + y1) / 2;
    cyl(x0 + 9, yc, 6, 6, 0, 72, M.cer); pb(x0, x1, y0, y1, 72, 88, M.cer);
    cyl(x0 + 4, yc, 1.5, 1.5, 88, 100, M.steelb); pb(x0 + 4, x0 + 12, yc - 0.5, yc + 0.5, 98, 100, M.steelb);
    pb(wallX, wallX + 2, y0 + 2, y1 - 2, 105, 165, M.mirror);
    bump('Servicios: lavamanos');
  };
  lavW(1328, 1364, 2150, 2190, 1327);
  // ---- Cocina ----
  pb(1710, 1766, 2100, 2155, 0, 180, M.fridgeM); pb(1708, 1710, 2146, 2150, 70, 140, M.steelb);       // refrigerador y manilla
  pb(1710, 1768, 2161, 2340, 0, 85, M.cabn); pb(1710, 1768, 2161, 2340, 85, 88, M.top);                // mesón contra el muro este
  pb(1714, 1762, 2238, 2288, 88, 89, M.steelb); pb(1717, 1759, 2242, 2284, 89, 89.5, M.dark);         // lavaplatos
  cyl(1722, 2263, 1.5, 1.5, 89, 112, M.steelb); pb(1722, 1736, 2262, 2264, 110, 112, M.steelb);       // grifería
  pb(1733, 1763, 2170, 2200, 88, 116, M.dark); pb(1731, 1733, 2175, 2195, 92, 112, M.mirror);          // microondas
  pb(1568, 1608, 2068, 2097, 0, 110, M.fridgeM); pb(1566, 1568, 2076, 2088, 70, 90, M.blueM);          // máquina de agua
  pb(1637, 1757, 2059, 2087, 100, 190, M.dark);                                                        // tablero eléctrico de 120 cm, en el nicho
  pb(1490, 1609, 2217, 2288, 73, 75, M.wood);                                                          // mesa de 120 × 70 y cuatro sillas
  [[1492, 2219], [1604, 2219], [1492, 2283], [1604, 2283]].forEach(([x, y]) => pb(x, x + 4, y, y + 4, 0, 73, M.steelb));
  [[1493, 1528, 2192, 2222, 0], [1563, 1598, 2192, 2222, 0], [1493, 1528, 2283, 2313, 1], [1563, 1598, 2283, 2313, 1]].forEach(c => {
    pb(c[0], c[1], c[2], c[3], 43, 47, M.chairM);
    [[c[0] + 2, c[2] + 2], [c[1] - 5, c[2] + 2], [c[0] + 2, c[3] - 5], [c[1] - 5, c[3] - 5]].forEach(([x, y]) => pb(x, x + 3, y, y + 3, 0, 43, M.steelb));
    c[4] ? pb(c[0], c[1], c[3] - 3, c[3], 47, 88, M.chairM) : pb(c[0], c[1], c[2], c[2] + 3, 47, 88, M.chairM);
    bump('Servicios: silla');
  });
  pb(1560, 1620, 2337, 2341, 110, 160, M.dark);                                                        // TV en el muro norte
  // lockers: 4 columnas de 30 cm, dos puertas cada una, con el frente al sur
  for (let i = 0; i < 4; i++) {
    const x0 = 1575 + 30 * i;
    pb(x0 + 0.3, x0 + 29.7, 1803, 1848, 0, 180, M.locker);
    [[2, 88], [92, 178]].forEach(([z0, z1]) => {
      pb(x0 + 1, x0 + 29, 1802.2, 1803, z0, z1, M.lockdoor); pb(x0 + 24, x0 + 27, 1801.4, 1802.2, (z0 + z1) / 2 - 6, (z0 + z1) / 2 + 6, M.steelb);
      bump('Servicios: locker');
    });
  }
  // lavamopa contra el muro este: receptáculo de piso con pretil de 30 cm, grifo y repisa de aseo arriba
  pb(1716, 1768, 1790, 1850, 0, 25, M.cer); pb(1719, 1765, 1793, 1847, 25, 25.5, M.dark);
  cyl(1742, 1851, 1.5, 1.5, 90, 110, M.steelb); pb(1741, 1743, 1840, 1851, 108, 110, M.steelb);
  pb(1716, 1768, 1800, 1850, 190, 192, M.part);
  return g;
}
function buildServiciosTalca(THREE, M, bump) {''')
rp("function buildAdmin(THREE, M, bump) {", '''function buildAdmin(THREE, M, bump) {
  // Mueble de administración de Chillán Vivo: mesón de 60 x 373 cm (x 541 a 601) pegado a un tabique de 12 cm, con caja fuerte, rack y monitor CCTV
  const g = new THREE.Group();
  const pb = (x0, x1, y0, y1, z0, z1, mat) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, z1 - z0, y1 - y0), mat);
    m.position.set(px((x0 + x1) / 2), (z0 + z1) / 2, pz((y0 + y1) / 2)); g.add(m); return m;
  };
  const X0 = 541, X1 = 601;
  pb(601, 613, 0, 385, 0, 240, M.part); bump('Admin: tabique');                          // tabique de 12 cm; la altura de 2,4 m es supuesta
  pb(X0, X1, 0, 373, 85, 90, M.orange); pb(X0, X0 + 2.5, 0, 373, 78, 85, M.orange);       // cubierta naranja y labio frontal
  pb(X0 + 3, X1, 50, 313, 4, 78, M.black);                                                // cuerpo bajo la cubierta
  for (let i = 0; i < 4; i++) {                                                           // cuatro puertas negras con tirador redondo
    const a = 51 + i * 65.75, b = a + 64.75;
    pb(X0 - 1.8, X0 + 0.2, a, b, 5, 79, M.black); pb(X0 - 3.4, X0 - 1.8, b - 8, b - 4.4, 62, 65.6, M.steelb);
    if (i) pb(X0 + 1, X1, a - 1.6, a + 0.1, 0, 85, M.orange);
  }
  pb(X0, X1, 0, 50, 0, 55, M.dark); pb(X0 - 1, X0, 20, 30, 25, 35, M.steelb); bump('Admin: caja fuerte');   // caja fuerte de 60 x 50 cm
  pb(X0, X1, 313, 373, 0, 200, M.dark); pb(X0 - 1, X0, 320, 366, 20, 190, M.steelb);                       // rack de control de 60 x 60 cm
  pb(X0 + 20, X0 + 24, 229, 265, 100, 136, M.dark); pb(X0 + 14, X0 + 26, 241, 253, 90, 92, M.steelb);    // monitor CCTV sobre la cubierta
  bump('Admin: mueble');
  return g;
}
function buildAdminTalca(THREE, M, bump) {''')
rp("function buildSalaPaint(THREE, M, logoTex, sw) {", "function buildSalaPaint(THREE, M, logoTex, sw) { return new THREE.Group(); }\nfunction buildSalaPaintTalca(THREE, M, logoTex, sw) {")
facade = r'''function buildFacade3D(THREE, M, sign) {
  // Fachada de Chillán Vivo (muro sur): medidas de la elevación a 1:50, en cm desde el muro oeste del local
  const W = FACW, H = FACH, g = new THREE.Group();
  g.position.set(px(0), 0, pz(0));
  const bx = (u0, u1, h0, h1, d0, d1, mat) => {
    if (u1 - u0 < 0.05 || h1 - h0 < 0.05) return;
    const m = new THREE.Mesh(new THREE.BoxGeometry(u1 - u0, h1 - h0, d1 - d0), mat);
    m.position.set((u0 + u1) / 2, (h0 + h1) / 2, (d0 + d1) / 2); g.add(m);
  };
  const adFrame = (u0, u1, h0, h1) => {
    const e = 6;
    bx(u0, u1, h0, h0 + e, 3, 8, M.adF); bx(u0, u1, h1 - e, h1, 3, 8, M.adF);
    bx(u0, u0 + e, h0 + e, h1 - e, 3, 8, M.adF); bx(u1 - e, u1, h0 + e, h1 - e, 3, 8, M.adF);
    bx(u0 + e, u1 - e, h0 + e, h1 - e, 3, 5, M.adP);
  };
  // muro de respaldo y revestimiento acanalado, con el vano de la vitrina y del acceso (u 629 a 1745, hasta 210 cm)
  bx(0, 629, 0, H, -8, 0, M.backW); bx(1745, W, 0, H, -8, 0, M.backW); bx(629, 1745, 210, H, -8, 0, M.backW);
  bx(0, 629, 0, H, 0, 3, M.acmG); bx(1745, W, 0, H, 0, 3, M.acmG); bx(629, 1745, 210, H, 0, 3, M.acmG);
  for (let u = 6; u < W - 4; u += 18) { const sf = u > 623 && u < 1751; bx(u, u + 5, sf ? 210 : 0, H, 3, 5, M.adF); }
  bx(0, W, H, H + 30, 0, 14, M.acm);                                                         // cornisa de 30 cm
  // paneles de ofertas de 70 x 120 cm, de 90 a 210 cm
  [63, 173, 283, 393, 503].forEach(u => adFrame(u, u + 70, 90, 210));
  // acceso: marco rojo de 191 x 210 cm, dos hojas y paño superior de vidrio
  bx(629, 635, 0, 210, 0, 8, M.redAl); bx(814, 820, 0, 210, 0, 8, M.redAl); bx(629, 820, 204, 210, 0, 8, M.redAl);
  bx(722, 727, 0, 204, 0, 9, M.redAl); bx(635, 814, 190, 196, 0, 8, M.redAl);
  bx(635, 722, 6, 190, 3, 4, M.glassM); bx(727, 814, 6, 190, 3, 4, M.glassM); bx(635, 814, 196, 204, 3, 4, M.glassM);
  bx(715, 718, 96, 112, 8, 11, M.steelb); bx(731, 734, 96, 112, 8, 11, M.steelb);
  // vitrinas C02 (3 módulos) y C01 (5 módulos): vidrio de 34 a 206 cm con perfilería de aluminio
  const vit = (u0, u1, muls) => {
    bx(u0, u1, 30, 34, 0, 8, M.adF); bx(u0, u1, 206, 210, 0, 8, M.adF); bx(u0, u0 + 4, 30, 210, 0, 8, M.adF); bx(u1 - 4, u1, 30, 210, 0, 8, M.adF);
    bx(u0, u1, 0, 30, 0, 4, M.acmG);
    let a = u0 + 4; muls.forEach(([m0, m1]) => { bx(m0, m1, 34, 206, 0, 8, M.adF); bx(a, m0, 34, 206, 3, 4, M.glassM); a = m1; }); bx(a, u1 - 4, 34, 206, 3, 4, M.glassM);
  };
  vit(820, 1177, [[938, 943], [1055, 1059]]);
  vit(1207, 1745, [[1314, 1318], [1421, 1425], [1528, 1532], [1635, 1639]]);
  bx(1177, 1207, 0, 210, 0, 6, M.acmD);                                                       // pilar entre vitrinas
  // letrero: dos piezas de 150 cm de alto (de 410 a 560 cm), con relieve de unos 5 cm
  const front = new THREE.MeshBasicMaterial({ map: (sign && sign.sur) || null, transparent: true, alphaTest: 0.4 });
  const back = new THREE.MeshBasicMaterial({ map: (sign && sign.sur) || null, transparent: true, alphaTest: 0.4, color: 0x45474b });
  for (let k = 0; k < 6; k++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(1784, 150), k < 5 ? back : front); m.position.set(-2 + 892, 410 + 75, 3.2 + k * 0.9); g.add(m); }
  return { frames: [g], halos: new THREE.Group() };
}
function buildFacade3DTalca(THREE, M, sign) {'''
rp("function buildFacade3D(THREE, M, sign) {", facade)
rp("pn: { sala: 780, bodega: 387 }", "pn: { sala: 1097, bodega: 1096 }")
rp("function buildStore(THREE, DATA, M, texs) {", '''function buildAltillo(THREE, M, A, bump) {
  // Altillo de acopio superior: losa en L con baranda de 1 m en los bordes libres y escalerilla; la losa queda sobre los tabiques de los baños y la cocina
  const g = new THREE.Group();
  const pb = (x0, x1, y0, y1, z0, z1, mat) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, z1 - z0, y1 - y0), mat);
    m.position.set(px((x0 + x1) / 2), (z0 + z1) / 2, pz((y0 + y1) / 2)); g.add(m); return m;
  };
  const T = 20, H = A.h, B = A.baranda || 100, t = 4;
  A.parts.forEach(p => { pb(p[0], p[1], p[2], p[3], H - T, H, M.acmG); pb(p[0], p[1], p[2], p[3], H - T, H - T + 3, M.pal.frame); bump('Altillo: losa'); });
  const pa = A.parts[0], pbb = A.parts[1], lad = A.ladder, gap = lad ? [lad[1] - 40, lad[1] + 40] : null;
  // tramo de baranda: postes cada ~120 cm, pasamanos a 1 m y travesaño a 50 cm; (a, b) sobre un eje fijo c
  const rail = (axis, c, a, b, skip) => {
    const segs = skip && axis === 'v' && skip[0] < b && skip[1] > a ? [[a, skip[0]], [skip[1], b]] : [[a, b]];
    segs.forEach(([s0, s1]) => {
      if (s1 - s0 < 5) return;
      const n = Math.max(1, Math.round((s1 - s0) / 120));
      for (let i = 0; i <= n; i++) { const u = s0 + (s1 - s0) * i / n; axis === 'h' ? pb(u - t / 2, u + t / 2, c - t / 2, c + t / 2, H, H + B, M.steelb) : pb(c - t / 2, c + t / 2, u - t / 2, u + t / 2, H, H + B, M.steelb); }
      [B - t, B / 2].forEach(z => axis === 'h' ? pb(s0, s1, c - t / 2, c + t / 2, H + z, H + z + t, M.steelb) : pb(c - t / 2, c + t / 2, s0, s1, H + z, H + z + t, M.steelb));
    });
    bump('Altillo: baranda');
  };
  rail('h', pa[2] + t / 2, pa[0], pa[1]);                          // borde sur de la parte oeste
  rail('v', pa[0] + t / 2, pa[2], pa[3], gap);                     // borde oeste, con el vano de la escalerilla
  rail('v', pbb[0] + t / 2, pbb[2], pa[2]);                        // escalón entre las dos partes
  rail('h', pbb[2] + t / 2, pbb[0], pbb[1]);                       // borde sur de la parte este
  if (lad) {                                                       // escalerilla de 50 cm de ancho contra el borde oeste, hasta 90 cm sobre la losa
    const x1 = pa[0], x0 = x1 - 4, top = H + 90;
    [lad[1] - 25, lad[1] + 21].forEach(y => pb(x0 - 4, x1, y, y + 4, 0, top, M.steelb));
    for (let z = 28; z < top; z += 28) pb(x0 - 3, x1 - 1, lad[1] - 21, lad[1] + 21, z, z + 3, M.steelb);
    bump('Altillo: escalerilla');
  }
  return g;
}
function buildStore(THREE, DATA, M, texs) {''')
rp("  DATA.cab.forEach(c => {\n    if (c.D > 80) {", '''  if (DATA.altillo) {
    const A = DATA.altillo;
    A.racks.forEach(h => put('valid', C_hp.build(THREE, { depth: h.D, modules: 1 }, M.hp), C_hp.SPEC.W, h.D, h.x, h.y, h.ang - 90, 'Rack HP altillo', A.h));
    layers.valid.push(buildAltillo(THREE, M, A, bump));
  }
  DATA.cab.forEach(c => {
    if (c.D > 80) {''')


# ---------- 3) armado de la tienda ----------
rp("    if (p.label === 'Rack neumáticos (bodega)') put('cab', C_neu.build(THREE, { modules: 1 }, M.neu), C_neu.SPEC.L, C_neu.SPEC.D, p.x, p.y, p.ang - 90, 'Rack neumáticos (aprox.)');",
   "    if (p.label === 'Rack neumáticos (bodega)') { const nc = C_neu.build(THREE, { modules: 1 }, M.neu); nc.scale.x = p.L / C_neu.SPEC.L; put('cab', nc, p.L, C_neu.SPEC.D, p.x, p.y, p.ang - 90, 'Rack neumáticos (aprox.)'); }")

# ---------- 4) visor: vistas, textos y listas ----------
a = src.index("browser = ") + len("browser = "); b = src.index("\nhtml = f'''<!doctype html>")
js = ast.literal_eval(src[a:b])
def rj(x, y):
    global js
    assert js.count(x) == 1, (x[:80], js.count(x)); js = js.replace(x, y)
cx, cz = round(D_W := 885), -1176
rj("const target = new THREE.Vector3(1660, 100, -640);", "const target = new THREE.Vector3(885, 100, -1176);")
rj("const fly = { pos: new THREE.Vector3(2300, 300, 300), yaw: 0, pitch: -0.2, speed: 500 };", "const fly = { pos: new THREE.Vector3(1500, 300, 700), yaw: 0, pitch: -0.2, speed: 500 };")
rj("planta: [1660, 0, -640, 0.0, 0.03, 4300], aerea: [1660, 100, -640, -0.45, 0.95, 3800], fachada: [2300, 350, -250, 0.7, 1.3, 3300],",
   "planta: [885, 0, -1176, 0.0, 0.03, 4300], aerea: [885, 100, -1176, -0.45, 0.95, 3800], fachada: [1000, 350, -150, 0.35, 1.3, 3300],")
rj("sala: [2600, 120, -640, -0.5, 1.0, 1700], bodega: [1000, 120, -640, -0.5, 1.0, 2000],","sala: [1000, 120, -700, -0.5, 1.0, 2300], bodega: [700, 120, -1900, -0.5, 1.0, 2000],")
rj("ojosSala: [2300, 165, -640, Math.PI / 2, 1.5, 520], ojosBodega: [1000, 165, -640, Math.PI / 2, 1.5, 520]","ojosSala: [900, 165, -350, Math.PI / 2, 1.5, 520], ojosBodega: [900, 165, -2000, Math.PI / 2, 1.5, 520]")
rj("const FLYV = { ojosSala: [2050, 165, -640, -Math.PI / 2, 0.2], ojosBodega: [1750, 165, -640, Math.PI / 2, 0.2] };","const FLYV = { ojosSala: [900, 165, -250, 0, 0.2], ojosBodega: [1300, 165, -2000, Math.PI / 2, 0.2] };")
rj("const DEFW = { sala: luzTop('sala') + 10, bodega: luzTop('bodega') + 10 };","const DEFW = { sala: (luzTop('sala') || 400) + 10, bodega: (luzTop('bodega') || 400) + 10 };      // sin plano eléctrico: se asumen luces a 4 m")
i = js.index("li('listValid', ["); j = js.index("  const pend = {};")
lists = r"""li('listValid', [
    'Racks HP: ' + (S['Rack HP'] || 0) + ' módulos de 120 × 30 o 120 × 60 cm, leídos del plano',
    'Perimetrales: ' + (S['Perimetral RV1'] || 0) + ' RV1, ' + (S['Perimetral RV2'] || 0) + ' RV2, ' + (S['Perimetral RN'] || 0) + ' RN y ' + (S['Perimetral RH'] || 0) + ' RH',
    'Islas de ofertas: ' + (S['Isla de ofertas'] || 0) + ' de 70 × 70 × 90 cm, como la foto de referencia (mueble amarillo "Súper precios" con repisas y bidones)',
    'Góndolas negras: ' + (S['Góndola negra'] || 0) + ' módulos dobles de 125 × 90 cm, en 5 islas inclinadas 12°',
    'Racks de baterías: 3 de 150 × 100 cm juntos, con la cenefa estándar de 3 cuerpos (gráfica "Conoce tu batería", tomada de tu foto)',
    'Racks de pallets (' + (S['Rack pallets'] || 0) + '): de 220 × 120 cm, 2 de ancho y 3 de alto',
    'Luminarias del plano eléctrico: ' + (S['Luminaria L02'] || 0) + ' lineales L02 de 1,2 m y ' + (S['Luminaria F01'] || 0) + ' focos embutidos F01 de 22 W, en el local y en el altillo',
    'Mesones de atención P.O.S.: ' + (S['Mesón atención'] || 0) + ' módulos de 124 × 90 cm y un mesón de accesorios de 175 cm, con cliente hacia el este',
    'Mueble de administración (' + (S['Admin: mueble'] || 0) + '): mesón de 60 × 373 cm con caja fuerte, rack, monitor CCTV y puertas, pegado a un tabique de 12 cm',
    'Bodega RESPEL: ' + (S['Bodega RESPEL'] || 0) + ' de 300 × 160 × 230 cm, ubicada por su etiqueta',
    'Altillo de acopio superior: losa en L de unos 6 × 3 m sobre los baños y la cocina, ' + (S['Rack HP altillo'] || 0) + ' racks HP (12 de 30 cm y 3 de 60 cm, como indica el plano), baranda de 1 m en los bordes libres y escalerilla de acceso',
    'Fachada sur con las medidas de la elevación: acceso de 191 cm, vitrinas C02 (3 módulos) y C01 (5), 5 paneles de ofertas de 70 × 120 cm, letrero de 150 cm de alto y cornisa, con el galpón de 10,97 m medido en el dibujo'
  ]);
  li('listApprox', [
    'Racks de neumáticos: ' + (S['Rack neumáticos (aprox.)'] || 0) + ' de 190 × 60 cm (el plano rotula 190 × 70, pero dibuja 190 × 60), con la altura del rack de Talca',
    'Cabeceras de góndola: ' + (S['Cabecera de góndola (aprox.)'] || 0) + ' cabeceras de 45 × 95 × 150 cm, con las repisas de la góndola hacia el pasillo y rejilla en los costados, sin productos y en la posición del plano; cabeceras de fila HP: ' + (S['Cabecera de fila HP (aprox.)'] || 0) + ' de 65 × 30 × 300 cm',
    'Baños y cocina leídos del plano: 2 baños con ' + (S['Servicios: WC'] || 0) + ' WC y ' + (S['Servicios: lavamanos'] || 0) + ' lavamanos, y cocina con refrigerador, mesón con lavaplatos, microondas, máquina de agua, tablero eléctrico, mesa con ' + (S['Servicios: silla'] || 0) + ' sillas y TV; ' + (S['Servicios: locker'] || 0) + ' lockers y lavamopa con repisa de aseo; ' + (S['Servicios: puerta'] || 0) + ' puertas',
    'Cielos y muros negros: se configuran en el panel Cielos, para todo el local'
  ]);
  """
js = js[:i] + lists + js[j:]
rj("$('readout').textContent = '402 m² · bodega 253 m² a 3,87 m · sala de ventas 150 m² a 7,8 m · ' + total + ' piezas colocadas';",
   "$('readout').textContent = '" + "' + Math.round(FACW * DATA.contour[2][1] / 10000) + ' m² · galpón de 10,97 m · ' + total + ' piezas colocadas · borrador desde PDF';")
rj("const selS = $('cSalaMode'),","['cBodMode', 'cBodW'].forEach(id => { const r = $(id).closest('.ceilrow'); if (r) r.style.display = 'none'; });      // una sola zona hasta confirmar el límite bodega/sala\n  const selS = $('cSalaMode'),")
src = src[:a] + repr(js) + src[b:]
rp("<title>Tienda Talca · modelo v39</title>", "<title>Autoplanet Chillán Vivo · borrador v0</title>")
rp("<h1>Autoplanet Talca · modelo 3D v39</h1>", "<h1>Autoplanet Chillán Vivo · borrador v0</h1>")
k0 = src.index("<h2>No incluido todavía</h2>"); k1 = src.index("</details>", k0)
src = src[:k0] + """<h2>No incluido todavía</h2>
  <ul class="pending">
    
    <li>Los círculos grandes del plano (no sé si son columnas o áreas de giro), el muro divisorio de la bodega y la diagonal estructural.</li>
    <li>3 focos exteriores del acceso, kits de emergencia, salidas, interruptores y canalizaciones del plano eléctrico.</li>
    <li>Pintura de los muros interiores y sus franjas.</li>
  </ul>
  <h2>Supuestos del conjunto</h2>
  <ul class="pending">
    <li>Escala 1:50 verificada con los racks de pallets (220 × 120 cm); el resto de las medidas sale de los rectángulos del plano, que dice "todas las medidas deben rectificarse en obra".</li>
    <li>El plano no trae alturas. El alto del galpón (10,97 m) y el de la fachada se midieron en la elevación; las alturas de los racks son las de Talca.</li>
    <li>Una sola zona: no sé dónde termina la bodega ni qué altura tiene, así que no hay cambio de alturas.</li>
    <li>El frente de los perimetrales mira hacia el centro de la sala; el de los racks HP, las góndolas y las baterías es un supuesto (sin confirmar).</li>
    <li>Baños y cocina: tabiques de 2,4 m (supuesto) con las tres puertas cerradas; alturas de artefactos estándar, lockers de 1,8 m, tablero de 100 a 190 cm y espejos y grifería agregados por mí. Las posiciones salen del plano, con unos 5 cm de error; el sentido de apertura de las puertas no se modela.</li>
    <li>Altillo: el plano no da su altura; uso el estándar de 2,60 m para la cara superior de la losa (sobre los tabiques de 2,4 m), con 20 cm de espesor y sin pilares. La forma, la baranda de 1 m, los racks y la escalerilla salen del plano; los tubos de la baranda y los peldaños son supuestos.</li>
    <li>Mesones P.O.S. y de accesorios: uso el módulo de atención de Talca, con el cliente hacia el este (supuesto). Mueble de administración y tabique: el contorno sale del plano; el tabique de 2,4 m, las puertas y la caja fuerte, el rack y el monitor son supuestos de forma y altura.</li>
    <li>Luminarias: ubicadas con el plano eléctrico, que viene a otra escala (0,9427 del de arquitectura) y se alineó con los muros: error de unos 5 cm. Los L02 van a 4 m, como en Talca; los focos embutidos, a 4 m en la sala y a 2,4 m en baños y cocina (bajo la losa del altillo); en el altillo van a 5 m. Son supuestos de altura.</li>
    <li>Islas de ofertas: se modelan a partir de la foto de referencia (mueble amarillo "Súper precios" de ~90 cm); los bidones son genéricos. Cabeceras de góndola: las repisas (con labio, como la góndola) miran hacia el pasillo, el respaldo perforado queda contra la isla y los costados llevan rejilla, como en las fotos; sin productos, con las medidas y posiciones del plano.</li>
    <li>Los volúmenes ámbar son los componentes que no están en la biblioteca, con 100 cm de alto supuesto.</li>
    <li>Color de la perfilería de las vitrinas: supuesto. El acceso es rojo, como en el dibujo.</li>
  </ul>
""" + src[k1:]
open("/home/claude/build/_chillan_build.py", "w", encoding="utf8").write(src)
exec(compile(src, "_chillan_build", "exec"))
