from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import db

app = Flask(__name__)

app.secret_key = 'gastrolab-secret-key-cambia-esto-en-produccion'

# ── AUTENTICACIÓN ──────────────────────────────────────────────────────────────

def login_required(f):
    """Decorador: redirige al login si el usuario no ha iniciado sesión."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=["GET", "POST"])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('inicio'))

    error = None
    username_prev = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        username_prev = username

        usuario = db.verificarLogin(username, password)
        if usuario:
            session['usuario_id']     = usuario['id_usuario']
            session['usuario_nombre'] = usuario['nombre']
            session['usuario_puesto'] = usuario['puesto']
            return redirect(url_for('inicio'))
        else:
            error = "Usuario o contraseña incorrectos, o no tienes permiso de acceso."

    return render_template('login.html', error=error, username_prev=username_prev)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=["GET", "POST"])
@login_required
def inicio():
    #Paginacion
    page = request.args.get('page', 1, type=int)
    per_page = 10

    #Recogida de datos para filtros
    categoria = request.args.get('categoria')
    dificultad = request.args.get('dificultad')
    receta_id = request.args.get('receta_id', type=int)

    #Busca las categorias en la BD, para poner los en el filtro
    categorias = db.categoriasBD()
    categorias = [cat[1] for cat in categorias]

    #Saca la receta y el total de recetas
    recetas, total = db.infoRecetaFiltrada(page, per_page, categoria, dificultad)
    total_pages = (total + per_page - 1) // per_page

    if request.method == "POST":
        db.guardarIngrediente(
            request.form.get("nombreIng"),
            request.form.get("unidad"),
            request.form.get("categoria"),
            request.form.get("calorias"),
            request.form.get("proteinas"),
            request.form.get("carbohidratos"),
            request.form.get("grasas"),
            request.form.get("fibra"),
            request.form.get("sodio"),
        )
        return redirect(url_for("inicio"))

    #Datos para ver las recetas cuando le das a mas detalle
    receta_detalle = None
    pasosReceta = None
    ingredientesReceta = None
    nutriReceta = None
    alergenoReceta = None
    if receta_id:
        receta_detalle = db.obtenerReceta(receta_id)
        pasosReceta = db.obtenerPasos(receta_id)
        ingredientesReceta = db.obtenerIngredientes(receta_id)
        nutriReceta = db.infoNutriReceta(receta_id)
        alergenoReceta = db.alergenosReceta(receta_id)

    # Datos para mini-cards del dashboard
    ingredientes_recientes = db.ingredientesRecientes(5)
    empleados_recientes = db.empleadosRecientes(5)
    todos_alergenos = db.listaAlergenosUnicos()

    return render_template('index.html',
                         categorias=categorias,
                         recetas=recetas,
                         page=page,
                         total_pages=total_pages,
                         categoria_actual=categoria,
                         dificultad_actual=dificultad,
                         receta_detalle=receta_detalle,
                         pasosReceta=pasosReceta,
                         ingredientesReceta=ingredientesReceta,
                         nutriReceta=nutriReceta,
                         alergenoReceta=alergenoReceta,
                         ingredientes_recientes=ingredientes_recientes,
                         empleados_recientes=empleados_recientes,
                         todos_alergenos=todos_alergenos)


@app.route('/nueva-receta', methods=["GET", "POST"])
@login_required
def nueva_receta():

    #Para los select
    categorias = db.categoriasBD()
    ingredientes = db.nombreIngredientes()

    #Recoge los datos del formulario de ingrediente o el de la receta
    if request.method == "POST":
        if request.form.get("nombreIng") is None:
            db.guardarReceta(
                request.form.get("nombre"),
                request.form.get("categoria"),
                request.form.get("dificultad"),
                request.form.get("raciones"),
                request.form.get("tiempo_preparacion"),
                request.form.get("tiempo_coccion"),
                request.form.get("descripcion"),
                request.form.getlist("ingredientes_ids[]"),
                request.form.getlist("cantidades[]"),
                request.form.getlist("unidades[]"),
                request.form.getlist("notas_ing[]"),
                request.form.getlist("notas_pasos[]")
            )
            return redirect(url_for("inicio"))
        else:
            db.guardarIngrediente(
                request.form.get("nombreIng"),
                request.form.get("unidad"),
                request.form.get("categoria"),
                request.form.get("calorias"),
                request.form.get("proteinas"),
                request.form.get("carbohidratos"),
                request.form.get("grasas"),
                request.form.get("fibra"),
                request.form.get("sodio"),
            )

    return render_template('nuevaReceta.html', categorias=categorias, ingredientes=ingredientes)


@app.route('/eliminar-receta/<int:id_receta>', methods=["POST"])
@login_required
def eliminar_receta(id_receta):
    db.eliminarReceta(id_receta)
    return redirect(url_for("inicio"))

#Obtiene los datos de la receta mediante el id, y redirige al app route del index con la info
@app.route('/ver-receta/<int:id_receta>', methods=["GET"])
@login_required
def ver_receta(id_receta):
    receta = db.obtenerReceta(id_receta)
    if receta is None:
        return "Receta no encontrada", 404
    return redirect(url_for('inicio', receta_id=id_receta))

#Lleva al mismo formulario que nueva receta, pero con los value="" autocompletados, con la informacion de id_receta
@app.route('/editar-receta/<int:id_receta>', methods=["GET", "POST"])
@login_required
def editar_receta(id_receta):
    #Recoge los datos
    categorias = db.categoriasBD()
    ingredientes = db.obtenerIngredientes(id_receta)
    loopIngredientes = db.nombreIngredientes()
    receta = db.obtenerReceta(id_receta)
    pasos = db.obtenerPasos(id_receta)

    if request.method == "POST":
        db.actualizarReceta(
            id_receta,
            request.form.get("nombre"),
            request.form.get("categoria"),
            request.form.get("dificultad"),
            request.form.get("raciones"),
            request.form.get("tiempo_preparacion"),
            request.form.get("tiempo_coccion"),
            request.form.get("descripcion"),
            request.form.getlist("ingredientes_ids[]"),
            request.form.getlist("cantidades[]"),
            request.form.getlist("unidades[]"),
            request.form.getlist("notas_ing[]"),
            request.form.getlist("notas_pasos[]")
        )
        return redirect(url_for("inicio"))

    return render_template('editarReceta.html', receta=receta,
                           categorias=categorias, ingredientes=ingredientes,
                           loopIngredientes=loopIngredientes, pasos=pasos)


@app.route('/ingredientes', methods=["GET", "POST"])
@login_required
def ingredientes():
    page             = request.args.get('page', 1, type=int)
    per_page         = 15
    categoria_actual = request.args.get('categoria')
    unidad_actual    = request.args.get('unidad')
    ing_id           = request.args.get('ing_id', type=int)
    id_ingrediente   = request.args.get('id_ingrediente', type=int)  # ✅ AÑADE ESTA LÍNEA

    if request.method == "POST":
        db.guardarIngrediente(
            request.form.get("nombreIng"),
            request.form.get("unidad"),
            request.form.get("categoria"),
            request.form.get("calorias"),
            request.form.get("proteinas"),
            request.form.get("carbohidratos"),
            request.form.get("grasas"),
            request.form.get("fibra"),
            request.form.get("sodio"),
        )
        return redirect(url_for("ingredientes"))

    ingredientes_list, total = db.obtenerIngredientesFiltrados(page, per_page, categoria_actual, unidad_actual)
    total_pages = (total + per_page - 1) // per_page
    categorias  = db.obtenerCategoriasIngredientes()

    ingrediente_detalle = db.obtenerIngrediente(ing_id) if ing_id else None
    alergenos_ingrediente = db.obtenerAlergenosIngrediente(ing_id) if ing_id else []

    ingrediente = None
    if id_ingrediente:  # Ahora usamos id_ingrediente de la URL
        ingrediente = db.obtenerIngrediente(id_ingrediente)

    return render_template('ingredientes.html',
                           ingredientes=ingredientes_list,
                           page=page,
                           total_pages=total_pages,
                           categorias=categorias,
                           categoria_actual=categoria_actual,
                           unidad_actual=unidad_actual,
                           ingrediente_detalle=ingrediente_detalle,
                           alergenos_ingrediente=alergenos_ingrediente,
                           todos_alergenos=db.listaAlergenosUnicos(),
                           ingrediente=ingrediente)


@app.route('/ver-ingrediente/<int:id_ingrediente>', methods=["GET"])
@login_required
def ver_ingrediente(id_ingrediente):
    return redirect(url_for('ingredientes', ing_id=id_ingrediente))


@app.route('/editar-ingrediente/<int:id_ingrediente>', methods=["GET", "POST"])
@login_required
def editar_ingrediente(id_ingrediente):
    return redirect(url_for('ingredientes', id_ingrediente=id_ingrediente))


@app.route('/eliminar-ingrediente/<int:id_ingrediente>', methods=["POST"])
@login_required
def eliminar_ingrediente(id_ingrediente):
    db.eliminarIngredienteDB(id_ingrediente)
    return redirect(url_for("ingredientes"))


@app.route('/empleados', methods=["GET", "POST"])
@login_required
def empleados():
    # Parámetros de paginación y filtros, hecho con IA
    page          = request.args.get('page', 1, type=int)
    per_page      = 10
    puesto_actual = request.args.get('puesto')
    activo_actual = request.args.get('activo')
    emp_id        = request.args.get('emp_id', type=int)
    editar_id     = request.args.get('editar', type=int)  # NUEVO: para el modal de edición

    # Guarda un nuevo empleado
    if request.method == "POST":
        db.guardarEmpleado(
            request.form.get("nombre"),
            request.form.get("apellidos"),
            request.form.get("puesto"),
            request.form.get("telefono"),
            request.form.get("email"),
            request.form.get("fecha_alta"),
            request.form.get("tipo_contrato"),
            request.form.get("horas"),
            request.form.get("salario_bruto"),
            request.form.get("salario_neto"),
            1 if request.form.get("activo") else 0
        )
        return redirect(url_for("empleados"))

    # Obtiene empleados filtrados y paginados
    empleados_list, total = db.obtenerEmpleadosFiltrados(page, per_page, puesto_actual, activo_actual)
    total_pages = (total + per_page - 1) // per_page
    
    # Empleado para el modal de edición
    empleado_editar = db.obtenerEmpleado(editar_id) if editar_id else None

    return render_template('empleados.html',
                           empleados=empleados_list,
                           page=page,
                           total_pages=total_pages,
                           puesto_actual=puesto_actual,
                           activo_actual=activo_actual,
                           empleado_editar=empleado_editar) 


@app.route('/ver-empleado/<int:id_empleado>', methods=["GET"])
@login_required
def ver_empleado(id_empleado):
    return redirect(url_for('empleados', emp_id=id_empleado))


@app.route('/editar-empleado/<int:id_empleado>', methods=["GET", "POST"])
@login_required
def editar_empleado(id_empleado):
    if request.method == "POST":
        # ── Datos del empleado ──
        db.actualizarEmpleado(
            id_empleado,
            request.form.get("nombre"),
            request.form.get("apellidos"),
            request.form.get("puesto"),
            request.form.get("telefono"),
            request.form.get("email"),
            request.form.get("fecha_alta")
        )
        # ── Datos del contrato ──
        fecha_fin_val = request.form.get("fecha_fin") or None  # vacío = indefinido
        id_contrato   = request.form.get("id_contrato")
        if id_contrato:
            db.actualizarContrato(
                id_contrato,
                request.form.get("tipo_contrato"),
                request.form.get("fecha_inicio"),
                fecha_fin_val,
                request.form.get("horas_semanales"),
                request.form.get("salario_bruto_anual"),
                request.form.get("salario_neto")
            )
        elif request.form.get("tipo_contrato"):
            db.crearContrato(
                id_empleado,
                request.form.get("tipo_contrato"),
                request.form.get("fecha_inicio"),
                fecha_fin_val,
                request.form.get("horas_semanales"),
                request.form.get("salario_bruto_anual"),
                request.form.get("salario_neto")
            )
        return redirect(url_for("empleados"))

    # Redirige a la página de empleados con el parámetro editar
    return redirect(url_for('empleados', editar=id_empleado))


@app.route('/eliminar-empleado/<int:id_empleado>', methods=["POST"])
@login_required
def eliminar_empleado(id_empleado):
    db.eliminarEmpleadoDB(id_empleado)
    return redirect(url_for("empleados"))


if __name__ == '__main__':
    app.run(port=5001)