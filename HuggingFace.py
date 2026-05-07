# Importamos pipeline de transformers
from transformers import pipeline
# Cargamos el modelo de HuggingFace
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-7B-Instruct")

# Datos de ejemplo (simulación de nuestra base)
recetas = [
    {
        "nombre": "Ensalada de pollo",
        "calorias": 350,
        "proteinas": 30,
        "carbohidratos": 10,
        "grasas": 15
    },
    {
        "nombre": "Pasta carbonara",
        "calorias": 700,
        "proteinas": 20,
        "carbohidratos": 80,
        "grasas": 30
    }
]
# Función principal
def recomendar_receta():   
    # Pedimos al usuario los filtros nutricionales
    max_calorias = int(input("Máx calorías: "))
    min_proteinas = int(input("Mín proteínas: "))
    # Filtrar las recetas que cumplen condiciones
    filtradas = [
        r for r in recetas
        if r["calorias"] <= max_calorias and r["proteinas"] >= min_proteinas
    ]
    if not filtradas:
        print("No hay recetas que cumplan los requisitos")
        return
  
    # Aquí usamos IA para decidir la mejor opción
    prompt = f"""
    Tengo estas recetas:
    {filtradas}
    """
    # Generamos respuesta con la IA
    respuesta = pipe(prompt, max_new_tokens=200)
    # Mostramos la respuesta
    print("\nRecomendación:\n")
    print(respuesta[0]["generated_text"])
