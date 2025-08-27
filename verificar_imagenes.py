import mysql.connector

CONFIG = {
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

try:
    print("=== Verificación de tabla producto_imagenes ===\n")
    
    conn = mysql.connector.connect(
        host=CONFIG["sql_host"],
        user=CONFIG["sql_user"],
        password=CONFIG["sql_pass"],
        database=CONFIG["sql_db"]
    )
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = %s 
        AND table_name = 'producto_imagenes'
    """, (CONFIG["sql_db"],))
    
    existe = cursor.fetchone()[0]
    
    if existe:
        print("✓ La tabla producto_imagenes existe\n")
        
        # Ver estructura de la tabla
        cursor.execute("DESCRIBE producto_imagenes")
        print("Estructura de la tabla:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} {row[2]} {row[3]}")
        
        # Ver cuántas imágenes hay
        cursor.execute("SELECT COUNT(*) FROM producto_imagenes")
        total = cursor.fetchone()[0]
        print(f"\nTotal de imágenes en la base: {total}")
        
        if total > 0:
            # Ver productos con imágenes
            cursor.execute("""
                SELECT producto_modelo, COUNT(*) as num_imagenes 
                FROM producto_imagenes 
                GROUP BY producto_modelo
                LIMIT 10
            """)
            
            print("\nProductos con imágenes:")
            for row in cursor.fetchall():
                print(f"  - {row[0]}: {row[1]} imágenes")
    else:
        print("✗ La tabla producto_imagenes NO existe")
        print("\nCreando tabla producto_imagenes...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS producto_imagenes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                producto_sku VARCHAR(100),
                producto_modelo VARCHAR(255),
                url_imagen TEXT,
                tamano_bytes INT,
                orden_posicion INT DEFAULT 1,
                fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_sku (producto_sku),
                INDEX idx_modelo (producto_modelo)
            )
        """)
        conn.commit()
        print("✓ Tabla creada exitosamente")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error al conectar o verificar la tabla: {e}")
