import mysql.connector
from datetime import datetime, date
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
        cursor.execute("SELECT id_categoria, nombre FROM Categorias_Receta")
        categorias = cursor.fetchall()
        cursor.close()
        return categorias
    
def nombreIngredientes():
    """Obtiene todos los ingredientes usando context manager"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_ingrediente, nombre FROM Ingredientes ORDER BY nombre ASC")
        ingredientes = cursor.fetchall()
        cursor.close()
    return ingredientes

def infoRecetaFiltrada(page, per_page, categoria=None, dificultad=None):
    """Obtiene recetas paginadas con filtros opcionales"""
    offset = (page - 1) * per_page
    
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        
        # Construir query dinámica
        query = """
        SELECT r.id_receta, r.nombre, c.nombre AS nombre_categoria,
               r.dificultad, r.tiempo_preparacion
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

def guardarReceta(nombre, id_categoria, dificultad, raciones, tiempo_preparacion, 
                tiempo_coccion, descripcion, listaIngredientes, 
                listaCantidades, listaNotas, listaPasos):
    """Inserta una nueva receta en la base de datos"""
    
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        
        query = """
        INSERT INTO Recetas 
        (nombre, id_categoria, dificultad, tiempo_preparacion, 
         tiempo_coccion, raciones, descripcion, id_creador, fecha_creacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (nombre, id_categoria, dificultad, tiempo_preparacion, 
                  tiempo_coccion, raciones, descripcion, 1, date.today())
        
        cursor.execute(query, valores)
        conexion.commit()  # Guardar los cambios
                
        query2 = """
        SELECT MAX(id_receta) FROM Recetas
        """
        
        cursor.execute(query2)
        ultimaReceta = cursor.fetchone()[0]
        
        contadorI = 0
        for i in listaIngredientes:
            
            query3 = """
            INSERT INTO Recetas_Ingredientes 
            (id_receta, id_ingrediente, cantidad, unidad, notas)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            if listaNotas == []:
                valores3 = (ultimaReceta, i, listaCantidades[contadorI], "g", None)
            elif listaNotas[contadorI] == '':
                valores3 = (ultimaReceta, i, listaCantidades[contadorI], "g", None)
            else:
                valores3 = (ultimaReceta, i, listaCantidades[contadorI], "g", listaNotas[contadorI])
            
            contadorI += 1
            cursor.execute(query3, valores3)
            conexion.commit()
        
        contadorP = 0
        for p in listaPasos:
            contadorP += 1
            
            query4 = """
            INSERT INTO Pasos_Receta
            (id_receta, numero_paso, descripcion)
            VALUES (%s, %s, %s)
            """
            
            valores4 = (ultimaReceta, contadorP, p)
            
            cursor.execute(query4, valores4)
            conexion.commit()
            
        cursor.close()

def eliminarReceta(id_receta):
    """Elimina una receta y sus datos relacionados"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        
        # Eliminar primero los datos dependientes (foreign keys)
        cursor.execute("DELETE FROM Pasos_Receta WHERE id_receta = %s", (id_receta,))
        cursor.execute("DELETE FROM Recetas_Ingredientes WHERE id_receta = %s", (id_receta,))
        cursor.execute("DELETE FROM Recetas WHERE id_receta = %s", (id_receta,))
        
        conexion.commit()
        cursor.close()

if __name__ == "__main__":
    conexionDB()
    guardarReceta("Tortilla", 2, "facil", 10, 5, 2, "Tortilla Francesa",
                  [12, 48], [50, 30], [], ["Batir huevos", "cocinar en la sarten"])