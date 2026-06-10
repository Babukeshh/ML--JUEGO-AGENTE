import pygame
import sys
import random
from config import RUTA_IMG, RUTA_AUDIO
from src.interfaz.constantes import TAMANO_CELDA, ANCHO_PANTALLA, ALTO_PANTALLA, TABLA_ANCHO, TABLA_ALTO, SALIR_ANCHO, SALIR_ALTO

class Recursos:
    # Variables estáticas para los sonidos
    s_paso_normal = None
    s_paso_arena = None
    s_canon = None
    s_pikmin = None
    s_fruta = None
    s_victoria = None
    s_derrota = None
    sonidos_cargados = False

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
        # --- CARGA DE AUDIO ---
        try:
            pygame.mixer.init()
            cls.s_paso_normal = pygame.mixer.Sound(str(RUTA_AUDIO / "paso_1.wav"))
            cls.s_paso_arena = pygame.mixer.Sound(str(RUTA_AUDIO / "paso_2.wav"))
            cls.s_canon = pygame.mixer.Sound(str(RUTA_AUDIO / "canon.wav"))
            cls.s_pikmin = pygame.mixer.Sound(str(RUTA_AUDIO / "atrapar_pikmin.wav"))
            cls.s_fruta = pygame.mixer.Sound(str(RUTA_AUDIO / "atrapar_fruta.wav"))
            cls.s_victoria = pygame.mixer.Sound(str(RUTA_AUDIO / "victoria.wav"))
            cls.s_derrota = pygame.mixer.Sound(str(RUTA_AUDIO / "derrota.wav"))
            
            # Ajuste de volumen
            cls.s_paso_normal.set_volume(0.6)
            cls.s_paso_arena.set_volume(0.6)
            cls.s_canon.set_volume(0.8)
            cls.s_pikmin.set_volume(0.8)
            
            # Música de fondo
            pygame.mixer.music.load(str(RUTA_AUDIO / "musica_fondo.wav"))
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1) # -1 significa Bucle Infinito
            
            cls.sonidos_cargados = True
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar los sonidos ({e})")
            cls.sonidos_cargados = False

        # --- CARGA DE IMÁGENES ---
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
            except: 
                cls.f_inicio, cls.b_aleat, cls.b_eval = None, None, None
        except Exception as e:
            print(f"Error cargando imágenes: {e}")
            sys.exit()