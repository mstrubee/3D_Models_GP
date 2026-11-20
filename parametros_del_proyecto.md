# Parámetros del Proyecto "Modelos 3D Autoplan" (versión 2, 20-nov-2026)

Todos los valores que usan los modelos y el visor. Origen: [plano] viene del plano, [usuario] lo dijo Matias, [supuesto] lo asumí y va en el panel "Supuestos por validar".

## Sistema de coordenadas y escalas
- Unidades: cm. El DXF de Talca declara mm pero está en cm: verificar con el área del contorno.
- Plano (x, y) al visor: X = x − x0, Z = −(y − y0), Y = altura. El norte del plano es −Z. Giro de un eje del plano con ángulo θ: el frente (+z local) apunta a (sin θ, −cos θ).
- PDF vectorial a 1:50: 1 pt = 1,7638888 cm. Chillán: el plano eléctrico venía a 0,9427 de la escala de arquitectura (1,871 cm/pt), calibrado con los muros (error ~5 cm).
- Verificar la escala con piezas de medida conocida (racks de pallets 220 × 120) y con los totales que declara el plano.
- Capturas del usuario sobre el plano: se calibran contra el PDF por correlación (Santa Rosa: 0,5 px/pt, el recorte parte en (172, 14) pt, correlación 0,89).

## Alturas y cielos
- Talca: sala 7,80 m, bodega 3,87 m, límite de alturas x = 16372 [supuesto], huella 402 m² (bodega 253 m², sala 150 m²).
- Chillán: galpón 10,97 m (medido en la elevación); altura de bodega y sala no dada: una sola zona [supuesto].
- Santa Rosa: interior 3,33 m [usuario] (el plano rotula 3,22 m); altura de muros del modelo = 333 (sala) y 332 (bodega).
- Altillo: tope de losa 2,60 m cuando el plano no da la altura [usuario]; losa de 20 cm, sin pilares [supuesto].
- Tabiques de baños y cocina: 2,4 m [supuesto]; tabique del mueble de administración 12 cm; espesor de muros del visor 12 cm.
- Cielo por defecto: luz más alta de la zona + 10 cm (Talca/Chillán: 4,10 m en sala; Santa Rosa: sin datos de luces, luces supuestas 40 cm bajo el interior, cielo a 303 cm). Opciones: sin cielo, americano blanco, americano negro, pintura negra con estructura; sala y bodega por separado.
- Muros negros: desde 10 cm sobre la luz más alta de la zona; con americano negro o pintura negra se activan solos; casilla Negros; altura mínima de la barra 300 cm (150 cm en Santa Rosa); en bodega solo desde 10 cm sobre las luces.
- El cielo marca el final: muebles que lo pasan se cortan 10 cm bajo el cielo; luminarias sobre el cielo se fijan a su cara inferior; tirantes terminan bajo el cielo (sin cielo, al tope del muro).

## Luces
- Haz de 100° a plena luz con caída suave hasta 140° [100° lo dijo el usuario; 140° supuesto]; SpotLight dirigido hacia abajo; el cielo no se ilumina; modo Noche con 3 niveles; muestreo de focos para el rendimiento.
- L02 lineal de 120 cm a 4,00 m (dato del cliente para Talca; estándar en Chillán). F01 foco embutido de 22 W: 4,0 m en sala, 2,4 m en baños y cocina, 5,0 m en altillo [supuesto]. Posiciones del plano eléctrico ±5 cm. Cada luminaria puede traer su altura h.
- Santa Rosa: sin plano eléctrico, sin luminarias y Noche a oscuras.

## Visor
- Fachada transparente: opacidad 22 % por defecto, incluye el revestimiento interior; el vidrio no cambia. Vidrio siempre transparente, sin reflejo ni metalicidad.
- Navegación: rueda y pellizco avanzan hacia el punto bajo el cursor o los dedos hasta 25 cm de cualquier objeto (vidrio y luminarias no cuentan); dos dedos o botón derecho / Shift desplazan; un dedo gira; la cámara baja hasta 25 cm del suelo; casilla "Acercarse hacia el cursor o los dedos" (activada por defecto). Ojos sala y Ojos bodega a 1,65 m.
- Vistas: Planta, Aérea, Fachada, Sala, Bodega, Ojos sala, Ojos bodega; modo Vuelo (W/A/S/D, Q/E, joystick, ▲▼).
- Recorrido en video (puntos, trayectoria suave, MediaRecorder), vistas guardadas con nombre, imágenes JPEG en almacenamiento local, exportación del HTML con vistas, imágenes, videos y recorrido; reabre con paneles cerrados.

## Componentes (cm)
- Vocabulario [usuario]: cabecera de repisas HP = unidad negra alta junto a las repisas HP, 3 m de alto; góndolas y cabeceras de góndola 1,5 m; perimetrales 2,4 m según el plano.
- Repisas HP: 30 y 60 cm de fondo. Perimetrales: RV1 122 × 50, RV2 122 × 70, RV3 122 × 40,6, RN, RH (miran al centro).
- Góndolas: hileras de 125 × 40 separadas ~50 cm se unen en módulos dobles; inclinadas 12° en Chillán y 11,7° en Santa Rosa. Cabeceras de góndola 45 × 95 × 150 con repisas hacia el pasillo (labio, base + 3), respaldo perforado contra la isla y rejilla en los costados. Cabeceras HP 65 × 30 × 300 como volúmenes.
- Islas de ofertas ~90 cm de alto; tamaño del plano (70 × 70, 100 × 120); rack de cajas 100 × 190.
- Racks de pallets 220 × 120; racks de neumáticos 190 × 60 (rótulo 190 × 70 en Chillán) y 240 × 60 (Santa Rosa); RESPEL 300 × 160; rack de baterías de 3 cuerpos con cenefa "Conoce tu batería" (un tercio de la imagen por cuerpo).
- P.O.S.: módulos de 124 y accesorio de 175 (mesón P.O.S. de 250 × 90 en Chillán), atienden hacia la góndola más cercana.
- Mueble de administración: 60 de fondo (z de 0 a 60, borde de 62,5) × 373 de largo, caja fuerte 60 × 50 × 55 en el extremo lejano al pasillo, rack y monitor CCTV; el largo se recorta contra el interior (Santa Rosa: 349). Origen corrido 30 cm en z.
- Baños y cocina: WC, lavamanos, refrigerador, lavaplatos, microondas, máquina de agua, mesa con 4 sillas, TV, lockers (4 × 2 en Chillán, 2 × 2 en Santa Rosa), lavamopa.

## Fachada sobre lados abiertos (Santa Rosa)
- Altura del muro = altura interior; cornisa 30 cm; respaldo interior 8 cm y revestimiento exterior 4 cm; límite de muebles 9 cm hacia adentro.
- Panel de letrero blanco de 90 cm (de 243 a 333 cm de alto); franjas de 80 cm (de 248 a 328) con puntas de 141 cm; logo 232 cm de ancho (relación 4,65) centrado, 152 cm libres a cada lado.
- Zona vidriada: 240 cm de alto, marcos rojos de 8 cm de fondo, módulos de ~115 cm, montantes de 5 cm, travesaño a 105–111 cm; puertas dobles de 183 cm con travesaño a 205 cm y paño superior; tiradores de acero.
- Puerta de carga roja: 207 cm de ancho × 250 de alto, marco de 4 cm, nervios horizontales cada 42 cm, manilla de acero.
- Santa Rosa, medidas: este 616 cm (logo en 308); chaflán 245 cm (solo franjas); sur 1539 cm (vidrio de 0 a 675 desde la esquina oeste, puertas de 329 a 512, logo en 420); oeste 1521 cm (puerta de carga de 240 a 447 desde el extremo sur, logo en 760). El lado sur del bloque de bodegas es medianero (muro).
- Parámetros FACP (modo solo plano, los define Matias; si no, valen estos): hf = altura interior (altura total del muro), cornisa 30, panelH 90 (alto del panel del letrero bajo el tope del muro), glassH 240, cargoH 250. La franja mide 8/9 del panel (80 cm con 90) y la punta, el logo y el hueco del logo escalan con ella. Probado con hf 400, cornisa 20, panelH 130, glassH 260, cargoH 270.
- Sin fachada (DATA.open): sin muro, pintura ni colisión en esos lados y botones de fachada ocultos.

## Santa Rosa (plano vC 23.10.2026, 1:50)
- 357 m² declarados, 345 m² leídos por dentro; 38 cuerpos de góndola (19 islas dobles, 5 pasillos inclinados 11,7°), 5 P.O.S. más mesón accesible, 70 repisas HP leídas (60 de 30 y 10 de 60; el plano dice 57 y 11), 23 perimetrales, 10 cabeceras, 6 islas de ofertas, 4 racks de neumáticos, 1 rack de baterías, 2 racks de pallets, RESPEL, mueble de administración (recortado), baños y cocina. Contorno irregular de 8 vértices; lados abiertos [2, 3, 4, 5].
## Chillán Vivo (plano 06 vI 15.04.2026, 1:50)
- ~1771 × 2352 cm; 75 repisas HP, 24 perimetrales, 25 cuerpos de góndola en 5 islas inclinadas 12°, 3 racks de baterías, 3 racks de pallets, 9 de neumáticos, 19 cabeceras, 10 cabeceras HP, 6 islas de ofertas, altillo en L con 15 racks HP, 2 baños y cocina, 6 módulos P.O.S. y accesorio, mueble de administración, 151 + 4 luminarias L02 y 163 + 4 focos F01, fachada sur con paneles ACM, vitrinas C02/C01, acceso de 191 cm.

## Fotomontaje (Santa Rosa)
- Cámara del render del usuario (ancho 1021 px): plano (4866, −120), altura 104 cm, yaw −65,2°, pitch 1,2°, f 1331 px (apertura horizontal 42°); error 4,1 px.
- Cámara del montaje (1280 × 960): plano (4789, −128), altura 189 cm, yaw −63,7°, pitch 1,0°, f 1592 px (horizontal 43,8°, vertical 33,6°). Puntos de alineación en la foto: esquina cóncava A en (530, 566), esquina convexa E3 en (785, 625), extremo este en x = 1195.
- Edificio antiguo: polígono (262,376) (520,396) (522,390) (600,364) (780,331) (1197,357) (1197,622) (1050,645) (785,634) (530,578) (262,568).
- Relleno: cielo por columna (mediana de 121 columnas, suavizado σ 25, +0,10 por píxel hacia abajo); vecino por filas con columnas 170–255; luz de la fachada ×(1,06, 1,04, 1,0) × 1,04 y gradiente de 10 %; sombra de contacto desplazada (−14, +12), desenfoque 9, 42 %.

## Estilo y entrega
- Español, respuestas cortas para pantalla de teléfono, sin preámbulos, sin viñetas al rechazar algo. Cada entrega: el archivo presentado, lo verificado, lo supuesto y una sola pregunta.
- Datos mínimos por tienda nueva: planta DXF o PDF, elevaciones PDF, plano eléctrico PDF, alturas interiores de bodega y sala, altura del cielo de la sala, límite entre ambas alturas y fotos de las piezas que no estén en la biblioteca.
