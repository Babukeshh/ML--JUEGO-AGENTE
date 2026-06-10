import sys
import time
from pathlib import Path

# --- 1. CONFIGURACIÓN DE RUTAS ---
ruta_raiz = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ruta_raiz))

from src.logic.mapas import GestorEscenarios
from src.logic.entorno import EntornoCTF
from src.logic.agente import AgenteQLearning

def iniciar_entrenamiento():
    tiempo_inicio = time.time() 
    
    gestor = GestorEscenarios()
    
    lista_mapas = gestor.cargar_todos_los_mapas()
    if len(lista_mapas) == 0:
        print("Generando 100 escenarios de entrenamiento...")
        while len(lista_mapas) < 100:
            mapa_prueba = gestor.generar_mapa_aleatorio()
            if gestor.validar_mapa_astar(mapa_prueba):
                lista_mapas.append(mapa_prueba)
        gestor.guardar_mapas(lista_mapas)

    agente_simulador_usuario = AgenteQLearning()
    agente_enemigo_real = AgenteQLearning()
    
    # --- PARÁMETROS DE PARADA TEMPRANA (EARLY STOPPING) ---
    MAX_GENERACIONES = 50          # Límite máximo de seguridad
    EPISODIOS_POR_MAPA_GEN = 10 
    
    META_VICTORIA = 90.0           # Porcentaje de victorias para considerar que la IA es "Experta"
    UMBRAL_CONVERGENCIA = 3        # Cuántas generaciones seguidas debe mantener ese porcentaje
    generaciones_consecutivas = 0  # Contador en tiempo real
    
    print("Iniciando Entrenamiento Cognitivo Híbrido Automático...")

    for generacion in range(MAX_GENERACIONES):
        victorias_enemigo = 0
        victorias_usuario = 0
        empates = 0
        
        print(f"\n--- INICIANDO GENERACIÓN {generacion + 1}/{MAX_GENERACIONES} ---")
        
        for mapa in lista_mapas:
            env = EntornoCTF(mapa)
            
            for e in range(EPISODIOS_POR_MAPA_GEN):
                env.reset()
                terminado = False
                pasos = 0 
                
                while not terminado and pasos < 400: 
                    
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
                    
                # Entrenamiento Asimétrico: Comentamos la línea del simulador para que sea un rival torpe 
                # agente_simulador_usuario.reducir_tau() 
                agente_enemigo_real.reducir_tau()
                    
        # --- CÁLCULO DE MÉTRICAS ---
        total_partidas = len(lista_mapas) * EPISODIOS_POR_MAPA_GEN
        tasa_enemigo = (victorias_enemigo / total_partidas) * 100
        tasa_usuario = (victorias_usuario / total_partidas) * 100
        tasa_empate = (empates / total_partidas) * 100
        
        print(f"Generación {generacion + 1}: IA {tasa_enemigo:.1f}% | Simulador {tasa_usuario:.1f}% | Empate {tasa_empate:.1f}%")
        print(f"Temperatura Tau actual (IA): {agente_enemigo_real.tau:.3f}")

        # --- LÓGICA DE PARADA TEMPRANA (EARLY STOPPING) ---
        if tasa_enemigo >= META_VICTORIA:
            generaciones_consecutivas += 1
            print(f"[*] Meta de {META_VICTORIA}% superada. Racha de convergencia: {generaciones_consecutivas}/{UMBRAL_CONVERGENCIA}")
            
            if generaciones_consecutivas >= UMBRAL_CONVERGENCIA:
                print(f"\n[!] CONVERGENCIA ALCANZADA: La IA demostró dominio táctico absoluto.")
                print(f"[!] Deteniendo el entrenamiento automáticamente en la generación {generacion + 1}.")
                break # Esto rompe el ciclo 'for' y salta directamente al guardado final
        else:
            if generaciones_consecutivas > 0:
                print("[!] La IA perdió su racha de victorias. Reiniciando contador de convergencia.")
            generaciones_consecutivas = 0 # Si baja del porcentaje, la racha se rompe

    print("-" * 40)
    print("¡Agente Táctico guardado exitosamente!")
    agente_enemigo_real.guardar_agente()
    
    tiempo_fin = time.time()
    minutos = (tiempo_fin - tiempo_inicio) / 60
    print(f"Tiempo total de procesamiento: {minutos:.2f} minutos")

if __name__ == "__main__":
    iniciar_entrenamiento()