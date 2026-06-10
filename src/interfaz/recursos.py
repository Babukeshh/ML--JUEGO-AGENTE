import pygame
import sys
import random
from config import RUTA_IMG
from src.interfaz.constantes import TAMANO_CELDA, ANCHO_PANTALLA, ALTO_PANTALLA, TABLA_ANCHO, TABLA_ALTO, SALIR_ANCHO, SALIR_ALTO

class Recursos:
    @staticmethod
    def recortar_transparencia(imagen):
        r = imagen.get_bounding_rect(min_alpha=10)
        return imagen.subsurface(r).copy() if r.width > 0 else imagen

    @staticmethod
    def escalar_turno(img, w_max, h_max):
        img = Recursos.recortar_transparencia(img)
        esc = min(w_max / img.get_width(), h_max / img.get_height())
        return pygame.transform.smoothscale(img, (max(1, int(img.get_width()*esc)), max(1, int(img.get_height()*esc))))

    @classmethod
    def cargar_todo(cls):
        try:
            cls.p_us = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "pikminazul.png")).convert_alpha(), (85, 110))
            cls.p_en = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "pikminrojo.png")).convert_alpha(), (85, 110))
            cls.t_madera = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "madera.png")).convert(), (TAMANO_CELDA, TAMANO_CELDA))
            cls.t_arbusto = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "arbusto.png")).convert_alpha(), (TAMANO_CELDA, TAMANO_CELDA))
            cls.t_muro = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "muro.png")).convert_alpha(), (TAMANO_CELDA, TAMANO_CELDA))
            cls.fondo = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "fondo.png")).convert(), (ANCHO_PANTALLA, ALTO_PANTALLA))
            cls.margen = pygame.image.load(str(RUTA_IMG / "margen.png")).convert_alpha()
            cls.tabla = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "tabla.png")).convert_alpha(), (TABLA_ANCHO, TABLA_ALTO))
            
            cls.t_azul = cls.escalar_turno(pygame.image.load(str(RUTA_IMG / "azul.png")).convert_alpha(), 90, 40)
            cls.t_rojo = cls.escalar_turno(pygame.image.load(str(RUTA_IMG / "rojo.png")).convert_alpha(), 120, 40)
            cls.t_canon = cls.escalar_turno(pygame.image.load(str(RUTA_IMG / "canon.png")).convert_alpha(), 120, 40)
            cls.pies = cls.escalar_turno(pygame.image.load(str(RUTA_IMG / "pies.png")).convert_alpha(), 50, 50)
            
            cls.v_img = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "victoria.png")).convert_alpha(), (420, 400))
            cls.d_img = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "derrota.png")).convert_alpha(), (420, 400))
            cls.b_salir = pygame.transform.smoothscale(cls.recortar_transparencia(pygame.image.load(str(RUTA_IMG / "salir.png")).convert_alpha()), (SALIR_ANCHO, SALIR_ALTO))
            
            frutas = [pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / f)).convert_alpha(), (45, 45)) for f in ["cerezas.png", "fresa.png", "granada.png", "kiwi.png", "melocoton.png"]]
            cls.f_us, cls.f_en = random.sample(frutas, 2)

            try:
                cls.f_inicio = pygame.transform.smoothscale(pygame.image.load(str(RUTA_IMG / "inicio.png")).convert(), (ANCHO_PANTALLA, ALTO_PANTALLA))
                cls.b_aleat = pygame.transform.smoothscale(cls.recortar_transparencia(pygame.image.load(str(RUTA_IMG / "mapaaleatorio.png")).convert_alpha()), (275, 150))
                cls.b_eval = pygame.transform.smoothscale(cls.recortar_transparencia(pygame.image.load(str(RUTA_IMG / "mapadeevaluacion.png")).convert_alpha()), (275, 150))
            except: cls.f_inicio, cls.b_aleat, cls.b_eval = None, None, None
        except Exception as e:
            print(f"Error cargando imágenes: {e}")
            sys.exit()