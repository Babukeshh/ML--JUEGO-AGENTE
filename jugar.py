import sys
import os
import pickle
import random
import pygame

from escenarios import GestorEscenarios, EntornoCTF, AgenteQLearning, FILAS, COLUMNAS

MAPA_EVALUACION = [
    [0, 0, 1, 1, 0, 2, 0, 0, 0, 0],
    [0, 2, 2, 1, 0, 2, 1, 2, 2, 0],
    [0, 0, 2, 0, 0, 0, 1, 0, 2, 0],
    [1, 0, 2, 0, 2, 2, 2, 0, 0, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 1, 1],
    [0, 2, 2, 0, 2, 0, 2, 2, 2, 0],
    [0, 2, 0, 0, 0, 0, 0, 0, 2, 0],
    [0, 2, 1, 2, 2, 2, 2, 0, 2, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 2, 0, 1, 1, 0, 0]
]

TAMANO_CELDA = 60
MARGEN_SUP = 40
MARGEN_INF = 120
TABLERO_ANCHO = COLUMNAS * TAMANO_CELDA
TABLERO_ALTO = FILAS * TAMANO_CELDA

# Ventana más alta, no más ancha.
# El ancho se mantiene compacto para que solo quepa el tablero con su marco.
GROSOR_MARCO = 90
ANCHO_PANTALLA = TABLERO_ANCHO + (GROSOR_MARCO * 2) + 120
ALTO_PANTALLA = 850

# Tabla de turnos sin estirar demasiado.
# Se mantiene más alta para respetar mejor su proporción original.
TABLA_ANCHO = 480
TABLA_ALTO = 270
TABLA_X = (ANCHO_PANTALLA - TABLA_ANCHO) // 2
TABLA_Y = -35

OFFSET_X = (ANCHO_PANTALLA - TABLERO_ANCHO) // 2
OFFSET_Y = 170

C_FONDO = (30, 30, 30)
C_NORMAL = (220, 220, 220)
C_ARENA = (237, 201, 175)
C_OBSTACULO = (60, 60, 60)
C_USUARIO = (255, 255, 255)
C_ENEMIGO = (255, 255, 255)
C_BASE_US = (0, 255, 255)
C_BASE_EN = (255, 0, 255)
C_CANON = (0, 0, 0)
C_TEXTO = (255, 255, 255)
C_BOTON = (70, 130, 180)
C_BOTON_HOVER = (100, 149, 237)

textura_arbusto = None
textura_madera = None
textura_muro = None
pikmin_usuario = None
pikmin_enemigo = None
fruta_usuario = None
fruta_enemigo = None
imagen_fondo = None
imagen_margen = None
tabla_turnos = None
img_turno_azul = None
img_turno_rojo = None
img_turno_canon = None
img_pies = None
img_victoria = None
img_derrota = None
turno_actual = "AZUL"


class EntornoVisual(EntornoCTF):
    def disparar_canon_visual(self):
        if not self.canon_activo:
            return False, []

        casillas_afectadas = []

        while len(casillas_afectadas) < 5:
            rx = random.randint(0, self.filas - 1)
            ry = random.randint(0, self.columnas - 1)

            if self.mapa[rx][ry] != 2 and (rx, ry) not in casillas_afectadas:
                casillas_afectadas.append((rx, ry))

        impacto = False

        if self.pos_usuario in casillas_afectadas:
            self.pos_usuario = self.base_usuario
            if not self.bandera_enemigo_en_base:
                self.bandera_enemigo_en_base = True
            impacto = True

        if self.pos_enemigo in casillas_afectadas:
            self.pos_enemigo = self.base_enemigo
            if not self.bandera_usuario_en_base:
                self.bandera_usuario_en_base = True
            impacto = True

        return impacto, casillas_afectadas


def dibujar_texto(pantalla, fuente, texto, x, y, color=C_TEXTO):
    superficie = fuente.render(texto, True, color)
    pantalla.blit(superficie, (x, y))


def recortar_transparencia(imagen):
    """Recorta los bordes transparentes de una imagen PNG."""
    rect = imagen.get_bounding_rect(min_alpha=10)

    if rect.width == 0 or rect.height == 0:
        return imagen

    return imagen.subsurface(rect).copy()


def preparar_imagen_turno(imagen, ancho_max=90, alto_max=30):
    """Recorta y escala una imagen de turno sin deformarla."""
    imagen = recortar_transparencia(imagen)
    ancho_original = imagen.get_width()
    alto_original = imagen.get_height()

    escala = min(ancho_max / ancho_original, alto_max / alto_original)
    nuevo_ancho = max(1, int(ancho_original * escala))
    nuevo_alto = max(1, int(alto_original * escala))

    return pygame.transform.smoothscale(imagen, (nuevo_ancho, nuevo_alto))


def dibujar_imagen_turno(pantalla):
    """Dibuja Azul, Rojo o Cañón justo debajo del texto 'TURNO DEL'."""
    if turno_actual == "AZUL":
        imagen = img_turno_azul
    elif turno_actual == "ROJO":
        imagen = img_turno_rojo
    else:
        imagen = img_turno_canon

    if imagen is None:
        return

    x_turno = TABLA_X + (TABLA_ANCHO - imagen.get_width()) // 2 + 15
    y_turno = TABLA_Y + 100

    pantalla.blit(imagen, (x_turno, y_turno))


def menu_principal(pantalla, fuente, fuente_grande):
    esperando_seleccion = True
    mapa_seleccionado = None

    ancho_boton = 400
    alto_boton = 60
    x_boton = (ANCHO_PANTALLA // 2) - (ancho_boton // 2)
    y_boton1 = ALTO_PANTALLA // 2 - 40
    y_boton2 = ALTO_PANTALLA // 2 + 60

    boton_aleatorio = pygame.Rect(x_boton, y_boton1, ancho_boton, alto_boton)
    boton_evaluacion = pygame.Rect(x_boton, y_boton2, ancho_boton, alto_boton)

    gestor = GestorEscenarios()

    while esperando_seleccion:
        pantalla.fill(C_FONDO)
        mx, my = pygame.mouse.get_pos()

        dibujar_texto(
            pantalla,
            fuente_grande,
            "BATALLA CTF: Q-LEARNING",
            ANCHO_PANTALLA // 2 - 220,
            MARGEN_SUP * 2,
            C_BASE_US
        )

        dibujar_texto(
            pantalla,
            fuente,
            "Selecciona el modo de juego:",
            ANCHO_PANTALLA // 2 - 130,
            MARGEN_SUP * 4,
            C_TEXTO
        )

        color_b1 = C_BOTON_HOVER if boton_aleatorio.collidepoint((mx, my)) else C_BOTON
        pygame.draw.rect(pantalla, color_b1, boton_aleatorio, border_radius=10)
        dibujar_texto(pantalla, fuente, "1. Jugar en Mapa Aleatorio", x_boton + 70, y_boton1 + 15)

        color_b2 = C_BOTON_HOVER if boton_evaluacion.collidepoint((mx, my)) else C_BOTON
        pygame.draw.rect(pantalla, color_b2, boton_evaluacion, border_radius=10)
        dibujar_texto(pantalla, fuente, "2. Jugar en Mapa de Evaluación", x_boton + 50, y_boton2 + 15)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_aleatorio.collidepoint((mx, my)):
                    print("Generando y validando un mapa nuevo mediante A*...")

                    while mapa_seleccionado is None:
                        prueba = gestor.generar_mapa_aleatorio()
                        if gestor.validar_mapa_astar(prueba):
                            mapa_seleccionado = prueba

                    esperando_seleccion = False

                elif boton_evaluacion.collidepoint((mx, my)):
                    print("Cargando el Mapa de Evaluación precargado...")
                    mapa_seleccionado = MAPA_EVALUACION

                    if not gestor.validar_mapa_astar(mapa_seleccionado):
                        print("ADVERTENCIA: El mapa de evaluación no tiene un camino válido según A*.")

                    esperando_seleccion = False

        pygame.display.flip()

    return mapa_seleccionado



def dibujar_tabla_turnos(pantalla, env, fuente):
    """Dibuja la imagen superior de turnos y escribe el estado dentro de cada cuadro."""
    if tabla_turnos is None:
        return

    pantalla.blit(tabla_turnos, (TABLA_X, TABLA_Y))

    # Pies encima de la tabla de turnos.
    # Modifica estos valores si después quieres moverlo:
    # PIES_X = TABLA_X + 210  -> izquierda/derecha
    # PIES_Y = TABLA_Y + 10   -> arriba/abajo
    if img_pies is not None:
    # Pie dentro del cuadro azul
        pantalla.blit(img_pies, (TABLA_X + 60, TABLA_Y + 90))

    # Pie dentro del cuadro rojo
        pantalla.blit(img_pies, (TABLA_X + TABLA_ANCHO - 135, TABLA_Y + 90))

    dibujar_imagen_turno(pantalla)

    estado_us = "" if not env.bandera_enemigo_en_base else ""
    estado_en = "" if not env.bandera_usuario_en_base else ""

    # Textos dentro del cuadro azul.
    dibujar_texto(
        pantalla,
        fuente,
        f"{env.movimientos_usuario}",
        TABLA_X + 125,
        TABLA_Y + 100,
        C_USUARIO
    )

    if estado_us:
        dibujar_texto(
            pantalla,
            fuente,
            estado_us,
            TABLA_X + 95,
            TABLA_Y + 140,
            C_USUARIO
        )

    # Textos dentro del cuadro rojo.
    dibujar_texto(
        pantalla,
        fuente,
        f"{env.movimientos_enemigo}",
        TABLA_X + TABLA_ANCHO - 80,
        TABLA_Y + 100,
        C_ENEMIGO
    )

    if estado_en:
        dibujar_texto(
            pantalla,
            fuente,
            estado_en,
            TABLA_X + TABLA_ANCHO - 175,
            TABLA_Y + 140,
            C_ENEMIGO
        )

def dibujar_marco_tablero(pantalla):
    if imagen_margen is None:
        return

    marco_w = TABLERO_ANCHO + (GROSOR_MARCO * 2)
    marco_h = TABLERO_ALTO + (GROSOR_MARCO * 2)
    marco_x = OFFSET_X - GROSOR_MARCO
    marco_y = OFFSET_Y - GROSOR_MARCO

    marco = pygame.transform.smoothscale(imagen_margen, (marco_w, marco_h))
    pantalla.blit(marco, (marco_x, marco_y))


def inicializar_juego(mapa_juego):
    enemigo = AgenteQLearning()

    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_cerebro = os.path.join(carpeta_actual, "agente_enemigo.pkl")

    try:
        with open(ruta_cerebro, "rb") as archivo:
            enemigo.Q = pickle.load(archivo)
        print("Cerebro de la IA cargado correctamente.")
        print(f"Ruta usada: {ruta_cerebro}")

    except FileNotFoundError:
        print(f"ERROR: No se encontró el cerebro en: {ruta_cerebro}")
        print("Verifica que agente_enemigo.pkl esté en la misma carpeta que jugar.py.")
        sys.exit()

    enemigo.tau = 0.01

    env = EntornoVisual(mapa_juego)
    return env, enemigo


def dibujar_escenario(pantalla, env, fuente, casillas_canon=None):
    if imagen_fondo is not None:
        pantalla.blit(imagen_fondo, (0, 0))
    else:
        pantalla.fill(C_FONDO)

    dibujar_tabla_turnos(pantalla, env, fuente)
    dibujar_marco_tablero(pantalla)

    for fila in range(env.filas):
        for col in range(env.columnas):
            x = OFFSET_X + col * TAMANO_CELDA
            y = OFFSET_Y + fila * TAMANO_CELDA

            tipo = env.mapa[fila][col]

            # tipo 0 = casilla normal, cuesta 1 movimiento.
            # Aquí usamos la textura de madera.
            if tipo == 0:
                pantalla.blit(textura_madera, (x, y))

            # tipo 1 = arbusto, cuesta 2 movimientos.
            elif tipo == 1:
                pantalla.blit(textura_arbusto, (x, y))

            # tipo 2 = muro/obstáculo, no se puede pasar.
            else:
                pantalla.blit(textura_muro, (x, y))

            # Si el cañón afecta una casilla, se pinta encima.
            if casillas_canon and (fila, col) in casillas_canon:
                pygame.draw.rect(
                    pantalla,
                    C_CANON,
                    (x, y, TAMANO_CELDA, TAMANO_CELDA)
                )

            # Borde de cada celda.
            pygame.draw.rect(
                pantalla,
                (40, 25, 15),
                (x, y, TAMANO_CELDA, TAMANO_CELDA),
                2
            )

    if env.bandera_usuario_en_base:
        x_fruta_usuario = OFFSET_X + env.base_usuario[1] * TAMANO_CELDA + (TAMANO_CELDA // 2) - (45 // 2)
        y_fruta_usuario = OFFSET_Y + env.base_usuario[0] * TAMANO_CELDA + (TAMANO_CELDA // 2) - (45 // 2)
        pantalla.blit(fruta_usuario, (x_fruta_usuario, y_fruta_usuario))

    if env.bandera_enemigo_en_base:
        x_fruta_enemigo = OFFSET_X + env.base_enemigo[1] * TAMANO_CELDA + (TAMANO_CELDA // 2) - (45 // 2)
        y_fruta_enemigo = OFFSET_Y + env.base_enemigo[0] * TAMANO_CELDA + (TAMANO_CELDA // 2) - (45 // 2)
        pantalla.blit(fruta_enemigo, (x_fruta_enemigo, y_fruta_enemigo))

    uy, ux = env.pos_usuario

    x_usuario = OFFSET_X + ux * TAMANO_CELDA + (TAMANO_CELDA // 2) - (85 // 2)
    y_usuario = OFFSET_Y + uy * TAMANO_CELDA - 45

    pantalla.blit(
        pikmin_usuario,
        (x_usuario, y_usuario)
    )

    ey, ex = env.pos_enemigo

    x_enemigo = OFFSET_X + ex * TAMANO_CELDA + (TAMANO_CELDA // 2) - (85 // 2)
    y_enemigo = OFFSET_Y + ey * TAMANO_CELDA - 45

    pantalla.blit(
        pikmin_enemigo,
        (x_enemigo, y_enemigo)
    )

    if env.canon_activo:
        dibujar_texto(
            pantalla,
            fuente,
            "",
            OFFSET_X,
            OFFSET_Y + TABLERO_ALTO + 25,
            C_CANON
        )

    pygame.display.flip()


def cargar_imagenes_pikmin():
    global pikmin_usuario, pikmin_enemigo, textura_madera, textura_arbusto, textura_muro, fruta_usuario, fruta_enemigo, imagen_fondo, imagen_margen, tabla_turnos, img_turno_azul, img_turno_rojo, img_turno_canon, img_pies, img_victoria, img_derrota

    carpeta_actual = os.path.dirname(os.path.abspath(__file__))

    ruta_azul = os.path.join(carpeta_actual, "pikminazul.png")
    ruta_rojo = os.path.join(carpeta_actual, "pikminrojo.png")
    ruta_madera = os.path.join(carpeta_actual, "madera.png")
    ruta_arbusto = os.path.join(carpeta_actual, "arbusto.png")
    ruta_muro = os.path.join(carpeta_actual, "muro.png")
    ruta_fondo = os.path.join(carpeta_actual, "fondo.png")
    ruta_margen = os.path.join(carpeta_actual, "margen.png")
    ruta_tabla = os.path.join(carpeta_actual, "tabla.png")
    ruta_turno_azul = os.path.join(carpeta_actual, "azul.png")
    ruta_turno_rojo = os.path.join(carpeta_actual, "rojo.png")
    ruta_turno_canon = os.path.join(carpeta_actual, "canon.png")
    ruta_pies = os.path.join(carpeta_actual, "pies.png")
    ruta_victoria = os.path.join(carpeta_actual, "victoria.png")
    ruta_derrota = os.path.join(carpeta_actual, "derrota.png")

    archivos_frutas = [
        "cerezas.png",
        "fresa.png",
        "granada.png",
        "kiwi.png",
        "melocoton.png"
    ]

    try:
        pikmin_usuario = pygame.image.load(ruta_azul).convert_alpha()
        pikmin_enemigo = pygame.image.load(ruta_rojo).convert_alpha()
        textura_madera = pygame.image.load(ruta_madera).convert()
        textura_arbusto = pygame.image.load(ruta_arbusto).convert_alpha()
        textura_muro = pygame.image.load(ruta_muro).convert_alpha()
        imagen_fondo = pygame.image.load(ruta_fondo).convert()
        imagen_margen = pygame.image.load(ruta_margen).convert_alpha()
        tabla_turnos = pygame.image.load(ruta_tabla).convert_alpha()
        img_turno_azul = pygame.image.load(ruta_turno_azul).convert_alpha()
        img_turno_rojo = pygame.image.load(ruta_turno_rojo).convert_alpha()
        img_turno_canon = pygame.image.load(ruta_turno_canon).convert_alpha()
        img_pies = pygame.image.load(ruta_pies).convert_alpha()
        img_victoria = pygame.image.load(ruta_victoria).convert_alpha()
        img_derrota = pygame.image.load(ruta_derrota).convert_alpha()

        frutas_cargadas = []
        for nombre_fruta in archivos_frutas:
            ruta_fruta = os.path.join(carpeta_actual, nombre_fruta)
            fruta = pygame.image.load(ruta_fruta).convert_alpha()
            fruta = pygame.transform.smoothscale(fruta, (45, 45))
            frutas_cargadas.append(fruta)

        fruta_usuario, fruta_enemigo = random.sample(frutas_cargadas, 2)

        pikmin_usuario = pygame.transform.smoothscale(pikmin_usuario, (85, 110))
        pikmin_enemigo = pygame.transform.smoothscale(pikmin_enemigo, (85, 110))
        textura_madera = pygame.transform.smoothscale( textura_madera, (TAMANO_CELDA, TAMANO_CELDA))
        textura_arbusto = pygame.transform.smoothscale(textura_arbusto, (TAMANO_CELDA, TAMANO_CELDA))
        textura_muro = pygame.transform.smoothscale(textura_muro, (TAMANO_CELDA, TAMANO_CELDA))
        imagen_fondo = pygame.transform.smoothscale(imagen_fondo, (ANCHO_PANTALLA, ALTO_PANTALLA))
        tabla_turnos = pygame.transform.smoothscale(tabla_turnos, (TABLA_ANCHO, TABLA_ALTO))
        img_turno_azul = preparar_imagen_turno(
            img_turno_azul,
            ancho_max=90,
            alto_max=40
        )

        img_turno_rojo = preparar_imagen_turno(
            img_turno_rojo,
            ancho_max=120,
            alto_max=40
        )

        img_turno_canon = preparar_imagen_turno(
            img_turno_canon,
            ancho_max=120,
            alto_max=40

            
        )

        img_pies = preparar_imagen_turno(
            img_pies,
            ancho_max=50,
            alto_max=50
        )

        img_victoria = pygame.transform.smoothscale(img_victoria, (420, 400))
        img_derrota = pygame.transform.smoothscale(img_derrota, (420, 400))
        
        print("Imágenes, texturas y frutas cargadas correctamente.")

    except FileNotFoundError as error:
        print("ERROR: No se encontró una imagen necesaria.")
        print("Debes tener estos archivos en la misma carpeta que jugar.py:")
        print("- pikminazul.png")
        print("- pikminrojo.png")
        print("- madera.png")
        print("- arbusto.png")
        print("- muro.png")
        print("- fondo.png")
        print("- margen.png")
        print("- tabla.png")
        print("- azul.png")
        print("- rojo.png")
        print("- canon.png")
        print("- victoria.png")
        print("- derrota.png")
        print("- cerezas.png")
        print("- fresa.png")
        print("- granada.png")
        print("- kiwi.png")
        print("- melocoton.png")
        print(f"Detalle: {error}")
        sys.exit()


def main():
    global turno_actual

    pygame.init()

    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("CTF Q-Learning")

    fuente = pygame.font.SysFont("Aptos Slab Black", 32, bold=True)
    fuente_grande = pygame.font.SysFont("Aptos Slab Black", 40, bold=True)
    reloj = pygame.time.Clock()

    cargar_imagenes_pikmin()

    mapa_juego = menu_principal(pantalla, fuente, fuente_grande)

    env, enemigo = inicializar_juego(mapa_juego)

    terminado = False
    estado_juego = "TURNO_USUARIO"
    turno_actual = "AZUL"

    while True:
        casillas_canon_actual = None

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and estado_juego == "TURNO_USUARIO":
                mx, my = pygame.mouse.get_pos()

                if OFFSET_X <= mx < OFFSET_X + TABLERO_ANCHO and OFFSET_Y <= my < OFFSET_Y + TABLERO_ALTO:
                    col_click = (mx - OFFSET_X) // TAMANO_CELDA
                    fila_click = (my - OFFSET_Y) // TAMANO_CELDA

                    fila_us, col_us = env.pos_usuario
                    accion = None

                    if col_click == col_us and fila_click == fila_us - 1:
                        accion = 0
                    elif col_click == col_us and fila_click == fila_us + 1:
                        accion = 1
                    elif col_click == col_us - 1 and fila_click == fila_us:
                        accion = 2
                    elif col_click == col_us + 1 and fila_click == fila_us:
                        accion = 3

                    if accion is not None:
                        _, terminado = env.step(accion, es_turno_usuario=True)

                        if env.movimientos_usuario <= 0 or terminado:
                            if not terminado:
                                turno_actual = "ROJO"
                                estado_juego = "TURNO_ENEMIGO"
                            else:
                                estado_juego = "FIN"

        if estado_juego == "TURNO_ENEMIGO":
            dibujar_escenario(pantalla, env, fuente)
            pygame.time.delay(400)

            estado_en = env.obtener_estado_relativo(es_usuario=False)
            accion = enemigo.elegir_accion_softmax(estado_en)
            _, terminado = env.step(accion, es_turno_usuario=False)

            if env.movimientos_enemigo <= 0 or terminado:
                if not terminado:
                    impacto, casillas_canon_actual = env.disparar_canon_visual()

                    if casillas_canon_actual:
                        turno_actual = "CANON"
                        dibujar_escenario(pantalla, env, fuente, casillas_canon_actual)
                        pygame.time.delay(1000)

                    env.movimientos_usuario = 4
                    env.movimientos_enemigo = 4
                    turno_actual = "AZUL"
                    estado_juego = "TURNO_USUARIO"
                else:
                    estado_juego = "FIN"

        dibujar_escenario(pantalla, env, fuente, casillas_canon_actual)

        if estado_juego == "FIN":
            msg = "¡VICTORIA!" if env.pos_usuario == env.base_usuario and not env.bandera_enemigo_en_base else "DERROTA"
            color_msg = C_BASE_US if msg == "¡VICTORIA!" else C_ENEMIGO

            imagen_final = img_victoria if msg == "¡VICTORIA!" else img_derrota

            if imagen_final is not None:
                x_final = (ANCHO_PANTALLA - imagen_final.get_width()) // 2
                y_final = (ALTO_PANTALLA - imagen_final.get_height()) // 2
                pantalla.blit(imagen_final, (x_final, y_final))
            else:
                dibujar_texto(
                    pantalla,
                    fuente_grande,
                    msg,
                    ANCHO_PANTALLA // 2 - 90,
                    OFFSET_Y + TABLERO_ALTO + 25,
                    color_msg
                )

            pygame.display.flip()

            esperando = True
            while esperando:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

        reloj.tick(30)


if __name__ == "__main__":
    main()