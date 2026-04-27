import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

DB_CONFIG = {
    'host': '192.168.1.10',
    'user': 'root',
    'password': '7365',
    'database': 'GastroLab'
}

@contextmanager     #Si hay algun error cierra la conexion.
def conexionDB():
    """Context manager para la conexión a BD"""
    conexion = None
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        yield conexion
    except Error as err:
        print(f"Error de conexión: {err}")
        raise
    finally:
        if conexion and conexion.is_connected():
            conexion.close()


def categoriaReceta():
    """Obtiene todas las categorías usando context manager"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM categoria_receta")
        resultados = cursor.fetchall()
        cursor.close()
        return resultados