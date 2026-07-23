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