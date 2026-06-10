import sys
import pygame
from src.interfaz.constantes import *
from src.interfaz.recursos import Recursos
from src.interfaz.render import dibujar_texto
from src.logic.mapas import GestorEscenarios
from config import MAPA_EVALUACION

def menu_principal(p, ui, f, f_grande, reloj):
    esperando, mapa = True, None
    gestor = GestorEscenarios()

    while esperando:
        if Recursos.f_inicio: p.blit(Recursos.f_inicio, (0, 0))
        else: p.fill(C_FONDO)

        mx, my = pygame.mouse.get_pos()
        r_b1, r_b2 = pygame.Rect(130, 700, 275, 150), pygame.Rect(480, 700, 275, 150)

        if Recursos.b_aleat and Recursos.b_eval:
            p.blit(Recursos.b_aleat, (130, 700))
            p.blit(Recursos.b_eval, (480, 700))
        else:
            pygame.draw.rect(p, C_BOTON_HOVER if r_b1.collidepoint((mx, my)) else C_BOTON, r_b1, border_radius=10)
            dibujar_texto(p, f, "Aleatorio", r_b1.x + 130, r_b1.y + 60, align="centro")
            pygame.draw.rect(p, C_BOTON_HOVER if r_b2.collidepoint((mx, my)) else C_BOTON, r_b2, border_radius=10)
            dibujar_texto(p, f, "Evaluación", r_b2.x + 130, r_b2.y + 60, align="centro")

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.VIDEORESIZE:
                p = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                ui.manejar_resize(e.w, e.h)
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                if r_b1.collidepoint((mx, my)):
                    while mapa is None:
                        prueba = gestor.generar_mapa_aleatorio()
                        if gestor.validar_mapa_astar(prueba): mapa = prueba
                    esperando = False
                elif r_b2.collidepoint((mx, my)):
                    mapa, esperando = MAPA_EVALUACION, False

        pygame.display.flip()
        reloj.tick(30)
    return mapa