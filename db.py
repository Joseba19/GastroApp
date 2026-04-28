import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'nas.latorreg.es',
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
        cursor.execute("SELECT nombre FROM Categorias_Receta")
        categorias = cursor.fetchall()
        cursor.close()
        return categorias
    
def nombreIngredientes():
    """Obtiene todos los ingredientes usando context manager"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_ingrediente, nombre FROM Ingredientes")
        ingredientes = cursor.fetchall()
        cursor.close()
        return ingredientes

def infoReceta(page, per_page):
    """Obtiene recetas paginadas"""
    offset = (page - 1) * per_page

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        query = """
        SELECT r.id_receta, r.nombre, c.nombre AS nombre_categoria,
               r.dificultad, r.tiempo_preparacion, r.activo
        FROM Recetas r
        LEFT JOIN Categorias_Receta c ON r.id_categoria = c.id_categoria
        LIMIT %s OFFSET %s;
        """

        cursor.execute(query, (per_page, offset))
        recetas = cursor.fetchall()

        #contar total de recetas
        cursor.execute("SELECT COUNT(*) FROM Recetas;")
        total = cursor.fetchone()[0]

        cursor.close()

        return recetas, total

def infoRecetaFiltrada(page, per_page, categoria=None, dificultad=None):
    """Obtiene recetas paginadas con filtros opcionales"""
    offset = (page - 1) * per_page
    
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        
        # Construir query dinámica
        query = """
        SELECT r.id_receta, r.nombre, c.nombre AS nombre_categoria,
               r.dificultad, r.tiempo_preparacion, r.activo
        FROM Recetas r
        LEFT JOIN Categorias_Receta c ON r.id_categoria = c.id_categoria
        WHERE 1=1
        """
        params = []
        
        # Filtrar por categoría
        if categoria and categoria != "Todas las categorías":
            query += " AND c.nombre = %s"
            params.append(categoria)
        
        # Filtrar por dificultad
        if dificultad and dificultad != "Todas las dificultades":
            query += " AND r.dificultad = %s"
            params.append(dificultad.lower())  # asegurar minúsculas
        
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        recetas = cursor.fetchall()
        
        # Contar total con mismos filtros
        count_query = """
        SELECT COUNT(*) 
        FROM Recetas r
        LEFT JOIN Categorias_Receta c ON r.id_categoria = c.id_categoria
        WHERE 1=1
        """
        count_params = []
        
        if categoria and categoria != "Todas las categorías":
            count_query += " AND c.nombre = %s"
            count_params.append(categoria)
        
        if dificultad and dificultad != "Todas las dificultades":
            count_query += " AND r.dificultad = %s"
            count_params.append(dificultad.lower())
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
        
        cursor.close()
        return recetas, total

def crearReceta(nombre, id_categoria, dificultad, tiempo_preparacion, 
                tiempo_coccion, raciones, descripcion, instrucciones, activo):
    """Inserta una nueva receta en la base de datos"""
    
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        
        query = """
        INSERT INTO Recetas 
        (nombre, id_categoria, dificultad, tiempo_preparacion, 
         tiempo_coccion, raciones, descripcion, instrucciones, activo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (nombre, id_categoria, dificultad, tiempo_preparacion, 
                  tiempo_coccion, raciones, descripcion, instrucciones, activo)
        
        cursor.execute(query, valores)
        conexion.commit()  # IMPORTANTE: Guardar los cambios
        
        cursor.close()
        return cursor.lastrowid  # Devuelve el ID de la nueva receta

if __name__ == "__main__":
    conexionDB()
    infoReceta()