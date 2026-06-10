import pygame
from src.interfaz.constantes import *
from src.interfaz.recursos import Recursos

def dibujar_texto(p, f, t, x, y, c=C_TEXTO, align="izq"):
    s = f.render(t, True, c)
    p.blit(s, (x - s.get_width()//2 if align=="centro" else x, y))

def dibujar_escenario(p, env, ui, f, turno, casillas_canon=None):
    p.blit(Recursos.fondo, (0, 0))
    p.blit(Recursos.b_salir, (SALIR_X, SALIR_Y))
    p.blit(Recursos.tabla, (TABLA_X, TABLA_Y))
    p.blit(Recursos.pies, (TABLA_X + 60, TABLA_Y + 90))
    p.blit(Recursos.pies, (TABLA_X + TABLA_ANCHO - 135, TABLA_Y + 90))
    
    img_t = Recursos.t_azul if turno == "AZUL" else Recursos.t_rojo if turno == "ROJO" else Recursos.t_canon
    p.blit(img_t, (TABLA_X + (TABLA_ANCHO - img_t.get_width()) // 2 + 15, TABLA_Y + 100))

    dibujar_texto(p, f, str(env.movimientos_usuario), TABLA_X + 125, TABLA_Y + 100, C_USUARIO)
    if not env.bandera_enemigo_en_base: dibujar_texto(p, f, " ", TABLA_X + 95, TABLA_Y + 140, C_USUARIO)
    
    dibujar_texto(p, f, str(env.movimientos_enemigo), TABLA_X + TABLA_ANCHO - 80, TABLA_Y + 100, C_ENEMIGO)
    if not env.bandera_usuario_en_base: dibujar_texto(p, f, " ", TABLA_X + TABLA_ANCHO - 175, TABLA_Y + 140, C_ENEMIGO)

    w_marco = (env.columnas * ui.tamano_celda) + (GROSOR_MARCO * 2)
    h_marco = (env.filas * ui.tamano_celda) + (GROSOR_MARCO * 2)
    p.blit(pygame.transform.smoothscale(Recursos.margen, (w_marco, h_marco)), (ui.offset_x - GROSOR_MARCO, ui.offset_y - GROSOR_MARCO))

    for f_idx in range(env.filas):
        for c_idx in range(env.columnas):
            x, y = ui.offset_x + c_idx * ui.tamano_celda, ui.offset_y + f_idx * ui.tamano_celda
            t = env.mapa[f_idx][c_idx]
            textura = Recursos.t_madera if t == 0 else Recursos.t_arbusto if t == 1 else Recursos.t_muro
            
            # Escalar textura en caso de pantalla responsiva
            if ui.tamano_celda != TAMANO_CELDA: textura = pygame.transform.smoothscale(textura, (ui.tamano_celda, ui.tamano_celda))
            p.blit(textura, (x, y))

            if casillas_canon and (f_idx, c_idx) in casillas_canon:
                pygame.draw.rect(p, C_CANON, (x, y, ui.tamano_celda, ui.tamano_celda))
            pygame.draw.rect(p, (40, 25, 15), (x, y, ui.tamano_celda, ui.tamano_celda), 2)

    if env.bandera_usuario_en_base: p.blit(Recursos.f_us, (ui.offset_x + env.base_usuario[1] * ui.tamano_celda + 7, ui.offset_y + env.base_usuario[0] * ui.tamano_celda + 7))
    if env.bandera_enemigo_en_base: p.blit(Recursos.f_en, (ui.offset_x + env.base_enemigo[1] * ui.tamano_celda + 7, ui.offset_y + env.base_enemigo[0] * ui.tamano_celda + 7))

    uy, ux = env.pos_usuario
    p.blit(Recursos.p_us, (ui.offset_x + ux * ui.tamano_celda - 12, ui.offset_y + uy * ui.tamano_celda - 45))
    ey, ex = env.pos_enemigo
    p.blit(Recursos.p_en, (ui.offset_x + ex * ui.tamano_celda - 12, ui.offset_y + ey * ui.tamano_celda - 45))

    pygame.display.flip()