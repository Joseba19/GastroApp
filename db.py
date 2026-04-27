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
    """Obtiene todas las categorías de recetas usando context manager"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM categoria_receta")
        categorias = cursor.fetchall()
        cursor.close()
        return categorias

def infoReceta(page, per_page):
    """Obtiene recetas paginadas"""
    offset = (page - 1) * per_page

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        query = """
        SELECT r.id_receta, r.nombre, c.nombre AS nombre_categoria,
               r.dificultad, r.tiempo_preparacion, r.activo
        FROM receta r
        LEFT JOIN categoria_receta c ON r.id_categoria = c.id_categoria
        LIMIT %s OFFSET %s;
        """

        cursor.execute(query, (per_page, offset))
        recetas = cursor.fetchall()

        #contar total de recetas
        cursor.execute("SELECT COUNT(*) FROM receta;")
        total = cursor.fetchone()[0]

        cursor.close()

        return recetas, total

if __name__ == "__main__":
    conexionDB()
    infoReceta()