"""Lee el plano eléctrico (PDF vectorial de AutoCAD) y deja datos/luces.json con las luminarias en coordenadas del DXF.
Uso: python3 extraer_luces_pdf.py plano_electrico.pdf [escala] [x0] [y0]
La escala (cm por punto) y el origen (x0, y0 del vértice suroeste del local en el PDF) se calibran con el contorno
del local: en Talca fueron 1.871, 328 y 1125, con el vértice suroeste del DXF en (14392, 516)."""
import sys, math, json, pdfplumber
from shapely.geometry import MultiPoint
pdf = sys.argv[1]; S = float(sys.argv[2]) if len(sys.argv) > 2 else 1.871
X0 = float(sys.argv[3]) if len(sys.argv) > 3 else 328; Y0 = float(sys.argv[4]) if len(sys.argv) > 4 else 1125
DXF_X0, DXF_Y0 = 14392, 516      # vértice suroeste del contorno en el DXF (cámbialo para otra tienda)
p = pdfplumber.open(pdf).pages[0]
col = lambda o: tuple(round(v, 1) for v in o['stroking_color']) if isinstance(o.get('stroking_color'), (list, tuple)) else None
RED, YEL = (1.0, 0.0, 0.0), (1.0, 1.0, 0.0)
shapes = [dict(col=col(r), pts=[(r['x0'], r['top']), (r['x1'], r['top']), (r['x1'], r['bottom']), (r['x0'], r['bottom'])]) for r in p.rects if col(r) in (RED, YEL) and (r['width'] > 2 or r['height'] > 2)]
shapes += [dict(col=col(c), pts=list(c['pts'])) for c in p.curves if col(c) in (RED, YEL) and len(c['pts']) <= 6]
dx = lambda x, y: (DXF_X0 + (x - X0) * S, DXF_Y0 + (Y0 - y) * S)
lum, heads = [], []
for s in shapes:
    r = MultiPoint(s['pts']).minimum_rotated_rectangle
    if r.geom_type != 'Polygon': continue
    q = list(zip(*r.exterior.coords.xy))[:4]
    e1 = (q[1][0] - q[0][0], q[1][1] - q[0][1]); e2 = (q[2][0] - q[1][0], q[2][1] - q[1][1])
    l1, l2 = math.hypot(*e1), math.hypot(*e2); long, short, u = (l1, l2, e1) if l1 >= l2 else (l2, l1, e2)
    ang = math.degrees(math.atan2(-u[1], u[0])) % 180; x, y = dx(r.centroid.x, r.centroid.y)
    if s['col'] == YEL and 55 < long < 75: lum.append(dict(t='L03', x=x, y=y, ang=ang))           # canoas de bodega
    elif s['col'] == RED and 55 < long < 75 and short < 8: lum.append(dict(t='L02', x=x, y=y, ang=ang))   # lineales de sala (L01 se separa por zona)
    elif s['col'] == RED and 9 < long < 16 and short < 6: heads.append(dict(t='L06', x=x, y=y, ang=ang))  # cabezales de riel
def dedup(L, tol):
    out = []
    for a in L:
        if not any(math.hypot(a['x'] - b['x'], a['y'] - b['y']) < tol for b in out): out.append(a)
    return out
json.dump(dict(lum=dedup(lum, 8), heads=dedup(heads, 3)), open('datos/luces.json', 'w'))
print('luminarias:', len(dedup(lum, 8)), '| cabezales L06:', len(dedup(heads, 3)))
