from flask import Flask, render_template
from db import categoriaReceta, infoReceta

app = Flask(__name__)

@app.route('/')
def inicio():
    # Llamar a la función del archivo db.py
    categorias = categoriaReceta()
    categorias = [categoria[0] for categoria in categorias]     # Convertir de [(nombre1,), (nombre2,)] a una lista simple

    recetas = infoReceta()
    for dato in recetas:
        print(dato[0])
    
    # Pasar los datos al template
    return render_template('index.html', categorias=categorias, recetas=recetas, var=0)

if __name__ == '__main__':
    app.run(debug=True)