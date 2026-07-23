# Documentación completa del archivo main.py

# ------------------------------
#         IMPORTACIONES
# ------------------------------
from kivy.app import App  
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.recycleview import RecycleView 
from kivy.properties import StringProperty,NumericProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior 
from kivy.properties import BooleanProperty 
from kivy.uix.recycleboxlayout import RecycleBoxLayout 
from kivy.uix.behaviors import FocusBehavior  
from kivy.uix.recycleview.layout import LayoutSelectionBehavior 
from kivy.uix.popup import Popup 
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.properties import NumericProperty
from database import insertar_producto, obtener_productos, buscar_producto
from database import obtener_productos, actualizar_stock
from database import actualizar_producto, eliminar_producto
from database import guardar_venta,guardar_detalle_venta
from datetime import datetime
from database import obtener_ventas,obtener_detalle_venta
from database import obtener_ventas
from database import obtener_detalle_venta
from database import obtener_ventas_fecha,total_ventas,total_vendido_hoy
from database import eliminar_venta
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from factura import generar_factura_pdf
from database import obtener_venta_por_id
from database import reiniciar_base_datos
from database import obtener_stock_bajo
from database import cantidad_ventas_hoy
from database import producto_mas_vendido
from database import obtener_control_inventario
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
#popup mostrar ventas
class HistorialVentasPopup(Popup):
    venta_seleccionada = None
    total_general = StringProperty("0")

    def cargar_datos(self):
        ventas = obtener_ventas()

        data = []

        for venta in ventas:
            data.append({
                "id_venta": str(venta[0]),
                "fecha": venta[1],
                "total": f"${venta[2]:.2f}"
            })

        self.ids.rv_ventas.data = data
        self.total_general = f"{total_ventas():,.2f}"
    
    def buscar_fecha(self):
        fecha = self.ids.txt_fecha.text

        ventas = obtener_ventas_fecha(fecha)

        data = []

        for venta in ventas:
            data.append({
                "id_venta": str(venta[0]),
                "fecha": venta[1],
                "total": f"${venta[2]:.2f}"
            })

        self.ids.rv_ventas.data = data

    def ver_detalle(self):

        if not self.venta_seleccionada:
            return

        popup = DetalleVentaPopup(
            venta_id=self.venta_seleccionada
        )

        popup.open()
        popup.cargar_datos()

#confirmacion antes de eliminar 

    def confirmar_eliminar_venta(self):

        if not self.venta_seleccionada:
            return

        contenido = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        mensaje = Label(
            text="¿Desea eliminar esta venta?"
        )

        botones = BoxLayout(
            size_hint_y=None,
            height="40dp",
            spacing=10
        )

        btn_si = Button(text="Sí")
        btn_no = Button(text="No")

        botones.add_widget(btn_si)
        botones.add_widget(btn_no)

        contenido.add_widget(mensaje)
        contenido.add_widget(botones)

        popup = Popup(
            title="Confirmar eliminación",
            content=contenido,
            size_hint=(0.5, 0.3),
            auto_dismiss=False
        )

        btn_no.bind(
            on_release=lambda x: popup.dismiss()
        )

        btn_si.bind(
            on_release=lambda x: self.eliminar_venta_confirmada(popup)
        )

        popup.open()


# metodo de eliminacion confirmada 
    def eliminar_venta_confirmada(self, popup):

        eliminar_venta(self.venta_seleccionada)

        popup.dismiss()

        self.cargar_datos()
#reimprimir factura de venta en pdf 

    def reimprimir_factura(self):

        if not self.venta_seleccionada:
            return

        venta = obtener_venta_por_id(
            self.venta_seleccionada
        )

        detalles = obtener_detalle_venta(
            self.venta_seleccionada
        )

        productos = []

        for d in detalles:

            productos.append({
                "codigo": d[0],
                "nombre": d[1],
                "cantidad_carrito": d[2],
                "precio": d[3],
                "precio_total": d[4]
            })

        generar_factura_pdf(
            venta[0],  # id venta
            venta[1],  # fecha
            productos,
            venta[2]   # total
        )

        print("Factura reimpresa correctamente")

class DetalleVentaPopup(Popup):

    def __init__(self, venta_id, **kwargs):
        super().__init__(**kwargs)
        self.venta_id = venta_id

    def cargar_datos(self):

        detalles = obtener_detalle_venta(self.venta_id)

        data = []

        for d in detalles:
            data.append({
                "codigo": str(d[0]),
                "nombre": str(d[1]),
                "cantidad": str(d[2]),
                "precio": f"${d[3]:.2f}",
                "subtotal": f"${d[4]:.2f}"
            })
        print(data) #<-- agrega esto

        self.ids.rv_detalle.data = data

#detalle stock bajo de productos 
class StockBajoPopup(Popup):
    codigo = StringProperty("")
    nombre = StringProperty("")
    cantidad = StringProperty("")

    def cargar_datos(self):

        productos = obtener_stock_bajo()

        data = []

        for p in productos:
            data.append({
                "codigo": str(p[1]),
                "nombre": p[2],
                "cantidad": str(p[4])
            })

        self.ids.rv_stock.data = data
#popup de estadisticas 

class EstadisticasPopup(Popup):

    def cargar_datos(self):

        total_hoy = total_vendido_hoy()
        ventas_hoy = cantidad_ventas_hoy()
        producto = producto_mas_vendido()

        self.ids.lbl_total_hoy.text = (
            f"Total vendido hoy: ${total_hoy:,.2f}"
        )
        self.ids.lbl_ventas_hoy.text = (
            f"ventas realizadas hoy: {ventas_hoy}"
        )
        if producto:
            self.ids.lbl_producto.text =(
                f"Producto más vendido: {producto[0]} ({producto[1]}unidades)")
        else:
            self.ids.lbl_producto.text =(
                "Producto más vendido: Sin datos"
                )
#popup control inventario
class ControlInventarioPopup(Popup):

    def cargar_datos(self):

        productos = obtener_control_inventario()

        data = []

        for p in productos:

            data.append({
                "codigo": str(p[0]),
                "nombre": p[1],
                "vendido": str(p[2]),
                "stock": str(p[3])
            })

        self.ids.rv_control.data = data

#control inventario
class FilaControlInventario(
    RecycleDataViewBehavior,
    BoxLayout
):

    codigo = StringProperty("")
    nombre = StringProperty("")
    vendido = StringProperty("")
    stock = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):

        self.codigo = data["codigo"]
        self.nombre = data["nombre"]
        self.vendido = data["vendido"]
        self.stock = data["stock"]

        return super().refresh_view_attrs(
            rv,
            index,
            data
        )
#stock bajo

class FilaStockBajo(RecycleDataViewBehavior, BoxLayout):

    codigo = StringProperty("")
    nombre = StringProperty("")
    cantidad = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):

        self.codigo = data.get("codigo", "")
        self.nombre = data.get("nombre", "")
        self.cantidad = data.get("cantidad", "")

        return super().refresh_view_attrs(rv, index, data)

class FilaHistorialVenta(RecycleDataViewBehavior, BoxLayout):
    id_venta = StringProperty("")
    fecha = StringProperty("")
    total = StringProperty("")

    index = NumericProperty(0)
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.id_venta = data["id_venta"]
        self.fecha = data["fecha"]
        self.total = data["total"]
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected

        if is_selected:
            popup = App.get_running_app().root.historial_popup
            popup.venta_seleccionada = int(rv.data[index]["id_venta"])

    def eliminar_venta(self):
        if not self.venta_seleccionada:
            return

        eliminar_venta_bd(self.venta_seleccionada)
        self.cargar_datos()

class FilaDetalleVenta(RecycleDataViewBehavior,BoxLayout):
    codigo = StringProperty("")
    nombre = StringProperty("")
    cantidad = StringProperty("")
    precio = StringProperty("")
    subtotal = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):
        self.codigo = data.get("codigo", "")
        self.nombre = data.get("nombre", "")
        self.cantidad = data.get("cantidad", "")
        self.precio = data.get("precio", "")
        self.subtotal = data.get("subtotal", "")

        return super().refresh_view_attrs(rv, index, data)


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

        Clock.schedule_once(
        self.verificar_stock_bajo,
        1
        )
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
        #fecha y hora de la venta 
        fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #guardar en cabezado de la venta
        venta_id=guardar_venta(fecha,self.total)

        productos_bd = obtener_productos()

        for item in self.ids.carrito_rv.data:

            #Guardar detalle de venta 
            guardar_detalle_venta(
                venta_id,
                item['codigo'],
                item['nombre'],
                item['cantidad_carrito'],
                item['precio'],
                item['precio_total']
                )
            #actualizar stock

            codigo = item['codigo']
            cantidad_vendida = item['cantidad_carrito']

            for p in productos_bd:
                if p[1] == codigo:
                    nuevo_stock = p[4] - cantidad_vendida
                    actualizar_stock(codigo, nuevo_stock)
                    break

        self.ids.notificacion_exito.text = "Pago realizado con éxito ✅"
        Clock.schedule_once(self._limpiar_notificacion, 3)
        generar_factura_pdf(
            venta_id,
            fecha,
            self.ids.carrito_rv.data,
            self.total
        )
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

# Metodo para abrir popup de historial de ventas 
    def abrir_historial_ventas(self):
        popup = HistorialVentasPopup()

        self.historial_popup=popup

        popup.cargar_datos()
        popup.open()
        # Mensaje opcional
        self.ids.notificacion_exito.text = "Venta cancelada con exito"
        Clock.schedule_once(self._limpiar_notificacion, 3)


    #reiniciar sistema:
    def reiniciar_sistema(self):

        reiniciar_base_datos()

        self.ids.notificacion_exito.text = (
            "Sistema reiniciado correctamente"
        )

        Clock.schedule_once(
            self._limpiar_notificacion,
            3
        )

    #confirmar reinicio
    def confirmar_reinicio(self):

        contenido = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10
        )

        mensaje = Label(
            text="¿Desea eliminar TODA la información?"
        )

        botones = BoxLayout(
            size_hint_y=None,
            height="40dp"
        )

        btn_si = Button(text="Sí")
        btn_no = Button(text="No")

        botones.add_widget(btn_si)
        botones.add_widget(btn_no)

        contenido.add_widget(mensaje)
        contenido.add_widget(botones)

        popup = Popup(
            title="Confirmar reinicio",
            content=contenido,
            size_hint=(0.6, 0.4),
            auto_dismiss=False
        )

        btn_no.bind(
            on_release=lambda x: popup.dismiss()
        )

        btn_si.bind(
            on_release=lambda x: self._reiniciar_confirmado(
                popup
            )
        )

        popup.open()

    #sistema reiniciado correctamente 

    def _reiniciar_confirmado(self, popup):

        reiniciar_base_datos()

        popup.dismiss()

        self.ids.notificacion_exito.text = (
            "Sistema reiniciado correctamente"
        )

        Clock.schedule_once(
            self._limpiar_notificacion,
            3
        )   
    #metodo stock bajo de productos 

    def ver_stock_bajo(self):

        productos = obtener_stock_bajo()

        print(productos)

    def abrir_stock_bajo(self):

        popup = StockBajoPopup()

        popup.open()

        popup.cargar_datos()

    def verificar_stock_bajo(self, dt):

        productos = obtener_stock_bajo()

        if len(productos) > 0:

            popup = Popup(
                title="Stock Bajo",
                content=Label(
                    text=f"Existen {len(productos)} productos con stock bajo."
                ),
                size_hint=(0.5, 0.3)
            )

            popup.open()

#metodo para abrir el popup de estadisticas

    def abrir_estadisticas(self):

        popup = EstadisticasPopup()

        popup.open()

        popup.cargar_datos()

#metodo de control inventario
    def abrir_control_inventario(self):

        popup = ControlInventarioPopup()

        popup.open()

        popup.cargar_datos()
#menu de opciones 
    def abrir_menu(self, boton):

        dropdown = DropDown()
        dropdown.auto_width = False
        dropdown.width = 220
        
        opciones = [
            ("Agregar Inventario", self.abrir_popup_agregar),
            ("Ver Inventario", self.abrir_popup_inventario),
            ("Historial Ventas", self.abrir_historial_ventas),
            ("Control Inventario", self.abrir_control_inventario),
            ("Estadísticas", self.abrir_estadisticas),
            ("Stock Bajo", self.abrir_stock_bajo),
            ("Reiniciar Sistema", self.confirmar_reinicio)
        ]

        for texto, accion in opciones:

            btn = Button(
                text=texto,
                size_hint_y=None,
                height=50,
                background_normal='',
                background_color=(0.22,0.22,0.22,1),
                color=(1,1,1,1),
                bold=True
            )

            btn.bind(on_release=lambda btn, a=accion:
                     (dropdown.dismiss(), a()))

            dropdown.add_widget(btn)

        dropdown.open(boton)
#-------------------------
#         APP PRINCIPAL
# ------------------------------
class VentasApp(App):
    def build(self):
        return VentasWindow()


if __name__ == '__main__':
    VentasApp().run()
