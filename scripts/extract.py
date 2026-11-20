import ezdxf, math, json
from collections import Counter, defaultdict
from shapely.geometry import Polygon, Point, LineString, MultiPoint, box
from shapely.ops import unary_union
import os
F=os.environ.get("PLANO_DXF","plano.dxf")   # ruta del DXF de la planta
doc=ezdxf.readfile(F); msp=doc.modelspace()
XB=16372   # límite de alturas (eje estructural), supuesto a confirmar

def wcs_polys(ins, min_vertices=4):
    out=[]
    for v in ins.virtual_entities():
        if v.dxftype()=="LWPOLYLINE":
            pts=[(p.x,p.y) for p in v.vertices_in_wcs()]
            if len(pts)>=min_vertices: out.append(pts)
    return out
def rect_of(pts):
    r=MultiPoint(pts).minimum_rotated_rectangle; xs,ys=r.exterior.coords.xy
    p=list(zip(xs,ys))[:4]
    e1=(p[1][0]-p[0][0],p[1][1]-p[0][1]); e2=(p[2][0]-p[1][0],p[2][1]-p[1][1])
    l1,l2=math.hypot(*e1),math.hypot(*e2)
    long,short,u=(l1,l2,e1) if l1>=l2 else (l2,l1,e2)
    ang=math.degrees(math.atan2(u[1],u[0]))
    return dict(long=long,short=short,ang=ang,cx=r.centroid.x,cy=r.centroid.y,poly=r)
# contorno
cont=None
for e in msp.query("LWPOLYLINE"):
    if e.closed and e.dxf.layer=="0":
        p=Polygon([(x,y) for x,y,*_ in e.get_points()])
        if p.is_valid and p.area>3e6: cont=p; break
cont=Polygon(list(cont.exterior.coords)[:-1])
bnd=cont.exterior
print("Contorno:", [(round(x),round(y)) for x,y in list(cont.exterior.coords)[:-1]])
minx,miny,maxx,maxy=cont.bounds
# zonas
bod=cont.intersection(box(minx-10,miny-10,XB,maxy+10)); sal=cont.intersection(box(XB,miny-10,maxx+10,maxy+10))
print("Área bodega m2:",round(bod.area/1e4,1)," sala m2:",round(sal.area/1e4,1))
seg=LineString([(XB,miny-10),(XB,maxy+10)]).intersection(cont)
print("Segmento del cambio de altura:", [(round(x),round(y)) for x,y in seg.coords])

inst=[]
def away_front(cx,cy):
    # frente = alejándose del muro más cercano
    pt=Point(cx,cy); d=bnd.project(pt); n=bnd.interpolate(d)
    dx,dy=n.x-cx,n.y-cy; L=math.hypot(dx,dy) or 1
    return math.degrees(math.atan2(-dy/L,-dx/L))   # dirección de frente (opuesta al muro)
def snap_perp(front_deg, axis_deg):
    # elige el frente perpendicular al eje más cercano a la dirección deseada
    c=[axis_deg+90, axis_deg-90]
    return min(c,key=lambda a:abs((a-front_deg+180)%360-180))

# Perimetrales RV1/RV2/RN
for ins in msp.query("INSERT"):
    n=ins.dxf.name
    if n in("RV1","RV2","RN"):
        polys=wcs_polys(ins)
        big=max(polys,key=lambda p:Polygon(p).area) if polys else None
        if not big: continue
        r=rect_of(big); f=snap_perp(away_front(r['cx'],r['cy']), r['ang'])
        inst.append(dict(t="per",kind=n,x=r['cx'],y=r['cy'],fa=f,L=r['long'],D=r['short']))
# Racks RA30 / RA60 (bloques)
ra=[]
for ins in msp.query("INSERT"):
    if ins.dxf.name in("RA30","RA60"):
        polys=wcs_polys(ins,4)
        if not polys: continue
        big=max(polys,key=lambda p:Polygon(p).area)
        r=rect_of(big); ra.append(dict(kind=ins.dxf.name,x=r['cx'],y=r['cy'],ang=r['ang'],L=r['long'],D=r['short']))
# rótulos
labels=[]
for e in msp:
    if e.dxftype()=="MTEXT": labels.append((e.plain_text().replace("\n"," | ").strip(), Point(e.dxf.insert.x,e.dxf.insert.y)))
hp=acop=other=0
for r in ra:
    rect=Polygon(rect_of([(r['x']-r['L']/2*math.cos(math.radians(r['ang'])), r['y']-r['L']/2*math.sin(math.radians(r['ang'])))]+[(r['x'],r['y'])])['poly'].exterior.coords) if False else None
    poly=box(r['x']-r['L']/2,r['y']-r['D']/2,r['x']+r['L']/2,r['y']+r['D']/2) if abs((r['ang']%180))<1 else (box(r['x']-r['D']/2,r['y']-r['L']/2,r['x']+r['D']/2,r['y']+r['L']/2) if abs((r['ang']%180)-90)<1 else Point(r['x'],r['y']).buffer(r['D']/2))
    near=[t for t,pt in labels if poly.buffer(25).contains(pt)]
    tag="hp" if any(t.startswith("Rack Repisas") for t in near) else ("acop" if any(t.startswith("Repisa Acopio") for t in near) else "otro")
    r['tag']=tag; r['near']=near[:1]
print("\nRA por etiqueta:",Counter((r['kind'],r['tag']) for r in ra))
print("RA zona (x<XB):",Counter((r['kind'], 'bodega' if r['x']<XB else 'sala') for r in ra))
print("Ejemplo otros:",[ (r['kind'],round(r['x']),round(r['y']),r['near']) for r in ra if r['tag']=='otro'][:6])
json.dump(dict(ra=ra,inst=inst),open("tmp1.json","w"),default=float)
print("\nPerimetrales:",Counter(i['kind'] for i in inst))
for i in inst: print("  ",i['kind'],round(i['x']),round(i['y']),"frente",round(i['fa']),"L×D",round(i['L']),round(i['D']))
