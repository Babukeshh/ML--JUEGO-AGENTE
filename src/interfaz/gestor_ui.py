class GestorUI:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.offset_x = 0
        self.offset_y = 0
        self.tamano_celda = 60

    def recalcular_cuadricula(self, filas, columnas):
        # Márgenes proporcionales a la altura actual de la ventana
        margen_s = int(self.alto * 0.22)  # El tablero baja de forma relativa (22% de la ventana)
        margen_i = int(self.alto * 0.14)  # Espacio libre inferior (14% de la ventana)
        
        # Dejamos un colchón lateral del 10% del ancho de la ventana
        disp_w = self.ancho - int(self.ancho * 0.10)
        disp_h = self.alto - margen_s - margen_i
        
        if disp_w < 10 or disp_h < 10: return
        
        # El tamaño de la celda se adapta armónicamente
        self.tamano_celda = max(5, min(disp_w // columnas, disp_h // filas))
        self.offset_x = (self.ancho - (columnas * self.tamano_celda)) // 2
        self.offset_y = margen_s + (disp_h - (filas * self.tamano_celda)) // 2

    def manejar_resize(self, w, h, filas=None, columnas=None):
        self.ancho = w
        self.alto = h
        if filas and columnas: 
            self.recalcular_cuadricula(filas, columnas)
        else:
            # Si estamos en el menú, calculamos con una cuadrícula base de 10x10
            self.recalcular_cuadricula(10, 10)