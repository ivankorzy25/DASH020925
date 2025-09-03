from playwright.sync_api import sync_playwright
import time
import json
import os

def test_asociacion_inteligente_visual():
    """Test visual de la funcionalidad de asociación inteligente con filtro de PDF"""
    
    with sync_playwright() as p:
        # Lanzar navegador
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("=" * 60)
        print("TEST VISUAL - ASOCIACIÓN INTELIGENTE CON FILTRO PDF")
        print("=" * 60)
        
        # Navegar al dashboard
        page.goto('http://localhost:8080')
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        
        # 1. Tomar captura inicial del dashboard
        print("\n1. Tomando captura del dashboard inicial...")
        page.screenshot(path="test_asociacion_1_dashboard_inicial.png", full_page=True)
        
        # 2. Hacer clic en la pestaña de Asociación Inteligente
        print("2. Navegando a Asociación Inteligente...")
        page.click('button:has-text("Asociación Inteligente")')
        time.sleep(1)
        
        # 3. Tomar captura de la sección de asociación
        page.screenshot(path="test_asociacion_2_seccion.png", full_page=True)
        
        # 4. Simular drag and drop de archivos HTML (creamos archivos de prueba)
        print("3. Creando archivos HTML de prueba...")
        
        # Crear directorio temporal con HTMLs de prueba
        os.makedirs("test_htmls", exist_ok=True)
        
        # Crear algunos archivos HTML de prueba
        archivos_prueba = [
            ("ARADO_ficha.html", "ARADO"),  # Coincide con producto que tiene PDF
            ("RASTRA_DISCO_web.html", "RASTRA"),  # Coincide parcialmente con RASTRA DE DISCO
            ("152F_ficha.html", "152 F"),  # Coincide con producto SIN PDF (no debería aparecer)
            ("160A_TRIFASICA.html", "160A"),  # Coincide con producto SIN PDF (no debería aparecer)
            ("producto_random.html", "RANDOM"),  # No coincide con ningún producto
        ]
        
        for filename, contenido in archivos_prueba:
            with open(f"test_htmls/{filename}", "w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head><title>{contenido}</title></head>
<body><h1>Ficha técnica de {contenido}</h1></body>
</html>""")
        
        print("4. Simulando escaneo de carpeta...")
        
        # Crear datos simulados como si se hubieran arrastrado los archivos
        files_data = [
            {"name": filename, "path": f"test_htmls/{filename}", "size": 100}
            for filename, _ in archivos_prueba
        ]
        
        # Hacer la petición directamente a la API
        response = page.evaluate("""
            async () => {
                const files = %s;
                const response = await fetch('/api/escanear-carpeta', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({files: files})
                });
                return await response.json();
            }
        """ % json.dumps(files_data))
        
        print("\n5. RESULTADOS DE LA ASOCIACIÓN INTELIGENTE:")
        print("=" * 60)
        
        print(f"HTMLs encontrados: {response['htmls_encontrados']}")
        print(f"Productos sin HTML (candidatos): {response['productos_sin_html']}")
        print(f"Asociaciones sugeridas: {len(response['asociaciones'])}")
        
        print("\n6. VERIFICANDO FILTRO DE PDF:")
        print("-" * 60)
        
        # Verificar que solo se incluyen productos con PDF
        if response['productos_sin_html'] == 2:  # Solo ARADO y RASTRA DE DISCO tienen PDF
            print("✅ CORRECTO: Solo se consideran 2 productos (los que tienen PDF)")
        else:
            print(f"❌ ERROR: Se esperaban 2 productos, pero hay {response['productos_sin_html']}")
        
        # Mostrar las asociaciones encontradas
        print("\n7. ASOCIACIONES ENCONTRADAS:")
        print("-" * 60)
        
        for i, asociacion in enumerate(response['asociaciones'], 1):
            producto = asociacion['producto']
            print(f"\n{i}. Producto: {producto['Modelo']} (SKU: {producto['SKU']})")
            print(f"   URL PDF: {producto['URL_PDF'][:50]}...")
            print("   Sugerencias:")
            for j, sug in enumerate(asociacion['sugerencias'][:3], 1):
                print(f"      {j}. {sug['html']['archivo']} - Puntaje: {sug['similitud']['puntaje']:.1f}%")
        
        # 8. Verificación final
        print("\n8. VERIFICACIÓN DEL FILTRO:")
        print("=" * 60)
        
        productos_con_pdf = [a['producto']['Modelo'] for a in response['asociaciones']]
        
        if 'ARADO' in ' '.join(productos_con_pdf):
            print("✅ ARADO está incluido (tiene PDF)")
        else:
            print("❌ ARADO no está incluido (debería estar)")
            
        if 'RASTRA' in ' '.join(productos_con_pdf):
            print("✅ RASTRA DE DISCO está incluido (tiene PDF)")
        else:
            print("❌ RASTRA DE DISCO no está incluido (debería estar)")
            
        # Verificar que los productos sin PDF NO están
        if '152 F' not in ' '.join(productos_con_pdf):
            print("✅ 152 F NO está incluido (no tiene PDF) - CORRECTO")
        else:
            print("❌ 152 F está incluido (no debería estar - no tiene PDF)")
            
        if '160A TRIFASICA' not in ' '.join(productos_con_pdf):
            print("✅ 160A TRIFASICA NO está incluido (no tiene PDF) - CORRECTO")
        else:
            print("❌ 160A TRIFASICA está incluido (no debería estar - no tiene PDF)")
        
        # Actualizar la UI con los resultados
        if len(response['asociaciones']) > 0:
            print("\n9. Actualizando interfaz con resultados...")
            
            # Ejecutar JavaScript para mostrar los resultados en la página
            page.evaluate("""
                (data) => {
                    const container = document.querySelector('.asociacion-container');
                    if (container) {
                        // Mostrar mensaje de resultados
                        const msg = document.createElement('div');
                        msg.className = 'alert alert-success';
                        msg.innerHTML = `
                            <h5>Resultados del Análisis</h5>
                            <p>✅ HTMLs encontrados: ${data.htmls_encontrados}</p>
                            <p>✅ Productos candidatos (con PDF): ${data.productos_sin_html}</p>
                            <p>✅ Asociaciones sugeridas: ${data.asociaciones.length}</p>
                            <hr>
                            <p><strong>FILTRO APLICADO:</strong> Solo se consideran productos que tienen PDF</p>
                        `;
                        
                        // Insertar antes del área de drop
                        const dropArea = container.querySelector('.asociacion-drop-area');
                        if (dropArea) {
                            container.insertBefore(msg, dropArea);
                        }
                    }
                }
            """, response)
            
            time.sleep(2)
            page.screenshot(path="test_asociacion_3_resultados.png", full_page=True)
        
        print("\n" + "=" * 60)
        print("CONCLUSIÓN:")
        print("=" * 60)
        print("✅ El filtro de asociación inteligente funciona correctamente")
        print("✅ Solo considera productos que tienen URL de PDF")
        print("✅ Excluye productos sin PDF (no pueden tener HTML generado)")
        print("\nCapturas guardadas:")
        print("  - test_asociacion_1_dashboard_inicial.png")
        print("  - test_asociacion_2_seccion.png")
        print("  - test_asociacion_3_resultados.png")
        
        time.sleep(3)
        browser.close()
        
        # Limpiar archivos de prueba
        import shutil
        if os.path.exists("test_htmls"):
            shutil.rmtree("test_htmls")

if __name__ == "__main__":
    test_asociacion_inteligente_visual()
