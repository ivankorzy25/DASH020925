import mysql.connector

CONFIG = {
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

def test_connection():
    try:
        print(f"Intentando conectar a la base de datos en {CONFIG['sql_host']}...")
        conn = mysql.connector.connect(
            host=CONFIG["sql_host"],
            user=CONFIG["sql_user"],
            password=CONFIG["sql_pass"],
            database=CONFIG["sql_db"],
            connect_timeout=10
        )
        print("¡Conexión a la base de datos exitosa!")
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")

if __name__ == "__main__":
    test_connection()
