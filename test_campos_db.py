import mysql.connector

CONFIG = {
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

def verificar_campos():
    conn = mysql.connector.connect(
        host=CONFIG["sql_host"],
        user=CONFIG["sql_user"],
        password=CONFIG["sql_pass"],
        database=CONFIG["sql_db"]
    )
    cursor = conn.cursor()
    
    print("=" * 60)
    print("CAMPOS DISPONIBLES EN LA TABLA")
    print("=" * 60)
    
    # Obtener todos los campos de la tabla
    cursor.execute("""
        SHOW COLUMNS FROM shop_master_gaucho_completo
    """)
    
    campos = cursor.fetchall()
    print("\nCampos en la tabla shop_master_gaucho_completo:")
    for campo in campos:
        print(f"  - {campo[0]} ({campo[1]})")
    
    # Buscar campos que puedan contener imágenes
    print("\n" + "=" * 60)
    print("CAMPOS POTENCIALES DE IMÁGENES")
    print("=" * 60)
    
    campos_imagen = []
    for campo in campos:
        nombre_campo = campo[0].lower()
        if any(word in nombre_campo for word in ['img', 'image', 'foto', 'photo', 'pic', 'url']):
            campos_imagen.append(campo[0])
            print(f"  - {campo[0]}")
    
    # Verificar contenido de campos de imagen
    if campos_imagen:
        print("\n" + "=" * 60)
        print("VERIFICANDO CONTENIDO DE CAMPOS DE IMAGEN")
        print("=" * 60)
        
        for campo in campos_imagen:
            cursor.execute(f"""
                SELECT {campo}, COUNT(*) as cantidad
                FROM shop_master_gaucho_completo
                WHERE {campo} IS NOT NULL AND {campo} != ''
                GROUP BY {campo}
                LIMIT 3
            """)
            resultados = cursor.fetchall()
            if resultados:
                print(f"\n{campo} (primeras 3 muestras):")
                for resultado in resultados:
                    print(f"  - {resultado[0][:100]}..." if len(str(resultado[0])) > 100 else f"  - {resultado[0]}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    verificar_campos()
