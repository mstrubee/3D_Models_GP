# Kit "Modelos 3D Autoplanet" (v2: Talca, Chillán Vivo, Santa Rosa y fotomontaje)

Convierte la planta (DXF), las elevaciones de fachada (PDF) y el plano eléctrico (PDF) de una tienda en un visor 3D
de un solo archivo HTML, con vuelo tipo dron, recorrido exportable en video, cielos configurables y modo Noche.

## Contenido
- `biblioteca/`: 10 componentes paramétricos con su visor (racks HP, racks de pallets, perimetrales RV/RN, góndolas, mesones, racks de baterías con cenefa, racks de neumáticos, cabeceras HP, jaulas, bodega RESPEL). Cada archivo trae su bloque de construcción entre `/*BUILD_START*/` y `/*BUILD_END*/`.
- `scripts/`: `extract.py` y `extract_final.py` (leen el DXF y dejan `data.json`), `extraer_luces_pdf.py` (luminarias del PDF eléctrico), `extraer_letrero_pdf.py` (letrero limpio desde la elevación), `cortar_franja.py` (cuerpo y punta curva de la franja para la pintura de los muros), `make_html.py` (arma el visor), `viewer.py` (visor de un componente), `probar_pagina.js` (prueba la página con jsdom y three r128), `capturas.py` (renderiza la página con Chromium y guarda capturas).
- `ejemplo_talca/`: datos de entrada y resultado de Talca (v39, la vigente), para comparar.
- `instrucciones_del_proyecto.md` (reglas 1 a 40, errores a evitar y preguntas abiertas) y `parametros_del_proyecto.md` (todos los valores): leerlos al empezar cada chat.
- `scripts/fotomontaje/` y `ejemplo_fotomontaje/`: fotomontaje de una tienda sobre la foto del lugar (ver su LEEME).
- `instalar.sh`: instala las librerías al empezar un chat.

## Flujo para una tienda nueva
1. `bash instalar.sh`
2. `PLANO_DXF=planta.dxf python3 scripts/extract_final.py` deja `data.json` (contorno, racks, perimetrales, góndolas, mesones, baterías, volúmenes pendientes).
3. `python3 scripts/extraer_luces_pdf.py electrico.pdf <escala> <x0> <y0>` deja `datos/luces.json`. La escala y el origen se calibran con el contorno del local.
4. `python3 scripts/extraer_letrero_pdf.py elevaciones.pdf x0 y0 x1 y1 datos/sign_sur.png` (una vez por fachada con letrero) y `python3 scripts/cortar_franja.py datos/sign_ori.png` para la pintura interior.
5. `python3 scripts/make_html.py` deja `salida/tienda.html`.
6. Verificar siempre: superponer las huellas del modelo sobre el plano, probar la página con `node scripts/probar_pagina.js` y mirar capturas reales con `python3 scripts/capturas.py` (Chromium de Playwright con WebGL por software; hay que tener three r128 local con `npm install three@0.128.0`).

## Qué es reutilizable y qué es propio de Talca
| Parte | Estado |
|---|---|
| Componentes de la biblioteca y sus medidas confirmadas | Reutilizable |
| Lectura de racks, perimetrales, góndolas, mesones y racks de baterías desde el DXF | Reutilizable si el plano sigue la plantilla de Autoplanet (bloques RA30/RA60/RV1/RV2/RN y rótulos "Mesón Atención", "Gondola Negra", etc.) |
| Luminarias desde el PDF eléctrico | Reutilizable si usa los mismos símbolos y colores (L01, L02, L03, L06); la calibración del plano es manual |
| Visor: vuelo, recorrido en video, cielos, Noche | Reutilizable |
| Fachada | **Propia de Talca**: las medidas de paños, puertas, vitrinas, pilastras y rejillas están escritas a mano en `buildFacade3D` |
| Baños, cocina y lockers | **Propios de Talca**: coordenadas escritas a mano en `buildServicios` |
| Mueble Admin | **Propio de Talca**: coordenadas escritas a mano en `buildAdmin` |
| Límite de alturas (x = 16372), ejes estructurales y cerchas | **Propios de Talca** (constantes `XB` y listas de ejes) |

## Lo que falta para que solo haya que subir planta y fachadas
1. Una segunda tienda para calibrar: hasta no verla funcionar sobre otro plano, no se puede asegurar que la lectura sea general.
2. Automatizar la fachada: clasificar las zonas de color de la elevación (gris claro = banda baja, rojo = puertas, gris oscuro = vidrio o revestimiento) y las juntas; ya se vio que el PDF lo permite, pero falta escribirlo.
3. Automatizar baños, cocina y Admin con reglas por rótulo ("ADMIN.", "Lockers", "Lavamopa", etc.).
4. Una ficha técnica estándar de los componentes (alturas de repisas, número de niveles, espesores), para reemplazar mis estimaciones.

## Convenciones
- Unidades en cm; el DXF de Talca declara milímetros pero está en centímetros: comprobar siempre con el área del contorno.
- Plano (x, y) a mundo: X = x − x0, Z = −(y − y0), Y = altura.
- En los bloques reflejados usar coordenadas del mundo (`vertices_in_wcs`), no las locales del objeto.


## Segunda tienda: Chillán Vivo (desde PDF)
- `scripts/extraer_planta_pdf.py planta.pdf salida.json`: lee una planta en PDF vectorial a 1:50, verifica la escala con los racks de pallets (220 × 120 cm) y reconoce cada componente por sus medidas (rectángulos de cualquier ángulo, sin anidados). Une en módulos dobles las hileras de góndola de 125 × 40 separadas ~50 cm.
- `ejemplo_chillan/`: datos leídos, letrero recortado de la elevación, imagen de control con lo detectado sobre el plano y el borrador del visor. `generador_chillan_referencia.py` muestra qué se cambió del visor de Talca (origen, alturas, fachada propia, una sola zona).
- Control obligatorio: dibujar lo detectado sobre el plano (overlay.png) y revisarlo antes de modelar.
- Lo que sigue pendiente para generalizar: límite y alturas bodega/sala, frente de racks y góndolas, plano eléctrico y los círculos grandes del plano.
- Lección de Chillán: el extractor solo reconoce solo rectángulos cerrados y de tamaño conocido. Los mesones P.O.S. (250 × 90), el de accesorios (175 × 90) y el mueble de administración (60 × 373 con su tabique de 12 cm) llevan etiqueta o son contornos de varios trazos, y quedaban como volúmenes ámbar o se omitían. Si algo que debería verse queda ámbar o falta, revisar primero cómo está clasificado en data.json.
- Plano eléctrico de Chillán: `scripts/extraer_luces_pdf_v2.py electrico.pdf datos_local.json luces.json` lee los lineales L02 (relleno o solo contorno, a cualquier ángulo) y los focos embutidos F01 (círculos magenta). El plano eléctrico venía a 0,9427 de la escala del de arquitectura (1,871 cm/pt); se calibró alineando sus muros con los de arquitectura (error de unos 5 cm). El altillo se dibuja aparte y se ubica por su esquina noreste. Cada luminaria puede traer su altura (`h`).

## Tercera tienda: Santa Rosa (desde PDF, con fachadas según zonas marcadas)
- Un solo PDF con la planta de arquitectura. El extractor admite un contorno irregular (`extraer_planta_pdf.py planta.pdf salida.json x_izq y_sur x_der y_norte poligono_pt.json`); aquí el contorno se leyó de los muros y de la línea de concesión (345 m² por dentro; el plano declara 357 m²).
- El plano trae sus propios totales (38 cuerpos de góndola, 5 P.O.S., 57 + 11 repisas HP, altura interior de 3,22 m): se usaron para verificar la lectura y para fijar la altura.
- `ejemplo_santarosa/`: datos leídos, imagen de control (`santarosa_lectura_del_plano.png`) y el visor.
- Fachadas de Santa Rosa: sin elevación, el usuario marcó sobre capturas del plano el vidrio (azul), la puerta de carga (rojo), los letreros (amarillo) y el muro medianero (verde). Se calibró cada captura contra el PDF (correlación, escala 0,5 px/pt) y se proyectó cada marca sobre su lado del contorno. Altura interior usada: 3,33 m (indicada por el usuario; el plano rotula 3,22 m).

## Fotomontaje (Santa Rosa)
- Ver `scripts/fotomontaje/LEEME.md`. Entradas: foto del lugar y captura del visor con la posición de cámara deseada. El resultado de Santa Rosa está en `ejemplo_fotomontaje/` con la foto original, el render con alfa y las cámaras ajustadas.
- Fachada sin elevación: `DATA.fachadas` (lista de lados con x0, y0, x1, y1, L, logoU, glass, door, cargo) se genera en `ejemplo_santarosa/generador_santarosa_referencia.py` con `_fac(i0, i1, ancla, ...)`; la función `buildFacade3D` del visor las dibuja.
- Recorte de muebles contra el contorno: bloque del mueble de administración en el mismo generador.

## Versiones
- v1: Talca. v2 (20-nov-2026): Chillán, Santa Rosa, fachadas por zonas marcadas, recorte de muebles, fotomontaje, parámetros consolidados.

## Modo "solo el plano" y datos faltantes
- Con solo la planta, la fachada usa `D["facp"]` (altura de fachada, panel del letrero, cornisa, vidrio, puerta de carga) en el generador; ver reglas 41 y 42 de las instrucciones.
- `instrucciones_para_pegar_en_el_proyecto.md` es el texto completo para el cuadro de instrucciones del proyecto (regla 43).

## Dónde vive el kit (versión 2.1)
- Repositorio público: https://github.com/mstrubee/3D_Models_GP. Al empezar un chat: `git clone --depth 1 https://github.com/mstrubee/3D_Models_GP /home/claude/kit` y luego `bash /home/claude/kit/instalar.sh`.
- En "Contexto" del proyecto solo queda `parametros_del_proyecto.md` (valores y preguntas abiertas); las reglas completas están en el cuadro de instrucciones y en `instrucciones_del_proyecto.md` de este repo.
- Claude no puede subir cambios al repo: entrega los archivos y los comandos `git add . && git commit -m "..." && git push`.
- Respaldo sin GitHub: el ZIP completo del kit, o `scripts/empaquetar_kit.py` (deja el kit en archivos de texto y un desempaquetador). El repo no incluye los resultados grandes de ejemplo (tienda_*.html, fotos y capturas); se regeneran con los scripts.

## Versiones
- v1: Talca. v2 (20-nov-2026): Chillán, Santa Rosa, fachadas por zonas marcadas, recorte de muebles, fotomontaje, parámetros consolidados. v2.1 (20-nov-2026): el kit pasa a GitHub, regla 44, preguntas abiertas en parametros_del_proyecto.md.

