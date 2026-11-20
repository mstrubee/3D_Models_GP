"""Empaqueta el kit en archivos compatibles con el proyecto (sin ZIP): kit_v2_texto.txt, kit_v2_imagenes_base64.txt y desempaquetar_kit.txt.
Uso: python3 scripts/empaquetar_kit.py [carpeta_del_kit] [carpeta_de_salida]"""
import os, sys, base64
kit = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
out = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else ".")
TXT = {".py", ".js", ".json", ".md", ".sh", ".html"}; IMG = {".png", ".jpg", ".jpeg", ".npy"}
def omitir(rel, size):
    if rel.startswith("salida/") or rel.startswith("ejemplo_fotomontaje/"): return rel.startswith("salida/") or (os.path.splitext(rel)[1] in {".png", ".jpg", ".jpeg"})
    if os.path.basename(rel).startswith("tienda_") and rel.endswith(".html"): return True       # resultados grandes de ejemplo
    return size > 300_000 and not rel.startswith("datos/")
tx, im = [], []
for root, _, fs in os.walk(kit):
    for f in sorted(fs):
        p = os.path.join(root, f); rel = os.path.relpath(p, kit).replace(os.sep, "/"); ext = os.path.splitext(f)[1].lower()
        if omitir(rel, os.path.getsize(p)): continue
        if ext in TXT: tx.append((rel, open(p, encoding="utf8").read()))
        elif ext in IMG: im.append((rel, base64.b64encode(open(p, "rb").read()).decode()))
with open(os.path.join(out, "kit_v2_texto.txt"), "w", encoding="utf8") as f:
    for rel, c in sorted(tx): f.write("\n#### FILE: " + rel + " ####\n" + c.rstrip("\n") + "\n#### END ####\n")
with open(os.path.join(out, "kit_v2_imagenes_base64.txt"), "w", encoding="utf8") as f:
    for rel, c in sorted(im): f.write("\n#### IMG: " + rel + " ####\n" + "\n".join(c[i:i + 100] for i in range(0, len(c), 100)) + "\n#### END ####\n")
print("textos:", len(tx), "| imágenes y datos:", len(im))
