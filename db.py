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
    """Obtiene todas las categorías de recetas"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_categoria, nombre FROM categorias_receta")
        categorias = cursor.fetchall()
        cursor.close()
        return categorias

def nombreIngredientes():
    """Obtiene todos los ingredientes"""
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

        query = """
        SELECT r.id_receta, r.nombre, c.nombre AS nombre_categoria,
               r.dificultad, r.tiempo_preparacion
        FROM recetas r
        LEFT JOIN categorias_receta c ON r.id_categoria = c.id_categoria
        WHERE 1=1
        """
        params = []

        if categoria and categoria != "Todas las categorías":
            query += " AND c.nombre = %s"
            params.append(categoria)

        if dificultad and dificultad != "Todas las dificultades":
            query += " AND r.dificultad = %s"
            params.append(dificultad.lower())

        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        recetas = cursor.fetchall()

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
        conexion.commit()

        # CORRECCIÓN: usar lastrowid en lugar de SELECT MAX para evitar race conditions
        ultimaReceta = cursor.lastrowid

        for idx, i in enumerate(listaIngredientes):
            nota = listaNotas[idx] if listaNotas and listaNotas[idx] != '' else None
            cursor.execute("""
                INSERT INTO recetas_ingredientes
                (id_receta, id_ingrediente, cantidad, unidad, notas)
                VALUES (%s, %s, %s, %s, %s)
            """, (ultimaReceta, i, listaCantidades[idx], listaUnidades[idx], nota))
            conexion.commit()

        for idx, p in enumerate(listaPasos, start=1):
            cursor.execute("""
                INSERT INTO pasos_receta
                (id_receta, numero_paso, descripcion)
                VALUES (%s, %s, %s)
            """, (ultimaReceta, idx, p))
            conexion.commit()

        cursor.close()

def eliminarReceta(id_receta):
    """Elimina una receta y sus datos relacionados (las FK CASCADE lo gestionan automáticamente)"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        # pasos_receta y recetas_ingredientes tienen ON DELETE CASCADE, pero borramos explícitamente
        cursor.execute("DELETE FROM pasos_receta WHERE id_receta = %s", (id_receta,))
        cursor.execute("DELETE FROM recetas_ingredientes WHERE id_receta = %s", (id_receta,))
        cursor.execute("DELETE FROM recetas WHERE id_receta = %s", (id_receta,))
        conexion.commit()
        cursor.close()

def obtenerReceta(id_receta):
    """Obtiene toda la información de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM recetas WHERE id_receta = %s", (id_receta,))
        datosReceta = cursor.fetchone()
        cursor.close()
        return datosReceta

def obtenerPasos(id_receta):
    """Obtiene todos los pasos de una receta ordenados"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT numero_paso, descripcion FROM pasos_receta WHERE id_receta = %s ORDER BY numero_paso ASC",
            (id_receta,)
        )
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

        ingredientesReceta = [list(item) for item in ingredientesReceta]
        for i in ingredientesReceta:
            if i[3] == i[3].to_integral_value():
                i[3] = str(int(i[3]))
            else:
                i[3] = f"{float(i[3]):.2f}"

        return ingredientesReceta

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

    if not nutri:
        return []

    # CORRECCIÓN: iterar sobre la única fila resultado, manejar None y usar lista_formateada
    nutri_formateado = []
    for valor in nutri:
        if valor is None:
            nutri_formateado.append("—")
        elif valor == valor.to_integral_value():
            nutri_formateado.append(str(int(valor)))
        else:
            nutri_formateado.append(f"{float(valor):.2f}")

    return nutri_formateado

def alergenosReceta(id_receta):
    """Obtiene todos los alérgenos de una receta"""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT alergenos
        FROM vista_nutricion_receta
        WHERE id_receta = %s;""", (id_receta,))

        resultado = cursor.fetchone()
        cursor.close()

    if not resultado or resultado[0] is None:
        return None

    # CORRECCIÓN: devolver alergenosFormateado, no alergenos en bruto
    alergenosFormateado = [a.strip() for a in resultado[0].split(",")]
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

        # CORRECCIÓN: borrar y reinsertar ingredientes en lugar de UPDATE sin contador
        cursor.execute("DELETE FROM recetas_ingredientes WHERE id_receta = %s", (id_receta,))
        for idx, i in enumerate(listaIngredientes):
            nota = listaNotas[idx] if listaNotas and listaNotas[idx] != '' else None
            cursor.execute("""
                INSERT INTO recetas_ingredientes (id_receta, id_ingrediente, cantidad, unidad, notas)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_receta, i, listaCantidades[idx], listaUnidades[idx], nota))
            conexion.commit()

        # CORRECCIÓN: borrar y reinsertar pasos en lugar de UPDATE con contador siempre 0
        cursor.execute("DELETE FROM pasos_receta WHERE id_receta = %s", (id_receta,))
        for idx, p in enumerate(listaPasos, start=1):
            cursor.execute("""
                INSERT INTO pasos_receta (id_receta, numero_paso, descripcion)
                VALUES (%s, %s, %s)
            """, (id_receta, idx, p))
            conexion.commit()

        cursor.close()

def guardarIngrediente(nombre, unidad, categoria, calorias, proteina, carbohidratos, grasas, fibra, sodio, alergenos=None):
    """Guarda un ingrediente en la base de datos y asigna sus alérgenos."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
        INSERT INTO ingredientes
        (nombre, unidad_medida, categoria, calorias_100g,
        proteinas_100g, carbohidratos_100g, grasas_100g, fibra_100g, sodio_100g)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nombre, unidad, categoria or None, calorias or None,
              proteina or None, carbohidratos or None, grasas or None,
              fibra or None, sodio or None))

        conexion.commit()
        id_ingrediente = cursor.lastrowid

        # Procesar alérgenos si se han proporcionado
        if alergenos:
            nombres_alergenos = [a.strip() for a in alergenos.split(',') if a.strip()]
            for nombre_alergeno in nombres_alergenos:
                cursor.execute("SELECT id_alergeno FROM alergenos WHERE nombre = %s", (nombre_alergeno,))
                fila = cursor.fetchone()
                if fila:
                    id_alergeno = fila[0]
                else:
                    cursor.execute("INSERT INTO alergenos (nombre) VALUES (%s)", (nombre_alergeno,))
                    conexion.commit()
                    id_alergeno = cursor.lastrowid
                cursor.execute("""
                    INSERT IGNORE INTO ingredientes_alergenos (id_ingrediente, id_alergeno)
                    VALUES (%s, %s)
                """, (id_ingrediente, id_alergeno))
                conexion.commit()

        cursor.close()


# ─────────────────────────────────────────────────────────────────────────────
# INGREDIENTES
# ─────────────────────────────────────────────────────────────────────────────

def obtenerIngredientesFiltrados(page, per_page, categoria=None, unidad=None):
    """Obtiene ingredientes paginados con filtros opcionales.
    Devuelve (lista, total).
    Cada fila: (id, nombre, categoria, unidad_medida, calorias_100g,
                proteinas_100g, carbohidratos_100g, grasas_100g,
                fibra_100g, sodio_100g, alergenos)
    CORRECCIÓN: la columna 'alergenos' no existe en la tabla ingredientes;
                se obtiene mediante JOIN con ingredientes_alergenos y alergenos.
    """
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
    """Devuelve la lista de categorías únicas de ingredientes (sin None)."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT DISTINCT categoria
            FROM ingredientes
            WHERE categoria IS NOT NULL AND categoria != ''
            ORDER BY categoria ASC
        """)
        categorias = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return categorias


def obtenerIngrediente(id_ingrediente):
    """Devuelve todos los datos de un ingrediente por su id.
    CORRECCIÓN: obtiene alergenos mediante JOIN, no de columna inexistente.
    """
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
            SET nombre = %s, unidad_medida = %s, categoria = %s,
                calorias_100g = %s, proteinas_100g = %s,
                carbohidratos_100g = %s, grasas_100g = %s,
                fibra_100g = %s, sodio_100g = %s
            WHERE id_ingrediente = %s
        """, (nombre, unidad, categoria or None, calorias or None, proteina or None,
              carbohidratos or None, grasas or None, fibra or None,
              sodio or None, id_ingrediente))
        conexion.commit()
        cursor.close()


def eliminarIngredienteDB(id_ingrediente):
    """Elimina un ingrediente. Las FK CASCADE eliminan sus referencias automáticamente."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        # ingredientes_alergenos tiene ON DELETE CASCADE, pero borramos explícitamente
        cursor.execute(
            "DELETE FROM ingredientes_alergenos WHERE id_ingrediente = %s",
            (id_ingrediente,)
        )
        cursor.execute(
            "DELETE FROM recetas_ingredientes WHERE id_ingrediente = %s",
            (id_ingrediente,)
        )
        cursor.execute(
            "DELETE FROM ingredientes WHERE id_ingrediente = %s",
            (id_ingrediente,)
        )
        conexion.commit()
        cursor.close()


# ─────────────────────────────────────────────────────────────────────────────
# ALÉRGENOS
# ─────────────────────────────────────────────────────────────────────────────

def asignarAlergeno(id_ingrediente, alergeno):
    """Asigna un alérgeno a un ingrediente usando la tabla ingredientes_alergenos.
    CORRECCIÓN: la versión original modificaba una columna 'alergenos' que no existe
                en ingredientes. Los alérgenos se gestionan mediante la tabla relacional.
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        # Buscar el alérgeno por nombre en la tabla maestra
        cursor.execute("SELECT id_alergeno FROM alergenos WHERE nombre = %s", (alergeno,))
        fila = cursor.fetchone()

        if fila:
            id_alergeno = fila[0]
        else:
            # Si no existe, insertarlo en la tabla maestra
            cursor.execute("INSERT INTO alergenos (nombre) VALUES (%s)", (alergeno,))
            conexion.commit()
            id_alergeno = cursor.lastrowid

        # Insertar relación (INSERT IGNORE evita error si ya existe la PK compuesta)
        cursor.execute("""
            INSERT IGNORE INTO ingredientes_alergenos (id_ingrediente, id_alergeno)
            VALUES (%s, %s)
        """, (id_ingrediente, id_alergeno))
        conexion.commit()
        cursor.close()


def recetasConAlergenos(page, per_page, alergeno_filtro=None):
    """Devuelve recetas con sus alérgenos, paginadas.
    Cada fila: (id_receta, nombre_receta, categoria, alergenos_str)
    """
    offset = (page - 1) * per_page

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        query = """
        SELECT r.id_receta, r.nombre, c.nombre AS categoria, v.alergenos
        FROM recetas r
        LEFT JOIN categorias_receta c ON r.id_categoria = c.id_categoria
        LEFT JOIN vista_nutricion_receta v ON r.id_receta = v.id_receta
        WHERE 1=1
        """
        params = []

        if alergeno_filtro:
            query += " AND v.alergenos LIKE %s"
            params.append(f"%{alergeno_filtro}%")

        query += " ORDER BY r.nombre ASC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        recetas = cursor.fetchall()

        count_query = """
        SELECT COUNT(*)
        FROM recetas r
        LEFT JOIN vista_nutricion_receta v ON r.id_receta = v.id_receta
        WHERE 1=1
        """
        count_params = []

        if alergeno_filtro:
            count_query += " AND v.alergenos LIKE %s"
            count_params.append(f"%{alergeno_filtro}%")

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        cursor.close()
        return recetas, total


def resumenAlergenos():
    """Devuelve cuántas recetas contienen cada alérgeno.
    Retorna lista de (nombre_alergeno, num_recetas).
    """
    alergenos_ue = [
        "Gluten", "Crustáceos", "Huevo", "Pescado", "Cacahuetes",
        "Soja", "Lácteos", "Frutos de cáscara", "Apio", "Mostaza",
        "Sésamo", "Dióxido de azufre", "Altramuces", "Moluscos"
    ]

    with conexionDB() as conexion:
        cursor = conexion.cursor()
        resumen = []
        for alergeno in alergenos_ue:
            cursor.execute("""
                SELECT COUNT(DISTINCT r.id_receta)
                FROM recetas r
                JOIN vista_nutricion_receta v ON r.id_receta = v.id_receta
                WHERE v.alergenos LIKE %s
            """, (f"%{alergeno}%",))
            count = cursor.fetchone()[0]
            resumen.append((alergeno, count))
        cursor.close()
        return resumen


def listaAlergenosUnicos():
    """Devuelve la lista de alérgenos existentes en la BD, ordenados alfabéticamente."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM alergenos ORDER BY nombre ASC")
        alergenos = [row[0] for row in cursor.fetchall()]
        cursor.close()
    # Si la tabla está vacía, devolver los 14 UE como fallback
    if not alergenos:
        alergenos = [
            "Apio", "Altramuces", "Cacahuetes", "Crustáceos", "Dióxido de azufre",
            "Frutos de cáscara", "Gluten", "Huevo", "Lácteos", "Moluscos",
            "Mostaza", "Pescado", "Sésamo", "Soja"
        ]
    return alergenos


def eliminarAlergeno(id_ingrediente, id_alergeno):
    """Elimina la relación entre un ingrediente y un alérgeno."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            DELETE FROM ingredientes_alergenos
            WHERE id_ingrediente = %s AND id_alergeno = %s
        """, (id_ingrediente, id_alergeno))
        conexion.commit()
        cursor.close()


def obtenerAlergenosIngrediente(id_ingrediente):
    """Devuelve los alérgenos asignados a un ingrediente con su id."""
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


# ─────────────────────────────────────────────────────────────────────────────
# MENÚS
# ─────────────────────────────────────────────────────────────────────────────

def obtenerMenusFiltrados(page, per_page, tipo=None, activo=None):
    """Obtiene menús paginados con filtros opcionales.
    CORRECCIÓN: eliminadas las columnas precio, fecha_inicio, fecha_fin que no
                existen en la tabla menus. Columnas reales: id_menu, nombre,
                descripcion, tipo, id_creador, fecha_creacion, activo.
    Cada fila devuelta: (id_menu, nombre, tipo, n_recetas, fecha_creacion, activo, descripcion)
    """
    offset = (page - 1) * per_page

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        query = """
        SELECT m.id_menu, m.nombre, m.tipo,
               COUNT(mr.id_receta) AS n_recetas,
               m.fecha_creacion, m.activo, m.descripcion
        FROM menus m
        LEFT JOIN menus_recetas mr ON m.id_menu = mr.id_menu
        WHERE 1=1
        """
        params = []

        if tipo:
            query += " AND m.tipo = %s"
            params.append(tipo)

        if activo is not None and activo != "":
            query += " AND m.activo = %s"
            params.append(int(activo))

        query += " GROUP BY m.id_menu ORDER BY m.nombre ASC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        menus = cursor.fetchall()

        count_query = "SELECT COUNT(*) FROM menus WHERE 1=1"
        count_params = []

        if tipo:
            count_query += " AND tipo = %s"
            count_params.append(tipo)

        if activo is not None and activo != "":
            count_query += " AND activo = %s"
            count_params.append(int(activo))

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        cursor.close()
        return menus, total


def obtenerMenuDetalle(id_menu):
    """Devuelve todos los datos de un menú por su id.
    CORRECCIÓN: eliminadas columnas precio, fecha_inicio, fecha_fin.
    Fila: (id_menu, nombre, tipo, n_recetas, fecha_creacion, activo, descripcion)
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT m.id_menu, m.nombre, m.tipo,
                   COUNT(mr.id_receta) AS n_recetas,
                   m.fecha_creacion, m.activo, m.descripcion
            FROM menus m
            LEFT JOIN menus_recetas mr ON m.id_menu = mr.id_menu
            WHERE m.id_menu = %s
            GROUP BY m.id_menu
        """, (id_menu,))
        menu = cursor.fetchone()
        cursor.close()
        return menu


def obtenerRecetasMenu(id_menu):
    """Devuelve las recetas asociadas a un menú.
    Cada fila: (id_receta, nombre, dificultad, tiempo_preparacion, tipo_plato)
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT r.id_receta, r.nombre, r.dificultad,
                   r.tiempo_preparacion, mr.tipo_plato
            FROM menus_recetas mr
            JOIN recetas r ON mr.id_receta = r.id_receta
            WHERE mr.id_menu = %s
            ORDER BY mr.orden ASC
        """, (id_menu,))
        recetas = cursor.fetchall()
        cursor.close()
        return recetas


def guardarMenu(nombre, tipo, activo, descripcion, lista_recetas, lista_tipo_plato):
    """Inserta un nuevo menú y sus recetas asociadas.
    CORRECCIÓN: eliminados parámetros precio, fecha_inicio, fecha_fin que no
                existen en la tabla. Añadidos id_creador y fecha_creacion (NOT NULL).
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO menus
            (nombre, tipo, descripcion, id_creador, fecha_creacion, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            nombre,
            tipo,
            descripcion or None,
            1,                          # id_creador: empleado por defecto
            date.today(),               # fecha_creacion: obligatorio NOT NULL
            1 if activo else 0
        ))
        conexion.commit()

        id_menu = cursor.lastrowid      # CORRECCIÓN: lastrowid en lugar de SELECT MAX

        for orden, (id_receta, tipo_plato) in enumerate(
                zip(lista_recetas, lista_tipo_plato), start=1):
            if id_receta:
                cursor.execute("""
                    INSERT INTO menus_recetas (id_menu, id_receta, tipo_plato, orden)
                    VALUES (%s, %s, %s, %s)
                """, (id_menu, id_receta, tipo_plato or None, orden))
                conexion.commit()

        cursor.close()


def actualizarMenu(id_menu, nombre, tipo, activo, descripcion,
                   lista_recetas, lista_tipo_plato):
    """Actualiza un menú y reemplaza completamente sus recetas.
    CORRECCIÓN: eliminados parámetros precio, fecha_inicio, fecha_fin.
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE menus
            SET nombre = %s, tipo = %s, activo = %s, descripcion = %s
            WHERE id_menu = %s
        """, (
            nombre,
            tipo,
            1 if activo else 0,
            descripcion or None,
            id_menu
        ))
        conexion.commit()

        cursor.execute("DELETE FROM menus_recetas WHERE id_menu = %s", (id_menu,))
        conexion.commit()

        for orden, (id_receta, tipo_plato) in enumerate(
                zip(lista_recetas, lista_tipo_plato), start=1):
            if id_receta:
                cursor.execute("""
                    INSERT INTO menus_recetas (id_menu, id_receta, tipo_plato, orden)
                    VALUES (%s, %s, %s, %s)
                """, (id_menu, id_receta, tipo_plato or None, orden))
                conexion.commit()

        cursor.close()


def eliminarMenuDB(id_menu):
    """Elimina un menú y sus relaciones con recetas."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM menus_recetas WHERE id_menu = %s", (id_menu,))
        cursor.execute("DELETE FROM menus WHERE id_menu = %s", (id_menu,))
        conexion.commit()
        cursor.close()


# ─────────────────────────────────────────────────────────────────────────────
# EMPLEADOS
# ─────────────────────────────────────────────────────────────────────────────

def obtenerEmpleadosFiltrados(page, per_page, puesto=None, activo=None):
    """Obtiene empleados paginados con filtros opcionales.
    CORRECCIÓN: eliminadas las columnas turno, salario, notas que no existen
                en la tabla empleados. Columnas reales: id_empleado, nombre,
                apellidos, email, telefono, puesto, activo, fecha_alta.
    Cada fila: (id, nombre, apellidos, puesto, telefono, email, fecha_alta, activo)
    """
    offset = (page - 1) * per_page

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        query = """
        SELECT id_empleado, nombre, apellidos, puesto,
               telefono, email, fecha_alta, activo
        FROM empleados
        WHERE 1=1
        """
        params = []

        if puesto:
            query += " AND puesto = %s"
            params.append(puesto)

        if activo is not None and activo != "":
            query += " AND activo = %s"
            params.append(int(activo))

        query += " ORDER BY apellidos ASC, nombre ASC LIMIT %s OFFSET %s"
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
    """Devuelve todos los datos de un empleado por su id.
    CORRECCIÓN: eliminadas columnas turno, salario, notas.
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id_empleado, nombre, apellidos, puesto,
                   telefono, email, fecha_alta, activo
            FROM empleados
            WHERE id_empleado = %s
        """, (id_empleado,))
        empleado = cursor.fetchone()
        cursor.close()
        return empleado


def obtenerResumenEmpleados():
    """Devuelve (total, activos, empleados_cocina, empleados_sala).
    CORRECCIÓN: los valores del ENUM de puesto son 'cocinero','docente','apoyo',
                'alumno_cocina','alumno_dietetica'. Los valores anteriores
                ('Chef', 'Sous Chef', etc.) no existen en el esquema.
    """
    puestos_cocina = ('cocinero', 'apoyo', 'alumno_cocina')
    puestos_docencia = ('docente', 'alumno_dietetica')

    with conexionDB() as conexion:
        cursor = conexion.cursor()

        cursor.execute("SELECT COUNT(*) FROM empleados")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM empleados WHERE activo = 1")
        activos = cursor.fetchone()[0]

        placeholders_cocina = ", ".join(["%s"] * len(puestos_cocina))
        cursor.execute(
            f"SELECT COUNT(*) FROM empleados WHERE puesto IN ({placeholders_cocina})",
            puestos_cocina
        )
        cocina = cursor.fetchone()[0]

        placeholders_docencia = ", ".join(["%s"] * len(puestos_docencia))
        cursor.execute(
            f"SELECT COUNT(*) FROM empleados WHERE puesto IN ({placeholders_docencia})",
            puestos_docencia
        )
        docencia = cursor.fetchone()[0]

        cursor.close()
        return total, activos, cocina, docencia


def guardarEmpleado(nombre, apellidos, puesto, telefono, email, fecha_alta, activo):
    """Inserta un nuevo empleado en la base de datos.
    CORRECCIÓN: eliminados parámetros turno, salario, notas que no existen
                en la tabla. El ENUM acepta: cocinero, docente, apoyo,
                alumno_cocina, alumno_dietetica.
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()
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
        conexion.commit()
        cursor.close()


def actualizarEmpleado(id_empleado, nombre, apellidos, puesto,
                       telefono, email, fecha_alta, activo):
    """Actualiza los datos de un empleado existente.
    CORRECCIÓN: eliminados parámetros turno, salario, notas.
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE empleados
            SET nombre = %s, apellidos = %s, puesto = %s,
                telefono = %s, email = %s, fecha_alta = %s, activo = %s
            WHERE id_empleado = %s
        """, (
            nombre,
            apellidos or None,
            puesto,
            telefono or None,
            email or None,
            fecha_alta or None,
            activo,
            id_empleado
        ))
        conexion.commit()
        cursor.close()


def eliminarEmpleadoDB(id_empleado):
    """Elimina un empleado de la base de datos."""
    with conexionDB() as conexion:
        cursor = conexion.cursor()
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
        rows = cursor.fetchall()
        cursor.close()
    return rows


def menusRecientes(limite=5):
    """Devuelve los últimos N menús con número de recetas.
    Cada fila: (id_menu, nombre, tipo, n_recetas)
    """
    with conexionDB() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT m.id_menu, m.nombre, m.tipo,
                   COUNT(mr.id_receta) AS n_recetas
            FROM menus m
            LEFT JOIN menus_recetas mr ON m.id_menu = mr.id_menu
            WHERE m.activo = 1
            GROUP BY m.id_menu
            ORDER BY m.id_menu DESC
            LIMIT %s
        """, (limite,))
        rows = cursor.fetchall()
        cursor.close()
    return rows


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
        rows = cursor.fetchall()
        cursor.close()
    return rows


if __name__ == "__main__":
    alergenosReceta(2)