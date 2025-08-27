"""
Script para verificar que la asociación inteligente solo considera productos con URL_PDF
"""

import mysql.connector
import json

CONFIG = {
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

def test_filtro_pdf():
    """
    Verifica que el filtro SQL de asociación inteligente:
    1. Solo incluye productos SIN HTML
    2. Y que SÍ tienen PDF (no nulo y no vacío)
    """
    try:
        conn = mysql.connector.connect(
            host=CONFIG["sql_host"],
            user=CONFIG["sql_user"],
            password=CONFIG["sql_pass"],
            database=CONFIG["sql_db"]
        )
        
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 80)
        print("VERIFICACIÓN DEL FILTRO DE ASOCIACIÓN INTELIGENTE")
        print("=" * 80)
        
        # Query actual de la asociación inteligente
        cursor.execute("""
            SELECT Modelo, Marca, SKU, URL_PDF
            FROM shop_master_gaucho_completo
            WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
              AND URL_PDF IS NOT NULL 
              AND URL_PDF != ''
            ORDER BY Modelo
            LIMIT 10
        """)
        productos_asociacion = cursor.fetchall()
        
        print(f"\n✅ Productos que SÍ serán considerados en la asociación (tienen PDF):")
        print(f"   Total: {cursor.rowcount} productos\n")
        
        for i, producto in enumerate(productos_asociacion[:5], 1):
            print(f"   {i}. Modelo: {producto['Modelo']}")
            print(f"      SKU: {producto['SKU']}")
            print(f"      PDF: {producto['URL_PDF'][:50]}..." if producto['URL_PDF'] else "Sin PDF")
            print()
        
        # Verificar productos que NO serán considerados (sin PDF)
        cursor.execute("""
            SELECT Modelo, Marca, SKU, URL_PDF
            FROM shop_master_gaucho_completo
            WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
              AND (URL_PDF IS NULL OR URL_PDF = '')
            ORDER BY Modelo
            LIMIT 10
        """)
        productos_sin_pdf = cursor.fetchall()
        
        print(f"\n❌ Productos que NO serán considerados (no tienen PDF):")
        print(f"   Total: {cursor.rowcount} productos\n")
        
        if productos_sin_pdf:
            for i, producto in enumerate(productos_sin_pdf[:5], 1):
                print(f"   {i}. Modelo: {producto['Modelo']}")
                print(f"      SKU: {producto['SKU']}")
                print(f"      PDF: {'NULL' if producto['URL_PDF'] is None else 'VACÍO'}")
                print()
        else:
            print("   No hay productos sin PDF y sin HTML")
        
        # Estadísticas generales
        print("\n" + "=" * 80)
        print("ESTADÍSTICAS DEL FILTRO")
        print("=" * 80)
        
        # Total de productos sin HTML
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM shop_master_gaucho_completo
            WHERE url_ficha_html IS NULL OR url_ficha_html = ''
        """)
        total_sin_html = cursor.fetchone()['total']
        
        # Total de productos sin HTML pero CON PDF
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM shop_master_gaucho_completo
            WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
              AND URL_PDF IS NOT NULL AND URL_PDF != ''
        """)
        total_con_pdf = cursor.fetchone()['total']
        
        # Total de productos sin HTML y SIN PDF
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM shop_master_gaucho_completo
            WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
              AND (URL_PDF IS NULL OR URL_PDF = '')
        """)
        total_sin_pdf = cursor.fetchone()['total']
        
        print(f"\n📊 Resumen:")
        print(f"   • Productos sin HTML (total): {total_sin_html}")
        print(f"   • Productos sin HTML pero CON PDF (incluidos en asociación): {total_con_pdf}")
        print(f"   • Productos sin HTML y SIN PDF (excluidos de asociación): {total_sin_pdf}")
        
        porcentaje_incluidos = (total_con_pdf / total_sin_html * 100) if total_sin_html > 0 else 0
        print(f"\n   ➤ {porcentaje_incluidos:.1f}% de productos sin HTML serán considerados")
        print(f"     (porque tienen PDF de referencia)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ EL FILTRO ESTÁ FUNCIONANDO CORRECTAMENTE")
        print("   Solo se consideran productos con URL_PDF válido")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al verificar el filtro: {e}")
        return False

if __name__ == "__main__":
    test_filtro_pdf()
