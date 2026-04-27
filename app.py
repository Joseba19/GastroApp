from flask import Flask, render_template
from db import categoriaReceta

app = Flask(__name__)

@app.route('/')
def inicio():
    # Llamar a la función del archivo db.py
    resultados = categoriaReceta()
    
    # Convertir de [(nombre1,), (nombre2,)] a una lista simple
    categorias = [categoria[0] for categoria in resultados]
    
    # Pasar los datos al template
    return render_template('index.html', categorias=categorias)

if __name__ == '__main__':
    app.run(debug=True)