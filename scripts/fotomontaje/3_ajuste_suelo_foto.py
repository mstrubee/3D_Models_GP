import numpy as np, math
from scipy.optimize import least_squares
p2=np.load("cam_img2.npy")   # cx,cy,cz,yaw,pit,f,cy0 (imagen 2, ancho 1021)
Wp,Hp=1280,960
W2=np.array([656,0.]); A=np.array([787,1515.]); E3=np.array([2320,1379.]); E2=np.array([2522,1517.])
def P(pl,y): return np.array([pl[0],y,-pl[1]])
ground=[(P(W2,0),(262,558)),(P(A,0),(530,566)),(P(E3,0),(785,625)),(P(E2,0),(1050,632))]
def proj(p,X):
    cx,cy,cz,yaw,pit,f=p
    fw=np.array([math.cos(pit)*math.sin(yaw),math.sin(pit),-math.cos(pit)*math.cos(yaw)])
    rt=np.cross(fw,[0,1,0]); rt/=np.linalg.norm(rt); up=np.cross(rt,fw)
    d=X-np.array([cx,cy,cz]); xc,yc,zc=d@rt,d@up,d@fw; zc=max(zc,1)
    return np.array([Wp/2+f*xc/zc, Hp/2-f*yc/zc])
# partida: la pose del render de imagen 2, con la misma apertura horizontal (f escalada al ancho de la foto) y la altura de una persona
f0=p2[5]*Wp/1021
p0=np.array([p2[0],165.0,p2[2],p2[3],p2[4],f0])
print("con la pose del render (sin ajustar): error medio contra los 4 puntos de suelo:",round(np.mean([np.linalg.norm(proj(p0,X)-np.array(u)) for X,u in ground]),1),"px")
for X,u in ground: print("  ",u,"→",np.round(proj(p0,X)).astype(int))
prior=np.array([200,12,200,0.03,0.03,250.0])
def res(p):
    r=[]
    for X,u in ground: r+=list(proj(p,X)-np.array(u))
    r+=list((p-p0)/prior*4)               # no alejarse mucho de la pose del render
    return np.array(r)
r=least_squares(res,p0,bounds=([p0[0]-1500,140,p0[2]-1500,p0[3]-.4,-.3,800],[p0[0]+1500,200,p0[2]+1500,p0[3]+.4,.3,3500]))
p=r.x
print("ajustada: cámara en el plano",round(p[0]),round(-p[2]),"| altura",round(p[1]),"| yaw",round(math.degrees(p[3]),1),"° | pitch",round(math.degrees(p[4]),1),"° | f",round(p[5]),"px (apertura horizontal",round(math.degrees(2*math.atan(640/p[5])),1),"°)")
print("error medio tras ajustar:",round(np.mean([np.linalg.norm(proj(p,X)-np.array(u)) for X,u in ground]),1),"px")
for X,u in ground: print("  ",u,"→",np.round(proj(p,X)).astype(int))
np.save("cam_foto.npy",p)
