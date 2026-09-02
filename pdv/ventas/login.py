import sqlite3

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.lang import Builder


# Cargar la interfaz de ventas
Builder.load_file("ventas.kv")

# Importar la ventana principal
from ventas import VentasWindow
# =========================================================
# CONTENEDOR PRINCIPAL DE LA APLICACIÓN
# =========================================================

class RootLayout(BoxLayout):

    def mostrar_ventas(self, nombre, rol):

        # Crear la ventana de ventas
        ventana_principal = VentasWindow(
            nombre_usuario=nombre,
            rol_usuario=rol
        )

        # Eliminar Login
        self.clear_widgets()

        # Mostrar Ventas
        self.add_widget(ventana_principal)


# =========================================================
# LOGIN
# =========================================================


#inicio de sesion del login 
class LoginWindow(BoxLayout):

    def iniciar_sesion(self):

        usuario = self.ids.txt_usuario.text.strip()
        contraseña = self.ids.txt_password.text

        # Verificación que los campos no estén vacíos
        if not usuario or not contraseña:
            self.mostrar_mensaje(
                "Error",
                "Por favor, ingrese usuario y contraseña."
            )
            return

        try:
            # Conectar con la base de datos
            conexion = sqlite3.connect("inventario.db")
            cursor = conexion.cursor()

            # Buscar el usuario
            cursor.execute("""
                SELECT nombre, usuario, contraseña, rol
                FROM usuarios
                WHERE usuario = ?
            """, (usuario,))

            resultado = cursor.fetchone()

            conexion.close()

            # Comprobar si existe
            if resultado is None:
                self.mostrar_mensaje(
                    "Error",
                    "El usuario no existe."
                )
                return

            nombre, usuario_db, contraseña_db, rol = resultado

            # Comprobar contraseña
            if contraseña != contraseña_db:
                self.mostrar_mensaje(
                    "Error",
                    "La contraseña es incorrecta."
                )
                return

             # =================================================
            # LOGIN CORRECTO
            # =================================================

            # Obtener el contenedor principal
            root_layout = self.parent

            # Cambiar Login por Ventas
            root_layout.mostrar_ventas(
                nombre,
                rol
            )


        except Exception as e:
            self.mostrar_mensaje(
                "Error",
                f"No se pudo conectar con la base de datos.\n\n{e}"
            )

    def mostrar_mensaje(self, titulo, mensaje):

        contenido = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        contenido.add_widget(Label(text=mensaje))

        boton = Button(
            text="Aceptar",
            size_hint_y=None,
            height="40dp"
        )

        contenido.add_widget(boton)

        popup = Popup(
            title=titulo,
            content=contenido,
            size_hint=(0.7, 0.35),
            auto_dismiss=False
        )

        boton.bind(on_release=popup.dismiss)

        popup.open()

# =========================================================
# APLICACIÓN
# =========================================================
class LoginApp(App):

    def build(self):
        root = RootLayout()

        login = LoginWindow()

        root.add_widget(login)

        return root


if __name__ == "__main__":
    LoginApp().run()