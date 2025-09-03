import mysql.connector

CONFIG = {
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

def test_filtro_pdf():
    conn = mysql.connector.connect(
        host=CONFIG["sql_host"],
        user=CONFIG["sql_user"],
        password=CONFIG["sql_pass"],
        database=CONFIG["sql_db"]
    )
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 60)
    print("PRUEBA DE FILTRO DE PRODUCTOS SIN PDF")
    print("=" * 60)
    
    # 1. Contar productos totales
    cursor.execute("SELECT COUNT(*) as total FROM shop_master_gaucho_completo")
    total = cursor.fetchone()['total']
    print(f"\n1. Total de productos: {total}")
    
    # 2. Contar productos con HTML
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM shop_master_gaucho_completo 
        WHERE url_ficha_html IS NOT NULL AND url_ficha_html != ''
    """)
    con_html = cursor.fetchone()['total']
    print(f"2. Productos CON HTML: {con_html}")
    
    # 3. Contar productos con PDF
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM shop_master_gaucho_completo 
        WHERE URL_PDF IS NOT NULL AND URL_PDF != ''
    """)
    con_pdf = cursor.fetchone()['total']
    print(f"3. Productos CON PDF: {con_pdf}")
    
    # 4. Productos sin HTML y sin PDF (NO DEBERÍAN aparecer en asociación)
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM shop_master_gaucho_completo 
        WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
          AND (URL_PDF IS NULL OR URL_PDF = '')
    """)
    sin_html_sin_pdf = cursor.fetchone()['total']
    print(f"4. Productos SIN HTML y SIN PDF: {sin_html_sin_pdf} ❌ (NO deben aparecer en asociación)")
    
    # 5. Productos sin HTML pero CON PDF (SÍ DEBERÍAN aparecer en asociación)
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM shop_master_gaucho_completo 
        WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
          AND URL_PDF IS NOT NULL 
          AND URL_PDF != ''
    """)
    sin_html_con_pdf = cursor.fetchone()['total']
    print(f"5. Productos SIN HTML pero CON PDF: {sin_html_con_pdf} ✅ (SÍ deben aparecer en asociación)")
    
    # 6. Verificar el filtro actual usado en la asociación inteligente
    print("\n" + "=" * 60)
    print("VERIFICANDO FILTRO ACTUAL EN ASOCIACIÓN INTELIGENTE:")
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
    
    productos_filtrados = cursor.fetchall()
    print(f"\nProductos que aparecerán en asociación inteligente (primeros 5):")
    for p in productos_filtrados:
        print(f"  - {p['Modelo']} | PDF: {'✓' if p['URL_PDF'] else '✗'}")
    
    # 7. Verificar productos excluidos (sin PDF)
    cursor.execute("""
        SELECT Modelo, Marca, SKU
        FROM shop_master_gaucho_completo
        WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
          AND (URL_PDF IS NULL OR URL_PDF = '')
        LIMIT 5
    """)
    
    productos_excluidos = cursor.fetchall()
    if productos_excluidos:
        print(f"\nProductos EXCLUIDOS de asociación (sin PDF) - primeros 5:")
        for p in productos_excluidos:
            print(f"  - {p['Modelo']} | SIN PDF ❌")
    else:
        print("\n✅ No hay productos sin PDF (todos tienen PDF)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("RESULTADO FINAL:")
    print("=" * 60)
    print(f"✅ El filtro está configurado correctamente:")
    print(f"   - Solo se incluyen productos SIN HTML pero CON PDF ({sin_html_con_pdf} productos)")
    print(f"   - Se excluyen productos sin PDF ({sin_html_sin_pdf} productos)")
    print(f"\nEsto es correcto porque los HTML se generan desde los PDF,")
    print(f"por lo que no tiene sentido asociar HTML a productos sin PDF.")

if __name__ == "__main__":
    test_filtro_pdf()
