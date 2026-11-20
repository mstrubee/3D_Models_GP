"""Lee el plano eléctrico de alumbrado en PDF (1:50 reescalado) y deja las luminarias en cm del local.
L02 = luminaria lineal de 120 cm (rojo, relleno o solo contorno, a cualquier ángulo); F01 = foco embutido (círculos magenta).
Uso: python3 extraer_luces_pdf_v2.py electrico.pdf datos_local.json salida.json
Calibración (Chillán): 1,871 cm/pt; esquina suroeste interior del local en (187.3, 1421.6) pt; altillo: esquina noreste interior en (1830.1, 316.4) pt.
Esas tres cifras se obtienen alineando los muros del plano eléctrico con los del de arquitectura (el eléctrico viene a 0,9427 de la escala)."""
import sys, math, json, collections
import pymupdf
from shapely.geometry import MultiPoint
PDF, DATOS, OUT = sys.argv[1:4]
S, X0, Y0 = 1.871, 187.3, 1421.6
AX1, AY0 = 1830.1, 316.4
meta = json.load(open(DATOS))["meta"]; W, D = meta["W"], meta["D"]
pg = pymupdf.open(PDF)[0]
RED, MAG = (1.0, 0.0, 0.0), (1.0, 0.0, 1.0)
lin, foc = [], []
for d in pg.get_drawings():
    col = tuple(round(v, 1) for v in d["color"]) if d.get("color") else None
    fil = tuple(round(v, 1) for v in d["fill"]) if d.get("fill") else None
    pts = []
    for it in d["items"]:
        if it[0] == "l": pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        elif it[0] == "re": r = it[1]; pts += [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
        elif it[0] == "qu": q = it[1]; pts += [(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)]
        elif it[0] == "c": pts += [(it[1].x, it[1].y), (it[4].x, it[4].y)]
    if len(pts) < 2: continue
    mr = MultiPoint(pts).minimum_rotated_rectangle
    if mr.geom_type != "Polygon": continue
    c = list(mr.exterior.coords); e1 = math.hypot(c[1][0] - c[0][0], c[1][1] - c[0][1]) * S; e2 = math.hypot(c[2][0] - c[1][0], c[2][1] - c[1][1]) * S
    ang = math.degrees(math.atan2(-(c[1][1] - c[0][1]), c[1][0] - c[0][0])) % 180
    if e1 < e2: ang = (ang + 90) % 180
    L, Dd = max(e1, e2), min(e1, e2); cx, cy = mr.centroid.x, mr.centroid.y
    if (col == RED or fil == RED) and 105 < L < 135 and Dd < 25: lin.append((cx, cy, ang))
    elif fil == MAG: foc.append((cx, cy))
def dedup(P, tol):
    out = []
    for p in P:
        if not any(math.hypot(p[0] - q[0], p[1] - q[1]) < tol for q in out): out.append(p)
    return out
def circulos(P, r):
    out = []
    for p in P:
        for c in out:
            if math.hypot(p[0] - c[0] / c[2], p[1] - c[1] / c[2]) < r: c[0] += p[0]; c[1] += p[1]; c[2] += 1; break
        else: out.append([p[0], p[1], 1])
    return [(c[0] / c[2], c[1] / c[2]) for c in out]
lin = dedup(lin, 10 / S); foc = circulos(foc, 16 / S)
luz = []
def local(px_, py_): return ((px_ - X0) * S, (Y0 - py_) * S)
def altillo(px_, py_): return (W - (AX1 - px_) * S, D - (py_ - AY0) * S)
for cx, cy, ang in lin:
    en_alt = cx > 1450                       # el dibujo del altillo está a la derecha del plano (el local termina en x = 1354 pt)
    x, y = altillo(cx, cy) if en_alt else local(cx, cy)
    luz.append(dict(t="L02", x=x, y=y, a=ang, alt=en_alt))
for cx, cy in foc:
    en_alt = cx > 1450
    x, y = altillo(cx, cy) if en_alt else local(cx, cy)
    luz.append(dict(t="F01", x=x, y=y, a=0, alt=en_alt))
json.dump(luz, open(OUT, "w"))
c = collections.Counter((l["t"], l["alt"]) for l in luz)
print("luminarias:", {f"{t}{' (altillo)' if a else ''}": n for (t, a), n in c.items()})
