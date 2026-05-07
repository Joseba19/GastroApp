# Importamos la librería pipeline de transformers
from transformers import pipeline
# Cargamos el modelo Qwen
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-7B-Instruct")


# Función: recomendar receta

def recomendar_receta(): 
    # Pedimos al usuario las condiciones
    condiciones = input("Introduce lhas condiciones que tú quieras (baja en calorías, sin gluten...): ")

    # Creamos el prompt 
    prompt = f"""
    Recomiéndame una receta con estas condiciones:
    {condiciones}
    """

    # Generamos la respuesta con la IA
    respuesta = pipe(prompt, max_new_tokens=200)

    # Mostramos la respuesta por pantalla
    print("\nLa respuesta del modelo es la siguiente:\n")
    print(respuesta[0]["generated_text"])


# Función: obtener ingredientes
def obtener_ingredientes():
    print("\n--- INGREDIENTES DE UNA RECETA ---")
    
    # Pedimos el nombre de la receta
    receta = input("Introduce el nombre de la receta: ")

    # Prompt para pedir SOLO ingredientes
    prompt = f"""
    Dime únicamente los ingredientes necesarios para hacer {receta}.
    """

    # Llamamos al modelo
    respuesta = pipe(prompt, max_new_tokens=200)

    # Mostramos resultado
    print("\nIngredientes:\n")
    print(respuesta[0]["generated_text"])

# Función: menú principal
def menu():
    while True:
        print("1. Recomendar receta")
        print("2. Ver ingredientes de una receta")
        print("3. Salir")

        # Pedimos opción al usuario
        opcion = input("Elige una opción: ")

        # Dependiendo de la opción llamamos a una función
        if opcion == "1":
            recomendar_receta()
        elif opcion == "2":
            obtener_ingredientes()
        elif opcion == "3":
            print("Saliendo...")
            break  
        else:
            print("La opción dada no es válida")

if __name__ == "__main__":
    menu()
