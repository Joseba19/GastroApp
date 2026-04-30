from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# ======================
# LOGIN
# ======================
USER = "admin"
PASS = "1234"

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if username == USER and password == PASS:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Usuario o   raseña incorrectos"})


# ======================
# RECETAS DESDE JSON
# ======================
def cargar_json():
    with open("recetas.json", encoding="utf-8") as f:
        return json.load(f)

def guardar_json(data):
    with open("recetas.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.route("/recetas")
def recetas():
    with open("recetas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


# ======================
# EDITAR RECETA
# ======================
@app.route("/editar_receta/<id>", methods=["POST"])
def editar_receta(id):
    data = request.get_json()
    recetas = cargar_json()

    for r in recetas:
        if r["id"] == id:
            r["nombre"] = data.get("nombre", r["nombre"])

    guardar_json(recetas)
    return jsonify({"success": True})


# ======================
# BORRAR RECETA
# ======================
@app.route("/borrar_receta/<id>", methods=["POST"])
def borrar_receta(id):
    recetas = cargar_json()
    recetas = [r for r in recetas if r["id"] != id]

    guardar_json(recetas)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)