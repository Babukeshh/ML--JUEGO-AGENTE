import random
import heapq
from src.logic.constantes_juego import NORMAL, ARENA, OBSTACULO, BASE_USUARIO, BASE_COMPUTADORA

class EntornoCTF:
    def __init__(self, mapa):
        self.mapa = mapa
        self.filas = len(mapa)
        self.columnas = len(mapa[0])
        self.base_usuario = BASE_USUARIO
        self.base_enemigo = BASE_COMPUTADORA
        self.diccionario_acciones = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
        self.reset()

    def reset(self):
        self.pos_usuario = self.base_usuario
        self.pos_enemigo = self.base_enemigo
        self.bandera_usuario_en_base = True
        self.bandera_enemigo_en_base = True
        self.movimientos_usuario = 4
        self.movimientos_enemigo = 4

    @property
    def canon_activo(self):
        """Propiedad dinámica: El cañón solo se activa si falta alguna bandera."""
        return not self.bandera_usuario_en_base or not self.bandera_enemigo_en_base

    def signo(self, z):
        return 1 if z > 0 else -1 if z < 0 else 0

    def costo_ruta_optima(self, inicio, meta, pos_rival=None):
        """A* modificado: El agente ahora considerará al rival como una zona de alto peligro."""
        if inicio == meta: return 0
        cola = [(0, inicio)]
        costos = {inicio: 0}
        
        while cola:
            costo_actual, actual = heapq.heappop(cola)
            if actual == meta: return costo_actual
            
            for dx, dy in self.diccionario_acciones.values():
                nx, ny = actual[0] + dx, actual[1] + dy
                if 0 <= nx < self.filas and 0 <= ny < self.columnas:
                    if self.mapa[nx][ny] == OBSTACULO: continue 
                    
                    costo_paso = 1 if self.mapa[nx][ny] == NORMAL else 2
                    
                    # Instinto de supervivencia: Evitar la casilla del rival
                    if pos_rival and (nx, ny) == pos_rival:
                        costo_paso += 15 
                        
                    nc = costo_actual + costo_paso
                    if (nx, ny) not in costos or nc < costos[(nx, ny)]:
                        costos[(nx, ny)] = nc
                        heapq.heappush(cola, (nc, (nx, ny)))
        return 999 

    def determinar_objetivo(self, es_usuario):
        mi_pos = self.pos_usuario if es_usuario else self.pos_enemigo
        rival_pos = self.pos_enemigo if es_usuario else self.pos_usuario
        mi_base = self.base_usuario if es_usuario else self.base_enemigo
        base_rival = self.base_enemigo if es_usuario else self.base_usuario
        tengo_band = not self.bandera_enemigo_en_base if es_usuario else not self.bandera_usuario_en_base
        rival_tiene_band = not self.bandera_usuario_en_base if es_usuario else not self.bandera_enemigo_en_base

        if tengo_band: return mi_base
        if rival_tiene_band: return rival_pos
            
        dist_rival_base = self.costo_ruta_optima(rival_pos, mi_base, pos_rival=mi_pos)
        
        if dist_rival_base <= 3: return rival_pos
        else: return base_rival

    # --- LA FUNCIÓN QUE TU PYTHON NO ESTABA ENCONTRANDO ---
    def obtener_estado_relativo(self, es_usuario=True):
        mi_pos = self.pos_usuario if es_usuario else self.pos_enemigo
        rival_pos = self.pos_enemigo if es_usuario else self.pos_usuario
        tengo_band = not self.bandera_enemigo_en_base if es_usuario else not self.bandera_usuario_en_base
        rival_tiene_band = not self.bandera_usuario_en_base if es_usuario else not self.bandera_enemigo_en_base

        radar = []
        for accion in range(4):
            dx, dy = self.diccionario_acciones[accion]
            nx, ny = mi_pos[0] + dx, mi_pos[1] + dy
            if 0 <= nx < self.filas and 0 <= ny < self.columnas: 
                radar.append(self.mapa[nx][ny]) 
            else: 
                radar.append(OBSTACULO)

        meta = self.determinar_objetivo(es_usuario)
        return tuple(radar + [self.signo(meta[0]-mi_pos[0]), self.signo(meta[1]-mi_pos[1]), 
                              self.signo(rival_pos[0]-mi_pos[0]), self.signo(rival_pos[1]-mi_pos[1]), 
                              tengo_band, rival_tiene_band])

    def step(self, accion_idx, es_turno_usuario=True):
        recompensa, terminado = 0, False
        pos_actual = self.pos_usuario if es_turno_usuario else self.pos_enemigo
        rival_pos = self.pos_enemigo if es_turno_usuario else self.pos_usuario 
        
        mov = self.diccionario_acciones[accion_idx]
        n_pos = (pos_actual[0] + mov[0], pos_actual[1] + mov[1])
        
        meta = self.determinar_objetivo(es_turno_usuario)
        d_antes = self.costo_ruta_optima(pos_actual, meta, pos_rival=rival_pos)
        
        if 0 <= n_pos[0] < self.filas and 0 <= n_pos[1] < self.columnas:
            tc = self.mapa[n_pos[0]][n_pos[1]]
            if tc == OBSTACULO:
                recompensa -= 10
                n_pos = pos_actual
                costo = 1
            else:
                costo = 1 if tc == NORMAL else 2
                recompensa -= costo
        else:
            recompensa -= 10
            n_pos = pos_actual
            costo = 1

        d_despues = self.costo_ruta_optima(n_pos, meta, pos_rival=rival_pos)
        if pos_actual != n_pos:
            if d_despues < d_antes: recompensa += 5   
            elif d_despues > d_antes: recompensa -= 5   

        if es_turno_usuario:
            if costo > self.movimientos_usuario: self.movimientos_usuario = 0
            else: self.pos_usuario, self.movimientos_usuario = n_pos, self.movimientos_usuario - costo
        else:
            if costo > self.movimientos_enemigo: self.movimientos_enemigo = 0
            else: self.pos_enemigo, self.movimientos_enemigo = n_pos, self.movimientos_enemigo - costo

        # Recolección Banderas
        if es_turno_usuario and self.bandera_enemigo_en_base and self.pos_usuario == self.base_enemigo:
            self.bandera_enemigo_en_base = False
            recompensa += 200
        elif not es_turno_usuario and self.bandera_usuario_en_base and self.pos_enemigo == self.base_usuario:
            self.bandera_usuario_en_base = False
            recompensa += 200 

        # Colisiones Simétricas
        if self.pos_usuario == self.pos_enemigo:
            if es_turno_usuario:
                enemigo_tenia_bandera = not self.bandera_usuario_en_base
                self.pos_enemigo = self.base_enemigo
                if enemigo_tenia_bandera: 
                    self.bandera_usuario_en_base = True
                    recompensa += 300 
            else:
                usuario_tenia_bandera = not self.bandera_enemigo_en_base
                dist_peligro = self.costo_ruta_optima(self.pos_usuario, self.base_enemigo)
                self.pos_usuario = self.base_usuario
                
                if usuario_tenia_bandera:
                    self.bandera_enemigo_en_base = True
                    recompensa += 300 
                else: 
                    bono_peligro = max(0, (20 - dist_peligro) * 5)
                    recompensa += 5 + bono_peligro  

        # Victoria
        if es_turno_usuario and not self.bandera_enemigo_en_base and self.pos_usuario == self.base_usuario:
            recompensa += 2000
            terminado = True
        elif not es_turno_usuario and not self.bandera_usuario_en_base and self.pos_enemigo == self.base_enemigo:
            recompensa += 2000
            terminado = True

        return recompensa, terminado

    def disparar_canon(self):
        casillas_afectadas = []
        while len(casillas_afectadas) < 5:
            rx = random.randint(0, self.filas - 1)
            ry = random.randint(0, self.columnas - 1)
            if self.mapa[rx][ry] != OBSTACULO and (rx, ry) not in casillas_afectadas:
                casillas_afectadas.append((rx, ry))
                
        impacto = False
        if self.pos_usuario in casillas_afectadas:
            self.pos_usuario = self.base_usuario
            if not self.bandera_enemigo_en_base: self.bandera_enemigo_en_base = True
            impacto = True
            
        if self.pos_enemigo in casillas_afectadas:
            self.pos_enemigo = self.base_enemigo
            if not self.bandera_usuario_en_base: self.bandera_usuario_en_base = True
            impacto = True
            
        return impacto