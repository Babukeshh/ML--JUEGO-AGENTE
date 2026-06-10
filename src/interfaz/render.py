import pygame
from src.interfaz.constantes import *
from src.interfaz.recursos import Recursos

def dibujar_texto(p, f, t, x, y, c=C_TEXTO, align="izq"):
    s = f.render(t, True, c)
    p.blit(s, (x - s.get_width()//2 if align=="centro" else x, y))

# --- NUEVO REPRODUCTOR DE ANIMACIONES ---
def reproducir_animacion_muerte(p, ui, posiciones_impacto):
    if not Recursos.anim_muerte or not posiciones_impacto: return
    
    # Tomamos una "fotografía" del tablero actual para dibujar el GIF encima
    fondo_temp = p.copy()
    
    # Reproducimos cada cuadro del GIF
    for frame in Recursos.anim_muerte:
        p.blit(fondo_temp, (0, 0)) # Restauramos la fotografía base
        
        # Escalamos el GIF para que cubra la celda de forma responsiva
        frame_esc = pygame.transform.smoothscale(frame, (int(ui.tamano_celda * 1.5), int(ui.tamano_celda * 1.5)))
        
        # Dibujamos la explosión en cada casilla afectada
        for (f_idx, c_idx) in posiciones_impacto:
            x = ui.offset_x + c_idx * ui.tamano_celda - (ui.tamano_celda * 0.25)
            y = ui.offset_y + f_idx * ui.tamano_celda - (ui.tamano_celda * 0.25)
            p.blit(frame_esc, (x, y))
        
        pygame.display.flip()
        pygame.time.delay(40) # Velocidad de la animación (ajusta este número si va muy rápido)

def dibujar_escenario(p, env, ui, f, turno, casillas_canon=None):
    fondo_escalado = pygame.transform.scale(Recursos.fondo, (ui.ancho, ui.alto))
    p.blit(fondo_escalado, (0, 0))
    p.blit(Recursos.b_salir, (SALIR_X, SALIR_Y))
    
    escala_tabla = min(1.0, ui.ancho / 800)
    ancho_t_act = int(TABLA_ANCHO * escala_tabla)
    alto_t_act = int(TABLA_ALTO * escala_tabla)
    
    tabla_x_dinamico = (ui.ancho - ancho_t_act) // 2
    img_tabla_esc = pygame.transform.smoothscale(Recursos.tabla, (ancho_t_act, alto_t_act))
    p.blit(img_tabla_esc, (tabla_x_dinamico, TABLA_Y))
    
    img_pies_esc = pygame.transform.smoothscale(Recursos.pies, (int(50 * escala_tabla), int(50 * escala_tabla)))
    p.blit(img_pies_esc, (tabla_x_dinamico + int(60 * escala_tabla), TABLA_Y + int(90 * escala_tabla)))
    p.blit(img_pies_esc, (tabla_x_dinamico + ancho_t_act - int(135 * escala_tabla), TABLA_Y + int(90 * escala_tabla)))
    
    img_t = Recursos.t_azul if turno == "AZUL" else Recursos.t_rojo if turno == "ROJO" else Recursos.t_canon
    w_t_act = int(img_t.get_width() * escala_tabla)
    h_t_act = int(img_t.get_height() * escala_tabla)
    img_t_esc = pygame.transform.smoothscale(img_t, (w_t_act, h_t_act))
    p.blit(img_t_esc, (tabla_x_dinamico + (ancho_t_act - w_t_act) // 2 + int(15 * escala_tabla), TABLA_Y + int(100 * escala_tabla)))

    dibujar_texto(p, f, str(env.movimientos_usuario), tabla_x_dinamico + int(125 * escala_tabla), TABLA_Y + int(100 * escala_tabla), C_USUARIO)
    if not env.bandera_enemigo_en_base: 
        dibujar_texto(p, f, "CON BANDERA", tabla_x_dinamico + int(95 * escala_tabla), TABLA_Y + int(140 * escala_tabla), C_USUARIO)
    
    dibujar_texto(p, f, str(env.movimientos_enemigo), tabla_x_dinamico + ancho_t_act - int(80 * escala_tabla), TABLA_Y + int(100 * escala_tabla), C_ENEMIGO)
    if not env.bandera_usuario_en_base: 
        dibujar_texto(p, f, "CON BANDERA", tabla_x_dinamico + ancho_t_act - int(175 * escala_tabla), TABLA_Y + int(140 * escala_tabla), C_ENEMIGO)

    grosor_dinamico = int(ui.tamano_celda * 1.5)
    w_marco = (env.columnas * ui.tamano_celda) + (grosor_dinamico * 2)
    h_marco = (env.filas * ui.tamano_celda) + (grosor_dinamico * 2)
    p.blit(pygame.transform.smoothscale(Recursos.margen, (w_marco, h_marco)), (ui.offset_x - grosor_dinamico, ui.offset_y - grosor_dinamico))

    for f_idx in range(env.filas):
        for c_idx in range(env.columnas):
            x, y = ui.offset_x + c_idx * ui.tamano_celda, ui.offset_y + f_idx * ui.tamano_celda
            t = env.mapa[f_idx][c_idx]
            textura = Recursos.t_madera if t == 0 else Recursos.t_arbusto if t == 1 else Recursos.t_muro
            
            textura = pygame.transform.smoothscale(textura, (ui.tamano_celda, ui.tamano_celda))
            p.blit(textura, (x, y))

            if casillas_canon and (f_idx, c_idx) in casillas_canon:
                pygame.draw.rect(p, C_CANON, (x, y, ui.tamano_celda, ui.tamano_celda))
            pygame.draw.rect(p, (40, 25, 15), (x, y, ui.tamano_celda, ui.tamano_celda), 2)

    if env.bandera_usuario_en_base: 
        f_us_esc = pygame.transform.smoothscale(Recursos.f_us, (int(ui.tamano_celda*0.75), int(ui.tamano_celda*0.75)))
        p.blit(f_us_esc, (ui.offset_x + env.base_usuario[1] * ui.tamano_celda + (ui.tamano_celda*0.12), ui.offset_y + env.base_usuario[0] * ui.tamano_celda + (ui.tamano_celda*0.12)))
    
    if env.bandera_enemigo_en_base: 
        f_en_esc = pygame.transform.smoothscale(Recursos.f_en, (int(ui.tamano_celda*0.75), int(ui.tamano_celda*0.75)))
        p.blit(f_en_esc, (ui.offset_x + env.base_enemigo[1] * ui.tamano_celda + (ui.tamano_celda*0.12), ui.offset_y + env.base_enemigo[0] * ui.tamano_celda + (ui.tamano_celda*0.12)))

    uy, ux = env.pos_usuario
    p_us_esc = pygame.transform.smoothscale(Recursos.p_us, (int(ui.tamano_celda*1.4), int(ui.tamano_celda*1.8)))
    p.blit(p_us_esc, (ui.offset_x + ux * ui.tamano_celda - (ui.tamano_celda*0.2), ui.offset_y + uy * ui.tamano_celda - (ui.tamano_celda*0.75)))
    
    ey, ex = env.pos_enemigo
    p_en_esc = pygame.transform.smoothscale(Recursos.p_en, (int(ui.tamano_celda*1.4), int(ui.tamano_celda*1.8)))
    p.blit(p_en_esc, (ui.offset_x + ex * ui.tamano_celda - (ui.tamano_celda*0.2), ui.offset_y + ey * ui.tamano_celda - (ui.tamano_celda*0.75)))

    pygame.display.flip()