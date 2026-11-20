# Fotomontaje de una tienda sobre la foto del lugar

Entradas: la foto del lugar y una captura del visor con la posición de cámara que el usuario quiere (su "posición").
Salida: la foto con el edificio existente reemplazado por la fachada del modelo, en el mismo encuadre.

1. `1_camara_desde_render.py`: recupera la cámara de la captura del usuario. Mide a mano, sobre la captura cuadriculada, el píxel (x, y) de aristas
   verticales conocidas del modelo (puertas, esquinas, extremos de fachada; arriba y abajo) y ajusta X, Y, Z, yaw, pitch, f y el punto principal
   vertical (la captura viene recortada) con mínimos cuadrados desde muchos arranques. Santa Rosa: error RMS 4,1 px.
2. `2_hipotesis_esquinas_foto.py`: prueba qué esquinas del modelo corresponden a qué quiebres de la foto (todas las asignaciones ordenadas); sirve
   para detectar si la foto y el diseño no son compatibles. Con la forma del edificio antiguo distinta del diseño no hay ajuste exacto.
3. `3_ajuste_suelo_foto.py`: ajuste con cuatro puntos del suelo; en Santa Rosa dio 77 px de error, señal de que la huella antigua no coincide.
4. `4_camara_final.py`: parte de la cámara del usuario (misma apertura horizontal) y la ajusta lo mínimo para que las esquinas A, E3 y E1 caigan
   donde están en la foto (con un prior que la mantiene cerca de la cámara del usuario). Guarda cam_final.npy.
5. `5_render_alfa.py`: renderiza el modelo con esa cámara, fondo transparente, tamaño de la foto.
6. `6_componer.py`: limpia el edificio antiguo y compone. Pasos: polígono del edificio antiguo; restos sobre la fachada nueva = cielo (relleno por
   columna con el color justo sobre el borde, mediana de 121 columnas y suavizado) o fachada del vecino (relleno por filas con columnas cercanas);
   restos bajo la fachada = inpainting; borra arbolitos que quedan flotando; luz de la fachada (x1,06 / 1,04 / 1,0, gradiente de 10 %), sombra de contacto
   (desplazada 14 px a la izquierda y 12 abajo, desenfoque 9, 42 %).

Lecciones: el render viene en RGB y OpenCV trabaja en BGR (al mezclar sin convertir, el rojo salió azul); un polinomio de cielo no se debe extrapolar
hacia el horizonte (sale una banda más clara); los objetos pequeños sobre el borde (árboles, antena) dejan franjas verticales si se muestrea cada columna
sin suavizar; la fachada nueva puede quedar más baja que el edificio antiguo y entonces hay que reconstruir lo que había detrás.
Decir siempre al usuario qué queda tapado (en Santa Rosa, la tienda Starken a la izquierda) y que el encuadre es aproximado.
Las rutas de los scripts son de la sesión de Santa Rosa: ajustarlas a la carpeta de trabajo.
