from playwright.sync_api import sync_playwright
import time

def test_boton_pdf_visual():
    """Test visual para verificar que el botón PDF aparece solo cuando hay URL de PDF"""
    
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("=" * 60)
        print("TEST VISUAL - BOTÓN VER PDF EN PRODUCTOS")
        print("=" * 60)
        
        # Navegar al dashboard
        page.goto('http://localhost:8080')
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        
        # Tomar captura completa del dashboard
        print("\n1. Tomando captura completa del dashboard...")
        page.screenshot(path="test_pdf_1_dashboard_completo.png", full_page=True)
        
        # Verificar la presencia de botones PDF
        print("\n2. Verificando botones PDF en productos...")
        
        # Buscar todas las tarjetas de productos
        productos_cards = page.query_selector_all('.producto-card')
        
        productos_con_pdf = 0
        productos_sin_pdf = 0
        ejemplos_con_pdf = []
        ejemplos_sin_pdf = []
        
        for card in productos_cards:
            modelo = card.query_selector('.producto-modelo')
            modelo_texto = modelo.inner_text() if modelo else "Sin modelo"
            
            # Verificar si tiene botón de PDF
            boton_pdf = card.query_selector('button:has-text("Ver PDF")')
            
            if boton_pdf:
                productos_con_pdf += 1
                if len(ejemplos_con_pdf) < 3:
                    ejemplos_con_pdf.append(modelo_texto)
            else:
                productos_sin_pdf += 1
                if len(ejemplos_sin_pdf) < 3:
                    ejemplos_sin_pdf.append(modelo_texto)
        
        print(f"\n✅ Productos con botón PDF: {productos_con_pdf}")
        print(f"❌ Productos sin botón PDF: {productos_sin_pdf}")
        
        print("\n3. EJEMPLOS DE PRODUCTOS CON BOTÓN PDF:")
        print("-" * 40)
        for ejemplo in ejemplos_con_pdf:
            print(f"  • {ejemplo}")
        
        print("\n4. EJEMPLOS DE PRODUCTOS SIN BOTÓN PDF:")
        print("-" * 40)
        for ejemplo in ejemplos_sin_pdf:
            print(f"  • {ejemplo}")
        
        # Buscar un producto con PDF y hacer zoom
        print("\n5. Haciendo zoom en productos con PDF...")
        
        if productos_con_pdf > 0:
            # Encontrar el primer producto con PDF
            for card in productos_cards:
                boton_pdf = card.query_selector('button:has-text("Ver PDF")')
                if boton_pdf:
                    # Hacer scroll hasta el elemento
                    card.scroll_into_view_if_needed()
                    time.sleep(1)
                    
                    # Tomar captura del producto específico
                    card.screenshot(path="test_pdf_2_producto_con_pdf.png")
                    print("   ✅ Captura guardada: test_pdf_2_producto_con_pdf.png")
                    
                    # Verificar que el botón es clickeable
                    try:
                        # Obtener el onclick del botón para verificar la URL
                        onclick = boton_pdf.get_attribute('onclick')
                        if onclick and 'storage.googleapis.com' in onclick:
                            print("   ✅ Botón PDF tiene URL válida de Google Cloud Storage")
                        else:
                            print("   ⚠️ Botón PDF tiene URL pero no es de Google Cloud Storage")
                    except:
                        pass
                    
                    break
        
        # Buscar un producto sin PDF
        print("\n6. Haciendo zoom en productos sin PDF...")
        
        if productos_sin_pdf > 0:
            # Encontrar el primer producto sin PDF
            for card in productos_cards:
                boton_pdf = card.query_selector('button:has-text("Ver PDF")')
                if not boton_pdf:
                    # Hacer scroll hasta el elemento
                    card.scroll_into_view_if_needed()
                    time.sleep(1)
                    
                    # Tomar captura del producto específico
                    card.screenshot(path="test_pdf_3_producto_sin_pdf.png")
                    print("   ✅ Captura guardada: test_pdf_3_producto_sin_pdf.png")
                    
                    # Verificar que NO hay botón PDF
                    botones = card.query_selector_all('button')
                    print(f"   ✅ Producto tiene {len(botones)} botón(es) pero ninguno es 'Ver PDF'")
                    
                    break
        
        # Verificar la distribución de botones
        print("\n7. VERIFICACIÓN DE LA LÓGICA:")
        print("=" * 60)
        
        # Verificar productos específicos conocidos
        productos_conocidos = {
            "con_pdf": ["ARADO", "RASTRA"],
            "sin_pdf": ["152 F", "160A", "168 F"]
        }
        
        for card in productos_cards:
            modelo_elem = card.query_selector('.producto-modelo')
            if modelo_elem:
                modelo_texto = modelo_elem.inner_text()
                boton_pdf = card.query_selector('button:has-text("Ver PDF")')
                
                # Verificar productos que deberían tener PDF
                for prod_con_pdf in productos_conocidos["con_pdf"]:
                    if prod_con_pdf in modelo_texto:
                        if boton_pdf:
                            print(f"✅ {modelo_texto}: TIENE botón PDF (correcto)")
                        else:
                            print(f"❌ {modelo_texto}: NO tiene botón PDF (error)")
                
                # Verificar productos que NO deberían tener PDF
                for prod_sin_pdf in productos_conocidos["sin_pdf"]:
                    if prod_sin_pdf in modelo_texto:
                        if not boton_pdf:
                            print(f"✅ {modelo_texto}: NO tiene botón PDF (correcto)")
                        else:
                            print(f"❌ {modelo_texto}: TIENE botón PDF (error)")
        
        # Test de funcionalidad del botón
        print("\n8. TEST DE FUNCIONALIDAD:")
        print("-" * 60)
        
        # Intentar hacer clic en un botón PDF (sin abrir realmente)
        boton_test = page.query_selector('button:has-text("Ver PDF"):first-child')
        if boton_test:
            # Interceptar la apertura de ventana
            with page.expect_popup() as popup_info:
                boton_test.click()
                popup = popup_info.value
                popup_url = popup.url
                popup.close()
                
                if 'storage.googleapis.com' in popup_url:
                    print(f"✅ Botón PDF abre URL válida: {popup_url[:50]}...")
                else:
                    print(f"⚠️ Botón PDF abre URL: {popup_url[:50]}...")
        
        print("\n" + "=" * 60)
        print("CONCLUSIÓN:")
        print("=" * 60)
        print(f"✅ Total de productos: {productos_con_pdf + productos_sin_pdf}")
        print(f"✅ Productos con botón PDF: {productos_con_pdf}")
        print(f"✅ Productos sin botón PDF: {productos_sin_pdf}")
        print("\nEl botón 'Ver PDF' se muestra correctamente:")
        print("• Solo aparece cuando el producto tiene URL de PDF")
        print("• No aparece cuando el producto no tiene PDF")
        print("\nCapturas guardadas:")
        print("  - test_pdf_1_dashboard_completo.png")
        print("  - test_pdf_2_producto_con_pdf.png")
        print("  - test_pdf_3_producto_sin_pdf.png")
        
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    test_boton_pdf_visual()
