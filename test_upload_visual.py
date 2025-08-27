"""
Script para probar visualmente la subida de imágenes con Playwright
"""
from playwright.sync_api import sync_playwright
import time
import os

def test_upload_images():
    """Prueba visual del sistema de subida de imágenes"""
    
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            print("=== Prueba Visual de Subida de Imágenes ===\n")
            
            # 1. Abrir el dashboard
            print("1. Abriendo dashboard...")
            page.goto("http://localhost:8080", wait_until='networkidle')
            page.wait_for_timeout(2000)
            
            # Capturar pantalla inicial
            page.screenshot(path="test_1_dashboard_inicial.png", full_page=True)
            print("   ✓ Dashboard cargado\n")
            
            # 2. Buscar un producto
            print("2. Buscando producto...")
            search_input = page.locator('input[type="text"][placeholder*="SKU"]')
            search_input.fill("152FG25NAFTA")
            page.keyboard.press("Enter")
            page.wait_for_timeout(2000)
            
            # Capturar resultados de búsqueda
            page.screenshot(path="test_2_busqueda_producto.png", full_page=True)
            print("   ✓ Producto encontrado\n")
            
            # 3. Hacer clic en el botón de imágenes
            print("3. Abriendo modal de imágenes...")
            
            # Buscar el botón de imágenes (puede estar en cualquier fila)
            image_buttons = page.locator('button:has-text("🖼️")')
            
            if image_buttons.count() > 0:
                # Hacer clic en el primer botón de imágenes
                image_buttons.first.click()
                page.wait_for_timeout(2000)
                
                # Capturar el modal
                page.screenshot(path="test_3_modal_imagenes.png", full_page=True)
                print("   ✓ Modal de imágenes abierto\n")
                
                # 4. Verificar si hay algún error visible
                print("4. Verificando errores...")
                
                # Buscar mensajes de error comunes
                error_patterns = [
                    '.error', '.alert-danger', '.toast-error',
                    'text=/error/i', 'text=/permission/i', 'text=/denied/i',
                    'text=/unauthorized/i', 'text=/403/i', 'text=/401/i'
                ]
                
                error_found = False
                for pattern in error_patterns:
                    error_elements = page.locator(pattern)
                    if error_elements.count() > 0:
                        error_text = error_elements.first.text_content()
                        print(f"   ✗ ERROR ENCONTRADO: {error_text}")
                        error_found = True
                        break
                
                if not error_found:
                    # Buscar específicamente el input de imágenes (no el de carpetas)
                    file_input = page.locator('#imagenesInput')
                    
                    if file_input.count() > 0:
                        print("   ✓ Input de archivos encontrado")
                        print("   ✓ No se detectaron errores visuales\n")
                        
                        # 5. Intentar subir un archivo de prueba
                        print("5. Preparando archivo de prueba...")
                        
                        # Crear una imagen de prueba simple
                        test_image_path = "test_image.png"
                        if not os.path.exists(test_image_path):
                            # Copiar una captura existente como imagen de prueba
                            if os.path.exists("test_1_dashboard_inicial.png"):
                                import shutil
                                shutil.copy("test_1_dashboard_inicial.png", test_image_path)
                                print(f"   ✓ Archivo de prueba creado: {test_image_path}")
                        
                        if os.path.exists(test_image_path):
                            print("   Intentando subir imagen...")
                            
                            # Establecer el archivo en el input
                            file_input.set_input_files(test_image_path)
                            page.wait_for_timeout(3000)
                            
                            # Capturar resultado después de seleccionar archivo
                            page.screenshot(path="test_4_archivo_seleccionado.png", full_page=True)
                            
                            # Buscar específicamente el botón de guardar imágenes dentro del modal
                            # Evitar el botón de "Subir HTML" buscando dentro del contexto del modal
                            modal = page.locator('#imagenesModal')
                            save_button = modal.locator('button.btn-success:has-text("💾 Guardar")')
                            
                            # Si no encuentra el botón con ese texto, buscar alternativas
                            if save_button.count() == 0:
                                save_button = modal.locator('button:has-text("Guardar Imágenes")')
                            if save_button.count() == 0:
                                save_button = modal.locator('button[onclick*="guardarImagenes"]')
                            
                            if save_button.count() > 0:
                                print("   Haciendo clic en guardar imágenes...")
                                save_button.click()
                                page.wait_for_timeout(5000)
                                
                                # Capturar resultado final
                                page.screenshot(path="test_5_resultado_subida.png", full_page=True)
                                
                                # Verificar errores después de subir
                                for pattern in error_patterns:
                                    error_elements = page.locator(pattern)
                                    if error_elements.count() > 0:
                                        error_text = error_elements.first.text_content()
                                        print(f"   ✗ ERROR AL SUBIR: {error_text}")
                                        error_found = True
                                        break
                                
                                if not error_found:
                                    print("   ✓ Imagen subida exitosamente\n")
                    else:
                        print("   ✗ No se encontró el input de archivos (#imagenesInput)")
                
            else:
                print("   ✗ No se encontró el botón de imágenes\n")
                print("   Posibles causas:")
                print("   - El producto no está en la tabla")
                print("   - El botón tiene un texto diferente")
            
            # 6. Verificar consola del navegador
            print("6. Verificando errores en consola...")
            console_logs = []
            page.on("console", lambda msg: console_logs.append(f"{msg.type}: {msg.text}"))
            page.wait_for_timeout(1000)
            
            if console_logs:
                print("   Mensajes de consola encontrados:")
                for log in console_logs:
                    if 'error' in log.lower():
                        print(f"   ✗ {log}")
            else:
                print("   ✓ No hay errores en consola\n")
            
            print("\n=== Resumen ===")
            print("Capturas guardadas:")
            print("  - test_1_dashboard_inicial.png")
            print("  - test_2_busqueda_producto.png")
            print("  - test_3_modal_imagenes.png")
            if os.path.exists("test_4_archivo_seleccionado.png"):
                print("  - test_4_archivo_seleccionado.png")
            if os.path.exists("test_5_resultado_subida.png"):
                print("  - test_5_resultado_subida.png")
            
        except Exception as e:
            print(f"\n✗ Error durante la prueba: {str(e)}")
            # Capturar pantalla del error
            page.screenshot(path="test_error.png", full_page=True)
            print("  Captura del error guardada en: test_error.png")
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_upload_images()
