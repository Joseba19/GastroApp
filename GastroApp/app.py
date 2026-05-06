from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

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
        return jsonify({"success": False, "error": "Usuario o contraseña incorrectos"})

def cargar_json():
    try:
        with open("recetas.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Crear archivo vacío si no existe
        with open("recetas.json", "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        return []

def guardar_json(data):
    with open("recetas.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route("/recetas")
def recetas():
    data = cargar_json()
    return jsonify(data)

@app.route("/editar_receta/<id>", methods=["POST"])
def editar_receta(id):
    data = request.get_json()
    recetas = cargar_json()

    for r in recetas:
        if str(r["id"]) == str(id):
            r["nombre"] = data.get("nombre", r["nombre"])
            r["descripcion"] = data.get("descripcion", r.get("descripcion", ""))
            r["tiempo"] = data.get("tiempo", r.get("tiempo", ""))
            r["dificultad"] = data.get("dificultad", r.get("dificultad", ""))
            r["ingredientes"] = data.get("ingredientes", r.get("ingredientes", []))
            r["pasos"] = data.get("pasos", r.get("pasos", []))
            break

    guardar_json(recetas)
    return jsonify({"success": True})

@app.route("/borrar_receta/<id>", methods=["POST"])
def borrar_receta(id):
    recetas = cargar_json()
    recetas = [r for r in recetas if str(r["id"]) != str(id)]
    guardar_json(recetas)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)