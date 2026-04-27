from flask import Flask, render_template, request
from db import categoriaReceta, infoReceta

app = Flask(__name__)

@app.route('/')
def inicio():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    categorias = categoriaReceta()
    categorias = [categoria[0] for categoria in categorias]

    recetas, total = infoReceta(page, per_page)

    total_pages = (total + per_page - 1) // per_page
    return render_template('index.html', categorias=categorias, recetas=recetas, page=page, total_pages=total_pages)

if __name__ == '__main__':
    app.run(debug=True)