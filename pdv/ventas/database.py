import sqlite3

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