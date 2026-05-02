from flask import Flask, render_template, request, redirect, url_for
import db

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def inicio():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    categoria = request.args.get('categoria')
    dificultad = request.args.get('dificultad')
    receta_id = request.args.get('receta_id', type=int)

    categorias = db.categoriasBD()
    categorias = [cat[1] for cat in categorias]

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
            request.form.get("sodio")
        )

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
                         alergenoReceta=alergenoReceta)


@app.route('/nueva-receta', methods=["GET", "POST"])
def nueva_receta():
    categorias = db.categoriasBD()
    ingredientes = db.nombreIngredientes()

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
                request.form.get("sodio")
            )

    return render_template('nuevaReceta.html', categorias=categorias, ingredientes=ingredientes)


@app.route('/eliminar-receta/<int:id_receta>', methods=["POST"])
def eliminar_receta(id_receta):
    db.eliminarReceta(id_receta)
    return redirect(url_for("inicio"))


@app.route('/ver-receta/<int:id_receta>', methods=["GET"])
def ver_receta(id_receta):
    receta = db.obtenerReceta(id_receta)
    if receta is None:
        return "Receta no encontrada", 404
    return redirect(url_for('inicio', receta_id=id_receta))


@app.route('/editar-receta/<int:id_receta>', methods=["GET", "POST"])
def editar_receta(id_receta):
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


# ── INGREDIENTES ──────────────────────────────────────────────────────────────

@app.route('/ingredientes', methods=["GET", "POST"])
def ingredientes():
    page             = request.args.get('page', 1, type=int)
    per_page         = 15
    categoria_actual = request.args.get('categoria')
    unidad_actual    = request.args.get('unidad')
    ing_id           = request.args.get('ing_id', type=int)

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
            request.form.get("sodio")
        )
        return redirect(url_for("ingredientes"))

    ingredientes_list, total = db.obtenerIngredientesFiltrados(page, per_page, categoria_actual, unidad_actual)
    total_pages = (total + per_page - 1) // per_page
    categorias  = db.obtenerCategoriasIngredientes()

    ingrediente_detalle = db.obtenerIngrediente(ing_id) if ing_id else None

    return render_template('ingredientes.html',
                           ingredientes=ingredientes_list,
                           page=page,
                           total_pages=total_pages,
                           categorias=categorias,
                           categoria_actual=categoria_actual,
                           unidad_actual=unidad_actual,
                           ingrediente_detalle=ingrediente_detalle)


@app.route('/ver-ingrediente/<int:id_ingrediente>', methods=["GET"])
def ver_ingrediente(id_ingrediente):
    return redirect(url_for('ingredientes', ing_id=id_ingrediente))


@app.route('/editar-ingrediente/<int:id_ingrediente>', methods=["GET", "POST"])
def editar_ingrediente(id_ingrediente):
    if request.method == "POST":
        db.actualizarIngrediente(
            id_ingrediente,
            request.form.get("nombreIng"),
            request.form.get("unidad"),
            request.form.get("categoria"),
            request.form.get("calorias"),
            request.form.get("proteinas"),
            request.form.get("carbohidratos"),
            request.form.get("grasas"),
            request.form.get("fibra"),
            request.form.get("sodio")
        )
        return redirect(url_for("ingredientes"))
    ingrediente = db.obtenerIngrediente(id_ingrediente)
    return render_template('editarIngrediente.html', ingrediente=ingrediente)


@app.route('/eliminar-ingrediente/<int:id_ingrediente>', methods=["POST"])
def eliminar_ingrediente(id_ingrediente):
    db.eliminarIngredienteDB(id_ingrediente)
    return redirect(url_for("ingredientes"))


# ── ALÉRGENOS ─────────────────────────────────────────────────────────────────

@app.route('/alergenos', methods=["GET", "POST"])
def alergenos():
    page            = request.args.get('page', 1, type=int)
    per_page        = 12
    alergeno_actual = request.args.get('alergeno')

    if request.method == "POST":
        db.asignarAlergeno(
            request.form.get("id_ingrediente"),
            request.form.get("alergeno")
        )
        return redirect(url_for("alergenos"))

    recetas_alergenos, total = db.recetasConAlergenos(page, per_page, alergeno_actual)
    total_pages       = (total + per_page - 1) // per_page
    resumen_alergenos = db.resumenAlergenos()
    lista_alergenos   = db.listaAlergenosUnicos()
    todos_ingredientes = db.nombreIngredientes()

    return render_template('alergenos.html',
                           recetas_alergenos=recetas_alergenos,
                           page=page,
                           total_pages=total_pages,
                           resumen_alergenos=resumen_alergenos,
                           lista_alergenos=lista_alergenos,
                           alergeno_actual=alergeno_actual,
                           todos_ingredientes=todos_ingredientes)


# ── MENÚS ─────────────────────────────────────────────────────────────────────

@app.route('/menus', methods=["GET", "POST"])
def menus():
    page          = request.args.get('page', 1, type=int)
    per_page      = 10
    tipo_actual   = request.args.get('tipo')
    activo_actual = request.args.get('activo')
    menu_id       = request.args.get('menu_id', type=int)

    if request.method == "POST":
        # CORRECCIÓN: eliminados precio, fecha_inicio, fecha_fin (no existen en BD)
        db.guardarMenu(
            request.form.get("nombre"),
            request.form.get("tipo"),
            request.form.get("activo"),
            request.form.get("descripcion"),
            request.form.getlist("recetas_ids[]"),
            request.form.getlist("tipo_plato[]")
        )
        return redirect(url_for("menus"))

    menus_list, total = db.obtenerMenusFiltrados(page, per_page, tipo_actual, activo_actual)
    total_pages = (total + per_page - 1) // per_page
    todas_recetas, _ = db.infoRecetaFiltrada(1, 9999)

    menu_detalle = None
    recetas_menu = []
    if menu_id:
        menu_detalle = db.obtenerMenuDetalle(menu_id)
        recetas_menu = db.obtenerRecetasMenu(menu_id)

    return render_template('menus.html',
                           menus=menus_list,
                           page=page,
                           total_pages=total_pages,
                           tipo_actual=tipo_actual,
                           activo_actual=activo_actual,
                           todas_recetas=todas_recetas,
                           menu_detalle=menu_detalle,
                           recetas_menu=recetas_menu)


@app.route('/ver-menu/<int:id_menu>', methods=["GET"])
def ver_menu(id_menu):
    return redirect(url_for('menus', menu_id=id_menu))


@app.route('/editar-menu/<int:id_menu>', methods=["GET", "POST"])
def editar_menu(id_menu):
    if request.method == "POST":
        # CORRECCIÓN: eliminados precio, fecha_inicio, fecha_fin
        db.actualizarMenu(
            id_menu,
            request.form.get("nombre"),
            request.form.get("tipo"),
            request.form.get("activo"),
            request.form.get("descripcion"),
            request.form.getlist("recetas_ids[]"),
            request.form.getlist("tipo_plato[]")
        )
        return redirect(url_for("menus"))
    menu = db.obtenerMenuDetalle(id_menu)
    recetas_menu = db.obtenerRecetasMenu(id_menu)
    todas_recetas, _ = db.infoRecetaFiltrada(1, 9999)
    return render_template('editarMenu.html', menu=menu,
                           recetas_menu=recetas_menu, todas_recetas=todas_recetas)


@app.route('/eliminar-menu/<int:id_menu>', methods=["POST"])
def eliminar_menu(id_menu):
    db.eliminarMenuDB(id_menu)
    return redirect(url_for("menus"))


# ── EMPLEADOS ─────────────────────────────────────────────────────────────────

@app.route('/empleados', methods=["GET", "POST"])
def empleados():
    page          = request.args.get('page', 1, type=int)
    per_page      = 10
    puesto_actual = request.args.get('puesto')
    activo_actual = request.args.get('activo')
    emp_id        = request.args.get('emp_id', type=int)

    if request.method == "POST":
        # CORRECCIÓN: eliminados turno, salario, notas (no existen en la tabla empleados)
        db.guardarEmpleado(
            request.form.get("nombre"),
            request.form.get("apellidos"),
            request.form.get("puesto"),
            request.form.get("telefono"),
            request.form.get("email"),
            request.form.get("fecha_alta"),
            1 if request.form.get("activo") else 0
        )
        return redirect(url_for("empleados"))

    # CORRECCIÓN: eliminado turno_actual (columna turno no existe)
    empleados_list, total = db.obtenerEmpleadosFiltrados(page, per_page, puesto_actual, activo_actual)
    total_pages = (total + per_page - 1) // per_page
    total_empleados, empleados_activos, empleados_cocina, empleados_docencia = db.obtenerResumenEmpleados()

    empleado_detalle = db.obtenerEmpleado(emp_id) if emp_id else None

    return render_template('empleados.html',
                           empleados=empleados_list,
                           page=page,
                           total_pages=total_pages,
                           puesto_actual=puesto_actual,
                           activo_actual=activo_actual,
                           total_empleados=total_empleados,
                           empleados_activos=empleados_activos,
                           empleados_cocina=empleados_cocina,
                           empleados_docencia=empleados_docencia,
                           empleado_detalle=empleado_detalle)


@app.route('/ver-empleado/<int:id_empleado>', methods=["GET"])
def ver_empleado(id_empleado):
    return redirect(url_for('empleados', emp_id=id_empleado))


@app.route('/editar-empleado/<int:id_empleado>', methods=["GET", "POST"])
def editar_empleado(id_empleado):
    if request.method == "POST":
        # CORRECCIÓN: eliminados turno, salario, notas
        db.actualizarEmpleado(
            id_empleado,
            request.form.get("nombre"),
            request.form.get("apellidos"),
            request.form.get("puesto"),
            request.form.get("telefono"),
            request.form.get("email"),
            request.form.get("fecha_alta"),
            1 if request.form.get("activo") else 0
        )
        return redirect(url_for("empleados"))
    empleado = db.obtenerEmpleado(id_empleado)
    return render_template('editarEmpleado.html', empleado=empleado)


@app.route('/eliminar-empleado/<int:id_empleado>', methods=["POST"])
def eliminar_empleado(id_empleado):
    db.eliminarEmpleadoDB(id_empleado)
    return redirect(url_for("empleados"))


if __name__ == '__main__':
    app.run(debug=True)