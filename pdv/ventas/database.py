import sqlite3

def conectar():
    return sqlite3.connect("inventario.db")


def crear_tabla():
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE,
        nombre TEXT,
        precio REAL,
        cantidad INTEGER
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