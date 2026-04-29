from flask import Flask, render_template, request
from db import categoriaReceta, infoRecetaFiltrada, nombreIngredientes, guardarReceta, eliminarReceta

app = Flask(__name__)

@app.route('/')
def inicio():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Obtener filtros de los parámetros URL
    categoria = request.args.get('categoria')
    dificultad = request.args.get('dificultad')
    
    categorias = categoriaReceta()
    categorias = [cat[1] for cat in categorias]  # [1] = nombre, y renombrado a cat
    
    # Usar función con filtros
    recetas, total = infoRecetaFiltrada(page, per_page, categoria, dificultad)
    
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('index.html', 
                         categorias=categorias, 
                         recetas=recetas, 
                         page=page, 
                         total_pages=total_pages,
                         categoria_actual=categoria,
                         dificultad_actual=dificultad)
    
from flask import redirect, url_for

@app.route('/nueva-receta', methods=["GET", "POST"])
def nueva_receta():
    categorias = categoriaReceta()

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
        listaNotas = request.form.getlist("notas_ing[]")
        listaPasos = request.form.getlist("notas_pasos[]")

        print(categoria)
        print(tiempo_coccion)
        print(tiempo_prep)

        # Guardar en la base de datos
        guardarReceta(nombre, categoria, dificultad, raciones,
                       tiempo_prep, tiempo_coccion, descripcion, 
                       listaIngredientes, listaCantidades, listaNotas, listaPasos)
        
        # Redirigir
        return redirect(url_for("inicio"))

    return render_template('nuevaReceta.html', categorias=categorias, ingredientes=ingredientes)

@app.route('/eliminar-receta/<int:id_receta>', methods=["POST"])
def eliminar_receta(id_receta):
    eliminarReceta(id_receta)
    return redirect(url_for("inicio"))

@app.route('/ver-receta/<int:id_receta>', methods=["GET"])
def ver_receta(id_receta):
    # Aquí irá la función de db.py que traiga los detalles de la receta
    receta = obtenerReceta(id_receta)  # pendiente de crear en db.py
    return render_template('verReceta.html', receta=receta)

@app.route('/editar-receta/<int:id_receta>', methods=["GET", "POST"])
def editar_receta(id_receta):
    categorias = categoriaReceta()
    ingredientes = nombreIngredientes()
    receta = obtenerReceta(id_receta)  # pendiente de crear en db.py

    if request.method == "POST":
        nombre = request.form.get("nombre")
        categoria = request.form.get("categoria")
        # ... resto de campos igual que en nueva_receta
        
        # actualizarReceta(id_receta, nombre, categoria, ...)  # pendiente de crear en db.py
        return redirect(url_for("inicio"))

    return render_template('editarReceta.html', receta=receta, 
                           categorias=categorias, ingredientes=ingredientes)

if __name__ == '__main__':
    app.run(debug=True)