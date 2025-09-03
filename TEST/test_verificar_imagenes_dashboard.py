"""
Script para verificar que las imágenes se muestren correctamente en el dashboard
"""
import requests
import time

def test_imagenes_dashboard():
    """Verifica que las imágenes se muestren en el dashboard"""
    
    print("=== Verificación de Imágenes en Dashboard ===\n")
    
    # 1. Obtener productos con sus imágenes
    print("1. Obteniendo productos desde el API...")
    try:
        response = requests.get("http://localhost:8080/api/productos")
        productos = response.json()
        
        # Buscar productos con imágenes
        productos_con_imagenes = [
            p for p in productos 
            if 'imagenes_adicionales' in p and p['imagenes_adicionales']
        ]
        
        if productos_con_imagenes:
            print(f"   ✓ {len(productos_con_imagenes)} productos tienen imágenes\n")
            
            # Mostrar detalles de algunos productos con imágenes
            print("2. Productos con imágenes cargadas:")
            for producto in productos_con_imagenes[:5]:  # Mostrar máximo 5
                print(f"\n   Producto: {producto['Modelo']}")
                print(f"   SKU: {producto['SKU']}")
                print(f"   Imágenes: {len(producto['imagenes_adicionales'])}")
                
                for img in producto['imagenes_adicionales']:
                    print(f"     - Orden #{img['orden_posicion']}: {img['url_imagen']}")
                    print(f"       Tamaño: {img['tamano_bytes']:,} bytes")
        else:
            print("   ℹ️ No hay productos con imágenes cargadas aún\n")
        
        # 3. Probar el endpoint específico de imágenes
        print("\n3. Probando endpoint de imágenes específico...")
        
        # Buscar el producto 152 F que sabemos que tiene imágenes
        producto_152f = next((p for p in productos if p['Modelo'] == '152 F'), None)
        
        if producto_152f:
            sku = producto_152f['SKU']
            print(f"   Obteniendo imágenes de {producto_152f['Modelo']} (SKU: {sku})...")
            
            response = requests.get(f"http://localhost:8080/api/imagenes/{sku}")
            if response.status_code == 200:
                imagenes = response.json()
                
                if imagenes:
                    print(f"   ✓ {len(imagenes)} imágenes encontradas:")
                    for img in imagenes:
                        print(f"     - Posición #{img['orden_posicion']}: {(img['tamano_bytes']/1024):.1f} KB")
                        print(f"       URL: {img['url_imagen']}")
                        
                        # Verificar si la imagen es accesible
                        try:
                            img_response = requests.head(img['url_imagen'], timeout=5)
                            if img_response.status_code == 200:
                                print(f"       ✓ Imagen accesible públicamente")
                            else:
                                print(f"       ✗ Error al acceder imagen: {img_response.status_code}")
                        except Exception as e:
                            print(f"       ✗ No se pudo verificar acceso: {str(e)}")
                else:
                    print("   ✗ No hay imágenes para este producto")
            else:
                print(f"   ✗ Error al obtener imágenes: {response.status_code}")
        
        # 4. Resumen
        print("\n=== RESUMEN ===")
        print(f"Total productos: {len(productos)}")
        print(f"Productos con imágenes: {len(productos_con_imagenes)}")
        
        if productos_con_imagenes:
            total_imagenes = sum(len(p['imagenes_adicionales']) for p in productos_con_imagenes)
            print(f"Total de imágenes en el sistema: {total_imagenes}")
            
            # URLs únicas de imágenes
            urls_unicas = set()
            for p in productos_con_imagenes:
                for img in p['imagenes_adicionales']:
                    urls_unicas.add(img['url_imagen'])
            
            print(f"URLs únicas de imágenes: {len(urls_unicas)}")
            
            print("\n✅ Las imágenes están correctamente asociadas a los productos")
            print("   y deberían mostrarse en el dashboard.")
            
            print("\n📋 INSTRUCCIONES PARA VERIFICAR:")
            print("1. Abre el dashboard en http://localhost:8080")
            print("2. Busca cualquiera de estos productos con imágenes:")
            for p in productos_con_imagenes[:3]:
                print(f"   - {p['Modelo']} ({len(p['imagenes_adicionales'])} imágenes)")
            print("3. Haz clic en el botón '🖼️ Imágenes' del producto")
            print("4. Deberías ver las imágenes en el modal")
        else:
            print("\n⚠️ No hay imágenes en el sistema para verificar")
            
    except requests.exceptions.ConnectionError:
        print("   ✗ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor Flask esté corriendo")
    except Exception as e:
        print(f"   ✗ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_imagenes_dashboard()
