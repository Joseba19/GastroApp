from flask import Flask, render_template, request, jsonify
import mysql.connector
import random

app = Flask(__name__)

USER = "admin"
PASS = "1234"

def get_db():
    conn = mysql.connector.connect(
        host="nas.latorreg.es",
        user="root",
        password="7365",
        database="gastrolab"
    )
    return conn

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT nombre, password_hash
        FROM usuarios
        WHERE nombre = %s AND activo = 1
    """, (username,))
    
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario and usuario["password_hash"] == password:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Usuario o contraseña incorrectos"})
@app.route("/recetas")
def recetas():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.id_receta, r.nombre, r.descripcion, r.tiempo_preparacion, r.dificultad
        FROM recetas r
    """)
    recetas = cursor.fetchall()


    resultado = []
    for r in recetas:
        cursor.execute("""
            SELECT i.nombre
            FROM recetas_ingredientes ri
            JOIN ingredientes i ON ri.id_ingrediente = i.id_ingrediente
            WHERE ri.id_receta = %s
        """, (r["id_receta"],))
        ingredientes = cursor.fetchall()

        cursor.execute("""
            SELECT descripcion
            FROM pasos_receta
            WHERE id_receta = %s
            ORDER BY numero_paso
        """, (r["id_receta"],))
        pasos = cursor.fetchall()

        lista_ingredientes = []
        for ing in ingredientes:
            lista_ingredientes.append({"nombre": ing["nombre"]})

        lista_pasos = []
        for paso in pasos:
            lista_pasos.append(paso["descripcion"])

        

        resultado.append({
            "id": r["id_receta"],
            "nombre": r["nombre"],
            "descripcion": r["descripcion"] or "",
            "tiempo": r["tiempo_preparacion"] or "",
            "dificultad": r["dificultad"] or "",
            
            "imagen":  "",
            "ingredientes": lista_ingredientes,
            "pasos": lista_pasos
        })

    cursor.close()
    conn.close()
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(debug=True)