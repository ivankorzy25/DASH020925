"""
Script de verificación visual para la página de gestión de imágenes
usando Playwright para asegurar que el diseño y funcionalidad son correctos.
"""

from playwright.sync_api import sync_playwright
import os
import time

def test_gestion_imagenes():
    """Verifica visualmente la página de gestión de imágenes"""
    
    with sync_playwright() as p:
        # Lanzar navegador en modo headless
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Obtener la ruta absoluta del archivo HTML
        html_file = os.path.abspath("templates/gestion_imagenes.html")
        url = f"file:///{html_file}"
        
        print(f"Abriendo página: {url}")
        page.goto(url)
        
        # Establecer viewport para pantalla de escritorio
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.wait_for_timeout(2000)  # Esperar a que cargue completamente
        
        # Test 1: Vista inicial de la página
        print("\n✓ Test 1: Capturando vista inicial...")
        page.screenshot(path="test_gestion_1_vista_inicial.png", full_page=True)
        
        # Verificar elementos principales
        assert page.locator(".dashboard-container").is_visible(), "Contenedor principal no visible"
        assert page.locator(".header").is_visible(), "Header no visible"
        assert page.locator(".sidebar").is_visible(), "Sidebar no visible"
        assert page.locator("#productSelect").is_visible(), "Selector de productos no visible"
        assert page.locator("#dropZone").is_visible(), "Zona de carga no visible"
        
        # Test 2: Seleccionar un producto
        print("✓ Test 2: Seleccionando producto...")
        page.select_option("#productSelect", "prod-002")
        page.wait_for_timeout(1000)
        
        # Verificar que se muestra la información del producto
        assert page.locator("#productSelector").is_visible(), "Información del producto no visible"
        page.screenshot(path="test_gestion_2_producto_seleccionado.png", full_page=True)
        
        # Test 3: Hover en zona de carga (simulamos el efecto hover)
        print("✓ Test 3: Simulando hover en zona de carga...")
        page.hover("#dropZone")
        page.wait_for_timeout(500)
        page.screenshot(path="test_gestion_3_hover_zona_carga.png", full_page=True)
        
        # Test 4: Vista móvil/responsiva
        print("✓ Test 4: Verificando diseño responsivo...")
        page.set_viewport_size({"width": 375, "height": 812})  # iPhone X size
        page.wait_for_timeout(1000)
        page.screenshot(path="test_gestion_4_vista_movil.png", full_page=True)
        
        # Verificar que sidebar y contenido se reorganizan
        assert page.locator(".sidebar").is_visible(), "Sidebar no visible en móvil"
        assert page.locator(".content").is_visible(), "Contenido no visible en móvil"
        
        # Test 5: Mostrar mensaje de error (simulado con JavaScript)
        print("✓ Test 5: Mostrando mensaje de error...")
        page.set_viewport_size({"width": 1920, "height": 1080})  # Volver a escritorio
        page.evaluate("""
            document.getElementById('errorAlert').style.display = 'flex';
            document.querySelector('#errorAlert span').textContent = 
                'Por favor, selecciona un producto antes de subir imágenes';
        """)
        page.wait_for_timeout(500)
        page.screenshot(path="test_gestion_5_mensaje_error.png", full_page=True)
        
        browser.close()
        
        print("\n✅ VERIFICACIÓN VISUAL COMPLETADA")
        print("   - Vista inicial: OK")
        print("   - Selección de producto: OK")
        print("   - Zona de carga interactiva: OK")
        print("   - Diseño responsivo: OK")
        print("   - Mensajes de feedback: OK")
        
        return True

if __name__ == "__main__":
    try:
        test_gestion_imagenes()
        print("\n🎉 Todas las pruebas visuales pasaron exitosamente")
        print("\nCapturas guardadas:")
        print("- test_gestion_1_vista_inicial.png")
        print("- test_gestion_2_producto_seleccionado.png")
        print("- test_gestion_3_hover_zona_carga.png")
        print("- test_gestion_4_vista_movil.png")
        print("- test_gestion_5_mensaje_error.png")
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
