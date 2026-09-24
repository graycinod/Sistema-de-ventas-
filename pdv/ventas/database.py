import sqlite3

PERMISOS_DISPONIBLES = [
    "agregar_inventario",
    "ver_inventario",
    "editar_inventario",
    "eliminar_inventario",
    "registrar_venta",
    "ver_historial",
    "eliminar_venta",
    "reimprimir_factura",
    "control_inventario",
    "estadisticas",
    "stock_bajo",
    "usuarios",
    "reiniciar"
]
def conectar():
    return sqlite3.connect("inventario.db")


def crear_tabla():

    conexion = conectar()
    cursor = conexion.cursor()

#tabla productos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        precio REAL,
        cantidad INTEGER
    )
    """)
    

# tabla ventas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        total REAL
    )
    """)
# tabla detalle venta
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        codigo_producto TEXT,
        nombre_producto TEXT,
        cantidad INTEGER,
        precio REAL,
        subtotal REAL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id)
    )
    """)


#table usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        usuario TEXT UNIQUE NOT NULL,
        contraseña TEXT NOT NULL,
        rol TEXT NOT NULL)
    """) 

# Tabla de permisos por usuario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permisos_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            permiso TEXT NOT NULL,
            permitido INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE(usuario_id, permiso)
        )
    """)
    
# Crear administrador por defecto
    cursor.execute("""
    SELECT COUNT(*) FROM usuarios
    """)

    cantidad = cursor.fetchone()[0]

    if cantidad == 0:
        cursor.execute("""
        INSERT INTO usuarios(nombre, usuario, contraseña, rol)
        VALUES (?, ?, ?, ?)
        """, (
            "Yulieth Vera",
            "admin",
            "1234",
            "Administrador"
        )) 


    conexion.commit()
    conexion.close() 
crear_tabla()



def insertar_producto(codigo, nombre, precio, cantidad):
    conexion = conectar()
    cursor = conexion.cursor()

     # verificar si ya existe
    cursor.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
    existe = cursor.fetchone()

    if existe:
        conexion.close()
        raise Exception("El código ya existe")

    cursor.execute("""
    INSERT INTO productos (codigo, nombre, precio, cantidad)
    VALUES (?, ?, ?, ?)
    """, (codigo, nombre, precio, cantidad))

    conexion.commit()
    conexion.close()


def obtener_productos():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()

    conexion.close()
    return datos


def buscar_producto(texto):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT * FROM productos
    WHERE codigo LIKE ? OR nombre LIKE ?
    """, (f"%{texto}%", f"%{texto}%"))

    datos = cursor.fetchall()
    conexion.close()
    return datos


def eliminar_producto(id_producto):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))

    conexion.commit()
    conexion.close()


def actualizar_stock(codigo, nueva_cantidad):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    UPDATE productos
    SET cantidad = ?
    WHERE codigo = ?
    """, (nueva_cantidad, codigo))

    conexion.commit()
    conexion.close()

def actualizar_producto(id_producto, codigo, nombre, precio, cantidad):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE productos
        SET codigo = ?, nombre = ?, precio = ?, cantidad = ?
        WHERE id = ?
    """, (codigo, nombre, precio, cantidad, id_producto))

    conexion.commit()
    conexion.close()

#guardado venta total

def guardar_venta(fecha, total):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO ventas(fecha, total)
        VALUES (?, ?)
    """, (fecha, total))

    venta_id = cursor.lastrowid

    conexion.commit()
    conexion.close()

    return venta_id

#impresion detalle de venta 

def guardar_detalle_venta(
        venta_id,
        codigo,
        nombre,
        cantidad,
        precio,
        subtotal):

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO detalle_venta(
            venta_id,
            codigo_producto,
            nombre_producto,
            cantidad,
            precio,
            subtotal
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    (
        venta_id,
        codigo,
        nombre,
        cantidad,
        precio,
        subtotal
    ))

    conexion.commit()
    conexion.close()

# Obtener todas las ventas
def obtener_ventas():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha, total
        FROM ventas
        ORDER BY id DESC
        """)

    datos = cursor.fetchall()

    conexion.close()
    return datos
#funcion para visualizar detalle de venta 

def obtener_detalle_venta(venta_id):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            codigo_producto,
            nombre_producto,
            cantidad,
            precio,
            subtotal
        FROM detalle_venta
        WHERE venta_id = ?
    """, (venta_id,))

    datos = cursor.fetchall()

    conexion.close()
    return datos

def obtener_ventas_fecha(fecha):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha, total
        FROM ventas
        WHERE fecha LIKE ?
        ORDER BY id DESC
    """, (f"%{fecha}%",))

    datos = cursor.fetchall()

    conexion.close()
    return datos

def total_ventas():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT SUM(total)
        FROM ventas
    """)

    total =cursor.fetchone()[0]

    conexion.close()

    return total if total else 0

def eliminar_venta(venta_id):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    # Eliminar primero los detalles
    cursor.execute("""
        DELETE FROM detalle_venta
        WHERE venta_id = ?
    """, (venta_id,))

    # Eliminar la venta
    cursor.execute("""
        DELETE FROM ventas
        WHERE id = ?
    """, (venta_id,))

    conexion.commit()
    conexion.close()

def obtener_venta_por_id(venta_id):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha, total
        FROM ventas
        WHERE id = ?
    """, (venta_id,))

    venta = cursor.fetchone()

    conexion.close()
    return venta

def reiniciar_base_datos():

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    # Vaciar tablas
    cursor.execute("DELETE FROM detalle_venta")
    cursor.execute("DELETE FROM ventas")
    cursor.execute("DELETE FROM productos")

    # Reiniciar contadores
    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name='detalle_venta'
    """)

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name='ventas'
    """)

    cursor.execute("""
        DELETE FROM sqlite_sequence
        WHERE name='productos'
    """)

    conexion.commit()
    conexion.close()

#obtener stock bajo
def obtener_stock_bajo(limite=5):

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT *
        FROM productos
        WHERE cantidad <= ?
        ORDER BY cantidad ASC
    """, (limite,))

    datos = cursor.fetchall()

    conexion.close()

    return datos

#total venta diaria 

def total_vendido_hoy():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT SUM(total)
        FROM ventas
        WHERE DATE(fecha) = DATE('now')
    """)

    resultado = cursor.fetchone()[0]

    conexion.close()

    return resultado if resultado else 0

#cantidad de ventas hoy
def cantidad_ventas_hoy():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM ventas
        WHERE DATE(fecha) = DATE('now')
    """)

    total = cursor.fetchone()[0]

    conexion.close()

    return total

#productos mas vendidos 
def producto_mas_vendido():

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            nombre_producto,
            SUM(cantidad) as total_vendido
        FROM detalle_venta
        GROUP BY nombre_producto
        ORDER BY total_vendido DESC
        LIMIT 1
    """)

    resultado = cursor.fetchone()

    conexion.close()

    return resultado

#control inventario
def obtener_control_inventario():

    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            p.codigo,
            p.nombre,

            COALESCE(
                (
                    SELECT SUM(d.cantidad)
                    FROM detalle_venta d
                    JOIN ventas v
                        ON d.venta_id = v.id
                    WHERE d.codigo_producto = p.codigo
                    AND DATE(v.fecha) = DATE('now')
                ),
                0
            ) AS vendido_hoy,

            p.cantidad AS stock_actual

        FROM productos p
        ORDER BY p.nombre
    """)

    datos = cursor.fetchall()

    conexion.close()

    return datos
#validación dde usuario

def validar_usuario(usuario, contraseña):

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT nombre, usuario, rol
    FROM usuarios
    WHERE usuario = ?
    AND contraseña = ?
    """, (usuario, contraseña))

    datos = cursor.fetchone()

    conexion.close()

    return datos
#Creación de usuarios en el sistema

def crear_usuario(nombre, usuario, contraseña, rol):

    conexion = conectar()
    cursor = conexion.cursor()
    try: 
        cursor.execute("""
        INSERT INTO usuarios(nombre,usuario,contraseña,rol)
        VALUES(?,?,?,?)
        """,(nombre,usuario,contraseña,rol))

        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False

    finally:
        conexion.close()

#funcion para guardar los permisos

def establecer_permiso(usuario_id, permiso, permitido):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO permisos_usuario (usuario_id, permiso, permitido)
        VALUES (?, ?, ?)
        ON CONFLICT(usuario_id, permiso)
        DO UPDATE SET permitido = excluded.permitido
    """, (usuario_id, permiso, 1 if permitido else 0))

    conexion.commit()
    conexion.close()

#funcion para consultar si el usuario tiene permisos

def tiene_permiso(usuario_id, permiso):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT permitido
        FROM permisos_usuario
        WHERE usuario_id = ? AND permiso = ?
    """, (usuario_id, permiso))

    resultado = cursor.fetchone()

    conexion.close()

    if resultado:
        return resultado[0] == 1

    return False
#funcion para obtener todos los permisos de usuario

def obtener_permisos_usuario(usuario_id):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT permiso, permitido
        FROM permisos_usuario
        WHERE usuario_id = ?
    """, (usuario_id,))

    resultados = cursor.fetchall()

    conexion.close()

    return resultados

#funcion para obtener el id de usuario

def obtener_usuario_por_nombre_usuario(usuario):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, usuario, rol
        FROM usuarios
        WHERE usuario = ?
    """, (usuario,))

    resultado = cursor.fetchone()

    conexion.close()

    return resultado

# Obtener todos los usuarios del sistema

def obtener_usuarios():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, nombre, usuario, rol
        FROM usuarios
        ORDER BY nombre
    """)

    resultados = cursor.fetchall()

    conexion.close()

    return resultados

#funcion para guardar todos los permisos de una vez 

def guardar_permisos_usuario(usuario_id, permisos):
    conexion = conectar()
    cursor = conexion.cursor()

    for permiso in PERMISOS_DISPONIBLES:
        permitido = 1 if permiso in permisos else 0

        cursor.execute("""
            INSERT INTO permisos_usuario (usuario_id, permiso, permitido)
            VALUES (?, ?, ?)
            ON CONFLICT(usuario_id, permiso)
            DO UPDATE SET permitido = excluded.permitido
        """, (usuario_id, permiso, permitido))

    conexion.commit()
    conexion.close()