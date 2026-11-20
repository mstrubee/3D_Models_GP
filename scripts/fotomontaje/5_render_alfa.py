"""Renderiza el modelo con una cámara dada, con fondo transparente, al tamaño de la foto.
Uso: python3 5_render_alfa.py visor.html cam_final.npy salida.png [ancho alto]
- El visor se abre con Playwright (Chromium con WebGL por software) y three r128 local (npm install three@0.128.0).
- Se inyecta window.__built y window.__scene en el visor; se ocultan muros del casco, cielos y pendientes; se crea un renderer
  propio con alpha:true (el del visor es opaco) y se renderiza la misma escena.
- cam_final.npy = [X, Y, Z, yaw, pitch, f]: X = x del plano, Z = -y del plano, Y = altura en cm; yaw 0 mira hacia el norte (-Z); f en px.
"""
import sys, math, base64, numpy as np
from playwright.sync_api import sync_playwright
html, camf, out = sys.argv[1:4]; W = int(sys.argv[4]) if len(sys.argv) > 4 else 1280; H = int(sys.argv[5]) if len(sys.argv) > 5 else 960
THREE = open('node_modules/three/build/three.min.js').read()
h = open(html, encoding='utf8').read(); a = "  const S = built.stats;"; assert h.count(a) == 1
open('/tmp/_mont.html', 'w', encoding='utf8').write(h.replace(a, "  window.__built = built; window.__scene = scene;\n" + a))
p = np.load(camf); cx, cy, cz, yaw, pit, f = [float(v) for v in p[:6]]; fovV = math.degrees(2 * math.atan((H / 2) / f))
js = """(args)=>{ const [cx,cy,cz,yaw,pit,fovV,W,H]=args, S=window.__scene, B=window.__built;
  B.shell.walls.visible=false; B.shell.ceil && (B.shell.ceil.visible=false);
  S.traverse(o=>{ if(o.userData && o.userData.pendiente) o.visible=false; });
  const bg=S.background; S.background=null; const cv=document.createElement('canvas'); cv.width=W; cv.height=H;
  const r=new THREE.WebGLRenderer({canvas:cv,alpha:true,antialias:true,preserveDrawingBuffer:true}); r.setSize(W,H,false); r.setClearColor(0x000000,0);
  const cam=new THREE.PerspectiveCamera(fovV,W/H,10,300000); cam.position.set(cx,cy,cz);
  const fw=new THREE.Vector3(Math.cos(pit)*Math.sin(yaw),Math.sin(pit),-Math.cos(pit)*Math.cos(yaw));
  cam.lookAt(new THREE.Vector3(cx,cy,cz).add(fw)); cam.updateMatrixWorld(); r.render(S,cam); const url=cv.toDataURL('image/png'); S.background=bg; return url; }"""
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--enable-webgl"])
    pg = b.new_page(viewport={"width": 1000, "height": 900}); pg.route("**/three.min.js", lambda r: r.fulfill(body=THREE, content_type="application/javascript"))
    pg.goto("file:///tmp/_mont.html"); pg.wait_for_timeout(3500)
    open(out, "wb").write(base64.b64decode(pg.evaluate(js, [cx, cy, cz, yaw, pit, fovV, W, H]).split(",")[1])); b.close()
print("render con alfa:", out)
