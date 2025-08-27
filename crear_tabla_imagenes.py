import mysql.connector

CONFIG = {
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

def crear_tabla_imagenes():
    """Crea la tabla para almacenar múltiples imágenes por producto"""
    
    conn = mysql.connector.connect(
        host=CONFIG["sql_host"],
        user=CONFIG["sql_user"],
        password=CONFIG["sql_pass"],
        database=CONFIG["sql_db"]
    )
    
    cursor = conn.cursor()
    
    try:
        # Crear la tabla de imágenes si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS producto_imagenes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                producto_sku VARCHAR(100) NOT NULL,
                producto_modelo VARCHAR(200) NOT NULL,
                url_imagen VARCHAR(500) NOT NULL,
                tamano_bytes INT NOT NULL,
                orden_posicion INT NOT NULL,
                fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_producto_sku (producto_sku),
                INDEX idx_producto_modelo (producto_modelo)
            )
        """)
        
        print("✅ Tabla 'producto_imagenes' creada o ya existe")
        
        # Verificar la estructura
        cursor.execute("DESCRIBE producto_imagenes")
        columnas = cursor.fetchall()
        
        print("\n📊 Estructura de la tabla:")
        for columna in columnas:
            print(f"  - {columna[0]}: {columna[1]}")
        
        # Contar registros existentes
        cursor.execute("SELECT COUNT(*) FROM producto_imagenes")
        count = cursor.fetchone()[0]
        print(f"\n📦 Total de imágenes existentes: {count}")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error al crear la tabla: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    crear_tabla_imagenes()
