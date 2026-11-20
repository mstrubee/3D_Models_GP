"""Lee una planta de arquitectura en PDF vectorial (escala 1:50) y genera data.json con los componentes del kit.
Uso: python3 extraer_planta_pdf.py planta.pdf salida.json [x_izq_pt y_sur_pt x_der_pt y_norte_pt]
Verifica la escala con los racks de pallets (220 x 120 cm) y reconoce cada componente por sus medidas."""
import sys, math, json, collections
import pymupdf
from shapely.geometry import Polygon

PDF, OUT = sys.argv[1], sys.argv[2]
POLI = json.load(open(sys.argv[7])) if len(sys.argv) > 7 else None          # contorno irregular del local, en puntos del PDF (opcional)
F = 50 * 25.4 / 72 / 10            # cm de local por punto del PDF a 1:50 (1,764)
doc = pymupdf.open(PDF); page = doc[0]
# límites interiores del local (pt): se pueden pasar por línea de comandos
XL, YS, XR, YN = (float(v) for v in sys.argv[3:7]) if len(sys.argv) >= 7 else (177, 1523.4, 1181, 190)
POLY = Polygon(POLI).buffer(15) if POLI else None

def to_cm(x, y): return ((x - XL) * F, (YS - y) * F)

# ---- rectángulos cerrados (cualquier ángulo) ----
rects = []; all_rects = []
for d in page.get_drawings():
    its = d["items"]
    if not 1 <= len(its) <= 12: continue
    pts, closed = [], False
    for it in its:
        if it[0] == "l": pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == "re": r = it[1]; pts += [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]; closed = True
        elif it[0] == "qu": q = it[1]; pts += [(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)]; closed = True
        else: pts = None; break
    if not pts or len(pts) < 4: continue
    u = [pts[0]]
    for q in pts[1:]:
        if math.hypot(q[0] - u[-1][0], q[1] - u[-1][1]) > 0.05: u.append(q)
    if d.get("closePath"): closed = True
    if not closed and math.hypot(u[0][0] - u[-1][0], u[0][1] - u[-1][1]) > 0.8: continue
    if len(u) < 3: continue
    try: pg = Polygon(u)
    except Exception: continue
    if not pg.is_valid or pg.area < 20: continue
    mr = pg.minimum_rotated_rectangle
    if pg.area / mr.area < 0.96: continue
    c = list(mr.exterior.coords); e1 = math.hypot(c[1][0] - c[0][0], c[1][1] - c[0][1]); e2 = math.hypot(c[2][0] - c[1][0], c[2][1] - c[1][1])
    ang = math.degrees(math.atan2(c[1][1] - c[0][1], c[1][0] - c[0][0])) % 180
    if e1 < e2: e1, e2 = e2, e1; ang = (ang + 90) % 180
    cx, cy = mr.centroid.x, mr.centroid.y
    x, y = to_cm(cx, cy)
    all_rects.append(dict(L=e1 * F, D=e2 * F, ang=(-ang) % 180, px=cx, py=cy, area=e1 * e2))
    if not (XL - 20 < cx < XR + 20 and YN - 20 < cy < YS + 20): continue
    if POLY is not None and not POLY.contains(mr.centroid): continue       # fuera del local (plaza, estacionamiento)
    rects.append(dict(L=e1 * F, D=e2 * F, ang=(-ang) % 180, x=x, y=y, area=e1 * e2))
# quitar contornos anidados (el interior de un rack repite al exterior)
rects.sort(key=lambda r: -r["area"]); keep = []
for r in rects:
    if any(math.hypot(r["x"] - k["x"], r["y"] - k["y"]) < 6 and r["area"] / k["area"] > 0.55 for k in keep): continue
    keep.append(r)
rects = keep

# ---- etiquetas de texto (cm de local) ----
labels = []
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        t = " ".join(s["text"] for s in l["spans"]).strip()
        if t: x, y = to_cm((l["bbox"][0] + l["bbox"][2]) / 2, (l["bbox"][1] + l["bbox"][3]) / 2); labels.append((t, x, y))
def inside(r, pad=4):
    ca, sa = math.cos(math.radians(r["ang"])), math.sin(math.radians(r["ang"])); out = []
    for t, x, y in labels:
        dx, dy = x - r["x"], y - r["y"]; u, v = dx * ca + dy * sa, -dx * sa + dy * ca
        if abs(u) <= r["L"] / 2 + pad and abs(v) <= r["D"] / 2 + pad: out.append(t)
    return out
def near(a, b, tol): return abs(a - b) <= tol
def is_(r, L, D, tol=7): return near(r["L"], L, tol) and near(r["D"], D, tol)

data = dict(hp=[], per=[], gon=[], cab=[], mes=[], bat=[], ph=[], luz=[], rails=[]); gon_mod = []; nolab = collections.Counter(); sin_clasificar = []
W, DEPTH = to_cm(XR, YN)
if POLI: W = max(to_cm(x, y)[0] for x, y in POLI); DEPTH = max(to_cm(x, y)[1] for x, y in POLI)
for r in rects:
    lab = [t for t in inside(r) if not t.strip().isdigit()]; txt = " ".join(lab)       # los números de fila (01, 02…) no son nombres
    if r["L"] > 1000 or "Revisar" in txt: continue
    x, y, ang = r["x"], r["y"], r["ang"]
    if lab and r["L"] > 100 and all(t.startswith(("RV", "RN", "RH", "RM")) or t.startswith("122x") for t in lab):
        data["per"].append(dict(kind=lab[0].split()[0], x=x, y=y, ang=ang, L=122, D=round(r["D"], 1)))
    elif is_(r, 190, 60): data["ph"].append(dict(cls="neu", label="Rack neumáticos (bodega)", x=x, y=y, ang=ang, L=190, D=60, h=350))
    elif txt.strip() == "Rack Neumáticos" and r["L"] > 150: data["ph"].append(dict(cls="neu", label="Rack neumáticos (bodega)", x=x, y=y, ang=ang, L=round(r["L"]), D=round(r["D"]), h=350))
    elif is_(r, 220, 120): data["ph"].append(dict(cls="pal", label="Rack pallets 120×220", x=x, y=y, ang=ang, L=220, D=120, h=300))
    elif is_(r, 155, 100, 8): data["bat"].append(dict(x=x, y=y, ang=ang, L=150, D=100))
    elif is_(r, 300, 160, 12): data["ph"].append(dict(cls="resp", label="Bodega residuos peligrosos", x=x, y=y, ang=ang, L=300, D=160, h=230))
    elif is_(r, 125, 40, 6) and 8 < min(ang % 180, 180 - ang % 180) < 16: gon_mod.append(dict(x=x, y=y, ang=ang))
    elif is_(r, 95, 45, 6): data["cab"].append(dict(x=x, y=y, ang=(ang - 90) % 180, L=45, D=95, h=150))
    elif is_(r, 65, 30, 5): data["cab"].append(dict(x=x, y=y, ang=ang, L=65, D=30, h=300))
    elif is_(r, 120, 50) : data["per"].append(dict(kind="RV1", x=x, y=y, ang=ang, L=122, D=50))
    elif is_(r, 120, 70) and (not lab or all(t.startswith(("RV", "RN", "RH", "RM")) or t.startswith("122x") for t in lab)): data["per"].append(dict(kind=(lab[0].split()[0] if lab else "R70"), x=x, y=y, ang=ang, L=122, D=70))
    elif is_(r, 120, 30) and not lab: data["hp"].append(dict(kind="RA30", x=x, y=y, ang=ang, L=120, D=30))
    elif is_(r, 120, 60) and not lab: data["hp"].append(dict(kind="RA60", x=x, y=y, ang=ang, L=120, D=60))
    elif lab and r["L"] > 45 and r["D"] > 25:
        data["ph"].append(dict(cls="pend", label=" ".join(lab)[:40], x=x, y=y, ang=ang, L=round(r["L"]), D=round(r["D"]), h=100))
    else: sin_clasificar.append((round(r["L"]), round(r["D"]), round(ang)))
# góndolas: dos hileras de 125 x 40 separadas ~50 cm forman un módulo doble de 125 x 90
used = set()
for i, a in enumerate(gon_mod):
    if i in used: continue
    ca, sa = math.cos(math.radians(a["ang"])), math.sin(math.radians(a["ang"]))
    best = None
    for j, b in enumerate(gon_mod):
        if j == i or j in used: continue
        dx, dy = b["x"] - a["x"], b["y"] - a["y"]; u, v = dx * ca + dy * sa, -dx * sa + dy * ca
        if abs(u) < 12 and 35 < abs(v) < 65 and (best is None or abs(abs(v) - 50) < best[0]): best = (abs(abs(v) - 50), j, u, v)
    if best:
        used.add(i); used.add(best[1]); b = gon_mod[best[1]]
        data["gon"].append(dict(x=(a["x"] + b["x"]) / 2, y=(a["y"] + b["y"]) / 2, ang=a["ang"]))
    else: data["ph"].append(dict(cls="pend", label="Góndola sin pareja", x=a["x"], y=a["y"], ang=a["ang"], L=125, D=40, h=150))
# orientación del frente de los perimetrales: hacia el interior desde el muro más cercano
if POLI:
    cg = Polygon([to_cm(x, y) for x, y in POLI]).centroid; CX, CY = cg.x, cg.y     # centro del local
else: CX, CY = W * 0.55, DEPTH * 0.42                                              # centro aproximado de la sala de ventas
for p in data["per"]:
    # el frente es la normal al eje largo que apunta hacia el centro
    best = max(((p["ang"] + 90) % 360, (p["ang"] - 90) % 360), key=lambda f: math.cos(math.radians(f)) * (CX - p["x"]) + math.sin(math.radians(f)) * (CY - p["y"]))
    p["fa"] = round(best, 1)
if not any(p.get("cls") == "resp" for p in data["ph"]):
    for t, x, y in labels:
        if "Residuos" in t or "Peligrosos" in t:
            data["ph"].append(dict(cls="resp", label="Bodega residuos peligrosos", x=x, y=y, ang=0, L=300, D=160, h=230)); break

# ---- altillo: dibujo aparte ("PLANTA ALTILLO"), con su esquina noreste sobre la esquina noreste del local ----
def leer_altillo():
    lab = None
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = " ".join(s["text"] for s in l["spans"]).strip()
            if "ALTILLO" in t.upper() and "PLANTA" in t.upper(): lab = l["bbox"]
    if not lab: return None
    R = pymupdf.Rect(lab[0] - 25, lab[1] - 365, lab[0] + 430, lab[1] - 15)
    Hs, Vs = [], []
    for d in page.get_drawings():
        if (d.get("width") or 0) < 0.9: continue
        for it in d["items"]:
            if it[0] != "l": continue
            a, b = it[1], it[2]
            if not (R.contains(a) and R.contains(b)) or math.hypot(a.x - b.x, a.y - b.y) < 30: continue
            if abs(a.y - b.y) < 0.4: Hs.append((a.y, min(a.x, b.x), max(a.x, b.x)))
            elif abs(a.x - b.x) < 0.4: Vs.append((a.x, min(a.y, b.y), max(a.y, b.y)))
    if not Hs or not Vs: return None
    x0 = min(v[0] for v in Vs); x1 = max(v[0] for v in Vs); y0 = min(h[0] for h in Hs); y1 = max(h[0] for h in Hs)
    mid = [v for v in Vs if x0 + 5 < v[0] < x1 - 5]; xs = mid[0][0] if mid else x1
    hl = [h for h in Hs if y0 + 5 < h[0] < y1 - 5]; ys = hl[0][0] if hl else y1
    X = lambda x: W - (x1 - x) * F; Y = lambda y: DEPTH - (y - y0) * F      # esquina noreste del dibujo = esquina noreste del local
    parts = [[X(x0), X(xs), Y(ys), DEPTH], [X(xs), W, Y(y1), DEPTH]]
    racks = []
    for r in all_rects:
        if not (R.x0 < r["px"] < R.x1 and R.y0 < r["py"] < R.y1) or r["D"] < 14: continue
        if is_(r, 120, 30) or is_(r, 120, 60):
            racks.append(dict(kind="RA60" if r["D"] > 45 else "RA30", x=X(r["px"]), y=Y(r["py"]), ang=r["ang"], L=120, D=60 if r["D"] > 45 else 30))
    lad = None
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = " ".join(s["text"] for s in l["spans"]).strip(); cx = (l["bbox"][0] + l["bbox"][2]) / 2; cy = (l["bbox"][1] + l["bbox"][3]) / 2
            if "Escalerilla" in t and R.x0 - 40 < cx < R.x1 and R.y0 < cy < R.y1: lad = [X(cx), Y(cy)]
    return dict(parts=parts, racks=racks, ladder=lad, h=260, baranda=100)  # altura estándar de la losa: 2,60 m (confirmada); el plano rotula la baranda de 1 m
    _ = dict()
data["altillo"] = leer_altillo()
data["contour"] = [list(to_cm(x, y)) for x, y in POLI] if POLI else [[0, 0], [W, 0], [W, DEPTH], [0, DEPTH]]
data["meta"] = dict(F=F, W=W, D=DEPTH, resumen={k: len(v) for k, v in data.items() if isinstance(v, list)}, sin_clasificar=collections.Counter(sin_clasificar).most_common(12))
json.dump(data, open(OUT, "w"), ensure_ascii=False)
print(json.dumps(data["meta"], ensure_ascii=False))
