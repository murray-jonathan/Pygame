import os
import pygame
import random
from Constantes import *


def configurar_dificultad(dificultad: int) -> tuple:
    """
    Configura la dificultad del juego de Buscaminas.

    Recibe:
        dificultad (int): Un entero que representa el nivel de dificultad.
                        0 para facil, 1 para medio, 2 para dificil.

    Devuelve:
        tuple: Una tupla que contiene tres enteros:
            - filas (int): Numero de filas del tablero.
            - columnas (int): Numero de columnas del tablero.
            - minas (int): Numero de minas en el tablero.
            
    """
    filas = 0
    columnas = 0
    minas = 0

    if dificultad == 0:
        filas, columnas, minas = (8, 8, 10)       
    elif dificultad == 1:
        filas, columnas, minas = (16, 16, 50)  
    else:
        filas, columnas, minas = (24, 24, 120)  

    return (filas, columnas, minas)


def inicializar_tablero(dificultad_actual: int) -> dict:
    """
    Inicializa el tablero del juego de Buscaminas.

    Recibe:
        dificultad_actual (int): El nivel de dificultad actual del juego.

    Devuelve:
        dict: Un diccionario que contiene las siguientes claves:
            - matriz_minas: Matriz de booleanos que indica la ubicacion de las minas.
                Cada celda contiene:
                    - True si hay una mina.
                    - False si no hay mina.
            - matriz_numeros: Matriz de enteros que indica la cantidad de minas adyacentes a cada celda.
                Cada celda contiene un número del 0 al 8.
            - matriz_estado: Matriz de booleanos que indica si una celda fue descubierta o no.
                Cada celda contiene:
                    - True si la celda esta descubierta.
                    - False si esta oculta.
            - matriz_banderas: Matriz de booleanos que indica si una celda tiene una bandera colocada por el jugador.
                Cada celda contiene:
                    - True si hay una bandera.
                    - False si no la hay.
            - minas_totales (int): Numero total de minas generadas en el tablero.
            - tiempo_inicio (int): Valor inicial del temporizador del juego (0 al comenzar).
            - timer_activo (bool): Indica si el temporizador esta actualmente en funcionamiento.
            - filas (int): Cantidad de filas del tablero.
            - columnas (int): Cantidad de columnas del tablero.
    """

    filas, columnas, cantidad_minas = configurar_dificultad(dificultad_actual)
    
    matriz_minas = inicializar_matriz(filas, columnas, cantidad_minas)
    matriz_numeros = generar_matriz_numeros(matriz_minas)
    
    matriz_estado = []
    
    for _ in range(filas):
        fila = []
        for _ in range(columnas):
            fila.append(False)
        matriz_estado.append(fila)
    
    matriz_banderas = []
    
    for _ in range(filas):
        fila = []
        for _ in range(columnas):
            fila.append(False)
        matriz_banderas.append(fila)
    
    return {
        'matriz_minas': matriz_minas,
        'matriz_numeros': matriz_numeros,
        'matriz_estado': matriz_estado,
        'matriz_banderas': matriz_banderas,
        'minas_totales': cantidad_minas,
        'tiempo_inicio': 0,
        'timer_activo': False,
        'filas': filas,
        'columnas': columnas
    }


def mostrar_pantalla_menu_principal(indice: int, ventana, imagen_fondo, dificultad_actual: int) -> None:
    """
    Muestra la pantalla del menu principal del juego Buscaminas.

    Dibuja el fondo, el titulo del juego y los botones principales del menu.
    Resalta el boton actualmente seleccionado segun el indice proporcionado.

    Recibe:
        indice (int): Indice del boton actualmente seleccionado (0-3).
        ventana (pygame.Surface): Superficie donde se dibuja el menu.
        imagen_fondo (pygame.Surface): Imagen de fondo del menu principal.
        dificultad_actual (int): Indice de la dificultad actual del juego.

    Retorna:
        None
    """
    ventana.blit(imagen_fondo, (0, 0))
    dibujar_titulo_centrado("BUSCAMINAS", 100, "grande")
    texto_dificultad = NOMBRES_DIFICULTAD[dificultad_actual]
    
    botones = [
        (crear_boton('jugar', ventana), "Jugar"),
        (crear_boton('dificultad', ventana), texto_dificultad),
        (crear_boton('puntajes', ventana), "Puntajes"),
        (crear_boton('salir', ventana), "Salir"),
    ]
    
    for i in range(len(botones)):
        dibujar_boton_en_pantalla(botones[i][0], botones[i][1], indice == i)


def mostrar_pantalla_juego(dificultad_actual: int, estado_juego: dict, banderas_colocadas: int,
                           fuente_texto_boton: pygame.font.Font, imagen_bomba: pygame.Surface,
                           imagen_bandera: pygame.Surface, mostrar_todas_bombas: bool,
                           indice_hover_actual: int, ventana_juego: pygame.Surface) -> None:
    """
    Muestra la pantalla principal del juego de Buscaminas en curso.
    
    Dibuja el tablero del juego, informacion del estado actual (tiempo, banderas, minas),
    y los botones de control. Actualiza el cronometro si el juego esta activo.
    
    Recibe:
        dificultad_actual (int): El indice de la dificultad actual del juego.
        estado_juego (dict): Diccionario con el estado del juego que contiene:
            - 'timer_activo' (bool): Si el cronometro esta funcionando
            - 'tiempo_transcurrido' (int): Tiempo transcurrido en segundos
            - 'tiempo_inicio' (int): Momento del inicio del juego
            - 'minas_totales' (int): Numero total de minas en el tablero
            - 'matriz_numeros' (list): Matriz con los numeros del buscaminas
            - 'matriz_estado' (list): Matriz con el estado de cada casilla
            - 'matriz_banderas' (list): Matriz con las banderas colocadas
        banderas_colocadas (int): Numero de banderas que el jugador ha colocado.
        fuente_texto_boton (pygame.font.Font): Fuente para renderizar el texto.
        imagen_bomba (pygame.Surface): Imagen que representa una bomba.
        imagen_bandera (pygame.Surface): Imagen que representa una bandera.
        mostrar_todas_bombas (bool): Si se deben mostrar todas las bombas (fin del juego).
        indice_hover_actual (int): Indice del boton actualmente resaltado.
        ventana_juego (pygame.Surface): La ventana/superficie donde se dibuja el juego.
    
    Devuelve:
        None
    """
    ventana_juego.fill(COLOR_FONDO)
    
    ancho_ventana = ventana_juego.get_width()
    alto_ventana = ventana_juego.get_height()
    
    dibujar_titulo_centrado(f"Nivel {NOMBRES_DIFICULTAD[dificultad_actual]}", 50, "mediana")
    
    pos_x_info = int(ancho_ventana * 0.8)  
    pos_y_inicial = int(alto_ventana * 0.45)  
    espaciado_vertical = fuente_texto_boton.get_height() + 5  
    
    if estado_juego['timer_activo']:
        estado_juego['tiempo_transcurrido'] = (pygame.time.get_ticks() - estado_juego['tiempo_inicio']) // 1000
        
        minutos = estado_juego['tiempo_transcurrido'] // 60
        segundos = estado_juego['tiempo_transcurrido'] % 60
        tiempo_formateado = f"{minutos:02d}:{segundos:02d}"
        
        texto_tiempo = fuente_texto_boton.render(f"Tiempo: {tiempo_formateado}", True, COLOR_TEXTO_NORMAL)
        ventana_juego.blit(texto_tiempo, (pos_x_info, pos_y_inicial))
    

    texto_banderas = fuente_texto_boton.render(f"Banderas: {banderas_colocadas}", True, COLOR_TEXTO_NORMAL)
    pos_y_banderas = pos_y_inicial + espaciado_vertical
    ventana_juego.blit(texto_banderas, (pos_x_info, pos_y_banderas))

    minas_restantes = estado_juego['minas_totales'] - banderas_colocadas
    texto_minas = fuente_texto_boton.render(f"Minas: {minas_restantes}", True, COLOR_TEXTO_NORMAL)
    pos_y_minas = pos_y_banderas + espaciado_vertical
    ventana_juego.blit(texto_minas, (pos_x_info, pos_y_minas))
    
    dibujar_matriz_buscaminas(ventana_juego, estado_juego['matriz_numeros'], estado_juego['matriz_estado'],
                             estado_juego['matriz_banderas'], fuente_texto_boton, imagen_bomba, imagen_bandera,
                             mostrar_todas_bombas)
    
    dibujar_boton_en_pantalla(crear_boton('reiniciar', ventana_juego), "Reiniciar", indice_hover_actual == 1)
    dibujar_boton_en_pantalla(crear_boton('volver', ventana_juego), "Volver", indice_hover_actual == 0)


def mostrar_pantalla_puntajes(ventana_juego: pygame.Surface, imagen_fondo_puntajes: pygame.Surface,
                              fuente_texto_boton: pygame.font.Font, indice_hover_actual: int) -> None:
    """
    Muestra la pantalla de puntajes del juego con interfaz completamente responsive.
    
    Dibuja el fondo de puntajes escalado al tamaño de la ventana, la lista de mejores 
    puntajes y el boton para volver al menu principal. Todos los elementos se adaptan
    automáticamente a diferentes resoluciones de pantalla.
    
    Recibe:
        ventana_juego (pygame.Surface): La ventana/superficie donde se dibuja la pantalla.
        imagen_fondo_puntajes (pygame.Surface): La imagen de fondo para la pantalla de puntajes.
        fuente_texto_boton (pygame.font.Font): Fuente para renderizar el texto de los botones.
        indice_hover_actual (int): Indice del boton actualmente resaltado (0 para el boton volver).
    
    Devuelve:
        None
    """
    ancho_ventana = ventana_juego.get_width()
    alto_ventana = ventana_juego.get_height()
    
    imagen_fondo_escalada = pygame.transform.scale(imagen_fondo_puntajes, (ancho_ventana, alto_ventana))
    ventana_juego.blit(imagen_fondo_escalada, (0, 0))
    
    mostrar_lista_puntajes(ventana=ventana_juego, fuente=fuente_texto_boton)
    
    dibujar_boton_en_pantalla(crear_boton('volver', ventana_juego), "Volver", indice_hover_actual == 0)


# ===============================================================================
# CREACION DE BOTONES
# ===============================================================================


def crear_boton(tipo_de_valor: str, ventana: pygame.Surface, pos_x: int = None, pos_y: int = None) -> pygame.Rect:
    """
    Crea un rectangulo de boton con posicion y tamaño especificos segun el tipo.
    
    Recibe:
        tipo_de_valor (str): Tipo de boton a crear.
        ventana (pygame.Surface): Superficie de la ventana donde se dibujara el boton.
        pos_x (int, opcional): Posición X personalizada. Si no se proporciona, usa la predefinida.
        pos_y (int, opcional): Posición Y personalizada. Si no se proporciona, usa la predefinida.
    
    Devuelve:
        pygame.Rect: Rectangulo que representa el boton con posicion y dimensiones.
    """
    ancho_ventana = ventana.get_width()
    alto_ventana = ventana.get_height()
    ancho = int(ancho_ventana * 0.2)
    alto = int(alto_ventana * 0.07)
    x_centro = (ancho_ventana - ancho) // 2
    
    posiciones = {
        'jugar':      (x_centro, int(alto_ventana * 0.35)),
        'dificultad': (x_centro, int(alto_ventana * 0.45)),
        'puntajes':   (x_centro, int(alto_ventana * 0.55)),
        'salir':      (x_centro, int(alto_ventana * 0.72)),
        'reiniciar': (int(ancho_ventana * 0.02), int(alto_ventana * 0.45)),
        'volver':     (int(ancho_ventana * 0.02), int(alto_ventana * 0.55))
    }
    

    if pos_x is not None and pos_y is not None:
        x, y = pos_x, pos_y
    else:
        x, y = posiciones.get(tipo_de_valor, (x_centro, int(alto_ventana * 0.5)))
    
    return pygame.Rect(x, y, ancho, alto)

# ===============================================================================
# DETECCION DE CLICKS Y HOVER
# ===============================================================================

def calcular_posicion_matriz(pos: tuple[int, int], superficie: pygame.Surface, filas: int, columnas: int) -> tuple[int, int]:
    """
    Convierte coordenadas de mouse en posicion de matriz del tablero de buscaminas.
    
    Recibe:
        pos (Tuple[int, int]): Coordenadas (x, y) del mouse en la ventana.
        superficie (pygame.Surface): Superficie donde se dibuja la matriz.
        filas (int): Numero de filas de la matriz.
        columnas (int): Numero de columnas de la matriz.
    
    Devuelve:
        Tuple[int, int]: Posicion (fila, columna) en la matriz.
        
        Retorna (-1, -1) si el click esta fuera de la matriz.
    """
    x_mouse, y_mouse = pos
    
    ancho_ventana = superficie.get_width()
    alto_ventana = superficie.get_height()
    
    tamaño_casilla_preferido = 40
    margen = 130
    ancho_disponible = ancho_ventana - 2 * margen
    alto_disponible = alto_ventana - 2 * margen
    
    tamaño_casilla = tamaño_casilla_preferido
    
    if columnas * tamaño_casilla > ancho_disponible:
        tamaño_casilla = ancho_disponible // columnas
    if filas * tamaño_casilla > alto_disponible:
        tamaño_casilla = min(tamaño_casilla, alto_disponible // filas)
    
    ancho_total_matriz = columnas * tamaño_casilla
    alto_total_matriz = filas * tamaño_casilla
    x_inicial = (ancho_ventana - ancho_total_matriz) // 2
    y_inicial = (alto_ventana - alto_total_matriz) // 2
    
    if (x_inicial <= x_mouse < x_inicial + ancho_total_matriz and
        y_inicial <= y_mouse < y_inicial + alto_total_matriz):
        col = (x_mouse - x_inicial) // tamaño_casilla
        fila = (y_mouse - y_inicial) // tamaño_casilla
        resultado = (fila, col)
    else:
        resultado = (-1, -1)
    
    return resultado


def procesar_click_en_menu_nuevo(posicion: tuple[int, int], ventana: pygame.Surface) -> int:
    """
    Detecta en que boton del menu principal se hizo click.
    
    Recibe:
        posicion (Tuple[int, int]): Coordenadas (x, y) del click del mouse.
        ventana (pygame.Surface): Superficie de la ventana.
        
    Devuelve:
        int: Indice del boton clickeado:
            - 0: Jugar
            - 1: Dificultad
            - 2: Puntajes
            - 3: Salir
            - -1: No se clickeo ningun boton
            
    """
    tipos_de_valor = ['jugar', 'dificultad', 'puntajes', 'salir']
    botones = []
    
    for tipo in tipos_de_valor:
        boton = crear_boton(tipo, ventana)
        botones.append(boton)
    
    indice = -1
    
    for i in range(len(botones)):
        if botones[i].collidepoint(posicion):
            indice = i
            break
    
    return indice


def detectar_hover_en_menu_nuevo(posicion: tuple[int, int], ventana: pygame.Surface) -> int:
    """
    Detecta sobre que boton del menu principal esta el cursor del mouse.
    
    Recibe:
        posicion (Tuple[int, int]): Coordenadas (x, y) del cursor del mouse.
        ventana (pygame.Surface): Superficie de la ventana.
        
    Devuelve:
        int: Indice del boton sobre el que esta el cursor:
            - 0: Jugar
            - 1: Dificultad
            - 2: Puntajes
            - 3: Salir
            - -1: No esta sobre ningún botón
            
    """
    tipos_de_valor = ['jugar', 'dificultad', 'puntajes', 'salir']
   
    botones = []
    
    for tipo in tipos_de_valor:
        boton = crear_boton(tipo, ventana)
        botones.append(boton)
    
    indice = -1
   
    for i in range(len(botones)):
        if botones[i].collidepoint(posicion):
            indice = i
            break
    
    return indice


def procesar_click_en_otras_pantallas(posicion: tuple[int, int], ventana: pygame.Surface) -> tuple[bool, bool]:
    """
    Detecta clicks en los botones de reiniciar y volver en pantallas secundarias.
    
    Recibe:
        posicion (Tuple[int, int]): Coordenadas (x, y) del click del mouse.
        ventana (pygame.Surface): Superficie de la ventana.
        
    Devuelve:
        Tuple[bool, bool]: Tupla con dos valores booleanos:
            - Primer valor: True si se clickeo "Reiniciar", False si no
            - Segundo valor: True si se clickeo "Volver", False si no
            
    """
   
    boton_volver = crear_boton('volver', ventana)
    boton_reiniciar = crear_boton('reiniciar', ventana)

    return (boton_reiniciar.collidepoint(posicion), boton_volver.collidepoint(posicion))


def detectar_hover_en_otras_pantallas(posicion: tuple[int, int], ventana: pygame.Surface) -> int:
    """
    Detecta sobre que boton esta el cursor en pantallas secundarias.
    
    Recibe:
        posicion (Tuple[int, int]): Coordenadas (x, y) del cursor del mouse.
        ventana (pygame.Surface): Superficie de la ventana.
        
    Devuelve:
        int: Indice del boton sobre el que esta el cursor:
            - 0: Volver
            - 1: Reiniciar
            - -2: No esta sobre ningun boton
            
    """
    boton_reiniciar = crear_boton('reiniciar', ventana)
    boton_volver = crear_boton('volver', ventana)
    
    indice = -2
   
    if boton_volver.collidepoint(posicion):
        indice = 0
    if boton_reiniciar.collidepoint(posicion):
        indice = 1
    
    return indice


# ===============================================================================
# INTERFAZ
# ===============================================================================

def dibujar_boton_en_pantalla(rect: pygame.Rect, texto: str, hover: bool) -> None:
    """
    Dibuja un boton en la pantalla con el texto especificado.
    
    Recibe:
        rect (pygame.Rect): Rectangulo que define la posicion y tamaño del boton.
        texto (str): Texto a mostrar en el botón.
        hover (bool): Si True, dibuja el boton con color de hover, si False con color normal.
        
    Devuelve:
        None
        
    """
    if hover:
        color = COLOR_BOTON_ENCIMA
    else:
        color = COLOR_BOTON_NORMAL

    pygame.draw.rect(pygame.display.get_surface(), color, rect)
    pygame.draw.rect(pygame.display.get_surface(), COLOR_TEXTO_NORMAL, rect, 2)
    
    fuente = pygame.font.SysFont("Verdana", 25)
    texto_surf = fuente.render(texto, True, COLOR_TEXTO_NORMAL)
    texto_rect = texto_surf.get_rect(center=rect.center)
    pygame.display.get_surface().blit(texto_surf, texto_rect)


def dibujar_titulo_centrado(texto: str, y: int, tipo_fuente: str) -> None:
    """
    Dibuja un titulo centrado horizontalmente en la pantalla.
    
    Recibe:
        texto (str): Texto del titulo a mostrar.
        y (int): Posicion vertical base donde dibujar el titulo.
        tipo_fuente (str): Tipo de fuente a usar:
            - "grande": Fuente Impact grande (6% del ancho de ventana)
            - "mediana": Fuente Verdana mediana (4% del ancho de ventana)
            - Cualquier otro valor: Fuente Verdana pequeña (2.5% del ancho de ventana)
            
    Devuelve:
        None

    """
    superficie = pygame.display.get_surface()
    ancho_ventana = superficie.get_width()
    alto_ventana = superficie.get_height()

    if tipo_fuente == "grande":
        tamaño_fuente = int(ancho_ventana * 0.06)
        fuente = pygame.font.SysFont("Impact", tamaño_fuente)
    elif tipo_fuente == "mediana":
        tamaño_fuente = int(ancho_ventana * 0.04)
        fuente = pygame.font.SysFont("Verdana", tamaño_fuente)
    else:
        tamaño_fuente = int(ancho_ventana * 0.025)
        fuente = pygame.font.SysFont("Verdana", tamaño_fuente)

    texto_surf = fuente.render(texto, True, COLOR_TITULO_PRINCIPAL)

    desplazamiento_y = int(alto_ventana * 0.05)
    rect = texto_surf.get_rect(center=(ancho_ventana // 2, y + desplazamiento_y))

    superficie.blit(texto_surf, rect)


# ===============================================================================
# MATRIZ BUSCAMINAS
# ===============================================================================

def inicializar_matriz(filas: int, columnas: int, minas: int) -> list[list[str]]:
    """
    Crea una matriz del buscaminas con minas distribuidas aleatoriamente.
    
    Recibe:
        filas (int): Numero de filas de la matriz.
        columnas (int): Numero de columnas de la matriz.
        minas (int): Numero de minas a colocar en la matriz.
        
    Devuelve:
        List[List[str]]: Matriz 2D donde 'X' representa una mina y '' representa casilla vacia.
        
    """
    matriz = []
   
    for _ in range(filas):
        fila = [''] * columnas
        matriz.append(fila)
    
    cantidad = 0
    
    while cantidad < minas:
        f = random.randint(0, filas - 1)
        c = random.randint(0, columnas - 1)
        if matriz[f][c] != 'X':
            matriz[f][c] = 'X'
            cantidad += 1
    
    return matriz


def generar_matriz_numeros(matriz: list[list[str]]) -> list[list[any]]:
    """
    Genera una matriz con numeros que indican cuantas minas hay alrededor de cada casilla.
    
    Recibe:
        matriz (List[List[str]]): Matriz original con minas ('X') y casillas vacías ('').
        
    Devuelve:
        List[List[Any]]: Matriz donde cada casilla contiene:
            - 'X' si hay una mina
            - int (0-8) indicando el numero de minas adyacentes
            
    """
    filas, columnas = len(matriz), len(matriz[0])
    numeros = []
    
    for i in range(filas):
        fila_numeros = []
        for j in range(columnas):
            if matriz[i][j] == 'X':
                fila_numeros.append('X')
            else:
                cuenta = 0
                vecinos = [
                    (i-1, j-1), (i-1, j), (i-1, j+1),
                    (i, j-1),             (i, j+1),
                    (i+1, j-1), (i+1, j), (i+1, j+1)
                ]
                for ni, nj in vecinos:
                    if ni < 0 or ni >= filas:
                        continue
                    if nj < 0 or nj >= columnas:
                        continue
                    if matriz[ni][nj] == 'X':
                        cuenta += 1
                fila_numeros.append(cuenta)
        numeros.append(fila_numeros)
  
    return numeros


def dibujar_matriz_buscaminas(superficie: pygame.Surface, numeros: list[list[any]], 
                            estado: list[list[bool]], banderas: list[list[bool]], 
                            fuente: pygame.font.Font, imagen_bomba: pygame.Surface, 
                            imagen_bandera: pygame.Surface, mostrar_todas_bombas: bool = False) -> None:
    """
    Dibuja la matriz del buscaminas en la pantalla con todos sus elementos visuales.
    
    Recibe:
        superficie (pygame.Surface): Superficie donde dibujar la matriz.
        numeros (List[List[Any]]): Matriz con numeros y minas ('X').
        estado (List[List[bool]]): Matriz que indica que casillas estan descubiertas.
        banderas (List[List[bool]]): Matriz que indica que casillas tienen banderas.
        fuente (pygame.font.Font): Fuente para dibujar los numeros.
        imagen_bomba (pygame.Surface): Imagen para mostrar las minas.
        imagen_bandera (pygame.Surface): Imagen para mostrar las banderas.
        mostrar_todas_bombas (bool, optional): Si True, muestra todas las minas. 
                                             Por defecto False.
                                             
    Devuelve:
        None
        
    """
    ancho_ventana = superficie.get_width()
    alto_ventana = superficie.get_height()
    
    filas = len(numeros)
    columnas = len(numeros[0])
    
    tamaño_casilla_preferido = 40
    
    ancho_total_preferido = columnas * tamaño_casilla_preferido
    alto_total_preferido = filas * tamaño_casilla_preferido
    
    margen = 130
    ancho_disponible = ancho_ventana - (2 * margen)
    alto_disponible = alto_ventana - (2 * margen)
    
    tamaño_casilla = tamaño_casilla_preferido
    
    if ancho_total_preferido > ancho_disponible:
        tamaño_por_ancho = ancho_disponible // columnas
        tamaño_casilla = tamaño_por_ancho
    
    if alto_total_preferido > alto_disponible:
        tamaño_por_alto = alto_disponible // filas
        if tamaño_por_alto < tamaño_casilla:
            tamaño_casilla = tamaño_por_alto
    
    ancho_total_matriz = columnas * tamaño_casilla
    alto_total_matriz = filas * tamaño_casilla
    
    x_inicial = (ancho_ventana - ancho_total_matriz) // 2
    y_inicial = (alto_ventana - alto_total_matriz) // 2
    
    for i in range(filas):
        for j in range(columnas):

            x = x_inicial + (j * tamaño_casilla)
            y = y_inicial + (i * tamaño_casilla)
            
            rect = pygame.Rect(x, y, tamaño_casilla, tamaño_casilla)
            
            if estado[i][j] or (mostrar_todas_bombas and numeros[i][j] == 'X'):
                pygame.draw.rect(superficie, COLOR_CASILLA_DESCUBIERTA, rect)
            else:
                pygame.draw.rect(superficie, COLOR_CASILLA_OCULTA, rect)
            
            pygame.draw.rect(superficie, COLOR_CASILLA_BORDE, rect, 1)
            
            if estado[i][j] or (mostrar_todas_bombas and numeros[i][j] == 'X'):
                valor = numeros[i][j]
                if valor == 'X':
                    if tamaño_casilla != tamaño_casilla_preferido:
                        imagen_escalada = pygame.transform.scale(imagen_bomba, (tamaño_casilla - 4, tamaño_casilla - 4))
                        superficie.blit(imagen_escalada, (x + 2, y + 2))
                    else:
                        superficie.blit(imagen_bomba, rect)
                elif valor > 0:
                    if tamaño_casilla != tamaño_casilla_preferido:
                        tamaño_fuente = tamaño_casilla // 2
                        fuente_escalada = pygame.font.Font(None, tamaño_fuente)
                        texto = fuente_escalada.render(str(valor), True, (0, 0, 0))
                    else:
                        texto = fuente.render(str(valor), True, (0, 0, 0))
                    superficie.blit(texto, texto.get_rect(center=rect.center))
            else:
                if banderas[i][j]:
                    if tamaño_casilla != tamaño_casilla_preferido:
                        imagen_escalada = pygame.transform.scale(imagen_bandera, (tamaño_casilla - 4, tamaño_casilla - 4))
                        superficie.blit(imagen_escalada, (x + 2, y + 2))
                    else:
                        superficie.blit(imagen_bandera, rect)



def descubrir_celda(matriz_estado: list[list[bool]], matriz_numeros: list[list[any]], 
                   fila: int, columna: int) -> None:
    """
    Descubre una celda y recursivamente descubre celdas vacias adyacentes.
    
    Recibe:
        matriz_estado (List[List[bool]]): Matriz que indica que celdas estan descubiertas.
        matriz_numeros (List[List[Any]]): Matriz con numeros y minas.
        fila (int): Fila de la celda a descubrir.
        columna (int): Columna de la celda a descubrir.
        
    Devuelve:
        None
        
    """
    if matriz_estado[fila][columna] or matriz_numeros[fila][columna] == 'X':
        pass  
    else:
        matriz_estado[fila][columna] = True

        if matriz_numeros[fila][columna] == 0:
            vecinos = [
                (fila - 1, columna - 1), (fila - 1, columna), (fila - 1, columna + 1),
                (fila, columna - 1),                            (fila, columna + 1),
                (fila + 1, columna - 1), (fila + 1, columna), (fila + 1, columna + 1)
            ]
            for ni, nj in vecinos:
                if ni < 0 or ni >= len(matriz_estado):
                    continue
                if nj < 0 or nj >= len(matriz_estado[0]):
                    continue
                descubrir_celda(matriz_estado, matriz_numeros, ni, nj)


def verificar_victoria(matriz_estado: list[list[bool]], matriz_minas: list[list[str]]) -> bool:
    """
    Verifica si el jugador ha ganado el juego.
    
    Recibe:
        matriz_estado (List[List[bool]]): Matriz que indica que celdas estan descubiertas.
        matriz_minas (List[List[str]]): Matriz original con minas.
        
    Devuelve:
        bool: True si el jugador gano (todas las celdas sin minas estan descubiertas),
              False en caso contrario.
              
    """
    victoria = True
   
    for i in range(len(matriz_estado)):
        for j in range(len(matriz_estado[0])):
            if not matriz_estado[i][j] and matriz_minas[i][j] != 'X':    
                victoria = False
   
    return victoria


def pedir_nombre(ventana: pygame.Surface, victoria: bool) -> str:
    """
    Solicita al jugador que ingrese su nombre al finalizar el juego.
    
    Recibe:
        ventana (pygame.Surface): Superficie de la ventana del juego.
        victoria (bool): True si el jugador gano, False si perdio.
        
    Devuelve:
        Optional[str]: El nombre ingresado por el jugador, o None si cerro la ventana.
                      El nombre esta limitado a 15 caracteres.
                      
    """
    font = pygame.font.SysFont(None, 40)
    nombre = ""
    activo = True
    color = (0, 0 ,0)


    while activo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    activo = False
                elif event.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]
                else:
                    if len(nombre) < 15 and event.unicode.isprintable():
                        nombre += event.unicode


        ancho = ventana.get_width()
        alto = ventana.get_height()

        ancho_input = 300
        alto_input = 40
        input_rect = pygame.Rect(
            (ancho - ancho_input) // 2,
            (alto - alto_input) // 2,
            ancho_input,
            alto_input
        )

        if victoria == True:
            fondo_color = (66, 245, 69)
            ventana.fill(fondo_color)

            mensaje = "GANASTE - Ingrese su nombre y presione Enter:"
            texto = font.render(mensaje, True, (0, 0, 0))
            texto_rect = texto.get_rect(center=(ancho // 2, input_rect.y - 25))
            ventana.blit(texto, texto_rect)

            pygame.draw.rect(ventana, color, input_rect, 2)
            texto_nombre = font.render(nombre, True, (0, 0, 0))
            ventana.blit(texto_nombre, (input_rect.x + 5, input_rect.y + 5))

            pygame.display.flip()
      
        else:
            fondo_color = (252, 0, 29)
            ventana.fill(fondo_color)

            mensaje = "PERDISTE - Ingrese su nombre y presione Enter:"
            texto = font.render(mensaje, True, (0, 0, 0))
            texto_rect = texto.get_rect(center=(ancho // 2, input_rect.y - 25))
            ventana.blit(texto, texto_rect)

            pygame.draw.rect(ventana, color, input_rect, 2)
            texto_nombre = font.render(nombre, True, (0, 0, 0))
            ventana.blit(texto_nombre, (input_rect.x + 5, input_rect.y + 5))
            
            pygame.display.flip()
         
            
    return nombre

def mover_bomba(matriz_minas: list[list[str]], fila_bomba: int, col_bomba: int) -> tuple[list[list[str]], list[list[any]]]:
    """
    Mueve una mina de su posicion actual a una nueva posicion aleatoria.
    
    Recibe:
        matriz_minas (List[List[str]]): Matriz con las minas.
        fila_bomba (int): Fila donde esta la mina a mover.
        col_bomba (int): Columna donde esta la mina a mover.
        
    Devuelve:
        Tuple[List[List[str]], List[List[Any]]]: Tupla con:
            - Matriz de minas actualizada
            - Matriz de numeros recalculada
            
    """
    filas = len(matriz_minas)
    columnas = len(matriz_minas[0])
    
    matriz_minas[fila_bomba][col_bomba] = ''
    
    while True:
        f = random.randint(0, filas - 1)
        c = random.randint(0, columnas - 1)
        if matriz_minas[f][c] != 'X' and (f != fila_bomba or c != col_bomba):  
            matriz_minas[f][c] = 'X'
            break
    
    matriz_numeros = generar_matriz_numeros(matriz_minas)
    
    return (matriz_minas, matriz_numeros)


# ===============================================================================
# PUNTAJES
# ===============================================================================

def calcular_puntaje(nivel: int, tiempo: int) -> int:
    """
    Calcula el puntaje basado en el nivel de dificultad y el tiempo transcurrido.
    A mayor tiempo, menor puntaje.
    
    Recibe:
        nivel (int): Nivel de dificultad:
            - 0: Facil
            - 1: Medio  
            - 2: Dificil
        tiempo (int): Tiempo transcurrido en segundos.
        
    Devuelve:
        int: Puntaje calculado segun la dificultad y tiempo (mayor tiempo = menor puntaje).
        
    """
   
    puntos_base = 0
    
    if nivel == 0:    
        puntos_base = 1000
    elif nivel == 1:   
        puntos_base = 2000
    elif nivel == 2:    
        puntos_base = 3000
    
   
    if tiempo <= 0:
        tiempo = 1
    
    puntaje = puntos_base // tiempo
    
    if puntaje < 1:
        puntaje = 1
    
    return puntaje

def guardar_puntaje(nombre: str, puntaje: int, tiempo: int) -> None:
    """
    Guarda un puntaje en el archivo CSV y mantiene solo los mejores 10.
    
    Recibe:
        nombre (str): Nombre del jugador.
        puntaje (int): Puntaje obtenido.
        tiempo (int): Tiempo transcurrido en segundos.
        
    Devuelve:
        None
        
    """
    puntajes = leer_puntajes()
    puntajes.append((nombre, puntaje, tiempo))
    puntajes.sort(key=lambda x: x[1], reverse=True)
    puntajes = puntajes[:10]
   
    with open(ARCHIVO_PUNTAJES, 'w') as archivo:
        archivo.write("Nombre,Puntaje\n")
        for nombre, puntaje, tiempo in puntajes:
            archivo.write(f"{nombre},{puntaje},{tiempo}\n")



def leer_puntajes() -> list[tuple[str, int, int]]:
    """
    Lee los puntajes desde el archivo CSV.
    
    Devuelve:
        List[Tuple[str, int, int]]: Lista de tuplas con (nombre, puntaje).
                                   Retorna lista vacia si el archivo no existe.
    """
    puntajes = [] 

    if os.path.exists(ARCHIVO_PUNTAJES):
        with open(ARCHIVO_PUNTAJES, 'r') as archivo:
            lineas = archivo.readlines()
            for linea in lineas[1:]:  
                partes = linea.strip().split(',')
                if len(partes) == 3 and partes[1].isdigit():
                    nombre, puntaje, tiempo = partes
                    puntajes.append((nombre, int(puntaje), int(tiempo)))

    return puntajes  



def mostrar_lista_puntajes(ventana: pygame.Surface, fuente: pygame.font.Font) -> None:
    """
    Muestra la lista de los mejores puntajes en pantalla de forma responsive.
    
    La interfaz se adapta automáticamente al tamaño de la ventana, manteniendo
    proporciones y espaciado adecuados en diferentes resoluciones.
    
    Recibe:
        ventana (pygame.Surface): Superficie donde mostrar los puntajes.
        fuente (pygame.font.Font): Fuente para el texto de los puntajes.
    
    Devuelve:
        None
    """
    puntajes = leer_puntajes()
    
    ancho_ventana = ventana.get_width()
    alto_ventana = ventana.get_height()
    
    ancho_cuadro = int(ancho_ventana * 0.4)  
    alto_base = int(alto_ventana * 0.4)     
    altura_por_puntaje = int(alto_ventana * 0.05)  
    alto_cuadro = max(alto_base, int(alto_ventana * 0.15) + altura_por_puntaje * len(puntajes))
    
    cuadro_x = (ancho_ventana - ancho_cuadro) // 2
    cuadro_y = (alto_ventana - alto_cuadro) // 2
    
    cuadro = pygame.Surface((ancho_cuadro, alto_cuadro))
    cuadro.fill((230, 230, 230))
    pygame.draw.rect(cuadro, (0, 0, 0), cuadro.get_rect(), 2)
    ventana.blit(cuadro, (cuadro_x, cuadro_y))
    
    tamaño_fuente_titulo = int(ancho_ventana * 0.03) 
    fuente_titulo = pygame.font.SysFont("Verdana", tamaño_fuente_titulo, bold=True)
    titulo = "Top 10 Puntajes"
    texto_titulo = fuente_titulo.render(titulo, True, (0, 0, 0))
    x_titulo = cuadro_x + (ancho_cuadro - texto_titulo.get_width()) // 2
    y_titulo = cuadro_y + int(alto_ventana * 0.02)  
    ventana.blit(texto_titulo, (x_titulo, y_titulo))
    
    mensaje = None
    
    if not puntajes:
        mensaje = fuente.render("No hay puntajes", True, (100, 100, 100))
    else:
        colores_podio = [(255, 215, 0), (192, 192, 192), (205, 127, 50)]
        

        y = cuadro_y + int(alto_ventana * 0.08) 
        posicion = 1
        

        margen_lateral = int(ancho_cuadro * 0.02)  
        ancho_entrada = ancho_cuadro - (margen_lateral * 2)
        alto_entrada = int(alto_ventana * 0.04) 
        
        for puntaje_data in puntajes:
            nombre = puntaje_data[0]
            puntaje = puntaje_data[1]
            tiempo = puntaje_data[2]
            
            rect_puntaje = pygame.Rect(cuadro_x + margen_lateral, y, ancho_entrada, alto_entrada)
            pygame.draw.rect(ventana, (255, 255, 255), rect_puntaje)
            pygame.draw.rect(ventana, (0, 0, 0), rect_puntaje, 1)
            
            en_podio = posicion <= 3
            
            if en_podio:
                color_texto_linea = colores_podio[posicion - 1]
            else:
                color_texto_linea = (0, 0, 0)
            
            linea = f"{posicion}. {nombre[:12]} - Pts: {puntaje}"
            texto = fuente.render(linea, True, color_texto_linea)
            
            x_texto = cuadro_x + margen_lateral + int(ancho_cuadro * 0.04)
            y_texto = y + (alto_entrada - texto.get_height()) // 2
            ventana.blit(texto, (x_texto, y_texto))
            
            y += altura_por_puntaje
            posicion += 1
    
    if mensaje:
        x_msg = cuadro_x + (ancho_cuadro - mensaje.get_width()) // 2
        y_msg = cuadro_y + int(alto_ventana * 0.12)  
        ventana.blit(mensaje, (x_msg, y_msg))
    
    return


# ===============================================================================
# MUSICA Y SONIDOS
# ===============================================================================

def inicializar_musica() -> None:
    """
    Inicializa el sistema de musica y reproduce la musica de fondo en bucle.
    
    Devuelve:
        None
        
    Nota:
        - Carga la musica desde 'Musica/Musica.mp3'
        - La reproduce en bucle infinito (-1)
        - Establece el volumen al 20% (0.2)
        
    """
    pygame.mixer.init()
    pygame.mixer.music.load('Musica/Musica.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)


def cargar_sonidos() -> dict[str, pygame.mixer.Sound]:
    """
    Carga todos los efectos de sonido del juego.
    
    Devuelve:
        Dict[str, pygame.mixer.Sound]: Diccionario con los sonidos cargados:
            - "click": Sonido de click en botones
            - "victoria": Sonido de victoria
            - "derrota": Sonido de derrota
            
    Nota:
        Todos los sonidos se configuran con volumen al 30% (0.3).
        
    """
    sonidos = {
        "click": pygame.mixer.Sound('Musica/click.mp3'),
        "victoria": pygame.mixer.Sound('Musica/victoria.mp3'),
        "derrota": pygame.mixer.Sound('Musica/derrota.mp3'),
    }
   
    for s in sonidos.values():
        s.set_volume(0.3)
    return sonidos


def reproducir_sonido(sonidos: dict[str, pygame.mixer.Sound], tipo: str) -> None:
    """
    Reproduce un sonido especifico si existe en el diccionario.
    
    Recibe:
        sonidos (dict[str, pygame.mixer.Sound]): Diccionario con los sonidos cargados.
        tipo (str): Tipo de sonido a reproducir ("click", "victoria", "derrota").
        
    Devuelve:
        None
        
    """
    if tipo in sonidos:
        sonidos[tipo].play()


def cambiar_musica_de_fondo(archivo_mp3: str = 'Musica/Musica.mp3') -> None:
    """
    Cambia la musica de fondo del juego.
    
    Recibe:
        archivo_mp3 (str, optional): Ruta del archivo MP3 a reproducir. 
                                   Por defecto 'Musica/Musica.mp3'.
                                   
    Devuelve:
        None
    """
    pygame.mixer.music.stop()
    pygame.mixer.music.load(archivo_mp3)
    pygame.mixer.music.play(-1)