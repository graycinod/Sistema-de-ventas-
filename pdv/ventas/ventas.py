# Documentación completa del archivo main.py

# ------------------------------
#         IMPORTACIONES
# ------------------------------
from kivy.app import App  
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.recycleview import RecycleView 
from kivy.uix.recycleview.views import RecycleDataViewBehavior 
from kivy.properties import BooleanProperty 
from kivy.uix.recycleboxlayout import RecycleBoxLayout 
from kivy.uix.behaviors import FocusBehavior  
from kivy.uix.recycleview.layout import LayoutSelectionBehavior 
from kivy.uix.popup import Popup 
from kivy.clock import Clock
from kivy.properties import NumericProperty


# ------------------------------
#         INVENTARIO
# ------------------------------
inventario = [
    {'codigo': '1001', 'nombre': 'Pan', 'precio': 1000, 'cantidad': 2},
    {'codigo': '1002', 'nombre': 'Leche', 'precio': 3500, 'cantidad': 1},
    {'codigo': '1003', 'nombre': 'Huevos x12', 'precio': 7800, 'cantidad': 1},
    {'codigo': '1004', 'nombre': 'Queso 250g', 'precio': 5600, 'cantidad': 3},
    {'codigo': '1005', 'nombre': 'Café 500g', 'precio': 8500, 'cantidad': 1}
]


# ------------------------------
#   CLASES PARA SELECCIÓN RV
# ------------------------------
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """Layout que permite seleccionar elementos dentro del RecycleView."""
    touch_deselect_last = BooleanProperty(True)


class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    """Fila seleccionable del RecycleView principal (carrito)."""

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Actualiza los textos de cada columna."""
        self.index = index
        
        self.selected = data.get('seleccionado', False)
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad_carrito'])
        self.ids['_precio_por_articulo'].text = "{:.2f}".format(data['precio'])
        self.ids['_precio'].text = "{:.2f}".format(data['precio_total'])
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """Detecta el toque para seleccionar la fila."""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Marca internamente si la fila está seleccionada."""
        self.selected = is_selected
        rv.data[index]['seleccionado'] = is_selected

# ------------------------------
#   SELECTOR PARA EL POPUP
# ------------------------------
class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    """Versión usada en el popup de buscar producto por nombre."""

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_codigo'].text = data['codigo']
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio'].text = "{:.2f}".format(data['precio'])
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        rv.data[index]['seleccionado'] = is_selected
        

# ------------------------------
#   MANEJO DEL RECYCLEVIEW
# ------------------------------
class RV(RecycleView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = []  # Aquí se guarda todo el carrito

    def agregar_articulo(self, articulo):
        """Agrega un producto o aumenta su cantidad."""
        articulo['seleccionado'] = False
        indice = -1

        for i in range(len(self.data)):
            if articulo['codigo'] == self.data[i]['codigo']:
                indice = i

        if indice >= 0:
            # Ya existe → aumentar cantidad
            self.data[indice]['cantidad_carrito'] += 1
            self.data[indice]['precio_total'] = (
                self.data[indice]['precio'] * self.data[indice]['cantidad_carrito']
            )
            self.refresh_from_data()
        else:
            # Nuevo producto
            self.data.append(articulo)

    def articulo_seleccionado(self):
        """Devuelve el índice del artículo marcado con seleccionado=True."""
        for i in range(len(self.data)):
            if self.data[i].get('seleccionado', False):
                return i
        return -1


# ------------------------------
#   POPUP BUSCAR POR NOMBRE
# ------------------------------
class ProductoPorNombrePopup(Popup):

    def __init__(self, nombre, cb_agregar, **kwargs):
        super().__init__(**kwargs)
        self.nombre = nombre
        self.cb_agregar = cb_agregar

    def mostrar_articulos(self):
        """Llena el popup con los productos que coinciden."""
        self.open()
        for prod in inventario:
            if prod['nombre'].lower().find(self.nombre) >= 0:
                self.ids.rvs.agregar_articulo({
                    'codigo': prod['codigo'],
                    'nombre': prod['nombre'],
                    'precio': prod['precio'],
                    'cantidad': prod['cantidad'],
                    'seleccionado': False
                })

    def seleccionar_articulo(self):
        """Agrega el artículo seleccionado desde el popup al carrito principal."""
        indice = self.ids.rvs.articulo_seleccionado()
        if indice < 0:
            return

        prod = self.ids.rvs.data[indice]

        articulo = {
            'codigo': prod['codigo'],
            'nombre': prod['nombre'],
            'precio': prod['precio'],
            'cantidad_carrito': 1,
            'cantidad_inventario': prod['cantidad'],
            'precio_total': prod['precio']
        }

        self.cb_agregar(articulo)
        self.dismiss()

class ModificarCantidadPopup(Popup):
    """Para modificar manualmente la cantidad de productos del carrito"""
    def __init__(self,item,on_confirmar,**kwargs):
        super().__init__(**kwargs)
        self.item=item   #producto a modificar
        self.on_confirmar=on_confirmar#Callback al confirmar
    def confirmar(self):
        texto =self.ids.input_cantidad.text
        self.on_confirmar(texto)
        self.dismiss()

class ConfirmarPagoPopup(Popup):
    total = NumericProperty(0.0)

    def __init__(self,total,confirmar_callback, **kwargs):
        super().__init__(**kwargs)
        self.total=total
        self.confirmar_callback=confirmar_callback

    def confirmar(self):
        self.confirmar_callback()
        self.dismiss()
        
# ------------------------------
#      VENTANA PRINCIPAL
# ------------------------------
class VentasWindow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sub_total = 0.0
        self.total=0.0

    # ---- AGREGAR POR CÓDIGO ----
    def agregar_producto_codigo(self, codigo):
        for p in inventario:
            if codigo == p['codigo']:
                articulo = {
                    'codigo': p['codigo'],
                    'nombre': p['nombre'],
                    'precio': p['precio'],
                    'cantidad_carrito': 1,
                    'cantidad_inventario': p['cantidad'],
                    'precio_total': p['precio'],
                    'seleccionado': False
                }
                self.agregar_producto(articulo)
                self.ids.buscar_codigo.text = ''
                break

    # ---- AGREGAR POR NOMBRE ----
    def agregar_producto_nombre(self, nombre):
        popup = ProductoPorNombrePopup(nombre, self.agregar_producto)
        self.ids.buscar_nombre.text = ""
        popup.mostrar_articulos()

    # ---- AGREGAR AL CARRITO ----
    def agregar_producto(self, articulo):
        self.total += articulo['precio']
        self.ids.sub_total.text = '$ ' + "{:.2f}".format(self.total)
        self.ids.total.text = '$ ' + "{:.2f}".format(self.total)
        self.ids.rvs.agregar_articulo(articulo)

    # ---- RE-CALCULAR TOTAL ----
    def recalcular_total(self):
        nuevo = 0.0
        for item in self.ids.rvs.data:
            nuevo += float(item['precio_total'])
        self.total = nuevo
        self.ids.sub_total.text = '$ ' + "{:.2f}".format(self.total)

    # ---- LIMPIAR NOTIFICACIONES ----
    def _limpiar_notificacion(self, dt):
        self.ids.notificacion_exito.text = ''

    # ------------------------------
    #        ELIMINAR PRODUCTO
    # ------------------------------
    def eliminar_producto(self):
        rv = self.ids.rvs
        # No hay artículos
        if not rv.data:
            self.ids.notificacion_exito.text = "No hay artículos en el carrito."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # Verificar si hay selección
        hay_sel = any(item.get('seleccionado', False) for item in rv.data)
        if not hay_sel:
            self.ids.notificacion_exito.text = "Seleccione un artículo para borrar."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # Eliminar seleccionados
        eliminados = 0
        for i in range(len(rv.data) - 1, -1, -1):
            if rv.data[i].get('seleccionado', False):
                rv.data.pop(i)
                eliminados += 1

            rv.refresh_from_data()
            self.recalcular_total()

            self.ids.notificacion_exito.text = f"{eliminados} artículo(s) eliminado(s)."
            Clock.schedule_once(self._limpiar_notificacion, 3)

    # ---- MÉTODOS VACÍOS ----
    def modificar_producto(self):
        print("modificar_producto presionado")
        """
        Modifica la cantidad del producto seleccionado en el carrito.

        Funcionamiento:
        1. Verifica si el carrito contiene artículos.
        2. Comprueba que exista un producto seleccionado.
        3. Valida que no se supere la cantidad disponible en inventario.
        4. Incrementa la cantidad del producto seleccionado.
        5. Actualiza el precio total del producto.
        6. Refresca el RecycleView y recalcula el total de la compra.
        7. Muestra un mensaje informativo al usuario.

        Este método evita cierres inesperados de la aplicación y garantiza
        que solo se modifique un producto válido.
        """

        rv = self.ids.rvs  # Referencia al RecycleView del carrito

        # 1. Verificar si el carrito está vacío
        if not rv.data:
            self.ids.notificacion_exito.text = "No hay artículos en el carrito."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # 2. Obtener el índice del producto seleccionado
        indice = rv.articulo_seleccionado()
        if indice < 0:
            self.ids.notificacion_exito.text = "Seleccione un artículo para modificar."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # 3. Obtener el producto seleccionado
        item = rv.data[indice]

        #Abrir Popup
        popup=ModificarCantidadPopup(
            item=item,
            on_confirmar=self._confirmar_cantidad
        )
        popup.open()

        # 4. Validar disponibilidad en inventario
        if item['cantidad_carrito'] >= item['cantidad_inventario']:
            self.ids.notificacion_exito.text = "No hay más unidades disponibles."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # 5. Incrementar la cantidad del producto
        item['cantidad_carrito'] += 1

        # 6. Recalcular el precio total del producto
        item['precio_total'] = item['cantidad_carrito'] * item['precio']

        # 7. Actualizar la vista y recalcular el total general
        rv.refresh_from_data()
        self.recalcular_total()

        # 8. Notificar al usuario
        self.ids.notificacion_exito.text = "Producto modificado correctamente."
        Clock.schedule_once(self._limpiar_notificacion, 3)
    def _confirmar_cantidad(self, texto):
        try:
            nueva = int(texto)
        except ValueError:
            self.ids.notificacion_exito.text = "Cantidad inválida."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return
        
        rv = self.ids.rvs
        indice = rv.articulo_seleccionado()
        if nueva <= 0:
            self.ids.notificacion_exito.text = "La cantidad debe ser mayor a cero."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

       

        if indice < 0:
            self.ids.notificacion_exito.text = "No hay producto seleccionado."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        item = rv.data[indice]

        if nueva > item['cantidad_inventario']:
            self.ids.notificacion_exito.text = "Cantidad supera el inventario."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # Actualizar datos
        item['cantidad_carrito'] = nueva
        item['precio_total'] = nueva * item['precio']

        rv.refresh_from_data()
        self.recalcular_total()

        self.ids.notificacion_exito.text = "Cantidad actualizada correctamente."
        Clock.schedule_once(self._limpiar_notificacion, 3)



    def pagar(self):
        if not self.ids.rvs.data:
            self.ids.notificacion_exito.text = "No hay productos a pagar."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        popup = ConfirmarPagoPopup(
            total=self.total,
            confirmar_callback=self.confirmar_pago
        )
        popup.open()

    def confirmar_pago(self):
        self.ids.notificacion_exito.text = "Pago realizado con éxito ✅"
        Clock.schedule_once(self._limpiar_notificacion, 3)

        # Limpiar carrito
        self.ids.rvs.data = []
        self.sub_total = 0.0
        self.total = 0.0

        self.ids.sub_total.text = "$ 0.00"
        self.ids.total.text = "$ 0.00"

    def nueva_compra(self):
        print("nueva_compra")

    def admin(self):
        print("Admin presionado")

    def signout(self):
        print("Signout presionado")


# ------------------------------
#         APP PRINCIPAL
# ------------------------------
class VentasApp(App):
    def build(self):
        return VentasWindow()


if __name__ == '__main__':
    VentasApp().run()
