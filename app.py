from flask import Flask, render_template, request
from db import categoriasBD, infoRecetaFiltrada, nombreIngredientes, guardarReceta, eliminarReceta, obtenerReceta, obtenerPasos, obtenerIngredientes, infoNutriReceta, alergenosReceta

app = Flask(__name__)

@app.route('/')
def inicio():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    categoria = request.args.get('categoria')
    dificultad = request.args.get('dificultad')
    receta_id = request.args.get('receta_id', type=int)  # ← AÑADIR
    
    categorias = categoriasBD()
    categorias = [cat[1] for cat in categorias]
    
    recetas, total = infoRecetaFiltrada(page, per_page, categoria, dificultad)
    total_pages = (total + per_page - 1) // per_page
    
    # Cargar receta detallada si se pidió
    receta_detalle = None
    pasosReceta = None
    ingredientesReceta = None
    nutriReceta = None
    alergenoReceta = None
    if receta_id:
        receta_detalle = obtenerReceta(receta_id)
        pasosReceta = obtenerPasos(receta_id)
        ingredientesReceta = obtenerIngredientes(receta_id)
        nutriReceta = infoNutriReceta(receta_id)
        alergenoReceta = alergenosReceta(receta_id)
    
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
                         nutriReceta = nutriReceta, 
                         alergenoReceta = alergenoReceta)
    
from flask import redirect, url_for

@app.route('/nueva-receta', methods=["GET", "POST"])
def nueva_receta():
    categorias = categoriasBD()

    ingredientes = nombreIngredientes()

    if request.method == "POST":
        # Recoger datos del formulario
        nombre = request.form.get("nombre")
        categoria = request.form.get("categoria")
        dificultad = request.form.get("dificultad")
        raciones = request.form.get("raciones")
        tiempo_prep = request.form.get("tiempo_preparacion")
        tiempo_coccion = request.form.get("tiempo_coccion")
        descripcion = request.form.get("descripcion")
        listaIngredientes = request.form.getlist("ingredientes_ids[]")
        listaCantidades = request.form.getlist("cantidades[]")
        listaUnidades = request.form.getlist("unidades[]")
        listaNotas = request.form.getlist("notas_ing[]")
        listaPasos = request.form.getlist("notas_pasos[]")

        # Guardar en la base de datos
        guardarReceta(nombre, categoria, dificultad, raciones,
                       tiempo_prep, tiempo_coccion, descripcion, 
                       listaIngredientes, listaCantidades, listaUnidades, listaNotas, listaPasos)
        
        # Redirigir
        return redirect(url_for("inicio"))

    return render_template('nuevaReceta.html', categorias=categorias, ingredientes=ingredientes)

@app.route('/eliminar-receta/<int:id_receta>', methods=["POST"])
def eliminar_receta(id_receta):
    eliminarReceta(id_receta)
    return redirect(url_for("inicio"))

@app.route('/ver-receta/<int:id_receta>', methods=["GET"])
def ver_receta(id_receta):
    receta = obtenerReceta(id_receta)
    if receta is None:
        return "Receta no encontrada", 404
    return redirect(url_for('inicio', receta_id=id_receta))

@app.route('/editar-receta/<int:id_receta>', methods=["GET", "POST"])
def editar_receta(id_receta):
    print(f"ID recibido: {id_receta}, tipo: {type(id_receta)}")
    
    categorias = categoriasBD()
    ingredientes = obtenerIngredientes(id_receta)
    loopIngredientes = nombreIngredientes()
    receta = obtenerReceta(id_receta)
    pasos = obtenerPasos(id_receta)
    
    print(f"Receta: {receta}")
    print(f"Ingredientes: {ingredientes}")
    print(f"Pasos: {pasos}")
    
    return render_template('editarReceta.html', receta=receta, 
                           categorias=categorias, ingredientes=ingredientes, 
                           loopIngredientes=loopIngredientes, pasos=pasos)

if __name__ == '__main__':
    app.run(debug=True)