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
        if Recursos.f_inicio: 
            fondo_escalado = pygame.transform.scale(Recursos.f_inicio, (ui.ancho, ui.alto))
            p.blit(fondo_escalado, (0, 0))
        else: 
            p.fill(C_FONDO)

        mx, my = pygame.mouse.get_pos()
        
        ancho_boton, alto_boton = 275, 150
        espacio_entre_botones = 50
        ancho_total_botones = (ancho_boton * 2) + espacio_entre_botones
        
        pos_x_base = (ui.ancho - ancho_total_botones) // 2
        pos_y_botones = ui.alto - alto_boton - 50 

        r_b1 = pygame.Rect(pos_x_base, pos_y_botones, ancho_boton, alto_boton)
        r_b2 = pygame.Rect(pos_x_base + ancho_boton + espacio_entre_botones, pos_y_botones, ancho_boton, alto_boton)

        if Recursos.b_aleat and Recursos.b_eval:
            p.blit(pygame.transform.scale(Recursos.b_aleat, (ancho_boton, alto_boton)), (r_b1.x, r_b1.y))
            p.blit(pygame.transform.scale(Recursos.b_eval, (ancho_boton, alto_boton)), (r_b2.x, r_b2.y))
        else:
            pygame.draw.rect(p, C_BOTON_HOVER if r_b1.collidepoint((mx, my)) else C_BOTON, r_b1, border_radius=10)
            dibujar_texto(p, f, "Aleatorio", r_b1.centerx, r_b1.centery - 15, align="centro")
            pygame.draw.rect(p, C_BOTON_HOVER if r_b2.collidepoint((mx, my)) else C_BOTON, r_b2, border_radius=10)
            dibujar_texto(p, f, "Evaluación", r_b2.centerx, r_b2.centery - 15, align="centro")

        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            if e.type == pygame.VIDEORESIZE:
                w_nuevo = max(e.w, 700)
                h_nuevo = max(e.h, 750)
                p = pygame.display.set_mode((w_nuevo, h_nuevo), pygame.RESIZABLE)
                ui.manejar_resize(w_nuevo, h_nuevo)
                
            if e.type == pygame.MOUSEBUTTONDOWN:
                if r_b1.collidepoint((mx, my)):
                    if Recursos.sonidos_cargados: Recursos.s_boton.play() # <-- EFECTO AL CLIC
                    while mapa is None:
                        prueba = gestor.generar_mapa_aleatorio()
                        if gestor.validar_mapa_astar(prueba): mapa = prueba
                    esperando = False
                elif r_b2.collidepoint((mx, my)):
                    if Recursos.sonidos_cargados: Recursos.s_boton.play() # <-- EFECTO AL CLIC
                    mapa, esperando = MAPA_EVALUACION, False

        pygame.display.flip()
        reloj.tick(30)
        
    return mapa