class LZW:
    def __init__(self):
        self.init = {}
    
    def CFD(self, mensaje):
        for i in range(len(mensaje)):
            current = mensaje[i]
            if current not in self.init:
                self.init[current] = len(self.init)
    
    def COMPRESS(self, mensaje):
        self.CFD(mensaje)
        w = None
        k = ""
        wk = ""
        salida = ""
        for i in range(len(mensaje)):
            k = mensaje[i]
            if w is None:
                wk = k
            else:
                wk = w + k
            if wk in self.init:
                w = wk
            else:
                salida += str(self.init[w]) + ","
                self.init[wk] = len(self.init)
                w = k
        salida += str(self.init[w]) + ","
        return salida
    
    def DECOMPRESS(self, compress):
        original = ""
        partes = compress.split(',')[:-1]
        for parte in partes:
            parte = int(parte)
            for key, value in self.init.items():
                if value == parte:
                    original += key
                    break
        return original

# Ejemplo de uso:
lzw = LZW()
mensaje = "LA NANA BANANA"
compressed = lzw.COMPRESS(mensaje)
print("Mensaje comprimido:", compressed)
decompressed = lzw.DECOMPRESS(compressed)
print("Mensaje descomprimido:", decompressed)
