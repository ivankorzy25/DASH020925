import mysql.connector

CONFIG = {
    "sql_host": "127.0.0.1",
    "sql_port": 3307,
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

def actualizar_esquema():
    """
    Añade la columna 'fecha_eliminacion' a la tabla 'producto_multimedia'
    para implementar la funcionalidad de borrado lógico (soft delete).
    """
    try:
        conn = mysql.connector.connect(
            host=CONFIG["sql_host"],
            port=CONFIG["sql_port"],
            user=CONFIG["sql_user"],
            password=CONFIG["sql_pass"],
            database=CONFIG["sql_db"]
        )
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE table_name = 'producto_multimedia' 
            AND column_name = 'fecha_eliminacion'
            AND table_schema = %s
        """, (CONFIG["sql_db"],))
        
        if cursor.fetchone()[0] == 0:
            print("Añadiendo columna 'fecha_eliminacion' a la tabla 'producto_multimedia'...")
            # Sentencia SQL para añadir la nueva columna
            sql_alter_table = """
            ALTER TABLE producto_multimedia
            ADD COLUMN fecha_eliminacion TIMESTAMP NULL DEFAULT NULL AFTER orden_posicion;
            """
            cursor.execute(sql_alter_table)
            conn.commit()
            print("Columna 'fecha_eliminacion' añadida exitosamente.")
        else:
            print("La columna 'fecha_eliminacion' ya existe.")

    except mysql.connector.Error as err:
        print(f"Error al actualizar la tabla: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == '__main__':
    actualizar_esquema()
