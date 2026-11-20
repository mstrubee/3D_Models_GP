"""Redibuja solo los trazos RELLENOS de una región de la elevación (PDF vectorial), sin rectángulos ni líneas del dibujo.
Uso: python3 extraer_letrero_pdf.py elevaciones.pdf x0 y0 x1 y1 salida.png
Las coordenadas están en puntos del PDF. Incluye todo trazo que cruce la región (no solo los que quedan dentro)."""
import sys, fitz
pdf, (x0, y0, x1, y1), out = sys.argv[1], [float(v) for v in sys.argv[2:6]], sys.argv[6]
page = fitz.open(pdf)[0]; nd = fitz.open(); np_ = nd.new_page(width=page.rect.width, height=page.rect.height); sh = np_.new_shape(); n = 0
for d in page.get_drawings():
    r = d['rect']
    if d.get('fill') is None or r.width > 500 or not (r.x1 > x0 and r.x0 < x1 and r.y1 > y0 and r.y0 < y1): continue
    for it in d['items']:
        k = it[0]
        if k == 'l': sh.draw_line(it[1], it[2])
        elif k == 'c': sh.draw_bezier(it[1], it[2], it[3], it[4])
        elif k == 're': sh.draw_rect(it[1])
        elif k == 'qu': sh.draw_quad(it[1])
    sh.finish(fill=d['fill'], color=None, fill_opacity=d.get('fill_opacity', 1) or 1, even_odd=d.get('even_odd', False), closePath=d.get('closePath', True)); n += 1
sh.commit(); np_.get_pixmap(clip=fitz.Rect(x0, y0, x1, y1), dpi=300, alpha=True).save(out); print(out, n, 'trazados')
