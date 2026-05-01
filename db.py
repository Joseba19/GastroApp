import mysql.connector
from datetime import datetime, date
from mysql.connector import Error
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'nas.latorreg.es',
    'user': 'root',
    'password': '7365',
    'database': 'gastrolab'
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

def categoriasBD():
    """Obtiene todas las categorías de recetas usando context manager"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_categoria, nombre FROM categorias_receta")
        categorias = cursor.fetchall()
        cursor.close()
        return categorias
    
def nombreIngredientes():
    """Obtiene todos los ingredientes usando context manager"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_ingrediente, nombre FROM ingredientes ORDER BY nombre ASC")
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
        FROM recetas r
        LEFT JOIN categorias_receta c ON r.id_categoria = c.id_categoria
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
        FROM recetas r
        LEFT JOIN categorias_receta c ON r.id_categoria = c.id_categoria
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
                listaCantidades, listaUnidades, listaNotas, listaPasos):
    """Inserta una nueva receta en la base de datos"""
    
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        
        query = """
        INSERT INTO recetas 
        (nombre, id_categoria, dificultad, tiempo_preparacion, 
         tiempo_coccion, raciones, descripcion, id_creador, fecha_creacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores = (nombre, id_categoria, dificultad, tiempo_preparacion, 
                  tiempo_coccion, raciones, descripcion, 1, date.today())
        
        cursor.execute(query, valores)
        conexion.commit()  # Guardar los cambios
                
        query2 = """
        SELECT MAX(id_receta) FROM recetas
        """
        
        cursor.execute(query2)
        ultimaReceta = cursor.fetchone()[0]
        
        contadorI = 0
        for i in listaIngredientes:
            
            query3 = """
            INSERT INTO recetas_ingredientes 
            (id_receta, id_ingrediente, cantidad, unidad, notas)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            if listaNotas == []:
                valores3 = (ultimaReceta, i, listaCantidades[contadorI], listaUnidades[contadorI], None)
            elif listaNotas[contadorI] == '':
                valores3 = (ultimaReceta, i, listaCantidades[contadorI], listaUnidades[contadorI], None)
            else:
                valores3 = (ultimaReceta, i, listaCantidades[contadorI], listaUnidades[contadorI], listaNotas[contadorI])
            
            contadorI += 1
            cursor.execute(query3, valores3)
            conexion.commit()
        
        contadorP = 0
        for p in listaPasos:
            contadorP += 1
            
            query4 = """
            INSERT INTO pasos_receta
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
        cursor.execute("DELETE FROM pasos_receta WHERE id_receta = %s", (id_receta,))
        cursor.execute("DELETE FROM recetas_ingredientes WHERE id_receta = %s", (id_receta,))
        cursor.execute("DELETE FROM recetas WHERE id_receta = %s", (id_receta,))
        
        conexion.commit()
        cursor.close()

def obtenerReceta(id_receta):
    """Obtiene toda la informacion de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM recetas WHERE id_receta = %s", (id_receta,))
        datosReceta = cursor.fetchone()
        cursor.close()
        return datosReceta

def obtenerPasos(id_receta):
    """Obtiene todos los pasos de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT numero_paso, descripcion FROM pasos_receta WHERE id_receta = %s", (id_receta,))
        pasosReceta = cursor.fetchall()
        cursor.close()
        return pasosReceta

def obtenerIngredientes(id_receta):
    """Obtiene todos los ingredientes de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT r.id_receta, r.id_ingrediente, i.nombre, r.cantidad, r.unidad, r.notas
        FROM recetas_ingredientes r
        JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
        WHERE r.id_receta = %s;""", (id_receta,))
        
        ingredientesReceta = cursor.fetchall()
        cursor.close()
        
        print(ingredientesReceta)
        
        
        ingredientesReceta = [list(item) for item in ingredientesReceta]
        for i in ingredientesReceta:
            if i[3] == i[3].to_integral_value():
                i[3] = str(int(i[3]))
            else:
                i[3] = f"{float(i[3]):.2f}"
        
        
        print(ingredientesReceta)
        
        return ingredientesReceta


def infoNutriReceta(id_receta):
    """Obtiene todos los macronutrientes de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT calorias_por_racion, proteinas_por_racion, carbohidratos_por_racion, grasas_por_racion, fibra_por_racion, sodio_por_racion
        FROM vista_nutricion_receta 
        WHERE id_receta = %s;""", (id_receta,))
        
        nutri = cursor.fetchall()
        cursor.close()

        # Convertir cada tupla a lista y formatear cada valor Decimal
        nutri_formateado = []
        for tupla in nutri:
            lista_formateada = []
            for valor in tupla:
                # Verificar si el valor es entero (en Decimal)
                if valor == valor.to_integral_value():
                    nutri_formateado.append(str(int(valor)))
                else:
                    nutri_formateado.append(f"{float(valor):.2f}")
        
        return nutri_formateado

def alergenosReceta(id_receta):
    """Obtiene todos los alergenos de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT alergenos
        FROM vista_nutricion_receta 
        WHERE id_receta = %s;""", (id_receta,))
        
        alergenos = cursor.fetchall()[0]
        cursor.close()
        
        print(alergenos)
        
        if alergenos[0] != None:
            alergenos = alergenos[0].split(",")

            alergenosFormateado = []
            for a in alergenos:
                a = a.strip()
                alergenosFormateado.append(a)
        else:
            alergenos = None
    
        #print(alergenosFormateado)

        return alergenos

if __name__ == "__main__":

    '''
    guardarReceta("Tortilla de Patata", 1, "facil", 2, 20, 15, "Tortilla de Patatas al estilo tradicional",
                  [12, 27], [6, 2], ["unidad", "unidad"], ["", "Cortada en laminas finas"], 
                  ["Pelar, cortar y poner la patata a pochar", 
                    "Batir los huevos", "Retirar la patata y mezclarla con los huevos",
                    "Reposar la mezcla 3 minutos y ponerla al punto de sal", 
                    "Poner la mezcla en una sarten y cocinarla minuto y medio por lado"])
    '''

    alergenosReceta(2)