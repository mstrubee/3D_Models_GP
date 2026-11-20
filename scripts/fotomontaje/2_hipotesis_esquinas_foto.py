import numpy as np, math, itertools, time
from scipy.optimize import least_squares
Wp,Hp=1280,960
M={"W2":(656,0.),"A":(787,1515.),"E3":(2320,1379.),"E2":(2522,1517.),"E1":(2570,2131.)}
K=[(262,558),(530,566),(785,625),(1050,632),(1195,None)]
def P(pl,y=0): return np.array([pl[0],y,-pl[1]])
def proj(p,X):
    cx,cy,cz,yaw,pit,f=p
    fw=np.array([math.cos(pit)*math.sin(yaw),math.sin(pit),-math.cos(pit)*math.cos(yaw)])
    rt=np.cross(fw,[0,1,0]); rt/=np.linalg.norm(rt); up=np.cross(rt,fw)
    d=X-np.array([cx,cy,cz]); xc,yc,zc=d@rt,d@up,d@fw; zc=max(zc,1)
    return np.array([Wp/2+f*xc/zc, Hp/2-f*yc/zc])
names=list(M); rng=np.random.default_rng(5); out=[]; t0=time.time()
for mi in itertools.combinations(range(5),4):
    for ki in itertools.combinations(range(5),4):
        pairs=[(M[names[a]],K[b]) for a,b in zip(mi,ki)]
        def res(p):
            r=[]
            for pl,(u,v) in pairs:
                q=proj(p,P(pl)); r.append(q[0]-u)
                if v is not None: r.append(q[1]-v)
            return np.array(r)
        best=None
        for s in range(14):
            cx=rng.uniform(1500,7000); cz=rng.uniform(-1500,3000); cy=rng.uniform(140,200)
            fwd=np.array([1500,0,-800])-np.array([cx,0,cz]); yaw=math.atan2(fwd[0],-fwd[2])
            p0=[cx,cy,cz,yaw,0.0,rng.uniform(800,1800)]
            try: r=least_squares(res,p0,max_nfev=50,bounds=([-3000,140,-4000,-7,-.35,700],[9000,200,5000,7,.35,2600]))
            except Exception: continue
            c=np.sqrt((r.fun**2).mean())
            if best is None or c<best[0]: best=(c,r.x)
        out.append((best[0],[names[a] for a in mi],ki,best[1]))
out.sort(key=lambda t:t[0])
for c,mn,ki,p in out[:6]:
    print("error",round(c,1),"px | modelo",mn,"→ fotos",[K[k][0] for k in ki],"| cámara plano",round(p[0]),round(-p[2]),"alt",round(p[1]),"yaw",round(math.degrees(p[3])),"f",round(p[5]))
print("tiempo",round(time.time()-t0),"s")
np.save("hip_best.npy",out[0][3])
