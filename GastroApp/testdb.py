import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Passw0rd",
        database="gastrolab"
    )
    print("Conexion exitosa a gastrolab")
    conn.close()
except Exception as e:
    print("Error:", e)