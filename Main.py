import pygame
from Funciones import *
from Constantes import *

############################ Inicializar Pygame ################################

pygame.init()
inicializar_musica()
sonidos = cargar_sonidos()

############################ Configurar ventana ################################

pygame.display.set_caption("Buscaminas")
ventana_juego = pygame.display.set_mode((DIMENSIONES_VENTANA), pygame.RESIZABLE)

############################ Imagenes y recursos ###############################

imagen_fondo = pygame.image.load('Imagenes/Fondo.jpg')
imagen_fondo_puntajes = pygame.image.load('Imagenes/Puntajes.jpg')
icono = pygame.image.load('Imagenes/bomb.png')
pygame.display.set_icon(icono)
imagen_bomba = pygame.image.load('Imagenes/bomb.png')
imagen_bomba = pygame.transform.scale(imagen_bomba, (40, 40))
imagen_bandera = pygame.image.load('Imagenes/bandera.png')
imagen_bandera = pygame.transform.scale(imagen_bandera, (40, 40))

############################## Fuentes ################################

fuente_titulo_grande = pygame.font.SysFont("Impact", 72)
fuente_texto_boton = pygame.font.SysFont("Verdana", 25)
fuente_subtitulo_pantalla = pygame.font.SysFont("Verdana", 48)

############################## Contadores y Banderas ################################ 

pantalla_actual = "menu"
dificultad_actual = 0
indice_hover_actual = -2
puntaje = 0
tiempo_transcurrido = 0
banderas_colocadas = 0
juego_terminado = False
juego_ejecutandose = True                              
mostrar_todas_bombas = False
primer_click = True

########################### Loop principal ##############################

while juego_ejecutandose:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            juego_ejecutandose = False

        elif evento.type == pygame.MOUSEMOTION:
            if pantalla_actual == "menu":
                indice_hover_actual = detectar_hover_en_menu_nuevo(evento.pos, ventana_juego)
            else:
                indice_hover_actual = detectar_hover_en_otras_pantallas(evento.pos, ventana_juego)

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1: 
                reproducir_sonido(sonidos, "click")

                if pantalla_actual == "menu":
                    i = procesar_click_en_menu_nuevo(evento.pos, ventana_juego)

                    if i == 0:  
                        estado_juego = inicializar_tablero(dificultad_actual)
                        banderas_colocadas = 0
                        mostrar_todas_bombas = False
                        pantalla_actual = "juego"
                        juego_terminado = False
                        primer_click = True

                    elif i == 1:  
                        dificultad_actual = (dificultad_actual + 1) % 3
                    elif i == 2:  
                        pantalla_actual = "puntajes"
                    elif i == 3:  
                        juego_ejecutandose = False

                elif pantalla_actual == "juego":
                    click_reiniciar, click_volver = procesar_click_en_otras_pantallas(evento.pos, ventana_juego)

                    if click_volver:
                        pantalla_actual = "menu"
                        primer_click = True

                    elif click_reiniciar:
                        estado_juego = inicializar_tablero(dificultad_actual)
                        banderas_colocadas = 0
                        mostrar_todas_bombas = False
                        juego_terminado = False
                        primer_click = True
                        estado_juego['tiempo_inicio'] = 0
                        estado_juego['timer_activo'] = False
                    else:
                        fila, col = calcular_posicion_matriz(evento.pos, ventana_juego, estado_juego['filas'], estado_juego['columnas'])                        
                       
                        fuera_de_filas = fila < 0 or fila >= len(estado_juego['matriz_minas'])
                        fuera_de_columnas = col < 0 or col >= len(estado_juego['matriz_minas'][0])

                        if fuera_de_filas or fuera_de_columnas:
                            continue

                        if not estado_juego['matriz_estado'][fila][col] and not estado_juego['matriz_banderas'][fila][col]:

                            if primer_click:
                                
                                if estado_juego['matriz_numeros'][fila][col] == 'X':
                                    estado_juego['matriz_minas'], estado_juego['matriz_numeros'] = mover_bomba(estado_juego['matriz_minas'], fila, col)
                                   
                                    for i in range(len(estado_juego['matriz_estado'])):
                                        for j in range(len(estado_juego['matriz_estado'][0])):
                                            estado_juego['matriz_estado'][i][j] = False
                                
                                    for i in range(len(estado_juego['matriz_banderas'])):
                                        for j in range(len(estado_juego['matriz_banderas'][0])):
                                            estado_juego['matriz_banderas'][i][j] = False
                                            
                                primer_click = False

                            if not estado_juego['timer_activo'] and estado_juego['matriz_numeros'][fila][col] != 'X':
                                estado_juego['tiempo_inicio'] = pygame.time.get_ticks()
                                estado_juego['timer_activo'] = True

                            descubrir_celda(estado_juego['matriz_estado'], estado_juego['matriz_numeros'], fila, col)

                            if estado_juego['matriz_numeros'][fila][col] == 'X':  
                                reproducir_sonido(sonidos, "derrota")
                                mostrar_todas_bombas = True
                                juego_terminado = True
                                tiempo_transcurrido = (pygame.time.get_ticks() - estado_juego['tiempo_inicio']) // 1000
                                mostrar_pantalla_juego(dificultad_actual, estado_juego, banderas_colocadas, fuente_texto_boton, imagen_bomba, imagen_bandera,  
                                                        mostrar_todas_bombas, indice_hover_actual, ventana_juego)
                                pygame.display.flip()
                                pygame.time.wait(2000)
                                nombre = pedir_nombre(ventana_juego, False)
                                
                                if nombre:
                                    puntaje = calcular_puntaje(dificultad_actual, tiempo_transcurrido)
                                    guardar_puntaje(nombre, puntaje, tiempo_transcurrido)
                                pantalla_actual = "menu"
                                
                            elif verificar_victoria(estado_juego['matriz_estado'], estado_juego['matriz_minas']):
                                reproducir_sonido(sonidos, "victoria")
                                juego_terminado = True
                                tiempo_transcurrido = (pygame.time.get_ticks() - estado_juego['tiempo_inicio']) // 1000

                elif pantalla_actual == "puntajes":
                    click_reiniciar, click_volver = procesar_click_en_otras_pantallas(evento.pos, ventana_juego)
                    if click_volver:
                        pantalla_actual = "menu"

            elif evento.button == 3 and pantalla_actual == "juego":  
                fila, col = calcular_posicion_matriz(evento.pos,ventana_juego,estado_juego['filas'],estado_juego['columnas'])               
                              
                fuera_de_filas = fila < 0 or fila >= len(estado_juego['matriz_banderas'])
                fuera_de_columnas = col < 0 or col >= len(estado_juego['matriz_banderas'][0])
                casilla_ya_descubierta = estado_juego['matriz_estado'][fila][col]

                if fuera_de_filas or fuera_de_columnas or casilla_ya_descubierta:
                    continue

                estado_juego['matriz_banderas'][fila][col] = not estado_juego['matriz_banderas'][fila][col]
               
                if estado_juego['matriz_banderas'][fila][col]:
                    banderas_colocadas += 1
                else:
                    banderas_colocadas -= 1

                reproducir_sonido(sonidos, "bandera")

    if juego_terminado and pantalla_actual == "juego":
        if estado_juego['timer_activo']:
            tiempo_transcurrido = (pygame.time.get_ticks() - estado_juego['tiempo_inicio']) // 1000
        
        es_victoria = verificar_victoria(estado_juego['matriz_estado'], estado_juego['matriz_minas'])
        mostrar_pantalla_juego(dificultad_actual, estado_juego, banderas_colocadas, fuente_texto_boton, imagen_bomba, imagen_bandera,  
                               mostrar_todas_bombas, indice_hover_actual, ventana_juego)
        nombre = pedir_nombre(ventana_juego, es_victoria)

        if nombre:
            puntaje = calcular_puntaje(dificultad_actual, tiempo_transcurrido)
            guardar_puntaje(nombre, puntaje, tiempo_transcurrido)     
        cambiar_musica_de_fondo('Musica/Musica.mp3')
        mostrar_todas_bombas = False
        juego_terminado = False
        estado_juego['timer_activo'] = False  
        primer_click = True
        pantalla_actual = "menu"
        continue  

    if pantalla_actual == "menu":
        mostrar_pantalla_menu_principal(indice_hover_actual, ventana_juego, imagen_fondo, dificultad_actual)
    elif pantalla_actual == "puntajes":
        mostrar_pantalla_puntajes(ventana_juego, imagen_fondo_puntajes, fuente_texto_boton, indice_hover_actual)
    elif pantalla_actual == "juego":
        mostrar_pantalla_juego(dificultad_actual, estado_juego, banderas_colocadas, fuente_texto_boton, imagen_bomba, imagen_bandera,  
                               mostrar_todas_bombas, indice_hover_actual, ventana_juego)

    pygame.display.flip()

pygame.mixer.music.stop()
pygame.quit()