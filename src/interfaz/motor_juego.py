import sys
import pickle
import random
import pygame
from src.logic.entorno import EntornoCTF
from src.logic.agente import AgenteQLearning
from src.interfaz.render import dibujar_escenario, dibujar_texto
from src.interfaz.pantallas import menu_principal
from src.interfaz.constantes import *
from src.interfaz.recursos import Recursos
from config import ARCHIVO_CEREBRO

class EntornoVisual(EntornoCTF):
    def disparar_canon_visual(self):
        casillas = []
        while len(casillas) < 5:
            rx, ry = random.randint(0, self.filas - 1), random.randint(0, self.columnas - 1)
            if self.mapa[rx][ry] != 2 and (rx, ry) not in casillas: casillas.append((rx, ry))
                
        impacto = False
        if self.pos_usuario in casillas:
            self.pos_usuario = self.base_usuario
            if not self.bandera_enemigo_en_base: self.bandera_enemigo_en_base = True
            impacto = True
        if self.pos_enemigo in casillas:
            self.pos_enemigo = self.base_enemigo
            if not self.bandera_usuario_en_base: self.bandera_usuario_en_base = True
            impacto = True
            
        return impacto, casillas

def inicializar_agentes(mapa_juego):
    enemigo = AgenteQLearning()
    try:
        with open(ARCHIVO_CEREBRO, "rb") as f: enemigo.Q = pickle.load(f)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el cerebro en {ARCHIVO_CEREBRO}. Ejecuta entrenar.py primero.")
        sys.exit()
    enemigo.tau = 0.01
    return EntornoVisual(mapa_juego), enemigo

def iniciar_partida(p, ui, f, f_grande, reloj, mapa_inicial):
    env, enemigo = inicializar_agentes(mapa_inicial)
    terminado, estado, turno = False, "TURNO_USUARIO", "AZUL"

    while True:
        casillas_canon = None
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.VIDEORESIZE:
                p = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                ui.manejar_resize(e.w, e.h, env.filas, env.columnas)

            accion = None
            if estado == "TURNO_USUARIO":
                # Control con teclado
                if e.type == pygame.KEYDOWN:
                    if e.key in [pygame.K_w, pygame.K_UP]: accion = 0
                    elif e.key in [pygame.K_s, pygame.K_DOWN]: accion = 1
                    elif e.key in [pygame.K_a, pygame.K_LEFT]: accion = 2
                    elif e.key in [pygame.K_d, pygame.K_RIGHT]: accion = 3

                # Control con mouse
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if pygame.Rect(SALIR_X, SALIR_Y, SALIR_ANCHO, SALIR_ALTO).collidepoint((mx, my)):
                        mapa = menu_principal(p, ui, f, f_grande, reloj)
                        env, enemigo = inicializar_agentes(mapa)
                        terminado, estado, turno = False, "TURNO_USUARIO", "AZUL"
                        continue

                    if ui.offset_x <= mx < ui.offset_x + (env.columnas * ui.tamano_celda) and ui.offset_y <= my < ui.offset_y + (env.filas * ui.tamano_celda):
                        col, fila = (mx - ui.offset_x) // ui.tamano_celda, (my - ui.offset_y) // ui.tamano_celda
                        f_us, c_us = env.pos_usuario
                        if col == c_us and fila == f_us - 1: accion = 0
                        elif col == c_us and fila == f_us + 1: accion = 1
                        elif col == c_us - 1 and fila == f_us: accion = 2
                        elif col == c_us + 1 and fila == f_us: accion = 3

                if accion is not None:
                    dx, dy = env.diccionario_acciones[accion]
                    nx, ny = env.pos_usuario[0] + dx, env.pos_usuario[1] + dy
                    # Validar límites y muros para no cobrar turnos a lo loco
                    if 0 <= nx < env.filas and 0 <= ny < env.columnas and env.mapa[nx][ny] != 2:
                        _, terminado = env.step(accion, True)
                        if env.movimientos_usuario <= 0 or terminado:
                            estado, turno = ("TURNO_ENEMIGO", "ROJO") if not terminado else ("FIN", turno)

        if estado == "TURNO_ENEMIGO":
            dibujar_escenario(p, env, ui, f, turno)
            pygame.time.delay(400)
            accion = enemigo.elegir_accion_softmax(env.obtener_estado_relativo(False))
            _, terminado = env.step(accion, False)

            if env.movimientos_enemigo <= 0 or terminado:
                if not terminado:
                    # El cañón solo se dispara si falta alguna bandera
                    if env.canon_activo:
                        _, casillas_canon = env.disparar_canon_visual()
                        dibujar_escenario(p, env, ui, f, "CANON", casillas_canon)
                        pygame.time.delay(1000)
                    env.movimientos_usuario, env.movimientos_enemigo = 4, 4
                    estado, turno = "TURNO_USUARIO", "AZUL"
                else: estado = "FIN"

        dibujar_escenario(p, env, ui, f, turno, casillas_canon)

        if estado == "FIN":
            msg = "¡VICTORIA!" if env.pos_usuario == env.base_usuario and not env.bandera_enemigo_en_base else "DERROTA"
            img_fin = Recursos.v_img if msg == "¡VICTORIA!" else Recursos.d_img
            if img_fin: p.blit(img_fin, ((ui.ancho - 420)//2, (ui.alto - 400)//2))
            else: dibujar_texto(p, f_grande, msg, ui.ancho//2, ui.offset_y + (env.filas*ui.tamano_celda) + 25, C_BASE_US if msg=="¡VICTORIA!" else C_ENEMIGO, "centro")
            pygame.display.flip()
            
            while True:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT: pygame.quit(); sys.exit()

        reloj.tick(30)