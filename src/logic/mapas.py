import random
import heapq
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import ARCHIVO_MAPAS
from src.logic.constantes_juego import FILAS, COLUMNAS, NORMAL, ARENA, OBSTACULO, BASE_USUARIO, BASE_COMPUTADORA

class Nodo:
    def __init__(self, x, y, g=0, h=0):
        self.x = x
        self.y = y
        self.g = g  
        self.h = h  
        self.f = g + h  
        self.padre = None 
    def __lt__(self, otro):
        return self.f < otro.f

class GestorEscenarios:
    def __init__(self, prob_normal=0.5, prob_arena=0.3, prob_obs=0.2):
        self.p_norm = prob_normal
        self.p_arena = prob_arena

    def generar_mapa_aleatorio(self):
        mapa = [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]
        for f in range(FILAS):
            for c in range(COLUMNAS):
                r = random.random()
                if r < self.p_norm: mapa[f][c] = NORMAL
                elif r < self.p_norm + self.p_arena: mapa[f][c] = ARENA
                else: mapa[f][c] = OBSTACULO
        mapa[BASE_USUARIO[0]][BASE_USUARIO[1]] = NORMAL
        mapa[BASE_COMPUTADORA[0]][BASE_COMPUTADORA[1]] = NORMAL 
        return mapa 
    
    def heuristica_manhattan(self, x, y):
        return abs(x - BASE_COMPUTADORA[0]) + abs(y - BASE_COMPUTADORA[1])

    def validar_mapa_astar(self, mapa):
        nodo_i = Nodo(BASE_USUARIO[0], BASE_USUARIO[1], h=self.heuristica_manhattan(BASE_USUARIO[0], BASE_USUARIO[1]))
        abierta = []
        heapq.heappush(abierta, nodo_i)
        visitados = set()
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while abierta:
            actual = heapq.heappop(abierta)
            if (actual.x, actual.y) == BASE_COMPUTADORA: return True
            if (actual.x, actual.y) in visitados: continue
            visitados.add((actual.x, actual.y))
            
            for dx, dy in movimientos:
                nx, ny = actual.x + dx, actual.y + dy
                if 0 <= nx < FILAS and 0 <= ny < COLUMNAS:
                    t = mapa[nx][ny]
                    if t == OBSTACULO or (nx, ny) in visitados: continue
                    costo = 1 if t == NORMAL else 2
                    nuevo = Nodo(nx, ny, g=actual.g + costo, h=self.heuristica_manhattan(nx, ny))
                    heapq.heappush(abierta, nuevo)
        return False

    def guardar_mapas(self, lista_mapas):
        ARCHIVO_MAPAS.parent.mkdir(parents=True, exist_ok=True)
        with open(ARCHIVO_MAPAS, 'w') as f:
            for i, mapa in enumerate(lista_mapas):
                f.write(f"Escenario {i + 1}:\n")
                for fila in mapa: f.write(" ".join(str(c) for c in fila) + "\n")
                f.write("-" * 20 + "\n")

    def cargar_todos_los_mapas(self):
        mapas = []
        try:
            with open(ARCHIVO_MAPAS, 'r') as f:
                mapa_act = []
                for linea in f:
                    if linea.startswith("Esc") or linea.startswith("---"):
                        if len(mapa_act) == FILAS: mapas.append(mapa_act)
                        mapa_act = []
                    else:
                        v = linea.strip().split()
                        if v: mapa_act.append([int(x) for x in v])
            return mapas
        except FileNotFoundError: return []