import sys
from pathlib import Path
import pygame

# Añadimos la raíz al PATH para evitar errores de importación
sys.path.append(str(Path(__file__).resolve().parent))

from src.interfaz.constantes import ANCHO_PANTALLA, ALTO_PANTALLA
from src.interfaz.gestor_ui import GestorUI
from src.interfaz.recursos import Recursos
from src.interfaz.pantallas import menu_principal
from src.interfaz.motor_juego import iniciar_partida

def main():
    # Pre-inicializamos el mixer con un buffer pequeño (512) ANTES de iniciar pygame
    pygame.mixer.pre_init(44100, -16, 2, 512) 
    pygame.init()
    
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.RESIZABLE)
    pygame.display.set_caption("CTF Q-Learning Inteligente")
    
    fuente = pygame.font.SysFont("Aptos Slab Black", 32, bold=True)
    fuente_grande = pygame.font.SysFont("Aptos Slab Black", 40, bold=True)
    reloj = pygame.time.Clock()
    ui = GestorUI(ANCHO_PANTALLA, ALTO_PANTALLA)

    Recursos.cargar_todo()

    mapa_juego = menu_principal(pantalla, ui, fuente, fuente_grande, reloj)
    ui.recalcular_cuadricula(len(mapa_juego), len(mapa_juego[0]))
    iniciar_partida(pantalla, ui, fuente, fuente_grande, reloj, mapa_juego)

if __name__ == "__main__":
    main()