# Documentación completa del archivo main.py

# ------------------------------
#         IMPORTACIONES
# ------------------------------
from kivy.app import App  
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.recycleview import RecycleView 
from kivy.properties import StringProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior 
from kivy.properties import BooleanProperty 
from kivy.uix.recycleboxlayout import RecycleBoxLayout 
from kivy.uix.behaviors import FocusBehavior  
from kivy.uix.recycleview.layout import LayoutSelectionBehavior 
from kivy.uix.popup import Popup 
from kivy.clock import Clock
from kivy.properties import NumericProperty
from database import insertar_producto, obtener_productos, buscar_producto
from database import obtener_productos, actualizar_stock
from database import actualizar_producto, eliminar_producto
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

# ------------------------------
#         INVENTARIO
# ------------------------------


# ------------------------------
#   CLASES PARA SELECCIÓN carrito_rv
# ------------------------------
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """Layout que permite seleccionar elementos dentro del RecycleView."""
    touch_deselect_last = BooleanProperty(True)


class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    """Fila seleccionable del RecycleView principal (carrito)."""

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, carrito_rv, index, data):
        """Actualiza los textos de cada columna."""
        self.index = index
        
        self.selected = data.get('seleccionado', False)
        self.ids['_hashtag'].text = str(1 + index)
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad_carrito'])
        self.ids['_precio_por_articulo'].text = "{:.2f}".format(data['precio'])
        self.ids['_precio'].text = "{:.2f}".format(data['precio_total'])
        return super().refresh_view_attrs(carrito_rv, index, data)

    def on_touch_down(self, touch):
        """Detecta el toque para seleccionar la fila."""
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, carrito_rv, index, is_selected):
        """Marca internamente si la fila está seleccionada."""
        self.selected = is_selected
        carrito_rv.data[index]['seleccionado'] = is_selected

        if is_selected:
            app = App.get_running_app()
            app.root.inventario_seleccionado = carrito_rv.data[index]

# Popup para agregar productos al inventario

class AgregarProductoPopup(Popup):
    def __init__(self, on_guardar, **kwargs):
        super().__init__(**kwargs)
        self.on_guardar = on_guardar

    def guardar(self):
        try:
            codigo = self.ids.codigo.text
            nombre = self.ids.nombre.text
            precio = float(self.ids.precio.text)
            cantidad = int(self.ids.cantidad.text)

            self.on_guardar(codigo, nombre, precio, cantidad)

            # Limpiar campos
            self.ids.codigo.text = ""
            self.ids.nombre.text = ""
            self.ids.precio.text = ""
            self.ids.cantidad.text = ""

            self.dismiss()  #  cerrar popup

        except ValueError:
            self.ids.mensaje.text = "Datos inválidos"
#Ver producto del inventario en popup
class VerInventarioPopup(Popup):

    def cargar_datos(self):
        productos = obtener_productos()

        data = []
        for p in productos:
            data.append({
                "id_producto": p[0], 
                "codigo": str(p[1]),
                "nombre": p[2],
               "precio":str(p[3]),
                "cantidad": str(p[4])
                })
        self.ids.rv_inventario.data = data

    def editar_item(self):
        app = App.get_running_app()
        item = app.root.inventario_seleccionado

        if item:
            app.root.abrir_popup_editar_inventario(item)
        else:
            print("No hay producto seleccionado")

    def eliminar_item(self):
        app = App.get_running_app()
        item = app.root.inventario_seleccionado

        if item:
            eliminar_producto(item['id_producto'])
            self.cargar_datos()
        else:
            print("No hay producto seleccionado")


class FilaInventario(RecycleDataViewBehavior, BoxLayout):
    id_producto = NumericProperty(0)
    codigo = StringProperty("")
    nombre = StringProperty("")
    precio = StringProperty("")
    cantidad = StringProperty("")
    index = NumericProperty(0)

    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.id_producto = data.get("id_producto", 0)
        self.codigo = data['codigo']
        self.nombre = data['nombre']
        self.precio = data['precio']
        self.cantidad = data['cantidad']
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        rv.data[index]['seleccionado'] = is_selected

        if is_selected:
            app = App.get_running_app()
            app.root.inventario_seleccionado = rv.data[index]

class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, carrito_rv, index, data):
        self.index = index
        self.ids['_codigo'].text = data['codigo']
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio'].text = "{:.2f}".format(data['precio'])
        return super().refresh_view_attrs(carrito_rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, carrito_rv, index, is_selected):
        self.selected = is_selected

        #!importante!llamado de seleccion de producto
        carrito_rv.data[index]['seleccionado'] = is_selected


        if is_selected:
            app = App.get_running_app()
            app.root.inventario_seleccionado = carrito_rv.data[index]

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
        self.open()
        inventario = obtener_productos()  # 👈 traer desde BD

        for p in inventario:
            if self.nombre.lower() in p[2].lower():
                self.ids.carrito_rv.agregar_articulo({
                    'codigo': p[1],
                    'nombre': p[2],
                    'precio': p[3],
                    'cantidad': p[4],
                    'seleccionado': False
                })

    def seleccionar_articulo(self):
        """Agrega el artículo seleccionado desde el popup al carrito principal."""
        print(self.ids.carrito_rv.data)
        indice = self.ids.carrito_rv.articulo_seleccionado()
        if indice < 0:
            return

        prod = self.ids.carrito_rv.data[indice]

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
        self.inventario_seleccionado = None

#Agregar inventario SQLite

    def cargar_inventario(self):
        datos = obtener_productos()

        inventario = []
        for p in datos:
            inventario.append({
                'codigo': p[1],
                'nombre': p[2],
                'precio': p[3],
                'cantidad': p[4]
            })
        return inventario

#Editar inventario
    def abrir_popup_editar_inventario(self, item):

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        nombre = TextInput(text=item['nombre'])
        precio = TextInput(text=str(item['precio']))
        cantidad = TextInput(text=str(item['cantidad']))
        #botones 

        btn_guardar = Button(text="Guardar")
        btn_cerrar = Button(text="Cerrar")

        layout.add_widget(nombre)
        layout.add_widget(precio)
        layout.add_widget(cantidad)

        botones = BoxLayout(size_hint_y=None, height=50, spacing=10)
        botones.add_widget(btn_guardar)
        botones.add_widget(btn_cerrar)

        layout.add_widget(botones)

        popup = Popup(title="Editar producto", content=layout, size_hint=(0.7, 0.6))

        def guardar(*args):
            actualizar_producto(
                item['id_producto'],
                item['codigo'],
                nombre.text,
                float(precio.text),
                int(cantidad.text)
            )
            popup.dismiss()
            self.abrir_popup_inventario()
        btn_guardar.bind(on_release=guardar)
        btn_cerrar.bind(on_release=popup.dismiss)
        popup.open()


#Abrir ventana popup

    def abrir_popup_agregar(self):
        popup = AgregarProductoPopup(on_guardar=self.guardar_producto)
        popup.open()
    #Abrir ventana de inventario

    def abrir_popup_inventario(self):
        popup = VerInventarioPopup()
        popup.open()
        popup.cargar_datos()

    # ---- AGREGAR POR CÓDIGO ----
    def agregar_producto_codigo(self, codigo):
        inventario = self.cargar_inventario()
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
        self.ids.carrito_rv.agregar_articulo(articulo)

    #----GUARDAR PRODUCTOS ----
    def guardar_producto(self, codigo, nombre, precio, cantidad):
        try:
            insertar_producto(codigo, nombre, precio, cantidad)
        except Exception as e:
            self.ids.notificacion_exito.text = "Error al guardar producto ya existe ese codigo"
            print("ERROR INSERTAR:", e)
            return

        # Esto ya no rompe el guardado
        try:
            self.mostrar_productos()
        except Exception as e:
            print("ERROR MOSTRAR:", e)

        self.ids.notificacion_exito.text = "Producto guardado correctamente"
        Clock.schedule_once(self._limpiar_notificacion, 3)          


    #----MOSTRAR PRODUCTO----
    def mostrar_productos(self):
        productos = obtener_productos()

        self.ids.rv_inventario.data = [
            {
                "codigo": p[1],
                "nombre": p[2],
                "precio": p[3],
                "cantidad": p[4],
                "cantidad_carrito": 1,
                "cantidad_inventario": p[4],
                "precio_total": p[3],
                "seleccionado": False
            }
            for p in productos
        ]
    #---BUSCAR PRODUCTO---
    def buscar_producto(self):
        texto = self.ids.buscar.text
        resultados = buscar_producto(texto)

        self.ids.rv_inventario.data = [
            {
                "codigo": p[1],
                "nombre": p[2],
                "precio": p[3],
                "cantidad": p[4],
                "cantidad_carrito": 1,
                "cantidad_inventario": p[4],
                "precio_total": p[3],
                "seleccionado": False
            }
            for p in resultados
        ]

    # ---- RE-CALCULAR TOTAL ----
    def recalcular_total(self):
        nuevo = 0.0
        for item in self.ids.carrito_rv.data:
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
        carrito_rv = self.ids.carrito_rv
        # No hay artículos
        if not carrito_rv.data:
            self.ids.notificacion_exito.text = "No hay artículos en el carrito."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # Verificar si hay selección
        hay_sel = any(item.get('seleccionado', False) for item in carrito_rv.data)
        if not hay_sel:
            self.ids.notificacion_exito.text = "Seleccione un artículo para borrar."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # Eliminar seleccionados
        eliminados = 0
        for i in range(len(carrito_rv.data) - 1, -1, -1):
            if carrito_rv.data[i].get('seleccionado', False):
                carrito_rv.data.pop(i)
                eliminados += 1

            carrito_rv.refresh_from_data()
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

        carrito_rv = self.ids.carrito_rv  # Referencia al RecycleView del carrito

        # 1. Verificar si el carrito está vacío
        if not carrito_rv.data:
            self.ids.notificacion_exito.text = "No hay artículos en el carrito."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # 2. Obtener el índice del producto seleccionado
        indice = carrito_rv.articulo_seleccionado()
        if indice < 0:
            self.ids.notificacion_exito.text = "Seleccione un artículo para modificar."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # 3. Obtener el producto seleccionado
        item = carrito_rv.data[indice]

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
        carrito_rv.refresh_from_data()
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
        
        carrito_rv = self.ids.carrito_rv
        indice = carrito_rv.articulo_seleccionado()
        if nueva <= 0:
            self.ids.notificacion_exito.text = "La cantidad debe ser mayor a cero."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

       

        if indice < 0:
            self.ids.notificacion_exito.text = "No hay producto seleccionado."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        item = carrito_rv.data[indice]

        if nueva > item['cantidad_inventario']:
            self.ids.notificacion_exito.text = "Cantidad supera el inventario."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        # Actualizar datos
        item['cantidad_carrito'] = nueva
        item['precio_total'] = nueva * item['precio']

        carrito_rv.refresh_from_data()
        self.recalcular_total()

        self.ids.notificacion_exito.text = "Cantidad actualizada correctamente."
        Clock.schedule_once(self._limpiar_notificacion, 3)



    def pagar(self):
        if not self.ids.carrito_rv.data:
            self.ids.notificacion_exito.text = "No hay productos a pagar."
            Clock.schedule_once(self._limpiar_notificacion, 3)
            return

        popup = ConfirmarPagoPopup(
            total=self.total,
            confirmar_callback=self.confirmar_pago
        )
        popup.open()


    def confirmar_pago(self):
        productos_bd = obtener_productos()

        for item in self.ids.carrito_rv.data:
            codigo = item['codigo']
            cantidad_vendida = item['cantidad_carrito']

            for p in productos_bd:
                if p[1] == codigo:
                    nuevo_stock = p[4] - cantidad_vendida
                    actualizar_stock(codigo, nuevo_stock)
                    break

        self.ids.notificacion_exito.text = "Pago realizado con éxito ✅"
        Clock.schedule_once(self._limpiar_notificacion, 3)

        # limpiar carrito
        self.ids.carrito_rv.data = []
        self.total = 0
        self.ids.sub_total.text = "$ 0.00"
        self.ids.total.text = "$ 0.00"

    def cancelar(self):
    # Limpia el carrito
        self.ids.carrito_rv.data = []

        # Reinicia totales
        self.total = 0
        self.ids.sub_total.text = "$ 0.00"
        self.ids.total.text = "$ 0.00"

        # Mensaje opcional
        self.ids.notificacion_exito.text = "Venta cancelada"
        Clock.schedule_once(self._limpiar_notificacion, 3)

# ------------------------------
#         APP PRINCIPAL
# ------------------------------
class VentasApp(App):
    def build(self):
        return VentasWindow()


if __name__ == '__main__':
    VentasApp().run()
