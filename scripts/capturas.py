import sys, json
from playwright.sync_api import sync_playwright
import os
THREE=open(os.environ.get('THREE_JS','node_modules/three/build/three.min.js')).read()   # three r128 local (npm install three@0.128.0)
def run(html, steps, w=1000, h=640):
    errs=[]
    with sync_playwright() as p:
        b=p.chromium.launch(args=["--use-gl=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist","--enable-webgl"])
        pg=b.new_page(viewport={"width":w,"height":h})
        pg.route("**/three.min.js", lambda r: r.fulfill(body=THREE, content_type="application/javascript"))
        pg.on("pageerror", lambda e: errs.append("pageerror: "+str(e)[:200])); pg.on("console", lambda m: errs.append("console."+m.type+": "+m.text[:200]) if m.type in ("error",) else None)
        pg.goto("file://"+html); pg.wait_for_timeout(2500)
        for s in steps:
            k=s[0]
            if k=="select": pg.select_option(s[1],s[2]); pg.wait_for_timeout(300)
            elif k=="click": pg.click(s[1]); pg.wait_for_timeout(300)
            elif k=="eval": pg.evaluate(s[1]); pg.wait_for_timeout(300)
            elif k=="wait": pg.wait_for_timeout(s[1])
            elif k=="shot": pg.screenshot(path=s[1]); print("captura:",s[1])
        b.close()
    print("errores:",errs if errs else "ninguno")
if __name__=="__main__":
    # Ejemplo: abre la tienda, elige cielo negro en la sala y captura la vista interior
    run(os.path.abspath("salida/tienda.html"),[("eval","document.getElementById('cielos').open=true"),("select","#cSalaMode","ab"),("click",'[data-view="ojosSala"]'),("eval","window.scrollTo(0,0)"),("wait",600),("shot","captura_interior.png")],w=1000,h=900)
