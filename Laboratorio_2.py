import sys
import json
import heapq
import collections
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QTextEdit, QFileDialog, \
    QLineEdit, QLabel, QMessageBox, QInputDialog, QWidget, QHBoxLayout, QComboBox

class Persona:
    def __init__(self, nombre, dpi, date_birth, address, empresa):
        self.nombre = nombre
        self.dpi = dpi
        self.date_birth = date_birth
        self.address = address
        self.empresa = empresa

class Nodo:
    def __init__(self, esHoja=False):
        self.claves = []
        self.hijos = []
        self.hoja = esHoja

class ArbolB:
    def __init__(self, grado):
        self.grado = grado
        self.raiz = Nodo(True)

    def insertar(self, persona):
        raiz = self.raiz
        if len(raiz.claves) == (2 * self.grado) - 1:
            temp = Nodo()
            temp.hijos.append(raiz)
            self.raiz = temp
            self.dividir(temp, 0)
        self.insertar_no_lleno(self.raiz, persona)

    def insertar_no_lleno(self, nodo, persona):
        i = len(nodo.claves) - 1
        if nodo.hoja:
            while i >= 0 and persona.dpi < nodo.claves[i].dpi:
                i -= 1
            i += 1
            nodo.claves.insert(i, persona)
        else:
            while i >= 0 and persona.dpi < nodo.claves[i].dpi:
                i -= 1
            i += 1
            if len(nodo.hijos) > i and len(nodo.hijos[i].claves) == (2 * self.grado) - 1:
                self.dividir(nodo, i)
                if persona.dpi > nodo.claves[i].dpi:
                    i += 1
            if i < len(nodo.hijos):
                self.insertar_no_lleno(nodo.hijos[i], persona)
            else:
                self.insertar_no_lleno(nodo.hijos[-1], persona)

    def dividir(self, nodo, i):
        t = self.grado
        y = nodo.hijos[i]
        z = Nodo(y.hoja)
        nodo.hijos.insert(i + 1, z)
        nodo.claves.insert(i, y.claves[t - 1])
        z.claves = y.claves[t: (2 * t) - 1]
        y.claves = y.claves[0: t - 1]
        if not y.hoja:
            z.hijos = y.hijos[t: 2 * t]
            y.hijos = y.hijos[0: t]

    def mostrar(self, nodo=None, l=0):
        if nodo is None:
            nodo = self.raiz

        resultado = []
        resultado.append(f"Level {l} {len(nodo.claves)}:")

        for i in nodo.claves:
            resultado.append(f"DPI: {i.dpi}")
            resultado.append(f"Nombre: {i.nombre}")
            resultado.append(f"Fecha de Nacimiento: {i.date_birth}")
            resultado.append(f"Dirección: {i.address}")

        l += 1
        if len(nodo.hijos) > 0:
            for i in nodo.hijos:
                child_result = self.mostrar(i, l)
                resultado.extend(child_result)

        return resultado

    def buscar(self, dpi, nodo=None):
        if nodo is None:
            nodo = self.raiz

        i = 0
        while i < len(nodo.claves) and dpi > nodo.claves[i].dpi:
            i += 1
        if i < len(nodo.claves) and dpi == nodo.claves[i].dpi:
            return nodo.claves[i]
        elif nodo.hoja:
            return None
        else:
            return self.buscar(dpi, nodo.hijos[i])

    def eliminar(self, dpi):
        if self.raiz is not None:
            resultado, nodo = self._eliminar_en_arbol(self.raiz, dpi)
            if resultado and len(nodo.claves) == 0:
                self.raiz = nodo.hijos[0] if nodo.hijos else None
            return resultado
        else:
            return False

    def _eliminar_en_arbol(self, nodo, dpi):
        if nodo is None:
            return False, None

        indice = 0
        while indice < len(nodo.claves) and dpi > nodo.claves[indice].dpi:
            indice += 1

        if indice < len(nodo.claves) and dpi == nodo.claves[indice].dpi:
            if nodo.hoja:
                nodo.claves.pop(indice)
            else:
                dpi_antecesor = self._obtener_dpi_antecesor(nodo, indice)
                nodo.claves[indice] = dpi_antecesor
                return self._eliminar_en_arbol(nodo.hijos[indice], dpi_antecesor.dpi)

        elif nodo.hoja:
            return False, None

        else:
            resultado, nodo_hijo = self._eliminar_en_arbol(nodo.hijos[indice], dpi)
            if resultado:
                if len(nodo_hijo.claves) < self.grado // 2:
                    if indice < len(nodo.claves):
                        self._mover_clave_derecha(nodo, indice)
                    else:
                        self._mover_clave_izquierda(nodo, indice)
                return self._eliminar_en_arbol(nodo.hijos[indice], dpi)

        return False, nodo

    def _obtener_dpi_antecesor(self, nodo, indice):
        nodo_actual = nodo.hijos[indice]
        while not nodo_actual.hoja:
            nodo_actual = nodo_actual.hijos[-1]
        return nodo_actual.claves[-1]

    def _mover_clave_izquierda(self, nodo, indice):
        hijo = nodo.hijos[indice]
        hermano_izq = nodo.hijos[indice - 1]
        hijo.claves.insert(0, nodo.claves[indice - 1])
        nodo.claves[indice - 1] = hermano_izq.claves.pop()
        if not hijo.hoja:
            hijo.hijos.insert(0, hermano_izq.hijos.pop())

    def _mover_clave_derecha(self, nodo, indice):
        hijo = nodo.hijos[indice]
        hermano_der = nodo.hijos[indice + 1]
        hijo.claves.append(nodo.claves[indice])
        nodo.claves[indice] = hermano_der.claves.pop(0)
        if not hijo.hoja:
            hijo.hijos.append(hermano_der.hijos.pop(0))

    def _verificar_y_ajustar(self, nodo, indice):
        if len(nodo.hijos[indice].claves) >= self.grado:
            return True, nodo
        if indice > 0 and len(nodo.hijos[indice - 1].claves) > self.grado // 2:
            self._mover_clave_derecha(nodo, indice)
        elif indice < len(nodo.claves) and len(nodo.hijos[indice + 1].claves) > self.grado // 2:
            self._mover_clave_izquierda(nodo, indice)
        elif indice > 0:
            self._combinar_nodos(nodo, indice - 1)
        else:
            self._combinar_nodos(nodo, indice)
        return False, nodo

    def _obtener_dpi_pred(self, nodo):
        if nodo.hoja:
            return nodo.claves.pop().dpi
        return self._obtener_dpi_pred(nodo.hijos.pop())

    def _obtener_dpi_succ(self, nodo):
        if nodo.hoja:
            return nodo.claves.pop(0).dpi
        return self._obtener_dpi_succ(nodo.hijos.pop(0))

    def _mover_clave_izquierda(self, nodo, indice):
        hijo = nodo.hijos[indice]
        hermano_izq = nodo.hijos[indice - 1]
        hijo.claves.insert(0, nodo.claves[indice - 1])
        nodo.claves[indice - 1] = hermano_izq.claves.pop()
        if not hijo.hoja:
            hijo.hijos.insert(0, hermano_izq.hijos.pop())

    def _mover_clave_derecha(self, nodo, indice):
        hijo = nodo.hijos[indice]
        hermano_der = nodo.hijos[indice + 1]
        hijo.claves.append(nodo.claves[indice])
        nodo.claves[indice] = hermano_der.claves.pop(0)
        if not hijo.hoja:
            hijo.hijos.append(hermano_der.hijos.pop(0))

    def _combinar_nodos(self, nodo, indice):
        hijo = nodo.hijos[indice]
        hermano = nodo.hijos[indice + 1]
        hijo.claves.append(nodo.claves.pop(indice))
        hijo.claves.extend(hermano.claves)
        if not hijo.hoja:
            hijo.hijos.extend(hermano.hijos)
        del nodo.hijos[indice + 1]

    def actualizar(self, dpi, nuevos_datos):
        persona_antigua = self.buscar(dpi, self.raiz)
        if persona_antigua:
            if 'nombre' in nuevos_datos and nuevos_datos['nombre'] != "":
                nombre_nuevo = nuevos_datos['nombre']
            else:
                nombre_nuevo = persona_antigua.nombre

            if 'date_birth' in nuevos_datos and nuevos_datos['date_birth'] != "":
                date_birth_nueva = nuevos_datos['date_birth']
            else:
                date_birth_nueva = persona_antigua.date_birth

            if 'address' in nuevos_datos and nuevos_datos['address'] != "":
                address_nueva = nuevos_datos['address']
            else:
                address_nueva = persona_antigua.address

            persona_nueva = Persona(nombre_nuevo, dpi, date_birth_nueva, address_nueva)

            return self._actualizar_en_arbol(self.raiz, dpi, persona_nueva)
        else:
            return False

    def _actualizar_en_arbol(self, nodo, dpi, persona_nueva):
        if nodo is None:
            return False

        indice = 0
        while indice < len(nodo.claves) and dpi > nodo.claves[indice].dpi:
            indice += 1

        if indice < len(nodo.claves) and dpi == nodo.claves[indice].dpi:
            nodo.claves[indice] = persona_nueva
            return True
        elif nodo.hoja:
            return False
        else:
            return self._actualizar_en_arbol(nodo.hijos[indice], dpi, persona_nueva)

    def calcular_frecuencia(dpi):
        frecuencia = collections.Counter(dpi)
        return frecuencia

    def construir_arbol_huffman(frecuencia):
        heap = [[frecuencia[caracter], [caracter, ""]] for caracter in frecuencia]
        heapq.heapify(heap)
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        return sorted(heapq.heappop(heap)[1:], key=lambda p: (len(p[-1]), p))

    def codificar_dpi(dpi, arbol_huffman):
        codificacion = ""
        for caracter in dpi:
            for pair in arbol_huffman:
                if caracter == pair[0]:
                    codificacion += pair[1]
        return codificacion

    def decodificar_dpi(codificacion, arbol_huffman):
        dpi_decodificado = ""
        while codificacion:
            for pair in arbol_huffman:
                if codificacion.startswith(pair[1]):
                    dpi_decodificado += pair[0]
                    codificacion = codificacion[len(pair[1]):]
        return dpi_decodificado


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Administrar Personas")
        self.setGeometry(100, 100, 400, 400)

        self.boton_cargar = QPushButton("Cargar", self)
        self.boton_cargar.setGeometry(120, 10, 140, 40)
        self.boton_cargar.clicked.connect(self.cargar)

        self.boton_buscar = QPushButton("Buscar", self)
        self.boton_buscar.setGeometry(120, 60, 140, 40)
        self.boton_buscar.clicked.connect(self.buscar)

        self.input_buscar = QLineEdit(self)
        self.input_buscar.setGeometry(100, 110, 180, 40)

        self.boton_actualizar = QPushButton("Actualizar", self)
        self.boton_actualizar.setGeometry(120, 160, 140, 40)
        self.boton_actualizar.clicked.connect(self.actualizar)

        self.boton_eliminar = QPushButton("Eliminar", self)
        self.boton_eliminar.setGeometry(120, 210, 140, 40)
        self.boton_eliminar.clicked.connect(self.eliminar)

        self.combo_empresa = QComboBox(self)
        self.combo_empresa.setGeometry(100, 260, 180, 40)
        self.combo_empresa.addItem("Empresa A")
        self.combo_empresa.addItem("Empresa B")

        self.arboles_por_empresa = {
            "Empresa A": ArbolB(2),
            "Empresa B": ArbolB(2)
        }

    def cargar(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo CSV", "", "CSV Files (*.csv)")
        if archivo:
            try:
                with open(archivo, 'r', newline='') as file:
                    csv_reader = csv.DictReader(file, delimiter=';')
                    empresa_seleccionada = self.combo_empresa.currentText()
                    
                    for row in csv_reader:
                        nombre = row['nombre']
                        dpi = row['dpi']
                        date_birth = row['date_birth']
                        address = row['address']
                        
                        persona = Persona(nombre, dpi, date_birth, address, empresa_seleccionada)
                        self.arboles_por_empresa[empresa_seleccionada].insertar(persona)
                
                QMessageBox.information(self, "Éxito", "Datos cargados exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar el archivo CSV: {str(e)}")

    def buscar(self):
        dpi_a_buscar = self.input_buscar.text()
        empresa_seleccionada = self.combo_empresa.currentText()

        if dpi_a_buscar:
            arbol_empresa = self.arboles_por_empresa[empresa_seleccionada]
            persona = arbol_empresa.buscar(dpi_a_buscar, arbol_empresa.raiz)

            if persona:
                QMessageBox.information(self, "Resultado de búsqueda", f"Persona encontrada en {empresa_seleccionada}:\n"
                                                                        f"DPI: {persona.dpi}\n"
                                                                        f"Nombre: {persona.nombre}\n"
                                                                        f"Fecha de Nacimiento: {persona.date_birth}\n"
                                                                        f"Dirección: {persona.address}")
            else:
                QMessageBox.warning(self, "Resultado de búsqueda", "No se encontró ninguna persona con el DPI especificado en la empresa seleccionada.")
        else:
            QMessageBox.warning(self, "Error", "Ingrese un DPI válido para buscar.")

    def actualizar(self):
        dpi_a_actualizar, ok = QInputDialog.getText(self, "Actualizar Persona", "Ingrese el DPI de la persona a actualizar:")
        empresa_seleccionada = self.combo_empresa.currentText()

        if ok:
            arbol_empresa = self.arboles_por_empresa[empresa_seleccionada]
            persona = arbol_empresa.buscar(dpi_a_actualizar, arbol_empresa.raiz)

            if persona:
                dialogo_actualizar = ActualizarPersonaDialog(persona)
                if dialogo_actualizar.exec_() == QDialog.Accepted:
                    nuevos_datos = dialogo_actualizar.obtener_datos_actualizados()
                    if nuevos_datos:
                        if arbol_empresa.actualizar(dpi_a_actualizar, nuevos_datos):
                            QMessageBox.information(self, "Éxito", f"Persona actualizada exitosamente en {empresa_seleccionada}.")
                        else:
                            QMessageBox.warning(self, "Error", "No se pudo actualizar la persona.")
                else:
                    QMessageBox.warning(self, "Error", "La operación de actualización fue cancelada.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró ninguna persona con el DPI especificado en la empresa seleccionada.")

    def eliminar(self):
        dpi_a_eliminar, ok = QInputDialog.getText(self, "Eliminar Persona", "Ingrese el DPI de la persona a eliminar:")
        empresa_seleccionada = self.combo_empresa.currentText()

        if ok:
            arbol_empresa = self.arboles_por_empresa[empresa_seleccionada]

            if arbol_empresa.eliminar(dpi_a_eliminar):
                QMessageBox.information(self, "Éxito", f"Persona eliminada exitosamente en {empresa_seleccionada}.")
            else:
                QMessageBox.warning(self, "Error", "No se encontró ninguna persona con el DPI especificado en la empresa seleccionada.")

class ActualizarPersonaDialog(QDialog):
    def __init__(self, persona):
        super().__init__()

        self.setWindowTitle("Actualizar Persona")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.input_nombre = QLineEdit(self)
        self.input_nombre.setPlaceholderText("Nombre")
        self.input_nombre.setText(persona.nombre)
        layout.addWidget(self.input_nombre)

        self.input_date_birth = QLineEdit(self)
        self.input_date_birth.setPlaceholderText("Fecha de Nacimiento")
        self.input_date_birth.setText(persona.date_birth)
        layout.addWidget(self.input_date_birth)

        self.input_address = QLineEdit(self)
        self.input_address.setPlaceholderText("Dirección")
        self.input_address.setText(persona.address)
        layout.addWidget(self.input_address)

        self.boton_actualizar = QPushButton("Actualizar", self)
        self.boton_actualizar.clicked.connect(self.accept)
        layout.addWidget(self.boton_actualizar)

        self.setLayout(layout)

    def obtener_datos_actualizados(self):
        nuevos_datos = {}
        nuevos_datos['nombre'] = self.input_nombre.text()
        nuevos_datos['date_birth'] = self.input_date_birth.text()
        nuevos_datos['address'] = self.input_address.text()
        return nuevos_datos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())