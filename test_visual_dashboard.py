from playwright.sync_api import sync_playwright
import time

def test_visual_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("Abriendo el dashboard...")
        page.goto("http://127.0.0.1:8080")
        
        # Esperar a que carguen los productos
        page.wait_for_selector('#productos-list', timeout=10000)
        time.sleep(3)  # Esperar a que carguen las imágenes
        
        # Tomar captura de pantalla completa
        print("Tomando captura de pantalla...")
        page.screenshot(path="dashboard_con_imagenes.png", full_page=True)
        
        # Hacer zoom en la sección de productos
        page.evaluate("document.querySelector('#productos-list').scrollIntoView()")
        time.sleep(1)
        
        # Tomar captura de los productos
        page.screenshot(path="productos_grid.png", full_page=False)
        
        print("✅ Capturas guardadas:")
        print("   - dashboard_con_imagenes.png (vista completa)")
        print("   - productos_grid.png (vista de productos)")
        
        # Verificar elementos específicos
        productos = page.query_selector_all('.producto-card')
        print(f"\n📊 Productos encontrados: {len(productos)}")
        
        # Verificar que hay imágenes
        imagenes = page.query_selector_all('.producto-imagen')
        print(f"🖼️  Productos con imágenes: {len(imagenes)}")
        
        # Verificar precios
        precios = page.query_selector_all('.producto-precio')
        if precios:
            primer_precio = page.query_selector('.producto-precio').inner_text()
            print(f"💵 Ejemplo de precio: {primer_precio}")
        
        browser.close()

if __name__ == "__main__":
    test_visual_dashboard()
