exec(open("extract.py").read().split("inst=[]")[0])
import json, math
from collections import Counter
labels=[]
for e in msp:
    if e.dxftype()=="MTEXT": labels.append((e.plain_text().replace("\n"," | ").strip(), Point(e.dxf.insert.x,e.dxf.insert.y)))
def rbox(cx,cy,L,D,ang):
    a=math.radians(ang); ux,uy=math.cos(a),math.sin(a); vx,vy=-uy,ux
    pts=[(cx+s*L/2*ux+t*D/2*vx, cy+s*L/2*uy+t*D/2*vy) for s,t in((-1,-1),(1,-1),(1,1),(-1,1))]
    return Polygon(pts)
def snap_perp(front_deg, axis_deg):
    c=[axis_deg+90, axis_deg-90]
    return min(c,key=lambda a:abs((a-front_deg+180)%360-180))
def away_front(cx,cy):
    pt=Point(cx,cy); d=bnd.project(pt); n=bnd.interpolate(d)
    dx,dy=n.x-cx,n.y-cy; L=math.hypot(dx,dy) or 1
    return math.degrees(math.atan2(-dy/L,-dx/L))
out=dict(contour=[list(p) for p in list(cont.exterior.coords)[:-1]], XB=XB,
         step=[list(p) for p in seg.coords],
         bodega=[list(p) for p in list(bod.exterior.coords)], sala=[list(p) for p in list(sal.exterior.coords)],
         per=[],hp=[],gon=[],cab=[],mes=[],bat=[],ph=[])
occupied=[]
# Perimetrales
for ins in msp.query("INSERT"):
    if ins.dxf.name in("RV1","RV2","RN"):
        polys=wcs_polys(ins); big=max(polys,key=lambda p:Polygon(p).area); r=rect_of(big)
        f=snap_perp(away_front(r['cx'],r['cy']), r['ang'])
        out['per'].append(dict(kind=ins.dxf.name,x=r['cx'],y=r['cy'],fa=f,L=r['long'],D=r['short']))
        occupied.append(r['poly'])
# Racks RA
for ins in msp.query("INSERT"):
    if ins.dxf.name in("RA30","RA60"):
        polys=wcs_polys(ins,4); big=max(polys,key=lambda p:Polygon(p).area); r=rect_of(big)
        poly=r['poly']; near=[t for t,pt in labels if poly.buffer(25).contains(pt)]
        acop=any(t.startswith("Repisa Acopio") for t in near)
        item=dict(kind=ins.dxf.name,x=r['cx'],y=r['cy'],ang=r['ang'],L=r['long'],D=r['short'])
        if acop: out['ph'].append(dict(cls="acop",label="Repisa acopio baterías",x=r['cx'],y=r['cy'],ang=r['ang'],L=r['long'],D=r['short'],h=100))
        else: out['hp'].append(item)
        occupied.append(poly)
# Góndolas: filas por bloque + fila por polilíneas
rows=[]
for ins in msp.query("INSERT"):
    if ins.dxf.name in ("A$C1fa00304","A$Cc7a0e745"):
        pts=[p for poly in wcs_polys(ins,3) for p in poly]; r=rect_of(pts)
        rows.append(dict(cx=r['cx'],cy=r['cy'],ang=r['ang']%180,long=r['long']))
strips=[]
for e in msp.query("LWPOLYLINE"):
    if e.dxf.layer=="A-PUERTAS":
        pts=[(p.x,p.y) for p in e.vertices_in_wcs()]
        if len(pts)>=4:
            r=rect_of(pts)
            if 122<=r['long']<=126 and 5<=r['short']<=7 and r['cx']>16400: strips.append(r)
strips.sort(key=lambda s:s['cx'])
if strips:
    cx=sum(s['cx'] for s in strips)/len(strips); cy=sum(s['cy'] for s in strips)/len(strips)
    rows.append(dict(cx=cx,cy=cy,ang=strips[0]['ang']%180,long=len(strips)*124+106))
for row in rows:
    n=round((row['long']-106)/124); a=math.radians(row['ang']); ux,uy=math.cos(a),math.sin(a)
    for k in range(n):
        s=-row['long']/2+53+124*(k+0.5)
        out['gon'].append(dict(x=row['cx']+s*ux,y=row['cy']+s*uy,ang=row['ang']))
    for s in (-row['long']/2+26.5, row['long']/2-26.5):
        out['cab'].append(dict(x=row['cx']+s*ux,y=row['cy']+s*uy,ang=row['ang'],L=53,D=95,h=150))
    occupied.append(rbox(row['cx'],row['cy'],row['long'],95,row['ang']))
# Mesones
env=[]
for e in msp.query("LWPOLYLINE"):
    if e.closed and e.dxf.layer=="MOBILIARIO":
        p=Polygon([(p.x,p.y) for p in e.vertices_in_wcs()])
        if p.is_valid and 44000<p.area<45500: env.append(p.bounds)
env.sort()
types=[["atn"]*4, ["atn","mr","tal","tal"]]
for (x0,y0,x1,y1),ts in zip(env,types):
    for k,tv in enumerate(ts):
        cx=(x0+x1)/2; cy=y0+124*k+62
        if tv=="mr": out['ph'].append(dict(cls="mr",label="Mesón movilidad reducida",x=(16133+16193)/2,y=(1232+1352)/2,ang=90,L=120,D=60,h=85))
        else: out['mes'].append(dict(v=tv,x=cx,y=cy))
    occupied.append(box(x0,y0,x1,y1))

# Bloques de bodega (neumáticos, residuos, 120x60)
for ins in msp.query("INSERT"):
    nm=ins.dxf.name
    if nm in("A$C2a3e009f","A$C9d4afb35","A$C9c812a9b"):
        polys=wcs_polys(ins,4)
        if not polys: continue
        big=max(polys,key=lambda p:Polygon(p).area); r=rect_of(big)
        lab={"A$C2a3e009f":"Rack neumáticos (bodega)","A$C9d4afb35":"Bodega residuos peligrosos","A$C9c812a9b":"Bodega 120×60"}[nm]
        out['ph'].append(dict(cls="otro",label=lab,x=r['cx'],y=r['cy'],ang=r['ang'],L=r['long'],D=r['short'],h=100))
        occupied.append(r['poly'])
# Racks de baterías
out['bat'].append(dict(x=(16323+16778)/2,y=1640,fa=-90))
occupied.append(box(16323,1590,16778,1690))
# Resto de mobiliario como volúmenes pendientes
cands=[]
for e in msp.query("LWPOLYLINE"):
    if e.closed and e.dxf.layer in("MOBILIARIO","P3 EQUIPAMIENTO","Muebles Bea","_Líneas finas_"):
        p=Polygon([(q.x,q.y) for q in e.vertices_in_wcs()])
        if p.is_valid and 1500<p.area<60000 and cont.contains(p.centroid):
            if any(o.buffer(8).contains(p.centroid) for o in occupied): continue
            r=rect_of(list(p.exterior.coords)); cands.append((r,p,e.dxf.layer))
# deduplicar por centro
seen=[]; 
for r,p,l in sorted(cands,key=lambda c:-c[1].area):
    if any(abs(r['cx']-s['cx'])<6 and abs(r['cy']-s['cy'])<6 for s in seen): continue
    seen.append(r)
    near=sorted([(pt.distance(p),t) for t,pt in labels if pt.distance(p)<45])
    out['ph'].append(dict(cls="otro",label=(near[0][1].split(" |")[0] if near else "Sin rótulo"),x=r['cx'],y=r['cy'],ang=r['ang'],L=r['long'],D=r['short'],h=100))

def nombre(p):
    L,D=round(p['L']),round(p['D'])
    if p['cls']!="otro" or p['label'] in("Rack neumáticos (bodega)","Bodega residuos peligrosos","Bodega 120×60"): return
    if (L,D)==(70,70): p['label']="Isla ofertas 70×70"
    elif (L,D) in((120,100),(100,120)): p['label']="Isla ofertas 100×120"
    elif (L,D)==(67,44): p['label']="Cabecera repisas HP"; p['h']=300; p['h_known']=True
    elif (L,D) in((219,120),(220,120)): p['label']="Rack pallets 120×220"
    elif (L,D) in((120,60),): p['label']="Bodega cartones/basura 120×60"
    else: p['label']="Mobiliario sin identificar"
for p in out['ph']: nombre(p)
print({k:(len(v) if isinstance(v,list) else v) for k,v in out.items() if k not in("contour","step","bodega","sala")})
print("Perimetrales por tipo:",Counter(p['kind'] for p in out['per']))
print("HP por profundidad:",Counter(round(h['D']) for h in out['hp']))
print("Góndolas (módulos):",len(out['gon']),"| cabeceras:",len(out['cab']))
print("Pendientes por tipo:",Counter((p['cls'],p['label'][:24],round(p['L']),round(p['D'])) for p in out['ph']).most_common(40))
json.dump(out,open("data.json","w"),default=float)
