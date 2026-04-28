from flask import Flask, render_template, request
from db import categoriaReceta, infoRecetaFiltrada, nombreIngredientes

app = Flask(__name__)

@app.route('/')
def inicio():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Obtener filtros de los parámetros URL
    categoria = request.args.get('categoria')
    dificultad = request.args.get('dificultad')
    
    categorias = categoriaReceta()
    categorias = [categoria[0] for categoria in categorias]
    
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
    categorias = [categoria[0] for categoria in categorias]

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
        activo = request.form.get("activo")
        listaIngredientes = request.form.getlist("ingredientes_ids[]")
        listaPasos = request.form.getlist("notas_pasos[]")

        print(listaIngredientes)

        # Checkbox → si no viene, es False
        activo = 1 if activo else 0

        # Guardar en la base de datos
        # (esto lo tienes que implementar tú en db.py)
        #guardar_receta(nombre, categoria, dificultad, raciones,
        #               tiempo_prep, tiempo_coccion, descripcion, activo)

        # Redirigir (MUY importante)
        return redirect(url_for("inicio"))

    return render_template('nuevaReceta.html', categorias=categorias, ingredientes=ingredientes)

if __name__ == '__main__':
    app.run(debug=True)