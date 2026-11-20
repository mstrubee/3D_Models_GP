import numpy as np, math, sys
from scipy.optimize import least_squares
W2=np.array([656,0.]); A=np.array([787,1515.]); E3=np.array([2320,1379.]); E2=np.array([2522,1517.]); E1=np.array([2570,2131.])
dw=(A-W2)/np.linalg.norm(A-W2)
def P(pl,y): return np.array([pl[0],y,-pl[1]])
pts=[]
for u,xp in ((240,21),(447,104)):
    q=W2+u*dw; pts.append((P(q,0),(xp,198))); pts.append((P(q,254),(xp,114)))
for nom,q,xp,yt,yb in (("A",A,446,90,192),("E3",E3,642,43,214),("E2",E2,756,37,217),("E1",E1,982,51,209)):
    pts.append((P(q,363),(xp,yt))); pts.append((P(q,0),(xp,yb)))
X3=np.array([p[0] for p in pts]); UV=np.array([p[1] for p in pts],float); Wimg=1021
def proj(p):
    cx,cy,cz,yaw,pit,f,cy0=p
    fw=np.array([math.cos(pit)*math.sin(yaw),math.sin(pit),-math.cos(pit)*math.cos(yaw)])
    rt=np.cross(fw,[0,1,0]); rt/=np.linalg.norm(rt); up=np.cross(rt,fw)
    d=X3-np.array([cx,cy,cz]); xc,yc,zc=d@rt,d@up,d@fw
    zc=np.where(zc<1,1,zc)
    return np.stack([Wimg/2+f*xc/zc, cy0-f*yc/zc],1)
def res(p): return (proj(p)-UV).ravel()
best=None; rng=np.random.default_rng(3)
for it in range(int(sys.argv[1])):
    cx=rng.uniform(-500,5000); cz=rng.uniform(-800,3500); cy=rng.uniform(120,260)
    fwd=np.array([1500,0,-800])-np.array([cx,0,cz]); yaw=math.atan2(fwd[0],-fwd[2])+rng.uniform(-.5,.5)
    p0=[cx,cy,cz,yaw,rng.uniform(-.1,.1),rng.uniform(600,2200),rng.uniform(80,200)]
    try: r=least_squares(res,p0,loss="soft_l1",f_scale=3.0,max_nfev=60,bounds=([-3000,100,-3000,-7,-.6,300,-200],[8000,450,6000,7,.6,4000,500]))
    except Exception: continue
    c=np.sqrt((r.fun**2).mean())
    if best is None or c<best[0]: best=(c,r.x)
c,p=best; np.save("cam_img2.npy",p)
print("error RMS:",round(c,1),"px | cámara en el plano (x,y):",round(p[0]),round(-p[2]),"| altura",round(p[1]),"cm | yaw",round(math.degrees(p[3]),1),"° | pitch",round(math.degrees(p[4]),1),"° | f",round(p[5]),"px | cy0",round(p[6]))
for (X,(u,v)),q in zip(pts,proj(p)): print((u,v),"→",tuple(np.round(q).astype(int)))
