import json
import os
from flask import Flask, render_template, abort

app = Flask(__name__)

def cargar_recetas():
    ruta = os.path.join(app.root_path, 'static', 'data', 'recetas.json')
    with open(ruta, encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def inicio():
    recetas = cargar_recetas()
    return render_template('index.html', recetas=recetas)

@app.route('/receta/<id_receta>')
def receta(id_receta):
    recetas = cargar_recetas()
    receta = next((r for r in recetas if r['id'] == id_receta), None)
    if receta is None:
        abort(404)
    return render_template('receta.html', receta=receta)

if __name__ == '__main__':
    app.run(debug=True)