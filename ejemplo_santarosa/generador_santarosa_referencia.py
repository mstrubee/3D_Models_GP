"""Genera el visor de Autoplanet Santa Rosa (sin fachada) reutilizando el visor base (make_html.py) y los datos leídos del PDF."""
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
D = json.load(open("/home/claude/santarosa/sr_data.json"))
cont = D["contour"]; W = max(p[0] for p in cont); DEPTH = max(p[1] for p in cont)
D["XB"] = 2; D["step"] = [[2, 0], [2, DEPTH]]                       # una sola zona hasta confirmar el límite bodega/sala
D["bodega"] = [[0, DEPTH - 2], [2, DEPTH - 2], [2, DEPTH], [0, DEPTH]]; D["sala"] = cont
D["open"] = [2, 3, 4, 5]                                              # lados sin muro: dan a la concesión (sin fachada)
D["luz"] = []; D["rails"] = []; D["altillo"] = None; D["mes"] = []
CRAD = math.pi / 180
from shapely.geometry import Polygon as _Pg
cg = _Pg(cont).centroid
def faz(x, y, ang):                                                   # frente hacia el centro del local
    return max(((ang + 90) % 360, (ang - 90) % 360), key=lambda f: math.cos(f * CRAD) * (cg.x - x) + math.sin(f * CRAD) * (cg.y - y))
nuevos = []; admin_pts = []
for p in D["ph"]:
    lab = p["label"]
    if p["cls"] == "resp":                                               # RESPEL: 160 de ancho por 300 de alto en el plano (el extractor lo ubicó por su etiqueta)
        p["ang"] = 90; p["x"] = 83; p["y"] = 443
    if p["cls"] == "pend" and lab.startswith("Mesón accesible"):          # columna de 744 cm = 6 módulos de 124 cm (5 P.O.S. y el mesón accesible)
        a = p["ang"]
        for k in range(6):
            off = (k - 2.5) * 124
            D["mes"].append(dict(v="atn", x=p["x"] + off * math.cos(a * CRAD), y=p["y"] + off * math.sin(a * CRAD), a=a))
    elif p["cls"] == "pend" and p["x"] < 520 and 560 < p["y"] < 900 and lab.split()[0] in ("Refri", "Mesa", "Lavamopa", "Lockers"):
        continue                                                      # baños y cocina: se modelan aparte
    elif p["cls"] == "pend" and 1550 < p["x"] < 1660 and 1450 < p["y"] < 1850 and lab.split()[0] in ("C.Fuerte", "Monitor", "Rack"):
        admin_pts.append((p["x"], p["y"], p["ang"]))                  # mueble de administración: se modela aparte
    else: nuevos.append(p)
D["ph"] = nuevos
D["admin"] = dict(x=sum(a[0] for a in admin_pts) / len(admin_pts), y=sum(a[1] for a in admin_pts) / len(admin_pts), a=admin_pts[0][2]) if admin_pts else None
# El mueble de administración se recorta para que termine en la cara interior de la fachada (9 cm de respaldo): no puede salir del local
if D["admin"]:
    A = D["admin"]; ar = A["a"] * CRAD; ux, uy = math.cos(ar), math.sin(ar); vx, vy = math.sin(ar), -math.cos(ar)       # u: eje largo; v: hacia el frente (+z local)
    ox, oy = A["x"] - 30 * vx, A["y"] - 30 * vy                        # el mesón ocupa de 0 a 60 cm en z: el centro medido es su línea media
    inner = _Pg(cont).buffer(-9)
    def _rect(s0, s1):
        return _Pg([(ox + s * ux + t * vx, oy + s * uy + t * vy) for s, t in ((s0, 0), (s1, 0), (s1, 63), (s0, 63))])
    s0, s1 = -186.5, 186.5; corte = [0, 0]
    while _rect(s0, s1).difference(inner).area > 1 and s1 - s0 > 150:
        if _rect(s0, s0 + 40).difference(inner).area >= _rect(s1 - 40, s1).difference(inner).area: s0 += 1; corte[0] += 1
        else: s1 -= 1; corte[1] += 1
    sc = (s0 + s1) / 2; A["x"] = ox + sc * ux; A["y"] = oy + sc * uy; A["L"] = s1 - s0; A["corte"] = corte
    print("mueble de administración recortado:", corte[0], "cm en el extremo sur y", corte[1], "cm en el norte; largo final", round(A["L"]), "cm")
bats = D["bat"]
if len(bats) == 1:                                                    # el plano rotula 3 racks juntos; solo se detectó 1 contorno: los otros dos van contiguos sobre el mismo eje
    b0 = bats[0]; ux, uy = math.cos(b0["ang"] * CRAD), math.sin(b0["ang"] * CRAD)
    cx, cy = b0["x"] + 150 * ux, b0["y"] + 150 * uy
    D["bat"] = [dict(x=cx, y=cy, fa=faz(cx, cy, b0["ang"]))]
elif bats:
    cx, cy = sum(b["x"] for b in bats) / len(bats), sum(b["y"] for b in bats) / len(bats)
    D["bat"] = [dict(x=cx, y=cy, fa=faz(cx, cy, bats[0]["ang"]))]
def _orient(P0, P1):                                                   # el eje u va de P0 a P1 y la normal derecha (+z local) apunta hacia afuera
    from shapely.geometry import Point as _Pt
    mx, my = (P0[0] + P1[0]) / 2, (P0[1] + P1[1]) / 2; dx, dy = P1[0] - P0[0], P1[1] - P0[1]; Ln = math.hypot(dx, dy)
    nx, ny = dy / Ln, -dx / Ln                                            # normal derecha del sentido P0 -> P1; es la exterior si un punto 30 cm hacia allá queda fuera del local
    return (P0, P1, False) if not _Pg(cont).contains(_Pt(mx + 30 * nx, my + 30 * ny)) else (P1, P0, True)
def _fac(i0, i1, anchor, logo=None, glass=None, door=None, cargo=None):   # lado del contorno i0 -> i1; las zonas se miden desde el punto 'anchor' (extremo i0 o i1)
    P0, P1, sw = _orient(cont[i0], cont[i1]); L = math.hypot(P1[0] - P0[0], P1[1] - P0[1]); a_is_p0 = (cont[anchor] == P0)
    z = lambda r: None if r is None else ([r[0], r[1]] if a_is_p0 else [L - r[1], L - r[0]])
    lu = None if logo is None else (logo if a_is_p0 else L - logo)
    return dict(x0=P0[0], y0=P0[1], x1=P1[0], y1=P1[1], L=L, logoU=lu, glass=z(glass), door=z(door), cargo=z(cargo))
D["facp"] = dict(hf=None, cornisa=30, panelH=90, glassH=240, cargoH=250)      # alturas de fachada y letrero: hf=None usa la altura interior
D["fachadas"] = [
    _fac(3, 2, 3, logo=308),                                                      # este: de 2570,2131 a 2522,1517
    _fac(4, 3, 4),                                                                # chaflán: solo franjas
    _fac(5, 4, 5, logo=420, glass=[0, 675], door=[329, 512]),                     # sur: vidrio de 6,75 m desde la esquina oeste, puertas dobles del acceso y letrero sobre ellas
    _fac(6, 5, 5, logo=760, cargo=[1074, 1281])                      # oeste: puerta roja de carga (zona marcada, medida desde el extremo norte)
]
def b64(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
SIGN = json.dumps({"sur": b64("/home/claude/pdfs/logo_ori.png"), "ori": b64("/home/claude/pdfs/logo_ori.png"), "logo": b64("/home/claude/pdfs/logo_ori.png"), "cenefaBat": "data:image/jpeg;base64," + base64.b64encode(open("/home/claude/pdfs/cenefa_baterias.jpg", "rb").read()).decode(), "swBody": b64("/home/claude/pdfs/sw_body.png"), "swTip": b64("/home/claude/pdfs/sw_tip.png")})
DATA = json.dumps(clean({k: D[k] for k in ("contour","XB","step","bodega","sala","per","hp","gon","cab","mes","bat","ph","luz","rails","altillo","open","admin","fachadas","facp")}), ensure_ascii=False, separators=(",",":"))
AREA = round(_Pg(cont).area / 10000)
'''
src = new_head + src[head_end:]
rp('open("/mnt/user-data/outputs/tienda_talca_v39.html"', 'open("/mnt/user-data/outputs/tienda_santarosa_v0.html"')

# ---------- 2) núcleo: origen, alturas (3,22 m interior, dato del plano), servicios, administración, sin fachada ----------
rp("const OX = 14392, OY = 516;", "const OX = 0, OY = 0;")
rp("const H_BOD = 387, H_SALA = 780, WALL_T = 12;", """const H_BOD = 332, H_SALA = 333, WALL_T = 12;
const FACS = ''' + json.dumps(D["fachadas"]) + r''';
const FACP = ''' + json.dumps(D["facp"]) + r''';""")
serv = r'''function buildServicios(THREE, M, bump) {
  // Baños y cocina de Santa Rosa: tabiques, puertas y artefactos ubicados con el plano (cm del local, y hacia el norte)
  const g = new THREE.Group();
  const pb = (x0, x1, y0, y1, z0, z1, mat) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, z1 - z0, y1 - y0), mat);
    m.position.set(px((x0 + x1) / 2), (z0 + z1) / 2, pz((y0 + y1) / 2)); g.add(m); return m;
  };
  const cyl = (x, y, rx, ry, z0, z1, mat) => {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, z1 - z0, 20), mat);
    m.scale.set(rx, 1, ry); m.position.set(px(x), (z0 + z1) / 2, pz(y)); g.add(m); return m;
  };
  const HP = 240;                                                   // altura supuesta de los tabiques
  [[0, 449, 872, 884], [276, 287, 599, 872], [437, 449, 599, 884], [0, 176, 599, 611], [256, 276, 599, 611], [287, 325, 599, 611], [415, 449, 599, 611]].forEach(w => pb(w[0], w[1], w[2], w[3], 0, HP, M.part));
  [[176, 256], [325, 415]].forEach(d => {                          // puertas cerradas: cocina P3 (80) y baño P2 (90)
    const yc = 605; pb(d[0], d[1], 599, 611, 210, HP, M.part); pb(d[0], d[1], yc - 1.75, yc + 1.75, 0, 210, M.door);
    pb(d[1] - 8, d[1] - 5, yc - 3.5, yc + 3.5, 98, 102, M.steelb); bump('Servicios: puerta');
  });
  // ---- Baño: WC contra el muro norte y lavamanos contra el muro este ----
  const wcN = (cx, yW) => {
    const cy = yW - 40; cyl(cx, cy, 13, 20, 0, 32, M.cer); cyl(cx, cy, 17, 26, 32, 42, M.cer);
    pb(cx - 19, cx + 19, yW - 15, yW, 32, 82, M.cer); cyl(cx, yW - 7, 2, 2, 82, 83.5, M.steelb); bump('Servicios: WC');
  };
  wcN(340, 872);
  const lavE = (x0, x1, y0, y1, wallX) => {
    const yc = (y0 + y1) / 2; cyl(x1 - 9, yc, 6, 6, 0, 72, M.cer); pb(x0, x1, y0, y1, 72, 88, M.cer);
    cyl(x1 - 4, yc, 1.5, 1.5, 88, 100, M.steelb); pb(x1 - 12, x1 - 4, yc - 0.5, yc + 0.5, 98, 100, M.steelb);
    pb(wallX - 2, wallX, y0 + 2, y1 - 2, 105, 165, M.mirror); bump('Servicios: lavamanos');
  };
  lavE(401, 437, 665, 705, 437);
  // ---- Cocina: refrigerador, mesón con lavaplatos, máquina de agua, microondas, mesa con 4 sillas y TV ----
  pb(2, 62, 811, 871, 0, 180, M.fridgeM); pb(60, 62, 856, 860, 70, 140, M.steelb);
  pb(62, 276, 812, 872, 0, 85, M.cabn); pb(62, 276, 812, 872, 85, 88, M.top);
  pb(208, 256, 822, 866, 88, 89, M.steelb); pb(211, 253, 826, 862, 89, 89.5, M.dark); cyl(218, 844, 1.5, 1.5, 89, 112, M.steelb);
  pb(64, 96, 822, 862, 88, 128, M.fridgeM); pb(112, 152, 826, 858, 88, 116, M.dark); pb(114, 116, 830, 854, 92, 112, M.mirror);
  pb(60, 130, 611, 731, 73, 75, M.wood);
  [[62, 613], [62, 727], [124, 613], [124, 727]].forEach(([x, y]) => pb(x, x + 4, y, y + 4, 0, 73, M.steelb));
  [[36, 66, 626, 656, 0], [36, 66, 686, 716, 0], [124, 154, 626, 656, 1], [124, 154, 686, 716, 1]].forEach(c => {
    pb(c[0], c[1], c[2], c[3], 43, 47, M.chairM);
    [[c[0] + 2, c[2] + 2], [c[1] - 5, c[2] + 2], [c[0] + 2, c[3] - 5], [c[1] - 5, c[3] - 5]].forEach(([x, y]) => pb(x, x + 3, y, y + 3, 0, 43, M.steelb));
    c[4] ? pb(c[1] - 3, c[1], c[2], c[3], 47, 88, M.chairM) : pb(c[0], c[0] + 3, c[2], c[3], 47, 88, M.chairM);
    bump('Servicios: silla');
  });
  pb(1, 5, 640, 700, 110, 160, M.dark);                              // TV en el muro oeste
  // ---- Lockers (2 bloques de 55 x 74 cm, frente al este) ----
  [736, 810].forEach(y0 => { for (let i = 0; i < 2; i++) {
    const ya = y0 + 37 * i;
    pb(450, 505, ya + 0.3, ya + 36.7, 0, 180, M.locker);
    [[2, 88], [92, 178]].forEach(([z0, z1]) => { pb(505, 505.8, ya + 1, ya + 36, z0, z1, M.lockdoor); pb(505.8, 506.6, ya + 28, ya + 31, (z0 + z1) / 2 - 6, (z0 + z1) / 2 + 6, M.steelb); bump('Servicios: locker'); });
  } });
  // ---- Lavamopa junto al baño: receptáculo con pretil, grifo y repisa de aseo arriba ----
  pb(388, 444, 582, 632, 0, 25, M.cer); pb(391, 441, 585, 629, 25, 25.5, M.dark);
  cyl(416, 633, 1.5, 1.5, 90, 110, M.steelb); pb(415, 417, 622, 633, 108, 110, M.steelb); pb(388, 444, 590, 632, 190, 192, M.part);
  return g;
}
function buildServiciosTalca(THREE, M, bump) {'''
rp("function buildServicios(THREE, M, bump) {", serv)
adm = r'''function buildAdmin(THREE, M, bump, DATA) {
  // Mueble de administración de Santa Rosa: mesón naranjo de 60 x 373 cm, con caja fuerte, rack de control, monitor CCTV y cuatro puertas negras
  const g = new THREE.Group(), A = DATA.admin;
  if (!A) return g;
  const pb = (x0, x1, z0, z1, y0, y1, mat) => {                      // x: largo del mesón, z: fondo, y: alto (marco local)
    const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), mat);
    m.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); g.add(m); return m;
  };
  const L = A.L || 373, h = L / 2;
  pb(-h, h, 0, 60, 85, 90, M.orange); pb(-h, h, 58, 62.5, 78, 85, M.orange);               // cubierta naranja y labio frontal (+z)
  pb(-h + 60, h - 60, 0, 58, 4, 78, M.black);                                                // cuerpo bajo la cubierta
  const nd = Math.max(1, Math.round((L - 120) / 63)), wd = (L - 121) / nd;
  for (let i = 0; i < nd; i++) {                                                             // puertas con tirador redondo (el número se adapta al largo)
    const a = -h + 61 + i * wd, b = a + wd - 1;
    pb(a, b, 58, 60.2, 5, 79, M.black); pb(b - 8, b - 4.4, 60.2, 61.8, 62, 65.6, M.steelb);
    if (i) pb(a - 1.6, a + 0.1, 0, 58, 0, 85, M.orange);
  }
  pb(-h, -h + 60, 5, 55, 0, 55, M.dark); pb(-h + 20, -h + 30, 55, 56, 25, 35, M.steelb); bump('Admin: caja fuerte');   // caja fuerte de 60 x 50 cm
  pb(h - 60, h, 0, 60, 0, 200, M.dark); pb(h - 50, h - 14, 60, 61, 20, 190, M.steelb);                                  // rack de control de 60 x 60 cm
  pb(-12, -8, 20, 56, 100, 136, M.dark); pb(-18, -6, 32, 44, 90, 92, M.steelb);                                         // monitor CCTV
  bump('Admin: mueble');
  g.rotation.y = A.a * Math.PI / 180; g.position.set(px(A.x), 0, pz(A.y));                  // eje largo a lo largo del ángulo del plano; el frente (+z) mira hacia el este
  return g;
}
function buildAdminTalca(THREE, M, bump) {'''
rp("function buildAdmin(THREE, M, bump) {", adm)
rp("layers.valid.push(buildAdmin(THREE, M, bump));","layers.valid.push(buildAdmin(THREE, M, bump, DATA));") if "layers.valid.push(buildAdmin(THREE, M, bump));" in src else None
rp("function buildSalaPaint(THREE, M, logoTex, sw) {", "function buildSalaPaint(THREE, M, logoTex, sw) { return new THREE.Group(); }\nfunction buildSalaPaintTalca(THREE, M, logoTex, sw) {")
rp("function buildFacade3D(THREE, M, sign) {", r'''function buildFacade3D(THREE, M, sign) {
  // Fachadas de Santa Rosa (3 fachadas sobre los lados abiertos): muro revestido, cornisa, letrero con franjas de extremos curvos y logo,
  // zona vidriada con marcos rojos y puertas dobles del acceso, y puerta metálica roja de carga. Medidas de las zonas marcadas por el usuario.
  const P = FACP, Hf = P.hf || H_SALA, frames = [];
  const tex = t => new THREE.MeshStandardMaterial({ map: t || null, transparent: true, alphaTest: 0.4, roughness: 0.8, side: THREE.DoubleSide });
  const bodyMat = tex(sign && sign.sw && sign.sw.body), tipMat = tex(sign && sign.sw && sign.sw.tip), logoMat = tex(sign && sign.logo);
  const PH = P.panelH || 90, PB = Hf - PH, YC = PB + PH / 2, HB = Math.round(PH * 80 / 90), k = HB / 80;     // panel del letrero (alto PH bajo el tope del muro) y franja a 8/9 de su alto
  const GH = P.glassH || 240, CH = P.cargoH || 250, CORN = (P.cornisa === undefined || P.cornisa === null) ? 30 : P.cornisa;
  const TIPW = 141 * k, LOGOW = 232 * k, GAP = 152 * k;                        // a 80 cm de franja la punta mide 141 cm y el logo 2,32 m; todo escala con la franja
  FACS.forEach(f => {
    const g = new THREE.Group(), L = f.L;
    g.position.set(px(f.x0), 0, pz(f.y0)); g.rotation.y = Math.atan2(f.y1 - f.y0, f.x1 - f.x0);      // u a lo largo del lado; +z hacia afuera
    const bx = (u0, u1, h0, h1, d0, d1, mat) => {
      if (u1 - u0 < 0.05 || h1 - h0 < 0.05) return;
      const m = new THREE.Mesh(new THREE.BoxGeometry(u1 - u0, h1 - h0, d1 - d0), mat);
      m.position.set((u0 + u1) / 2, (h0 + h1) / 2, (d0 + d1) / 2); g.add(m);
    };
    const pl = (w, h, u, y, d, mat, flip) => { const p = new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat); p.position.set(u, y, d); if (flip) p.scale.x = -1; g.add(p); };
    const wall = (u0, u1, h0, h1) => { bx(u0, u1, h0, h1, -8, 0, M.backW); bx(u0, u1, h0, h1, 0, 4, M.acmG); };
    // muro con los vanos del vidrio (hasta 240 cm) y de la puerta de carga (hasta 250 cm)
    const ops = []; if (f.glass) ops.push([f.glass[0], f.glass[1], GH]); if (f.cargo) ops.push([f.cargo[0], f.cargo[1], CH]);
    ops.sort((a, b) => a[0] - b[0]);
    let u = 0; ops.forEach(([a, b, t]) => { wall(u, a, 0, Hf); wall(a, b, t, Hf); u = b; }); wall(u, L, 0, Hf);
    bx(0, L, Hf, Hf + CORN, 0, 12, M.acm);                                        // cornisa (30 cm por defecto)
    // letrero: panel blanco de 90 cm con franjas roja y naranja; el logo va en f.logoU y las franjas terminan en punta curva junto a él
    bx(0, L, PB, Hf, 4, 5.5, M.acm);
    const band = (u0, u1, tipL, tipR) => {
      const a = tipL ? u0 + TIPW - 1 : u0, b = tipR ? u1 - TIPW + 1 : u1;
      if (b > a) pl(b - a, HB, (a + b) / 2, YC, 5.8, bodyMat);
      if (tipR) pl(TIPW, HB, u1 - TIPW / 2, YC, 5.9, tipMat);
      if (tipL) pl(TIPW, HB, u0 + TIPW / 2, YC, 5.9, tipMat, true);
    };
    if (f.logoU !== null && f.logoU !== undefined) {
      const lo = f.logoU - GAP, ro = f.logoU + GAP;
      if (lo > 20) band(0, lo, false, lo > TIPW); if (L - ro > 20) band(ro, L, L - ro > TIPW, false);
      pl(LOGOW, LOGOW / 4.65, f.logoU, YC, 6.3, logoMat);
    } else band(0, L, false, false);
    // zona vidriada: marcos rojos, módulos de vidrio y puertas dobles del acceso
    if (f.glass) {
      const g0 = f.glass[0], g1 = f.glass[1], dr = f.door;
      bx(g0, g1, 0, 12, 0, 8, M.redAl); bx(g0, g1, GH - 12, GH, 0, 8, M.redAl); bx(g0, g0 + 6, 0, GH, 0, 8, M.redAl); bx(g1 - 6, g1, 0, GH, 0, 8, M.redAl);
      const mods = []; if (dr) { const nl = Math.max(1, Math.round((dr[0] - g0) / 115)), nr = Math.max(1, Math.round((g1 - dr[1]) / 115));
        for (let i = 0; i < nl; i++) mods.push([g0 + (dr[0] - g0) * i / nl, g0 + (dr[0] - g0) * (i + 1) / nl, 0]);
        mods.push([dr[0], dr[1], 1]);
        for (let i = 0; i < nr; i++) mods.push([dr[1] + (g1 - dr[1]) * i / nr, dr[1] + (g1 - dr[1]) * (i + 1) / nr, 0]);
      } else { const n = Math.max(1, Math.round((g1 - g0) / 115)); for (let i = 0; i < n; i++) mods.push([g0 + (g1 - g0) * i / n, g0 + (g1 - g0) * (i + 1) / n, 0]); }
      mods.forEach(([a, b, isDoor]) => {
        bx(a - 2.5, a + 2.5, 0, GH, 0, 8, M.redAl);                                            // montante
        if (!isDoor) { bx(a + 2.5, b - 2.5, 105, 111, 0, 8, M.redAl); bx(a + 2.5, b - 2.5, 12, 105, 3, 4, M.glassM); bx(a + 2.5, b - 2.5, 111, GH - 12, 3, 4, M.glassM); }
        else {                                                                                  // acceso: dos hojas de vidrio, travesaño y paño superior
          const mid = (a + b) / 2;
          bx(mid - 2.5, mid + 2.5, 0, GH - 30, 0, 9, M.redAl); bx(a, b, GH - 35, GH - 29, 0, 8, M.redAl);
          bx(a + 2.5, mid - 2.5, 8, GH - 35, 3, 4, M.glassM); bx(mid + 2.5, b - 2.5, 8, GH - 35, 3, 4, M.glassM); bx(a + 2.5, b - 2.5, GH - 29, GH - 12, 3, 4, M.glassM);
          bx(mid - 14, mid - 11, 96, 112, 8, 11, M.steelb); bx(mid + 11, mid + 14, 96, 112, 8, 11, M.steelb);
        }
      });
      bx(g1 - 2.5, g1 + 2.5, 0, GH, 0, 8, M.redAl);
    }
    // puerta metálica roja de carga
    if (f.cargo) {
      const c0 = f.cargo[0], c1 = f.cargo[1];
      bx(c0 - 4, c0, 0, CH + 4, 0, 8, M.dark); bx(c1, c1 + 4, 0, CH + 4, 0, 8, M.dark); bx(c0 - 4, c1 + 4, CH, CH + 4, 0, 8, M.dark);   // marco
      bx(c0, c1, 0, CH, 0, 5, M.redAl);
      for (let h = 40; h < CH; h += 42) bx(c0 + 3, c1 - 3, h, h + 1.5, 5, 6, M.dark);          // nervios horizontales de la hoja
      bx(c0 + 12, c0 + 15, 100, 135, 5, 9, M.steelb);
    }
    frames.push(g);
  });
  return { frames, halos: new THREE.Group() };
}
function buildFacade3DTalca(THREE, M, sign) {''')
rp("const DEF = { aw: { sala: 450, bodega: 387 }, ab: { sala: 450, bodega: 387 }, pn: { sala: 780, bodega: 387 } };", "const DEF = { aw: { sala: 333, bodega: 332 }, ab: { sala: 333, bodega: 332 }, pn: { sala: 333, bodega: 332 } };")
rp("    if (p.label === 'Rack neumáticos (bodega)') put('cab', C_neu.build(THREE, { modules: 1 }, M.neu), C_neu.SPEC.L, C_neu.SPEC.D, p.x, p.y, p.ang - 90, 'Rack neumáticos (aprox.)');",
   "    if (p.label === 'Rack neumáticos (bodega)') { const nc = C_neu.build(THREE, { modules: 1 }, M.neu); nc.scale.x = p.L / C_neu.SPEC.L; put('cab', nc, p.L, C_neu.SPEC.D, p.x, p.y, p.ang - 90, 'Rack neumáticos (aprox.)'); }")

# ---------- 3) visor: vistas, alturas, textos y listas ----------
a = src.index("browser = ") + len("browser = "); b = src.index("\nhtml = f'''<!doctype html>")
js = ast.literal_eval(src[a:b])
def rj(x, y):
    global js
    assert js.count(x) == 1, (x[:80], js.count(x)); js = js.replace(x, y)
rj("const target = new THREE.Vector3(1660, 100, -640);", "const target = new THREE.Vector3(1300, 100, -1300);")
rj("const fly = { pos: new THREE.Vector3(2300, 300, 300), yaw: 0, pitch: -0.2, speed: 500 };", "const fly = { pos: new THREE.Vector3(2900, 300, -400), yaw: 0.6, pitch: -0.2, speed: 500 };")
rj("planta: [1660, 0, -640, 0.0, 0.03, 4300], aerea: [1660, 100, -640, -0.45, 0.95, 3800], fachada: [2300, 350, -250, 0.7, 1.3, 3300],",
   "planta: [1300, 0, -1300, 0.0, 0.03, 4400], aerea: [1300, 100, -1300, -0.45, 0.95, 4000], fachada: [1700, 250, -1100, 0.9, 1.25, 3300],")
rj("sala: [2600, 120, -640, -0.5, 1.0, 1700], bodega: [1000, 120, -640, -0.5, 1.0, 2000],","sala: [1500, 120, -1800, -0.5, 1.0, 2400], bodega: [250, 120, -600, -0.5, 1.0, 1500],")
rj("ojosSala: [2300, 165, -640, Math.PI / 2, 1.5, 520], ojosBodega: [1000, 165, -640, Math.PI / 2, 1.5, 520]","ojosSala: [1500, 165, -1300, Math.PI / 2, 1.5, 520], ojosBodega: [200, 165, -500, Math.PI / 2, 1.5, 520]")
rj("const FLYV = { ojosSala: [2050, 165, -640, -Math.PI / 2, 0.2], ojosBodega: [1750, 165, -640, Math.PI / 2, 0.2] };","const FLYV = { ojosSala: [1300, 165, -1000, 0, 0.2], ojosBodega: [150, 165, -300, -Math.PI / 2, 0.2] };")
rj("const DEFW = { sala: luzTop('sala') + 10, bodega: luzTop('bodega') + 10 };","const DEFW = { sala: (luzTop('sala') || 293) + 10, bodega: (luzTop('bodega') || 293) + 10 };      // sin plano eléctrico: se asumen luces 40 cm bajo el interior (3,33 m)")
i = js.index("li('listValid', ["); j = js.index("  const pend = {};")
lists = r"""li('listValid', [
    'Racks HP: ' + (S['Rack HP'] || 0) + ' módulos de 120 × 30 o 120 × 60 cm, leídos del plano (el plano indica 57 de 30 cm y 11 de 60 cm)',
    'Perimetrales: ' + (S['Perimetral RV1'] || 0) + ' RV1, ' + (S['Perimetral RV2'] || 0) + ' RV2 y ' + (S['Perimetral RV3'] || 0) + ' RV3 de 122 × 40,6 cm',
    'Góndolas negras: ' + (S['Góndola negra'] || 0) + ' módulos dobles de 125 × 90 cm = 38 cuerpos, como indica el plano, en 5 pasillos inclinados 11,7°',
    'Islas de ofertas: ' + (S['Isla de ofertas'] || 0) + ' (70 × 70 y 100 × 120 cm) de 90 cm de alto, como la foto de referencia',
    'Mesones P.O.S.: ' + (S['Mesón atención'] || 0) + ' módulos de 124 × 90 cm (5 P.O.S. y el mesón accesible), con el cliente hacia las góndolas',
    'Racks de baterías: 3 de 150 × 100 cm con la cenefa estándar de 3 cuerpos',
    'Racks de pallets (' + (S['Rack pallets'] || 0) + ') de 220 × 120 cm y bodega RESPEL (' + (S['Bodega RESPEL'] || 0) + ') de 300 × 160 cm',
    'Mueble de administración (' + (S['Admin: mueble'] || 0) + '): mesón de 60 cm de fondo con caja fuerte, rack y monitor CCTV, recortado donde chocaba con la fachada',
    'Fachadas en los lados que dan a la concesión (este, chaflán, sur y oeste): tres letreros "Autoplanet" con franjas, uno sobre el acceso principal; vidrio con marcos rojos y puertas dobles de 1,83 m en la zona azul; puerta roja de carga de 2,07 m; el muro sur del bloque es medianero, sin fachada',
    'Altura interior de 3,33 m, la que indicaste (el plano dice 3,22 m)'
  ]);
  li('listApprox', [
    'Racks de neumáticos: ' + (S['Rack neumáticos (aprox.)'] || 0) + ' de 240 × 60 cm, con la altura del rack de Talca',
    'Cabeceras de góndola: ' + (S['Cabecera de góndola (aprox.)'] || 0) + ' de 45 × 95 × 150 cm, con las repisas de la góndola hacia el pasillo y rejilla en los costados, sin productos',
    'Baños y cocina leídos del plano: ' + (S['Servicios: WC'] || 0) + ' baño con WC y lavamanos, cocina con refrigerador, mesón con lavaplatos, microondas, máquina de agua, mesa con ' + (S['Servicios: silla'] || 0) + ' sillas y TV; ' + (S['Servicios: locker'] || 0) + ' lockers y lavamopa; ' + (S['Servicios: puerta'] || 0) + ' puertas',
    'Cielos y muros negros: se configuran en el panel Cielos, para todo el local'
  ]);
  """
js = js[:i] + lists + js[j:]
rj("$('readout').textContent = '402 m² · bodega 253 m² a 3,87 m · sala de ventas 150 m² a 7,8 m · ' + total + ' piezas colocadas';",
   "$('readout').textContent = '" + "345 m² por dentro (357 m² según el plano) · interior de 3,33 m · ' + total + ' piezas colocadas · borrador desde PDF';")
rj("const selS = $('cSalaMode'),","['cBodMode', 'cBodW'].forEach(id => { const r = $(id).closest('.ceilrow'); if (r) r.style.display = 'none'; });      // una sola zona\n  const selS = $('cSalaMode'),")
src = src[:a] + repr(js) + src[b:]
rp("<title>Tienda Talca · modelo v39</title>", "<title>Autoplanet Santa Rosa · borrador v0</title>")
rp("<h1>Autoplanet Talca · modelo 3D v39</h1>", "<h1>Autoplanet Santa Rosa · borrador v0</h1>")
rp('min="300" max="800" step="5" value="410"', 'min="150" max="333" step="5" value="293"', 2)
k0 = src.index("<h2>No incluido todavía</h2>"); k1 = src.index("</details>", k0)
src = src[:k0] + """<h2>No incluido todavía</h2>
  <ul class="pending">
    <li>La concesión, las áreas verdes, los estacionamientos y la línea de concesión: son del entorno y no del local.</li>
    <li>Plano eléctrico: sin él no hay luminarias, y el modo Noche queda a oscuras.</li>
    <li>Pintura de los muros interiores y sus franjas.</li>
  </ul>
  <h2>Supuestos del conjunto</h2>
  <ul class="pending">
    <li>Escala 1:50 verificada con los racks de pallets (220 × 120 cm) y con los totales que trae el plano: 38 cuerpos de góndola, 11 repisas HP de 60 cm, 5 P.O.S. El plano dice "todas las medidas deben rectificarse en obra".</li>
    <li>Contorno: leído por los muros interiores (345 m²); el plano declara 357 m², probablemente medidos a las caras exteriores.</li>
    <li>Altura interior de 3,33 m, la que indicaste (el plano rotula 3,22 m), para todo el local; las alturas de los racks son las de Talca. Con esa altura, los racks de neumáticos (3,5 m), si se pusieran sobre el cielo, se cortan: usa el panel Cielos.</li>
    <li>Fachadas: sin elevación, las medidas salen de las zonas que marcaste sobre el plano (vidrio, puerta de carga y letreros): la altura del vidrio (2,4 m), el panel del letrero (90 cm) y la cornisa (30 cm) son supuestos; el letrero del acceso principal se centra sobre las puertas dobles (que leí del plano).</li>
    <li>Una sola zona: no sé dónde termina la bodega ni qué altura tiene.</li>
    <li>El frente de los perimetrales mira hacia el centro del local; el de los racks HP, las góndolas y las baterías es un supuesto.</li>
    <li>Baños y cocina: tabiques de 2,4 m (supuesto), puertas cerradas, alturas de artefactos estándar y posiciones leídas del plano con unos 10 cm de error; el sentido de apertura de las puertas no se modela.</li>
    <li>Mueble de administración: se ubicó por las etiquetas del plano (C.Fuerte, Monitor CCTV, Rack), con el frente hacia el este (supuesto).</li>
    <li>Rack de cajas, bodegas de basura y cartones, Starken, recepción de mercadería: volúmenes ámbar de 100 cm de alto supuesto.</li>
  </ul>
""" + src[k1:]
open("/home/claude/build/_santarosa_build.py", "w", encoding="utf8").write(src)
exec(compile(src, "_santarosa_build", "exec"))
