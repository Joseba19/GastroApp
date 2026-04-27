from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Usuario de prueba
USER = "admin"
PASS = "1234"

# Datos en memoria
recetas = [
    {"id": 1, "nombre": "Pasta"},
    {"id": 2, "nombre": "Pizza"},
    {"id": 3, "nombre": "Ensalada"}
]

# HOME
@app.route('/')
def inicio():
    return render_template('index.html')

# LOGIN
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if data.get("username") == USER and data.get("password") == PASS:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Usuario o contraseña incorrectos"})

# OBTENER RECETAS
@app.route("/recetas", methods=["GET"])
def obtener_recetas():
    return jsonify(recetas)

# EDITAR
@app.route("/editar_receta/<int:id>", methods=["POST"])
def editar_receta(id):
    data = request.get_json()

    for r in recetas:
        if r["id"] == id:
            r["nombre"] = data.get("nombre")
            return jsonify({"success": True})

    return jsonify({"success": False})

# BORRAR
@app.route("/borrar_receta/<int:id>", methods=["POST"])
def borrar_receta(id):
    global recetas
    recetas = [r for r in recetas if r["id"] != id]
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)