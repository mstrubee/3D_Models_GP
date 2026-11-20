# Instrucciones del Proyecto "Modelos 3D Autoplan" (versión 2, 20-nov-2026)

Estas instrucciones reemplazan a las anteriores y las contienen completas. Regla de mantenimiento: las instrucciones solo se agregan o se precisan; nada se borra. Los números y valores están en parametros_del_proyecto.md.

Objetivo: generar modelos 3D precisos y rápidos de tiendas Autoplanet en diseño, a partir de la planta (DXF), las
elevaciones de fachada (PDF) y el plano eléctrico (PDF), con la biblioteca y los scripts de este proyecto.

Al empezar cada chat: leer LEEME.md, parametros_del_proyecto.md y estas instrucciones; si el kit no está en /home/claude/kit, reconstruirlo con `python3 /mnt/project/desempaquetar_kit.txt` (el proyecto no acepta ZIP: el kit está en kit_v2_texto.txt y kit_v2_imagenes_base64.txt); ejecutar instalar.sh y trabajar con los scripts del proyecto.

Reglas de trabajo
1. Unidades en cm. Verificar la escala del DXF con el área del contorno antes de usar cualquier medida.
2. Todo dato que no venga del plano ni de lo que diga Matias es un supuesto: se marca como tal en el panel del visor ("Supuestos por validar") y se avisa en la respuesta.
3. Verificar siempre con una superposición de las huellas del modelo sobre el plano, probar la página con probar_pagina.js y mirar capturas reales con capturas.py antes de entregar. Mirar las capturas habría evitado errores como un cielo que no se veía desde adentro por el encuadre de la cámara.
4. No inventar componentes: si falta una pieza, usar un volumen ámbar "pendiente" y pedir el dato.
5. Corregir de inmediato cuando un dato nuevo contradiga un supuesto anterior, y decirlo.
6. Los vidrios siempre son transparentes: al agregar muros, pinturas o piezas, comprobar con una captura que nada opaco tape un vano de vidrio. El material de vidrio no lleva reflejo de cielo ni metalicidad: con reflejo, los paños vacíos se ven como superficie sólida.
7. Los cielos de la sala y de la bodega se configuran por separado: el usuario puede dejarlos iguales, pero es una decisión suya.
8. Muros negros por zona: se pintan de negro desde 10 cm sobre la luz más alta de esa zona (se calcula de los datos de luces; hoy 4,10 m en sala y bodega), regulable con la barra Muros. Se activan solos con cielo de pintura negra o americano negro, y el usuario puede activarlos o quitarlos con la casilla Negros, también sin cielo (llegan a la altura del muro). Si el negro parte sobre el muro, el tramo intermedio queda sin pintar.
9. La luz de las luminarias apunta solo hacia abajo: haz de 100° a plena luz con caída suave más allá (hasta 140°), nunca hacia el techo. Se usan focos dirigidos (SpotLight), no puntuales, y de noche el cielo no se ve iluminado.
10. Las franjas roja y naranja de los muros interiores terminan con curvas (forma tomada del letrero).
11. El gabinete alto del mueble Admin va en el extremo más lejano al pasillo (en Talca, el sur).
12. Baños y cocina siempre deben estar en el modelo cuando estén dibujados en el plano: tabiques, puertas, artefactos, lockers y lavamopa, ubicados con las líneas y símbolos del plano.
13. Si el plano muestra un altillo, siempre se modela: losa con su forma, racks, baranda y escalerilla del plano. Si el plano no da la altura, el estándar es 2,60 m para la cara superior de la losa (confirmado por el usuario).
14. Los mesones siempre atienden hacia las góndolas: el lado del cliente mira hacia la góndola más cercana (se calcula, no se fija).
15. Los tirantes de las luminarias terminan debajo del cielo, en caso de existir (en la cara inferior del cielo o de la estructura); sin cielo llegan al tope del muro. Verificado midiendo la altura final de cada tirante.
16. El cielo marca el final, si existe: ninguna luminaria ni mueble llega más alto. Los muebles que lo sobrepasarían se cortan 10 cm bajo el término del cielo (corte en el shader, con altura por zona); las luminarias que quedarían sobre el cielo se fijan a su cara inferior y el resto no se toca. Las luminarias van sueltas (no mezcladas) para poder moverlas. Verificado midiendo la altura de cada luminaria con cielos bajos.
17. Al editar el generador de otra tienda, cuidar que el texto del núcleo siga siendo literal (r''') después de insertar valores; si no, los saltos de línea de los shaders se rompen.
18. Fachadas: todas las que muestren los planos se pueden dejar semitransparentes con el botón "Fachada transp." (incluye el revestimiento interior de sus muros; el vidrio no cambia) para ver el interior desde afuera.
19. Isla de ofertas: unos 90 cm de alto y el tamaño del plano; mueble amarillo "Súper precios" con dos paneles con logo y dos caras abiertas con repisas (foto de referencia).
20. Cabeceras de góndola: las repisas (con labio, como la góndola: base + 3) miran siempre hacia el pasillo; el respaldo perforado queda contra el extremo de la isla y los costados llevan rejilla, como en las fotos de referencia. Sin productos por ahora, con las medidas y posiciones específicas del plano.
21. Imágenes: el visor guarda capturas en el almacenamiento local del navegador (galería con descarga y borrado).
22. Exportación: el HTML se exporta con las vistas guardadas (además de las predeterminadas), las imágenes, el recorrido y los videos generados, y se reabre con todo restaurado; siempre con los paneles cerrados y los botones en su estado inicial.
23. Cenefa del rack de baterías: la gráfica "Conoce tu batería" (datos/cenefa_baterias.jpg, tomada de una foto con la perspectiva corregida) es estándar para 3 cuerpos: un tercio de la imagen por cada cuerpo.
24. Navegación en la vista exterior: la rueda y el pellizco no son un zoom, la cámara avanza de verdad hacia el punto bajo el cursor o entre los dedos, sin tope de distancia, y se detiene a 25 cm de cualquier mueble, de la fachada, del altillo, de un muro o del suelo (el vidrio no cuenta; las luminarias tampoco). Dos dedos (o botón derecho / Shift con el mouse) desplazan la vista paralela a la pantalla, incluso hacia abajo; un dedo gira, y la cámara puede bajar hasta 25 cm del suelo. El centro de giro queda a la profundidad del punto al que se avanza. La casilla "Acercarse hacia el cursor o los dedos" permite avanzar hacia el centro de la pantalla. Verificado midiendo la distancia a los objetos.
25. Lados abiertos del contorno (DATA.open): no llevan muro del visor; si el plano no trae elevación, la fachada se arma sobre esos lados con las zonas que marque el usuario sobre el plano (vidrio con marcos rojos y puertas dobles del acceso, puerta de carga, letreros). Cada fachada lleva su letrero con franjas de extremos curvos y el logo; el letrero del acceso principal va sobre las puertas. Los muros medianeros (zona verde) son muro, no fachada. El lado exterior de cada fachada se decide con un punto de prueba fuera del polígono (el centroide falla en locales en L). Las zonas marcadas en imágenes se ubican calibrando la imagen contra el PDF por correlación (ejemplo_santarosa/calib.json). El contorno puede ser irregular y los totales del plano se usan para verificar la lectura.
26. Mesones inclinados: el eje largo y el lado del cliente se calculan con el ángulo del plano y la góndola más cercana.
27. Ningún mueble sale del local: el contorno interior (con 9 cm de respaldo de fachada) es el límite. Si algún mueble del plano lo atraviesa, se recorta contra él (en Santa Rosa, el mueble de administración perdió 24 cm en su extremo sur); se revisa con los rectángulos de cada componente contra el polígono.
28. Cada entrega: el HTML presentado, lo verificado, lo supuesto y una sola pregunta.

Reglas agregadas en la versión 2 (Santa Rosa, fachadas por zonas marcadas, recorte de muebles, fotomontaje, modo solo plano e información faltante)
29. Altura interior: si el usuario indica una altura distinta de la que rotula el plano, se usa la del usuario, se avisa del conflicto y se pregunta cuál es la correcta (Santa Rosa: el usuario dijo 3,33 m y el plano rotula 3,22 m; quedó 3,33 m y la pregunta sigue abierta).
30. Lo que el usuario marque con colores sobre capturas del plano manda sobre cualquier supuesto. Se separan las marcas por color (azul, rojo, amarillo, verde), se calibra cada captura contra el PDF (correlación con cv2.matchTemplate; Santa Rosa: 0,5 px/pt, correlación 0,89) y se proyecta cada marca sobre su lado del contorno, midiendo de qué largo cubre. Se verifica que las zonas calcen con lo que el plano muestra (el vidrio coincidió con las puertas del acceso; el amarillo cubrió el 100 % de los lados abiertos).
31. Fachada armada sobre los lados abiertos cuando no hay elevación: muro revestido con respaldo, cornisa, panel de letrero con franjas de extremos curvos y logo, zona vidriada con marcos rojos y puertas dobles del acceso, y puerta metálica roja de carga, según las zonas marcadas. Cada lado se orienta con su eje u y la normal hacia afuera (+z local).
32. El lado exterior de cada fachada se decide probando un punto 30 cm hacia el lado de la normal: si cae dentro del polígono del local, se invierte. No usar el centroide: en locales en L falla (la fachada oeste de Santa Rosa salió mirando hacia adentro).
33. Las zonas se miden desde un extremo ancla (por ejemplo la esquina oeste) y se convierten una sola vez al sentido real del lado. Convertir dos veces las dejó espejadas en la puerta de carga.
34. Un letrero "Autoplanet" por fachada; el del acceso principal va centrado sobre las puertas dobles. El chaflán lleva solo franjas, sin logo. El logo mide 232 cm de ancho con 152 cm libres a cada lado antes de las puntas curvas.
35. Los muros medianeros (lado que deslinda con otro local) son muro, no fachada, y no llevan letrero ni vidrio.
36. Ningún mueble sale del local ni de la fachada: el límite es el contorno interior con 9 cm de respaldo. Antes de entregar se revisan los rectángulos de cada componente contra el polígono; lo que sobresale se recorta por el extremo que sobresale (mueble de administración de Santa Rosa: 24 cm por el sur, largo final 349 cm; la caja fuerte queda en el nuevo extremo y las puertas se reparten sobre el nuevo largo).
37. El mueble de administración ocupa de 0 a 60 cm hacia su frente: su origen se corre 30 cm para que el eje medido en el plano sea su línea media.
38. Fotomontaje: se hace con la foto y la posición de cámara de la captura que adjunte el usuario. Pasos en scripts/fotomontaje/LEEME.md: recuperar la cámara de la captura, afinarla a la foto con las esquinas, renderizar con fondo transparente, limpiar el edificio existente (cielo, vecino, base), componer con luz y sombra. Es aproximado y siempre se dice así.
39. En un fotomontaje se avisa qué queda tapado o cambiado de la foto (Santa Rosa: la fachada oeste cubre la tienda Starken de la izquierda) y se ofrece la alternativa.
40. Cada vez que se agregue o cambie una regla o un parámetro se actualiza el kit (instrucciones, parámetros, LEEME, ejemplos) y la memoria del proyecto, y se empaqueta de nuevo con un número de versión; no se borran versiones antiguas de los modelos sin que el usuario lo pida.

41. Modo "solo el plano": se puede partir con solo la planta (DXF o PDF). Si no hay elevación, la fachada se arma sobre los lados abiertos con las alturas que defina Matias: altura de la fachada (por defecto la altura interior), alto del panel del letrero (90 cm por defecto, bajo el tope del muro), cornisa (30 cm), altura del vidrio (240 cm) y de la puerta de carga (250 cm). Esos valores son los parámetros FACP del generador (hf, panelH, cornisa, glassH, cargoH); la franja, el logo y las puntas escalan con el panel. Sin esos datos se usan los valores por defecto y se marcan como supuestos.
42. Información faltante: al empezar cada chat se revisa qué datos mínimos faltan y se piden de a uno, el que más cambia el modelo, como la única pregunta de la entrega. Mientras no lleguen, se modela con el valor por defecto marcado como supuesto en el panel "Supuestos por validar". Orden de prioridad: (1) planta; (2) alturas interiores de bodega y sala; (3) altura del cielo y límite entre alturas; (4) fachada: elevación o, en modo solo plano, alturas de fachada y letrero más las zonas de vidrio, acceso, puerta de carga y muros medianeros marcadas sobre el plano; (5) plano eléctrico; (6) fotos de las piezas que no estén en la biblioteca; (7) foto del lugar y posición de cámara si se quiere fotomontaje. Lo que Matias responde se anota en los parámetros del kit y en la memoria del proyecto.
43. El cuadro de instrucciones del proyecto lleva el texto completo de estas reglas (instrucciones_para_pegar_en_el_proyecto.md). Claude no puede editar ese cuadro: cada vez que cambie una regla entrega de nuevo ese texto para que Matias lo vuelva a pegar, junto con el kit nuevo.

Errores a evitar (aprendidos)
- Mezclar RGB (render, PIL) con BGR (OpenCV): el rojo sale azul.
- Extrapolar un ajuste de cielo hacia el horizonte: genera una banda más clara. Muestrear el color real justo sobre el borde y suavizar a lo ancho.
- Fijar la orientación de una fachada con el centroide del local.
- Convertir dos veces una zona medida desde un ancla.
- Dar por buena una lectura del plano sin superponerla y sin contrastar con los totales que declara el plano (cuerpos de góndola, P.O.S., repisas HP).
- Reemplazar el núcleo del generador por un texto que deje de ser literal (r''') o que meta valores en una sola línea.
- Usar polígonos reducidos con inset para detectar muebles "fuera": los que apoyan contra un muro dan falsos positivos; usar el contorno con 2 cm de holgura.
- El render del visor tiene fondo opaco: para un fotomontaje se crea un renderer propio con alpha.

Estilo: español, respuestas cortas para pantalla de teléfono, sin preámbulos, sin viñetas al rechazar algo.

Datos mínimos por tienda nueva: planta DXF o PDF, elevaciones PDF (o, en modo solo plano, las alturas de fachada y letrero), plano eléctrico PDF, alturas interiores de bodega y sala, altura del cielo de la sala, límite entre ambas alturas, y fotos de las piezas que no estén en la biblioteca. Lo que falte se pide de a uno por entrega (regla 42).

Preguntas abiertas (consolidadas)
- Santa Rosa: ¿la altura interior es 3,33 m (la indicada) o 3,22 m (la del plano)? Plano eléctrico de Santa Rosa (pedido, sin respuesta). Límite y alturas bodega/sala. Orientación de racks y góndolas. Diferencia entre repisas HP leídas (60 de 30 y 10 de 60) y las del plano (57 y 11). Altura de RV2. ¿Starken debe seguir visible en el fotomontaje?
- Chillán: límite y alturas bodega/sala (galpón 10,97 m medido de la elevación), frente de racks y góndolas, estándar de alturas de los muebles guardados.
- Talca: límite de alturas x = 16372 (eje estructural, supuesto), L02 a 4 m sobre el cielo de 3,87 m de la bodega, qué rack de pallets mira hacia dónde, accesorios de baños y cocina.
- General: si las cabeceras HP (65 × 30) deben construirse como repisas HP; si la cenefa de baterías debe verse también por la espalda (hoy se refleja); si el desplazamiento con dos dedos debe seguir el piso en lugar de ser paralelo a la pantalla; si se limpian las versiones antiguas de Talca (v0 a v28; la vigente es v39).
