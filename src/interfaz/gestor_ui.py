class GestorUI:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.offset_x = 0
        self.offset_y = 0
        self.tamano_celda = 60

    def recalcular_cuadricula(self, filas, columnas):
        margen_s, margen_i = 170, 120
        disp_w, disp_h = self.ancho - 40, self.alto - margen_s - margen_i
        if disp_w < 10 or disp_h < 10: return
        self.tamano_celda = max(5, min(disp_w // columnas, disp_h // filas))
        self.offset_x = (self.ancho - (columnas * self.tamano_celda)) // 2
        self.offset_y = margen_s + (disp_h - (filas * self.tamano_celda)) // 2

    def manejar_resize(self, w, h, filas=None, columnas=None):
        self.ancho = w
        self.alto = h
        if filas and columnas: self.recalcular_cuadricula(filas, columnas)