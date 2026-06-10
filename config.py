from pathlib import Path

# Detección automática de la raíz del proyecto
RAIZ_PROYECTO = Path(__file__).resolve().parent

# Rutas principales
RUTA_SRC = RAIZ_PROYECTO / "src"
RUTA_LOGIC = RUTA_SRC / "logic"
RUTA_INTERFAZ = RUTA_SRC / "interfaz"
RUTA_MODELOS = RAIZ_PROYECTO / "model"
RUTA_IMG = RAIZ_PROYECTO / "img"

# Archivos específicos
ARCHIVO_CEREBRO = RUTA_MODELOS / "agente_enemigo.pkl"
ARCHIVO_MAPAS = RUTA_LOGIC / "escenarios_validos.txt"

# Mapa del profesor (Día de la evaluación)
MAPA_EVALUACION = [
    [0, 0, 1, 1, 0, 2, 0, 0, 0, 0],
    [0, 2, 2, 1, 0, 2, 1, 2, 2, 0],
    [0, 0, 2, 0, 0, 0, 1, 0, 2, 0],
    [1, 0, 2, 0, 2, 2, 2, 0, 0, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 1, 1],
    [0, 2, 2, 0, 2, 0, 2, 2, 2, 0],
    [0, 2, 0, 0, 0, 0, 0, 0, 2, 0],
    [0, 2, 1, 2, 2, 2, 2, 0, 2, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    [1,0, 1, 0, 1, 0, 1, 0, 1, 0]
]