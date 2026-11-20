import numpy as np, cv2
from PIL import Image
ph=cv2.imread("/mnt/user-data/uploads/WhatsApp_Image_2026-11-20_at_12_58_32.jpeg"); H,W=ph.shape[:2]
rd=np.array(Image.open("render_alpha.png").convert("RGBA")).astype(np.float32)   # RGBA, 1280x960
al=(rd[...,3]/255.0)
# columnas: techo y base de la fachada nueva
ys=np.arange(H)[:,None]
opaco=(al>0.5)
top=np.where(opaco.any(0),opaco.argmax(0),H); bot=np.where(opaco.any(0),H-1-opaco[::-1].argmax(0),-1)
# polígono del edificio antiguo (Pullman GO), en px de la foto
OB=np.array([(262,376),(520,396),(522,390),(600,364),(780,331),(1197,357),(1197,622),(1050,645),(785,634),(530,578),(262,568)],np.int32)
m_ob=np.zeros((H,W),np.uint8); cv2.fillPoly(m_ob,[OB],255)
xx=np.arange(W)[None,:].repeat(H,0); yy=np.arange(H)[:,None].repeat(W,1)
sobre=(m_ob>0)&(yy<top[None,:]-1)&(~opaco)        # restos que asoman sobre la fachada nueva
bajo=(m_ob>0)&(yy>bot[None,:]+1)&(~opaco)         # restos bajo la fachada nueva (base antigua, portón, poste)
# cielo: ajuste de color en función de (x, y) con píxeles limpios de cielo
sky=np.zeros((H,W),bool); sky[15:325,380:1020]=True
vals=ph.astype(np.float32)
A_=np.stack([np.ones(sky.sum()),xx[sky],yy[sky],yy[sky]**2,xx[sky]*yy[sky]],1).astype(np.float64)
coef=[np.linalg.lstsq(A_,vals[...,c][sky].astype(np.float64),rcond=None)[0] for c in range(3)]
def skyfill(mask):
    out=ph.copy().astype(np.float32); X=xx[mask].astype(np.float64); Y=np.minimum(yy[mask].astype(np.float64),322.0)
    B_=np.stack([np.ones(len(X)),X,Y,Y**2,X*Y],1)
    for c in range(3): out[...,c][mask]=B_@coef[c]
    return out
cielo=sobre&(xx>=580)                               # a la derecha: detrás hay cielo
izq=sobre&(xx<580)                                  # a la izquierda: detrás está la fachada del otro local
res=ph.copy().astype(np.float32)
# cielo: cada columna toma el color del cielo justo sobre el borde superior del polígono antiguo (a la derecha de 1030 hay árboles: se usa la columna 1015), con un leve aclarado hacia el horizonte
topOB=np.full(W,H,int)
for xcol in range(W):
    col=np.nonzero(m_ob[:,xcol])[0]
    if len(col): topOB[xcol]=col.min()
colores=np.zeros((W,3),np.float32); ysrc_c=np.zeros(W,int)
for xcol in range(W):
    src_x=min(max(xcol,525),1015); ysrc=max(topOB[min(xcol,W-1)]-4 if topOB[xcol]<H else topOB[src_x]-4,0)
    ysrc_c[xcol]=ysrc
    colores[xcol]=np.median(ph[max(ysrc-6,0):ysrc,max(src_x-4,0):src_x+5,:].reshape(-1,3),axis=0)
# se suaviza a lo ancho: así los árboles pequeños, la antena y otros objetos no dejan franjas verticales
k=121; pad=np.pad(colores,((k//2,k//2),(0,0)),mode="edge")
med=np.stack([np.median(np.lib.stride_tricks.sliding_window_view(pad[:,c],k),axis=1) for c in range(3)],1)
med=cv2.GaussianBlur(med.reshape(1,W,3),(0,0),sigmaX=25,sigmaY=0.1).reshape(W,3)
for xcol in range(580,W):
    ysrc=ysrc_c[xcol]
    filas=np.nonzero(cielo[:,xcol])[0]
    for yv in filas: res[yv,xcol]=np.clip(med[xcol]+0.10*(yv-ysrc)*np.array([1.2,0.6,0.2]),0,255)
res=np.clip(res,0,255).astype(np.uint8)
# suaviza la costura del relleno con el cielo original
borde=cv2.dilate((cielo*255).astype(np.uint8),np.ones((7,7),np.uint8))-cv2.erode((cielo*255).astype(np.uint8),np.ones((7,7),np.uint8))
res=np.where((borde>0)[...,None],cv2.GaussianBlur(res,(0,0),2.0),res)
fondo_izq=np.median(ph[:,170:255,:],axis=1).astype(np.float32)          # a la izquierda: color por fila del local vecino
res[izq]=np.clip(fondo_izq[np.nonzero(izq)[0]],0,255).astype(np.uint8)
mask_inp=cv2.dilate(((bajo)*255).astype(np.uint8),np.ones((3,3),np.uint8))
res=cv2.inpaint(res,mask_inp,6,cv2.INPAINT_TELEA)                          # restos de la base antigua bajo la fachada
m_arb=np.zeros((H,W),np.uint8)                                              # los dos arbolitos que asomaban sobre el techo antiguo se borran (su tronco estaba tras el edificio)
for (x0,y0,x1,y1) in ((790,298,832,342),(945,300,992,346)): m_arb[y0:y1,x0:x1]=255
res=cv2.inpaint(res,m_arb,5,cv2.INPAINT_TELEA)
# la fachada nueva: ajuste de luz hacia la foto (más cálida y con contraste) y sombra de contacto
rgb=rd[...,:3][...,::-1].copy()                       # RGB -> BGR, igual que la foto
rgb=np.clip(rgb*np.array([1.06,1.04,1.0])*1.04,0,255)
gradiente=np.clip(1.0-0.10*((ys-top[None,:])/np.maximum(1,bot[None,:]-top[None,:]+1)).clip(0,1),0.8,1.0)[...,None]
rgb=rgb*gradiente
sombra=cv2.GaussianBlur((opaco.astype(np.uint8)*255),(0,0),9).astype(np.float32)/255.0
M=np.float32([[1,0,-14],[0,1,12]]); sombra=cv2.warpAffine(sombra,M,(W,H))
base=res.astype(np.float32)*(1-0.42*sombra[...,None]*(1-al[...,None]))   # sombra sobre el suelo y el cielo/edificios contiguos solo bajo la línea de base
# solo sombra sobre el suelo (bajo la línea de base de la fachada)
suelo=(yy>bot[None,:]-2)&(yy<bot[None,:]+34)
base=np.where(suelo[...,None],base,res.astype(np.float32))
out=base*(1-al[...,None])+rgb*al[...,None]
out=np.clip(out,0,255).astype(np.uint8)
cv2.imwrite("/mnt/user-data/outputs/fotomontaje_santarosa.jpg",out,[cv2.IMWRITE_JPEG_QUALITY,92])
cv2.imwrite("montaje_vista.png",out)
print("listo",out.shape)
