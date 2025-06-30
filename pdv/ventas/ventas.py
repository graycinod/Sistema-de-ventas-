from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
#Lista de diccionario que usaremos de prueba para verificar el funcionamiento de el sistema respecto a los productos.

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
#Permite que los elementos en un RecycleView 
# se puedan seleccionar y navegar usando el teclado o mouse.

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behavior to the view. '''
    touch_deselect_last= BooleanProperty(True)
#Hace que cada elemento de texto en la lista sea seleccionable. Se usa dentro del RecycleView.
#Atributos y métodos:
#selected: si está seleccionado o no.
#refresh_view_attrs: actualiza atributos cuando cambia la vista.
#on_touch_down: detecta el toque y selecciona el elemento.
#apply_selection: imprime el cambio de selección (por consola).

class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
       self.index=index
       self.ids['_hashtag'].text = str(1+index)
       self.ids['_articulo'].tex = data['nombre'].capitalize()
       self.ids['_cantidad'].text = str(data['cantidad_carrito'])
       self.ids['_precio_por_articulo'].text =str("{:.2f}".format(data['precio']))
       self.ids['_precio'].text = str("{:.2f}".format(data['precio_total']))
       return super(SelectableBoxLayout, self).refresh_view_attrs(
        rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayout, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

class SelectableBoxLayoutPopup(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
       self.index=index
       self.ids['_codigo'].text= data['codigo']
       self.ids['_articulo'].text= data['nombre'].capitalize()
       self.ids['_cantidad'].text= str(data['cantidad'])
       self.ids['_precio'].text=str['{:.2f}'.format(data['precio'])]
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
            print("selection changed to {0}".format(rv.data[index]))
        else:
            print("selection removed for {0}".format(rv.data[index]))

#Es la lista que muestra los elementos. Aquí genera 100 elementos de ejemplo (0 a 99) como etiquetas

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []

    def agregar_articulo(self, articulo):
        articulo['seleccionar']= False
        indice= -1
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
class ProductoPorNombrePopup(Popup):
    def __init__(self,input_nombre, **kwargs):
       super(ProductoPorNombrePopup, self).__init__(**kwargs)
       self.input_nombre=input_nombre

    def mostrar_articulos(self):
        self.open()
        for nombre in inventario:
            if nombre['nombre'].lower().find(self.input_nombre)>=0:#lower coloca en mayusculas,find :busca el parametro ingresado por el usuario
                producto={
                'codigo': nombre ['codigo'],
                'nombre': nombre ['nombre'],
                'precio': nombre ['precio'],
                'cantidad':nombre['cantidad']}
                self.ids.rvs.agregar_articulo(producto)
#Contenedor principal de la interfaz. Hereda de BoxLayout, lo que organiza los widgets en filas o columnas.

class VentasWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total=0.0

    def agregar_producto_codigo(self, codigo):
        for producto in inventario:
            if codigo == producto['codigo']:
                articulo={}
                articulo['codigo']= producto['codigo']
                articulo['nombre']= producto['nombre']
                articulo['precio']= producto['precio']
                articulo['cantidad_carrito']= 1
                articulo['cantidad_inventario']=producto['cantidad'] 
                articulo['precio_total']= producto['precio']
                self.agregar_producto(articulo)
                self.ids.buscar_codigo.text=''
                break


    def agregar_producto_nombre(self, nombre):
        self.ids.buscar_nombre.text=''
        popup=ProductoPorNombrePopup(nombre)
        popup.mostrar_articulos()

    def agregar_producto(self, articulo):
        self.total+=articulo['precio']
        self.ids.sub_total.text='$'+"{: .2f}".format(self.total)
        self.ids.rvs.agregar_articulo(articulo)

    def eliminar_producto(self):
        print("eliminar_producto presionado")

    def pagar(self):
        print("pagar")

    def nueva_compra(self):
        print("nueva_compra")
        
    def modificar_producto(self):
        print("modificar_producto presionado") 

    def admin(self):
        print("admin presionado")

    def signout(self):
        print("signout presionado")

#Es la aplicación principal. Kivy ejecuta esta clase y llama a build() para mostrar la interfaz que retorna VentasWindow.

class VentasApp(App):
    def build(self):
        return VentasWindow()


if __name__ == '__main__':
    VentasApp().run()