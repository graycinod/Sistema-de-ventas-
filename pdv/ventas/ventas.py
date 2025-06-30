# Importación de clases necesarias de Kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup

# Lista de productos de ejemplo (simula un inventario)
inventario=ventas = [
    {'codigo': '1001',
    'nombre': 'Pan',
    'precio': 1000,
    'cantidad': 2},
    {
        "codigo": "1002",
        "nombre": "Leche",
        "precio": 3500,
        "cantidad": 1
    },
    {
        "codigo": "1003",
        "nombre": "Huevos x12",
        "precio": 7800,
        "cantidad": 1
    },
    {
        "codigo": "1004",
        "nombre": "Queso 250g",
        "precio": 5600,
        "cantidad": 3
    },
    {
        "codigo": "1005",
        "nombre": "Café 500g",
        "precio": 8500,
        "cantidad": 1
    }
]

# Clase que permite selección dentro de un RecycleView
#Permite que los elementos en un RecycleView 
# se puedan seleccionar y navegar usando el teclado o mouse.
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)

# Clase para representar un ítem seleccionable dentro del carrito de compras
class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        # Se actualizan los atributos visuales de cada fila
        self.index = index
        self.ids['_hashtag'].text = str(1+index)
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad_carrito'])
        self.ids['_precio_por_articulo'].text = str("{:.2f}".format(data['precio']))
        self.ids['_precio'].text = str("{:.2f}".format(data['precio_total']))
        return super(SelectableBoxLayout, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        # Detecta el toque para seleccionar el ítem
        if super(SelectableBoxLayout, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        # Cambia el estado de seleccionado y lo guarda en data
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']=True
        else:
            rv.data[index]['seleccionado']=False
# Clase para representar un ítem seleccionable en el popup de búsqueda por nombre
class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        # Actualiza los valores visuales de cada fila en el popup
        self.index = index
        self.ids['_codigo'].text = data['codigo']
        self.ids['_articulo'].text = data['nombre'].capitalize()
        self.ids['_cantidad'].text = str(data['cantidad'])
        self.ids['_precio'].text = str("{:.2f}".format(data['precio']))
        return super(SelectableBoxLayoutPopup, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayoutPopup, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']=True
        else:
            rv.data[index]['seleccionado']=False

# Clase que contiene y gestiona la lista del RecycleView
class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []# Lista de datos mostrados

    def agregar_articulo(self, articulo):
        # Agrega un artículo a la lista o incrementa su cantidad si ya existe
        articulo['seleccionado']=False
        indice=-1
        if self.data:
            for i in range(len(self.data)):
                if articulo['codigo']==self.data[i]['codigo']:
                    indice=i
            if indice >=0:
                self.data[indice]['cantidad_carrito']+=1
                self.data[indice]['precio_total']=self.data[indice]['precio']*self.data[indice]['cantidad_carrito']
                self.refresh_from_data()
            else:
                self.data.append(articulo)
        else:
            self.data.append(articulo)

    def articulo_seleccionado(self):
        # Retorna el índice del artículo seleccionado
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice=i
                break
        return indice

# Popup que aparece al buscar un producto por nombre
class ProductoPorNombrePopup(Popup):
    def __init__(self, input_nombre, agregar_producto_callback, **kwargs):
        super(ProductoPorNombrePopup, self).__init__(**kwargs)
        self.input_nombre=input_nombre
        self.agregar_producto=agregar_producto_callback# Función que agrega el producto al carrito

    def mostrar_articulos(self):
        # Muestra los productos cuyo nombre coincide parcial o totalmente
        self.open()
        for nombre in inventario:
            if nombre['nombre'].lower().find(self.input_nombre)>=0:
                producto={'codigo': nombre['codigo'], 'nombre': nombre['nombre'], 'precio': nombre['precio'], 'cantidad': nombre['cantidad']}
                self.ids.rvs.agregar_articulo(producto)

    def seleccionar_articulo(self):
        # Permite al usuario seleccionar un producto del popup
        indice=self.ids.rvs.articulo_seleccionado()
        if indice>=0:
            _articulo=self.ids.rvs.data[indice]
            articulo={}
            articulo['codigo']=_articulo['codigo']
            articulo['nombre']=_articulo['nombre']
            articulo['precio']=_articulo['precio']
            articulo['cantidad_carrito']=1
            articulo['cantidad_inventario']=_articulo['cantidad']
            articulo['precio_total']=_articulo['precio']
            if callable(self.agregar_producto):
                self.agregar_producto(articulo)
            self.dismiss()


# Ventana principal de ventas
class VentasWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total=0.0

    def agregar_producto_codigo(self, codigo):
        # Agrega un producto al carrito buscando por código
        for producto in inventario:
            if codigo==producto['codigo']:
                articulo={}
                articulo['codigo']=producto['codigo']
                articulo['nombre']=producto['nombre']
                articulo['precio']=producto['precio']
                articulo['cantidad_carrito']=1
                articulo['cantidad_inventario']=producto['cantidad']
                articulo['precio_total']=producto['precio']
                self.agregar_producto(articulo)
                self.ids.buscar_codigo.text=''
                break

    def agregar_producto_nombre(self, nombre):
        # Llama al popup de búsqueda por nombre
        self.ids.buscar_nombre.text=''
        popup=ProductoPorNombrePopup(nombre, self.agregar_producto)
        popup.mostrar_articulos()

    def agregar_producto(self, articulo):
        # Suma el precio del producto y lo añade al RecycleView
        self.total+=articulo['precio']
        self.ids.sub_total.text= '$ '+"{:.2f}".format(self.total)
        self.ids.rvs.agregar_articulo(articulo)

    # Métodos de acción que puedes completar más adelante
    def eliminar_producto(self):
        print("eliminar_producto presionado")

    def modificar_producto(self):
        print("eliminar_producto presionado")

    def pagar(self):
        print("pagar")

    def nueva_compra(self):
        print("nueva_compra")

    def admin(self):
        print("Admin presionado")

    def signout(self):
        print("Signout presionado")
        
# Clase principal que inicia la aplicación
class VentasApp(App):
    def build(self):
        return VentasWindow()

# Punto de entrada de la aplicación
if __name__=='__main__':
    VentasApp().run()