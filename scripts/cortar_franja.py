"""Corta, desde el letrero extraído (sign_ori.png), el cuerpo y la punta curva de la franja roja y naranja,
para usarlos en la pintura interior de los muros. Uso: python3 cortar_franja.py datos/sign_ori.png"""
import sys, json
import numpy as np
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGBA'); W, H = im.size; al = np.array(im)[..., 3] > 128
left = al[:, :int(W * 0.26)]                       # swoosh izquierdo, antes del logo
cols = np.where(left.any(axis=0))[0]; x0, x1 = cols.min(), cols.max()
rows = np.where(left.any(axis=1))[0]; y0, y1 = rows.min(), rows.max()
top = [np.where(left[:, x])[0].min() for x in range(x0, x1 + 1)]
xt = next(i for i, t in enumerate(top) if t > top[10] + 2)    # donde el borde superior empieza a curvarse
im.crop((x0 + 10, y0, x0 + 40, y1 + 1)).save('datos/sw_body.png'); im.crop((x0 + xt - 4, y0, x1 + 1, y1 + 1)).save('datos/sw_tip.png')
print(json.dumps({'alto_px': int(y1 - y0 + 1), 'punta_px': int(x1 - x0 - xt + 6)}))
