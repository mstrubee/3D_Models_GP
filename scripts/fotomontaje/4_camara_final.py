import numpy as np, math
from scipy.optimize import least_squares
Wp,Hp=1280,960
p2=np.load("cam_img2.npy")
def P(pl,y=0): return np.array([pl[0],y,-pl[1]])
A=(787,1515.); E3=(2320,1379.); E1=(2570,2131.); E2=(2522,1517.)
def proj(p,X):
    cx,cy,cz,yaw,pit,f=p
    fw=np.array([math.cos(pit)*math.sin(yaw),math.sin(pit),-math.cos(pit)*math.cos(yaw)])
    rt=np.cross(fw,[0,1,0]); rt/=np.linalg.norm(rt); up=np.cross(rt,fw)
    d=X-np.array([cx,cy,cz]); xc,yc,zc=d@rt,d@up,d@fw; zc=max(zc,1)
    return np.array([Wp/2+f*xc/zc, Hp/2-f*yc/zc])
# partida: pose de tu render; misma apertura horizontal; altura de persona
p0=np.array([p2[0],165.0,p2[2],p2[3],p2[4],p2[5]*Wp/1021])
prior=np.array([250,20,250,0.06,0.04,150.0])
def res(p):
    r=[]
    for pl,u,v in ((A,530,566),(E3,785,625)):
        q=proj(p,P(pl)); r+=[q[0]-u,q[1]-v]
    q=proj(p,P(E1)); r.append(q[0]-1195)
    r+=list((p-p0)/prior*6)
    return np.array(r)
r=least_squares(res,p0,bounds=([p0[0]-2500,140,p0[2]-2500,p0[3]-.5,-.25,700],[p0[0]+2500,200,p0[2]+2500,p0[3]+.5,.25,3200]))
p=r.x; np.save("cam_final.npy",p)
print("cámara final: plano",round(p[0]),round(-p[2]),"| altura",round(p[1]),"| yaw",round(math.degrees(p[3]),1),"| pitch",round(math.degrees(p[4]),1),"| f",round(p[5]),"→ apertura horizontal",round(math.degrees(2*math.atan(640/p[5])),1),"°")
for nom,pl in (("A",A),("E3",E3),("E2",E2),("E1",E1)):
    print(nom,"suelo →",tuple(np.round(proj(p,P(pl))).astype(int)),"| tope 363 →",tuple(np.round(proj(p,P(pl,363))).astype(int)))
