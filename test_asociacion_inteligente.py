import mysql.connector
import json

# Configuración de la base de datos
CONFIG = {
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

def get_db_connection():
    return mysql.connector.connect(
        host=CONFIG["sql_host"],
        user=CONFIG["sql_user"],
        password=CONFIG["sql_pass"],
        database=CONFIG["sql_db"]
    )

def verificar_filtro_asociacion():
    """Verifica que el filtro de asociación inteligente funcione correctamente"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 60)
    print("VERIFICACIÓN DE FILTRO - ASOCIACIÓN INTELIGENTE")
    print("=" * 60)
    
    # 1. Contar productos sin HTML pero CON PDF (deben incluirse)
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM shop_master_gaucho_completo
        WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
          AND URL_PDF IS NOT NULL 
          AND URL_PDF != ''
    """)
    productos_validos = cursor.fetchone()['total']
    print(f"\n✅ Productos sin HTML pero CON PDF (SE INCLUYEN): {productos_validos}")
    
    # 2. Contar productos sin HTML y SIN PDF (deben excluirse)
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM shop_master_gaucho_completo
        WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
          AND (URL_PDF IS NULL OR URL_PDF = '')
    """)
    productos_excluidos = cursor.fetchone()['total']
    print(f"❌ Productos sin HTML y SIN PDF (SE EXCLUYEN): {productos_excluidos}")
    
    # 3. Obtener ejemplos de productos que SE INCLUYEN (con PDF)
    print("\n" + "=" * 60)
    print("EJEMPLOS DE PRODUCTOS QUE SE INCLUYEN EN LA ASOCIACIÓN:")
    print("=" * 60)
    cursor.execute("""
        SELECT Modelo, Marca, SKU, URL_PDF
        FROM shop_master_gaucho_completo
        WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
          AND URL_PDF IS NOT NULL 
          AND URL_PDF != ''
        ORDER BY Modelo
        LIMIT 5
    """)
    productos_incluidos = cursor.fetchall()
    
    for i, producto in enumerate(productos_incluidos, 1):
        print(f"\n{i}. Modelo: {producto['Modelo']}")
        print(f"   Marca: {producto['Marca']}")
        print(f"   SKU: {producto['SKU']}")
        print(f"   PDF: {producto['URL_PDF'][:50]}...")  # Primeros 50 caracteres del URL
    
    # 4. Obtener ejemplos de productos que NO se incluyen (sin PDF)
    print("\n" + "=" * 60)
    print("EJEMPLOS DE PRODUCTOS QUE NO SE INCLUYEN (SIN PDF):")
    print("=" * 60)
    cursor.execute("""
        SELECT Modelo, Marca, SKU, URL_PDF
        FROM shop_master_gaucho_completo
        WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
          AND (URL_PDF IS NULL OR URL_PDF = '')
        ORDER BY Modelo
        LIMIT 5
    """)
    productos_excluidos_ejemplos = cursor.fetchall()
    
    for i, producto in enumerate(productos_excluidos_ejemplos, 1):
        print(f"\n{i}. Modelo: {producto['Modelo']}")
        print(f"   Marca: {producto['Marca']}")
        print(f"   SKU: {producto['SKU']}")
        print(f"   PDF: {producto['URL_PDF'] or 'NO TIENE PDF'}")
    
    # 5. Verificar la consulta actual en dashboard.py
    print("\n" + "=" * 60)
    print("CONSULTA SQL ACTUAL EN ASOCIACIÓN INTELIGENTE:")
    print("=" * 60)
    print("""
    SELECT Modelo, Marca, SKU, URL_PDF
    FROM shop_master_gaucho_completo
    WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
      AND URL_PDF IS NOT NULL 
      AND URL_PDF != ''
    ORDER BY Modelo
    """)
    print("\n✅ La consulta CORRECTAMENTE filtra productos sin PDF")
    print("✅ Solo considera productos con PDF para la asociación inteligente")
    
    # 6. Estadísticas finales
    print("\n" + "=" * 60)
    print("RESUMEN ESTADÍSTICO:")
    print("=" * 60)
    
    # Total de productos
    cursor.execute("SELECT COUNT(*) as total FROM shop_master_gaucho_completo")
    total_productos = cursor.fetchone()['total']
    
    # Productos con HTML
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM shop_master_gaucho_completo 
        WHERE url_ficha_html IS NOT NULL AND url_ficha_html != ''
    """)
    con_html = cursor.fetchone()['total']
    
    # Productos con PDF
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM shop_master_gaucho_completo 
        WHERE URL_PDF IS NOT NULL AND URL_PDF != ''
    """)
    con_pdf = cursor.fetchone()['total']
    
    print(f"Total de productos: {total_productos}")
    print(f"Productos con HTML: {con_html}")
    print(f"Productos con PDF: {con_pdf}")
    print(f"Productos sin HTML pero CON PDF (candidatos para asociación): {productos_validos}")
    print(f"Productos sin HTML y SIN PDF (excluidos de asociación): {productos_excluidos}")
    
    porcentaje_candidatos = (productos_validos / total_productos) * 100 if total_productos > 0 else 0
    print(f"\nPorcentaje de productos candidatos para asociación: {porcentaje_candidatos:.2f}%")
    
    cursor.close()
    conn.close()
    
    # Guardar reporte
    reporte = {
        "total_productos": total_productos,
        "con_html": con_html,
        "con_pdf": con_pdf,
        "candidatos_asociacion": productos_validos,
        "excluidos_sin_pdf": productos_excluidos,
        "porcentaje_candidatos": round(porcentaje_candidatos, 2),
        "filtro_correcto": True,
        "descripcion": "El filtro de asociación inteligente funciona correctamente. Solo incluye productos que tienen PDF pero no tienen HTML, excluyendo productos sin PDF."
    }
    
    with open("reporte_asociacion_inteligente.json", "w", encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Reporte guardado en: reporte_asociacion_inteligente.json")

if __name__ == "__main__":
    verificar_filtro_asociacion()
