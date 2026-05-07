import mysql.connector
import bcrypt
from datetime import datetime, date
from mysql.connector import Error
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'nas.latorreg.es',
    'user': 'root',
    'password': '7365',
    'database': 'gastrolab'
}

@contextmanager
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
    """Obtiene todas las categorías de las recetas"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_categoria, nombre FROM categorias_receta")
        categorias = cursor.fetchall()
        cursor.close()
        return categorias

def nombreIngredientes():
    """Obtiene los nombres de todos los ingredientes"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_ingrediente, nombre FROM ingredientes ORDER BY nombre ASC")
        ingredientes = cursor.fetchall()
        cursor.close()
    return ingredientes

def infoRecetaFiltrada(page, per_page, categoria=None, dificultad=None):
    """Obtiene recetas paginadas con filtros opcionales"""
    offset = (page - 1) * per_page      #Paginacion hecha con IA, sino la web es larguisima

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        query = """
        SELECT r.id_receta, r.nombre, c.nombre AS nombre_categoria,
               r.dificultad, r.tiempo_preparacion
        FROM recetas r
        LEFT JOIN categorias_receta c ON r.id_categoria = c.id_categoria
        WHERE 1=1
        """
        
        # Añade las condiciones a la query y los valores a la lista param
        param = []
        if categoria and categoria != "Todas las categorías":
            query += " AND c.nombre = %s"
            param.append(categoria)

        if dificultad and dificultad != "Todas las dificultades":
            query += " AND r.dificultad = %s"
            param.append(dificultad.lower())

        query += " LIMIT %s OFFSET %s"
        param.extend([per_page, offset])        #Parte de la paginacion, extend sirve para introducir iterables en una lista

        cursor.execute(query, param)
        recetas = cursor.fetchall()

        #Cuenta la cantidad de recetas, para ajustar las paginas
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
        # Elimina los datos dependientes de la receta primero, y luego la rceta
        cursor.execute("DELETE FROM pasos_receta WHERE id_receta = %s", (id_receta,))
        cursor.execute("DELETE FROM recetas_ingredientes WHERE id_receta = %s", (id_receta,))
        cursor.execute("DELETE FROM recetas WHERE id_receta = %s", (id_receta,))
        
        conexion.commit()
        cursor.close()

def obtenerReceta(id_receta):
    """Obtiene toda la información de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM recetas WHERE id_receta = %s", (id_receta,))      #Al ser una sola variable, hay que poner una coma al final (sinsentido)
        datosReceta = cursor.fetchone()
        cursor.close()
        return datosReceta

def obtenerPasos(id_receta):
    """Obtiene todos los pasos de una receta ordenados"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT numero_paso, descripcion 
        FROM pasos_receta 
        WHERE id_receta = %s ORDER BY numero_paso ASC""", (id_receta,))
        
        pasosReceta = cursor.fetchall()
        cursor.close()
        return pasosReceta

def obtenerIngredientes(id_receta):
    """Obtiene todos los datos de un ingrediente"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT r.id_receta, r.id_ingrediente, i.nombre, r.cantidad, r.unidad, r.notas
        FROM recetas_ingredientes r
        JOIN ingredientes i ON r.id_ingrediente = i.id_ingrediente
        WHERE r.id_receta = %s;""", (id_receta,))

        ingredientesReceta = cursor.fetchall()
        cursor.close()

        listaIngredientes = []
        for i in ingredientesReceta:
            listaIngredientes.append(list(i))      #list() convierte tuplas en listas

        #Bucle para hacer que los ingredientes tengan 2 decimales o ninguno
        for i in listaIngredientes:
            if i[3] == i[3].to_integral_value():
                i[3] = str(int(i[3]))
            else:
                i[3] = f"{float(i[3]):.2f}"

        return listaIngredientes

def infoNutriReceta(id_receta):
    """Obtiene todos los macronutrientes de una receta usando la vista"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT calorias_por_racion, proteinas_por_racion, carbohidratos_por_racion,
               grasas_por_racion, fibra_por_racion, sodio_por_racion
        FROM vista_nutricion_receta
        WHERE id_receta = %s;""", (id_receta,))

        nutri = cursor.fetchone()
        cursor.close()

    #Manejo de errores
    if not nutri:
        return []

    #Bucle para cambiar las cadenas vacias por "—" y formatear los numeros como antes
    nutri_formateado = []
    for info in nutri:
        if info is None:
            nutri_formateado.append("—")
        elif info == info.to_integral_value():
            nutri_formateado.append(str(int(info)))
        else:
            nutri_formateado.append(f"{float(info):.2f}")

    return nutri_formateado

def alergenosReceta(id_receta):
    """Obtiene todos los alérgenos de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT alergenos
        FROM vista_nutricion_receta
        WHERE id_receta = %s;""", (id_receta,))

        alergenos = cursor.fetchone()
        cursor.close()

    #Manejo de errores
    if alergenos[0] is None:
        return None

    #Bucle para pasar de una tupla con una cadena de texto, a una lista bien separada
    alergenosFormateado = []
    for a in alergenos[0].split(","):
        alergenosFormateado.append(a.strip())

    return alergenosFormateado

def actualizarReceta(id_receta, nombre, id_categoria, dificultad, raciones, tiempo_preparacion,
                tiempo_coccion, descripcion, listaIngredientes,
                listaCantidades, listaUnidades, listaNotas, listaPasos):
    """Actualiza una receta de la base de datos"""

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
        UPDATE recetas
        SET nombre = %s, descripcion = %s, tiempo_preparacion = %s, tiempo_coccion = %s,
        raciones = %s, dificultad = %s, id_categoria = %s
        WHERE id_receta = %s;
        """, (nombre, descripcion, tiempo_preparacion, tiempo_coccion, raciones,
              dificultad, id_categoria, id_receta))
        conexion.commit()
        
        #Borramos los datos dependientes y los reescribimos
        cursor.execute("DELETE FROM recetas_ingredientes WHERE id_receta = %s", (id_receta,))
        
        contadorI = 0
        for i in listaIngredientes:
            
            query3 = """
            INSERT INTO recetas_ingredientes 
            (id_receta, id_ingrediente, cantidad, unidad, notas)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            if listaNotas == []:
                valores3 = (id_receta, i, listaCantidades[contadorI], listaUnidades[contadorI], None)
            elif listaNotas[contadorI] == '':
                valores3 = (id_receta, i, listaCantidades[contadorI], listaUnidades[contadorI], None)
            else:
                valores3 = (id_receta, i, listaCantidades[contadorI], listaUnidades[contadorI], listaNotas[contadorI])
            
            contadorI += 1
            cursor.execute(query3, valores3)
            conexion.commit()

        cursor.execute("DELETE FROM pasos_receta WHERE id_receta = %s", (id_receta,))

        contadorP = 0
        for p in listaPasos:
            contadorP += 1
            
            query4 = """
            INSERT INTO pasos_receta
            (id_receta, numero_paso, descripcion)
            VALUES (%s, %s, %s)
            """
            
            valores4 = (id_receta, contadorP, p)
            
            cursor.execute(query4, valores4)
            conexion.commit()

        cursor.close()

def guardarIngrediente(nombre, unidad, categoria, calorias, proteina, carbohidratos, grasas, fibra, sodio):
    """Guarda un ingrediente en la base de datos y asigna sus alérgenos"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
        INSERT INTO ingredientes
        (nombre, unidad_medida, categoria, calorias_100g,
        proteinas_100g, carbohidratos_100g, grasas_100g, fibra_100g, sodio_100g)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, unidad, categoria, calorias,
              proteina, carbohidratos, grasas,
              fibra, sodio))

        conexion.commit()
        cursor.close()

# INGREDIENTES

#Paginacion echa con IA
def obtenerIngredientesFiltrados(page, per_page, categoria=None, unidad=None):
    """Obtiene ingredientes paginados con filtros opcionales"""
    offset = (page - 1) * per_page

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        query = """
        SELECT i.id_ingrediente, i.nombre, i.categoria, i.unidad_medida,
               i.calorias_100g, i.proteinas_100g, i.carbohidratos_100g,
               i.grasas_100g, i.fibra_100g, i.sodio_100g,
               GROUP_CONCAT(a.nombre ORDER BY a.nombre SEPARATOR ', ') AS alergenos
        FROM ingredientes i
        LEFT JOIN ingredientes_alergenos ia ON i.id_ingrediente = ia.id_ingrediente
        LEFT JOIN alergenos a ON ia.id_alergeno = a.id_alergeno
        WHERE 1=1
        """
        params = []

        if categoria:
            query += " AND i.categoria = %s"
            params.append(categoria)

        if unidad:
            query += " AND i.unidad_medida = %s"
            params.append(unidad)

        query += " GROUP BY i.id_ingrediente ORDER BY i.nombre ASC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        ingredientes = cursor.fetchall()

        count_query = "SELECT COUNT(*) FROM ingredientes WHERE 1=1"
        count_params = []

        if categoria:
            count_query += " AND categoria = %s"
            count_params.append(categoria)

        if unidad:
            count_query += " AND unidad_medida = %s"
            count_params.append(unidad)

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        cursor.close()
        return ingredientes, total

def obtenerCategoriasIngredientes():
    """Devuelve la lista de categorías únicas de ingredientes"""
    
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT DISTINCT categoria
            FROM ingredientes
            WHERE categoria IS NOT NULL
            ORDER BY categoria ASC
        """)

        categorias = []
        for row in cursor.fetchall():
            categorias.append(row[0])
        
        cursor.close()
        return categorias

def obtenerIngrediente(id_ingrediente):
    """Devuelve todos los datos de un ingrediente por su id"""
   
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT i.id_ingrediente, i.nombre, i.categoria, i.unidad_medida,
                   i.calorias_100g, i.proteinas_100g, i.carbohidratos_100g,
                   i.grasas_100g, i.fibra_100g, i.sodio_100g,
                   GROUP_CONCAT(a.nombre ORDER BY a.nombre SEPARATOR ', ') AS alergenos
            FROM ingredientes i
            LEFT JOIN ingredientes_alergenos ia ON i.id_ingrediente = ia.id_ingrediente
            LEFT JOIN alergenos a ON ia.id_alergeno = a.id_alergeno
            WHERE i.id_ingrediente = %s
            GROUP BY i.id_ingrediente
        """, (id_ingrediente,))

        ingrediente = cursor.fetchone()
        cursor.close()
        return ingrediente


def actualizarIngrediente(id_ingrediente, nombre, unidad, categoria,
                          calorias, proteina, carbohidratos, grasas, fibra, sodio):
    """Actualiza los datos de un ingrediente existente."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE ingredientes
            SET nombre = %s, unidad_medida = %s, categoria = %s, calorias_100g = %s, 
                proteinas_100g = %s, carbohidratos_100g = %s, grasas_100g = %s,
                fibra_100g = %s, sodio_100g = %s
            WHERE id_ingrediente = %s
            """, (nombre, unidad, categoria, calorias, proteina,
            carbohidratos, grasas, fibra, sodio, id_ingrediente))
        
        conexion.commit()
        cursor.close()


def eliminarIngredienteDB(id_ingrediente):
    """Elimina un ingrediente. Las FK CASCADE eliminan sus referencias automáticamente"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        # Elimina los datos dependientes del ingrediente primero, y luego el ingrediente
        cursor.execute("DELETE FROM ingredientes_alergenos WHERE id_ingrediente = %s", (id_ingrediente,))
        cursor.execute("DELETE FROM recetas_ingredientes WHERE id_ingrediente = %s", (id_ingrediente,))
        cursor.execute("DELETE FROM ingredientes WHERE id_ingrediente = %s",(id_ingrediente,))

        conexion.commit()
        cursor.close()

# ALÉRGENOS

def asignarAlergeno(id_ingrediente, alergeno):
    """Asigna un alérgeno a un ingrediente usando la tabla ingredientes_alergenos"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        # Buscar el alérgeno por nombre en la tabla
        cursor.execute("SELECT id_alergeno FROM alergenos WHERE nombre = %s", (alergeno,))
        fila = cursor.fetchone()

        id_alergeno = fila[0]
            
        # Insertar relación (IGNORE evita error si ya existe la PK compuesta)
        cursor.execute("""
            INSERT IGNORE INTO ingredientes_alergenos (id_ingrediente, id_alergeno)
            VALUES (%s, %s)
            """, (id_ingrediente, id_alergeno))
        conexion.commit()
        
        cursor.close()

def listaAlergenosUnicos():
    """Devuelve la lista de alérgenos existentes en la BD, ordenados alfabéticamente"""
    alergenos = [
        "Apio", "Altramuces", "Cacahuetes", "Crustáceos", "Dióxido de azufre",
        "Frutos de cáscara", "Gluten", "Huevo", "Lácteos", "Moluscos",
        "Mostaza", "Pescado", "Sésamo", "Soja"
        ]
    return alergenos

def eliminarAlergeno(id_ingrediente, id_alergeno):
    """Elimina la relación entre un ingrediente y un alérgeno"""
    
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM ingredientes_alergenos
            WHERE id_ingrediente = %s AND id_alergeno = %s
        """, (id_ingrediente, id_alergeno))

        conexion.commit()
        cursor.close()

def obtenerAlergenosIngrediente(id_ingrediente):
    """Devuelve los alérgenos asignados a un ingrediente con su id"""

    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT a.id_alergeno, a.nombre
            FROM ingredientes_alergenos ia
            JOIN alergenos a ON ia.id_alergeno = a.id_alergeno
            WHERE ia.id_ingrediente = %s
            ORDER BY a.nombre ASC
        """, (id_ingrediente,))

        alergenos = cursor.fetchall()
        cursor.close()
    return alergenos

# EMPLEADOS

#Paginacion hecha con IA
def obtenerEmpleadosFiltrados(page, per_page, puesto=None, activo=None):
    """Obtiene empleados paginados con filtros opcionales"""
    offset = (page - 1) * per_page

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        query = """
        SELECT e.id_empleado, e.nombre, e.apellidos, e.puesto,
               e.telefono, e.email, e.fecha_alta, e.activo,
               c.tipo_contrato, c.fecha_inicio, c.fecha_fin,
               c.horas_semanales, c.salario_bruto_anual, c.salario_neto, c.activo
        FROM empleados e
        LEFT JOIN contratos c
            ON c.id_empleado = e.id_empleado
            AND c.id_contrato = (
                SELECT id_contrato FROM contratos
                WHERE id_empleado = e.id_empleado
                ORDER BY activo DESC, fecha_inicio DESC
                LIMIT 1
            )
        WHERE 1=1
        """
        params = []

        if puesto:
            query += " AND e.puesto = %s"
            params.append(puesto)

        if activo is not None and activo != "":
            query += " AND e.activo = %s"
            params.append(int(activo))

        query += " ORDER BY e.apellidos ASC, e.nombre ASC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        empleados = cursor.fetchall()

        count_query = "SELECT COUNT(*) FROM empleados WHERE 1=1"
        count_params = []

        if puesto:
            count_query += " AND puesto = %s"
            count_params.append(puesto)

        if activo is not None and activo != "":
            count_query += " AND activo = %s"
            count_params.append(int(activo))

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        cursor.close()
        return empleados, total


def obtenerEmpleado(id_empleado):
    """Devuelve todos los datos de un empleado por su id"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT e.id_empleado, e.nombre, e.apellidos, e.puesto, e.telefono, e.email, e.fecha_alta, e.activo,
                   c.tipo_contrato, c.fecha_inicio, c.fecha_fin, c.horas_semanales, c.salario_bruto_anual, 
                   c.salario_neto, c.activo, c.id_contrato
            FROM empleados e
            LEFT JOIN contratos c
                ON c.id_empleado = e.id_empleado
                AND c.id_contrato = (
                    SELECT id_contrato FROM contratos
                    WHERE id_empleado = e.id_empleado
                    ORDER BY activo DESC, fecha_inicio DESC
                    LIMIT 1
                )
            WHERE e.id_empleado = %s
        """, (id_empleado,))

        empleado = cursor.fetchone()
        cursor.close()
        return empleado


def guardarEmpleado(nombre, apellidos, puesto, telefono, email, fecha_alta,
                    tipo_contrato, horas_semanales, salario_bruto_anual, salario_neto, activo):
    """Inserta un nuevo empleado en la base de datos y su contrato asociado."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        # Insertar empleado
        cursor.execute("""
            INSERT INTO empleados
            (nombre, apellidos, puesto, telefono, email, fecha_alta, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre,
            apellidos or None,
            puesto,
            telefono or None,
            email or None,
            fecha_alta or None,
            activo
        ))

        # Obtener el ID del empleado recién insertado
        id_empleado = cursor.lastrowid

        # Insertar contrato asociado
        cursor.execute("""
            INSERT INTO contratos
            (id_empleado, tipo_contrato, fecha_inicio, horas_semanales, salario_bruto_anual, salario_neto, activo)
            VALUES (%s, %s, CURDATE(), %s, %s, %s, 1)
        """, (
            id_empleado,
            tipo_contrato,
            horas_semanales,
            salario_bruto_anual,
            salario_neto
        ))

        conexion.commit()
        cursor.close()


def actualizarEmpleado(id_empleado, nombre, apellidos, puesto,
                       telefono, email, fecha_alta):
    """Actualiza los datos personales de un empleado existente."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE empleados
            SET nombre = %s, apellidos = %s, puesto = %s,
                telefono = %s, email = %s, fecha_alta = %s
            WHERE id_empleado = %s
        """, (
            nombre,
            apellidos or None,
            puesto,
            telefono or None,
            email or None,
            fecha_alta or None,
            id_empleado
        ))
        conexion.commit()
        cursor.close()


def actualizarContrato(id_contrato, tipo_contrato, fecha_inicio, fecha_fin,
                       horas_semanales, salario_bruto_anual, salario_neto):
    """Actualiza los datos de un contrato existente."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE contratos
            SET tipo_contrato = %s, fecha_inicio = %s, fecha_fin = %s,
                horas_semanales = %s, salario_bruto_anual = %s, salario_neto = %s
            WHERE id_contrato = %s
        """, (
            tipo_contrato,
            fecha_inicio or None,
            fecha_fin or None,
            horas_semanales or None,
            salario_bruto_anual or None,
            salario_neto or None,
            id_contrato
        ))
        conexion.commit()
        cursor.close()


def crearContrato(id_empleado, tipo_contrato, fecha_inicio, fecha_fin,
                  horas_semanales, salario_bruto_anual, salario_neto):
    """Crea un nuevo contrato para un empleado.
    Marca como inactivos los contratos previos antes de insertar el nuevo.
    """
    
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE contratos SET activo = 0 WHERE id_empleado = %s
        """, (id_empleado,))
        cursor.execute("""
            INSERT INTO contratos
            (id_empleado, tipo_contrato, fecha_inicio, fecha_fin,
             horas_semanales, salario_bruto_anual, salario_neto, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
        """, (
            id_empleado,
            tipo_contrato,
            fecha_inicio or None,
            fecha_fin or None,
            horas_semanales or None,
            salario_bruto_anual or None,
            salario_neto or None
        ))
        conexion.commit()
        cursor.close()


def eliminarEmpleadoDB(id_empleado):
    """Elimina un empleado y sus contratos asociados de la base de datos."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        # Primero eliminar los contratos asociados (FK lo exige)
        cursor.execute(
            "DELETE FROM contratos WHERE id_empleado = %s",
            (id_empleado,)
        )

        # Luego eliminar el empleado
        cursor.execute(
            "DELETE FROM empleados WHERE id_empleado = %s",
            (id_empleado,)
        )

        conexion.commit()
        cursor.close()


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def ingredientesRecientes(limite=5):
    """Devuelve los últimos N ingredientes añadidos a la BD.
    Cada fila: (id_ingrediente, nombre, calorias_100g)
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id_ingrediente, nombre, calorias_100g
            FROM ingredientes
            ORDER BY id_ingrediente DESC
            LIMIT %s
        """, (limite,))
        fila = cursor.fetchall()
        cursor.close()
    return fila


def empleadosRecientes(limite=5):
    """Devuelve los últimos N empleados activos.
    Cada fila: (id_empleado, nombre, apellidos, puesto, activo)
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id_empleado, nombre, apellidos, puesto, activo
            FROM empleados
            ORDER BY id_empleado DESC
            LIMIT %s
        """, (limite,))
        fila = cursor.fetchall()
        cursor.close()
    return fila


# ─────────────────────────────────────────────────────────────────────────────
# AUTENTICACIÓN
# ─────────────────────────────────────────────────────────────────────────────

# Puestos que tienen acceso al sistema. Los alumnos nunca pueden entrar.
PUESTOS_CON_ACCESO = ('cocinero', 'docente', 'apoyo')


def verificarLogin(username, password):
    """Comprueba credenciales y devuelve un diccionario con datos del usuario"""

    with conexionDB() as conexion:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT ul.id_usuario, ul.password_hash, ul.activo,
                   e.id_empleado, e.nombre, e.apellidos, e.puesto, e.activo AS emp_activo
            FROM usuarios_login ul
            JOIN empleados e ON ul.id_empleado = e.id_empleado
            WHERE ul.username = %s
        """, (username,))
        row = cursor.fetchone()
        cursor.close()

    if not row:
        return None  # Usuario no existe

    # Comprobar que el login y el empleado están activos
    if not row['activo'] or not row['emp_activo']:
        return None

    # Los alumnos nunca tienen acceso, aunque tuviesen entrada en usuarios_login
    if row['puesto'] not in PUESTOS_CON_ACCESO:
        return None

    # Verificar contraseña con bcrypt
    if not bcrypt.checkpw(password.encode('utf-8'), row['password_hash'].encode('utf-8')):
        return None

    return {
        'id_usuario': row['id_usuario'],
        'nombre':     f"{row['nombre']} {row['apellidos']}",
        'puesto':     row['puesto'],
    }

if __name__ == "__main__":
    
    recetario, total = infoRecetaFiltrada(1, 30)

    recetas = []

    for r in recetario:
        recetas.append(r[1])
    
    print(recetas)