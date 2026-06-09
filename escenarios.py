import random
import heapq 
import os
import pickle
import math

# --- 1. CONSTANTES GLOBALES ---
FILAS = 10 
COLUMNAS = 10
NORMAL = 0 
ARENA = 1 
OBSTACULO = 2

RUTA_MAPAS = r"D:\t.escom\Elem escuela\5 Semestre\Machine Learning\Practica 11 (Juego)\RUTA_MAPAS"

BASE_USUARIO = (0, 0)
BASE_COMPUTADORA = (FILAS - 1, COLUMNAS - 1)

# --- 2. CLASE NODO PARA A* ---
class Nodo:
    def __init__(self, x, y, g=0, h=0):
        self.x = x
        self.y = y
        self.g = g  
        self.h = h  
        self.f = g + h  
        self.padre = None 

    def __lt__(self, otro_nodo):
        return self.f < otro_nodo.f

# --- 3. CLASE GESTOR DE ESCENARIOS ---
class GestorEscenarios:
    def __init__(self, prob_normal=0.5, prob_arena=0.3, prob_obs=0.2):
        self.prob_normal = prob_normal
        self.prob_arena = prob_arena
        self.prob_obs = prob_obs

    def generar_mapa_aleatorio(self):
        mapa = [[0 for _ in range(COLUMNAS)] for _ in range(FILAS)]
        for fila in range(FILAS):
            for columna in range(COLUMNAS):
                rand = random.random()
                if rand < self.prob_normal:
                    mapa[fila][columna] = NORMAL
                elif rand < self.prob_normal + self.prob_arena:
                    mapa[fila][columna] = ARENA
                else:
                    mapa[fila][columna] = OBSTACULO
        mapa[BASE_USUARIO[0]][BASE_USUARIO[1]] = NORMAL
        mapa[BASE_COMPUTADORA[0]][BASE_COMPUTADORA[1]] = NORMAL 
        return mapa 
    
    def heuristica_manhattan(self, x_actual, y_actual):
        return abs(x_actual - BASE_COMPUTADORA[0]) + abs(y_actual - BASE_COMPUTADORA[1])

    def validar_mapa_astar(self, mapa):
        h_inicial = self.heuristica_manhattan(BASE_USUARIO[0], BASE_USUARIO[1])
        nodo_inicial = Nodo(BASE_USUARIO[0], BASE_USUARIO[1], g=0, h=h_inicial)
        
        lista_abierta = []
        heapq.heappush(lista_abierta, nodo_inicial)
        visitados = set()
        
        movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while lista_abierta:
            nodo_actual = heapq.heappop(lista_abierta)
            
            if (nodo_actual.x, nodo_actual.y) == BASE_COMPUTADORA:
                return True
                
            if (nodo_actual.x, nodo_actual.y) in visitados:
                continue
                
            visitados.add((nodo_actual.x, nodo_actual.y))
            
            for dx, dy in movimientos:
                nx = nodo_actual.x + dx
                ny = nodo_actual.y + dy
                
                if 0 <= nx < FILAS and 0 <= ny < COLUMNAS:
                    tipo_casilla = mapa[nx][ny]
                    if tipo_casilla == OBSTACULO or (nx, ny) in visitados:
                        continue
                        
                    costo_movimiento = 1 if tipo_casilla == NORMAL else 2
                    nuevo_g = nodo_actual.g + costo_movimiento
                    nuevo_h = self.heuristica_manhattan(nx, ny)
                    
                    nuevo_nodo = Nodo(nx, ny, g=nuevo_g, h=nuevo_h)
                    nuevo_nodo.padre = nodo_actual
                    
                    heapq.heappush(lista_abierta, nuevo_nodo)
                    
        return False

    def guardar_mapas(self, lista_mapas, nombre_archivo="escenarios_validos.txt"):
        if not os.path.exists(RUTA_MAPAS):
            os.makedirs(RUTA_MAPAS)
        ruta_completa = os.path.join(RUTA_MAPAS, nombre_archivo)
        with open(ruta_completa, 'w') as archivo:
            for indice, mapa in enumerate(lista_mapas):
                archivo.write(f"Escenario {indice + 1}:\n")
                for fila in mapa:
                    fila_str = " ".join(str(casilla) for casilla in fila)
                    archivo.write(fila_str + "\n")
                archivo.write("-" * 20 + "\n")

    def cargar_todos_los_mapas(self, nombre_archivo="escenarios_validos.txt"):
        ruta_completa = os.path.join(RUTA_MAPAS, nombre_archivo)
        mapas = []
        try:
            with open(ruta_completa, 'r') as archivo:
                lineas = archivo.readlines()
                mapa_actual = []
                for linea in lineas:
                    if linea.startswith("Escenario") or linea.startswith("---"):
                        if len(mapa_actual) == FILAS:
                            mapas.append(mapa_actual)
                        mapa_actual = []
                    else:
                        valores = linea.strip().split()
                        if valores:
                            mapa_actual.append([int(v) for v in valores])
            return mapas
        except FileNotFoundError:
            return []

# --- 4. CLASE ENTORNO MULTIJUGADOR ---
class EntornoCTF:
    def __init__(self, mapa):
        self.mapa = mapa
        self.filas = len(mapa)
        self.columnas = len(mapa[0])
        self.base_usuario = (0, 0)
        self.base_enemigo = (self.filas - 1, self.columnas - 1)
        self.reset()
        
        self.diccionario_acciones = {
            0: (-1, 0), # Arriba
            1: (1, 0),  # Abajo
            2: (0, -1), # Izquierda
            3: (0, 1)   # Derecha
        }

    def reset(self):
        self.pos_usuario = self.base_usuario
        self.pos_enemigo = self.base_enemigo
        self.bandera_usuario_en_base = True
        self.bandera_enemigo_en_base = True
        self.movimientos_usuario = 4
        self.movimientos_enemigo = 4
        self.canon_activo = False

    def signo(self, z):
        if z > 0: return 1
        if z < 0: return -1
        return 0

    def costo_ruta_optima(self, inicio, meta):
        if inicio == meta: return 0
        cola = []
        heapq.heappush(cola, (0, inicio))
        costos = {inicio: 0}

        while cola:
            costo_actual, actual = heapq.heappop(cola)
            if actual == meta: return costo_actual

            for dx, dy in self.diccionario_acciones.values():
                nx, ny = actual[0] + dx, actual[1] + dy
                if 0 <= nx < self.filas and 0 <= ny < self.columnas:
                    tipo = self.mapa[nx][ny]
                    if tipo == 2: continue 
                    
                    nuevo_costo = costo_actual + (1 if tipo == 0 else 2)
                    if (nx, ny) not in costos or nuevo_costo < costos[(nx, ny)]:
                        costos[(nx, ny)] = nuevo_costo
                        heapq.heappush(cola, (nuevo_costo, (nx, ny)))
                        
        return 999 

    def determinar_objetivo(self, es_usuario):
        mi_pos = self.pos_usuario if es_usuario else self.pos_enemigo
        rival_pos = self.pos_enemigo if es_usuario else self.pos_usuario
        mi_base = self.base_usuario if es_usuario else self.base_enemigo
        base_rival = self.base_enemigo if es_usuario else self.base_usuario
        
        tengo_bandera = not self.bandera_enemigo_en_base if es_usuario else not self.bandera_usuario_en_base
        rival_tiene_bandera = not self.bandera_usuario_en_base if es_usuario else not self.bandera_enemigo_en_base

        if tengo_bandera:
            return mi_base
            
        if rival_tiene_bandera:
            return rival_pos
            
        dist_rival_a_mi_base = self.costo_ruta_optima(rival_pos, mi_base)
        dist_yo_a_su_base = self.costo_ruta_optima(mi_pos, base_rival)
        
        if dist_rival_a_mi_base < dist_yo_a_su_base - 1:
            return rival_pos
        else:
            return base_rival

    def obtener_estado_relativo(self, es_usuario=True):
        mi_pos = self.pos_usuario if es_usuario else self.pos_enemigo
        rival_pos = self.pos_enemigo if es_usuario else self.pos_usuario
        
        tengo_bandera = not self.bandera_enemigo_en_base if es_usuario else not self.bandera_usuario_en_base
        rival_tiene_bandera = not self.bandera_usuario_en_base if es_usuario else not self.bandera_enemigo_en_base

        radar = []
        for accion in range(4):
            dx, dy = self.diccionario_acciones[accion]
            nx, ny = mi_pos[0] + dx, mi_pos[1] + dy
            if 0 <= nx < self.filas and 0 <= ny < self.columnas:
                radar.append(self.mapa[nx][ny]) 
            else:
                radar.append(2)

        meta_estrategica = self.determinar_objetivo(es_usuario)
        dir_meta_x = self.signo(meta_estrategica[0] - mi_pos[0])
        dir_meta_y = self.signo(meta_estrategica[1] - mi_pos[1])

        dir_rival_x = self.signo(rival_pos[0] - mi_pos[0])
        dir_rival_y = self.signo(rival_pos[1] - mi_pos[1])

        return tuple(radar + [dir_meta_x, dir_meta_y, dir_rival_x, dir_rival_y, tengo_bandera, rival_tiene_bandera])

    def step(self, accion_idx, es_turno_usuario=True):
        recompensa = 0
        terminado = False
        
        pos_actual = self.pos_usuario if es_turno_usuario else self.pos_enemigo
        movimiento = self.diccionario_acciones[accion_idx]
        nueva_pos = (pos_actual[0] + movimiento[0], pos_actual[1] + movimiento[1])
        
        meta = self.determinar_objetivo(es_turno_usuario)
        dist_antes = self.costo_ruta_optima(pos_actual, meta)
        
        if (0 <= nueva_pos[0] < self.filas and 0 <= nueva_pos[1] < self.columnas):
            tipo_casilla = self.mapa[nueva_pos[0]][nueva_pos[1]]
            if tipo_casilla == 2:
                recompensa -= 10 
                nueva_pos = pos_actual 
                costo_movimiento = 1   
            else:
                costo_movimiento = 1 if tipo_casilla == 0 else 2 
                recompensa -= costo_movimiento 
        else:
            recompensa -= 10
            nueva_pos = pos_actual
            costo_movimiento = 1

        dist_despues = self.costo_ruta_optima(nueva_pos, meta)

        if pos_actual != nueva_pos:
            if dist_despues < dist_antes:
                recompensa += 5   
            elif dist_despues > dist_antes:
                recompensa -= 5   

        if es_turno_usuario:
            if costo_movimiento > self.movimientos_usuario:
                self.movimientos_usuario = 0
            else:
                self.pos_usuario = nueva_pos
                self.movimientos_usuario -= costo_movimiento
        else:
            if costo_movimiento > self.movimientos_enemigo:
                self.movimientos_enemigo = 0
            else:
                self.pos_enemigo = nueva_pos
                self.movimientos_enemigo -= costo_movimiento

        if es_turno_usuario and self.bandera_enemigo_en_base and self.pos_usuario == self.base_enemigo:
            self.bandera_enemigo_en_base = False
            self.canon_activo = True
            recompensa += 200
        elif not es_turno_usuario and self.bandera_usuario_en_base and self.pos_enemigo == self.base_usuario:
            self.bandera_usuario_en_base = False
            self.canon_activo = True
            recompensa += 200 

        if self.pos_usuario == self.pos_enemigo:
            usuario_tenia_bandera = not self.bandera_enemigo_en_base
            self.pos_usuario = self.base_usuario
            if not self.bandera_enemigo_en_base:
                self.bandera_enemigo_en_base = True
                
            if es_turno_usuario:
                recompensa -= 200 
            else:
                if usuario_tenia_bandera:
                    recompensa += 300 
                else:
                    recompensa += 50  

        if es_turno_usuario and not self.bandera_enemigo_en_base and self.pos_usuario == self.base_usuario:
            recompensa += 2000
            terminado = True
        elif not es_turno_usuario and not self.bandera_usuario_en_base and self.pos_enemigo == self.base_enemigo:
            recompensa += 2000
            terminado = True

        return recompensa, terminado

    def disparar_canon(self):
        if not self.canon_activo:
            return False
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
            
        return impacto

# --- 5. AGENTE Q-LEARNING CON SOFTMAX ---
class AgenteQLearning:
    def __init__(self, alpha=0.1, gamma=0.9, tau=5.0, tau_min=0.1, tau_decay=0.999): # <- Cambio aplicado aquí (0.999)
        self.Q = {} 
        self.acciones = [0, 1, 2, 3]
        self.alpha = alpha
        self.gamma = gamma
        self.tau = tau
        self.tau_min = tau_min
        self.tau_decay = tau_decay

    def obtener_valor_q(self, estado, accion):
        if estado not in self.Q:
            self.Q[estado] = {a: 0.0 for a in self.acciones}
        return self.Q[estado][accion]

    def elegir_accion_softmax(self, estado):
        if estado not in self.Q:
            self.Q[estado] = {a: 0.0 for a in self.acciones}
            
        valores_q = [self.Q[estado][a] for a in self.acciones]
        max_q = max(valores_q)
        
        exponenciales = []
        suma_exp = 0.0
        for q in valores_q:
            exp_val = math.exp((q - max_q) / self.tau)
            exponenciales.append(exp_val)
            suma_exp += exp_val
            
        probabilidades = [p / suma_exp for p in exponenciales]
        return random.choices(self.acciones, weights=probabilidades, k=1)[0]

    def aprender(self, estado, accion, recompensa, siguiente_estado):
        q_actual = self.obtener_valor_q(estado, accion)
        if siguiente_estado not in self.Q:
            self.Q[siguiente_estado] = {a: 0.0 for a in self.acciones}
        max_q_siguiente = max(self.Q[siguiente_estado].values())
        nuevo_q = q_actual + self.alpha * (recompensa + self.gamma * max_q_siguiente - q_actual)
        self.Q[estado][accion] = nuevo_q

    def reducir_tau(self):
        if self.tau > self.tau_min:
            self.tau *= self.tau_decay

    def guardar_agente(self, nombre_archivo="agente_enemigo.pkl"):
        if not os.path.exists(RUTA_MAPAS):
            os.makedirs(RUTA_MAPAS)
        ruta_completa = os.path.join(RUTA_MAPAS, nombre_archivo)
        with open(ruta_completa, 'wb') as archivo:
            pickle.dump(self.Q, archivo)

# --- 6. ENTRENAMIENTO EVOLUTIVO POR GENERACIONES ---
if __name__ == "__main__":
    gestor = GestorEscenarios()
    
    lista_mapas = gestor.cargar_todos_los_mapas()
    if len(lista_mapas) == 0:
        print("Generando 100 escenarios...")
        while len(lista_mapas) < 100:
            mapa_prueba = gestor.generar_mapa_aleatorio()
            if gestor.validar_mapa_astar(mapa_prueba):
                lista_mapas.append(mapa_prueba)
        gestor.guardar_mapas(lista_mapas)

    agente_simulador_usuario = AgenteQLearning()
    agente_enemigo_real = AgenteQLearning()
    
    GENERACIONES = 8
    EPISODIOS_POR_MAPA_GEN = 10 
    
    print("Iniciando Entrenamiento Cognitivo Híbrido...")

    for generacion in range(GENERACIONES):
        victorias_enemigo = 0
        victorias_usuario = 0
        empates = 0
        
        print(f"\n--- INICIANDO GENERACIÓN {generacion + 1}/{GENERACIONES} ---")
        
        for mapa in lista_mapas:
            env = EntornoCTF(mapa)
            
            for e in range(EPISODIOS_POR_MAPA_GEN):
                env.reset()
                terminado = False
                pasos = 0 
                
                while not terminado and pasos < 150: 
                    
                    # TURNO USUARIO SIMULADO
                    while env.movimientos_usuario > 0 and not terminado:
                        estado_us = env.obtener_estado_relativo(es_usuario=True)
                        accion = agente_simulador_usuario.elegir_accion_softmax(estado_us)
                        recompensa, terminado = env.step(accion, es_turno_usuario=True)
                        siguiente_estado_us = env.obtener_estado_relativo(es_usuario=True)
                        
                        agente_simulador_usuario.aprender(estado_us, accion, recompensa, siguiente_estado_us)
                        pasos += 1
                        if terminado: break
                        
                    if terminado: break
                        
                    # TURNO ENEMIGO REAL
                    while env.movimientos_enemigo > 0 and not terminado:
                        estado_en = env.obtener_estado_relativo(es_usuario=False)
                        accion = agente_enemigo_real.elegir_accion_softmax(estado_en)
                        recompensa, terminado = env.step(accion, es_turno_usuario=False)
                        siguiente_estado_en = env.obtener_estado_relativo(es_usuario=False)
                        
                        agente_enemigo_real.aprender(estado_en, accion, recompensa, siguiente_estado_en)
                        pasos += 1
                        if terminado: break

                    if not terminado:
                        env.disparar_canon()
                        env.movimientos_usuario = 4
                        env.movimientos_enemigo = 4
                        
                # --- EVALUACIÓN DE VICTORIA ---
                if env.pos_usuario == env.base_usuario and not env.bandera_enemigo_en_base:
                    victorias_usuario += 1
                elif env.pos_enemigo == env.base_enemigo and not env.bandera_usuario_en_base:
                    victorias_enemigo += 1
                else:
                    empates += 1
                    
                # <- Cambio aplicado aquí: Enfriamiento MÁS agresivo, después de cada partida
                agente_simulador_usuario.reducir_tau()
                agente_enemigo_real.reducir_tau()
                    
        total_partidas = len(lista_mapas) * EPISODIOS_POR_MAPA_GEN
        tasa_enemigo = (victorias_enemigo / total_partidas) * 100
        tasa_usuario = (victorias_usuario / total_partidas) * 100
        
        print(f"Generación {generacion + 1}: IA {tasa_enemigo:.1f}% | Simulador {tasa_usuario:.1f}% | Empate {100 - tasa_enemigo - tasa_usuario:.1f}%")
        print(f"Temperatura Tau actual (IA): {agente_enemigo_real.tau:.3f}")

    print("-" * 40)
    print("¡Agente Táctico completamente entrenado!")
    agente_enemigo_real.guardar_agente("agente_enemigo.pkl")