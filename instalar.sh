#!/bin/bash
# Instala lo necesario al comenzar un chat nuevo del proyecto (tarda unos segundos).
# Livianas: ezdxf, trimesh, shapely, pymupdf. No se instala cadquery (trae un motor CAD completo): solo si una pieza con curvas complejas lo exige.
pip install ezdxf trimesh shapely pymupdf pdfplumber pillow scipy numpy matplotlib opencv-python-headless playwright --break-system-packages -q
# Chromium para capturas y fotomontajes (solo si falta)
python3 - <<'PY' || playwright install chromium
from playwright.sync_api import sync_playwright
with sync_playwright() as p: p.chromium.launch().close()
PY
npm install three@0.128.0 jsdom   # para probar la página y renderizar (three r128 local)
echo "Listo: ezdxf, trimesh, shapely, pymupdf, pdfplumber, pillow, scipy, numpy, matplotlib, opencv, playwright, three r128"
