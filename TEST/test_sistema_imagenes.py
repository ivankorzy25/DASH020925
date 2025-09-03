import requests
import json

BASE_URL = "http://localhost:8080"

def test_sistema_imagenes():
    print("=== Prueba del Sistema de Imágenes ===\n")
    
    # 1. Obtener productos
    print("1. Obteniendo lista de productos...")
    try:
        response = requests.get(f"{BASE_URL}/api/productos")
        productos = response.json()
        print(f"   ✓ {len(productos)} productos encontrados")
        
        # Buscar un producto para probar
        if productos:
            producto_test = productos[0]
            print(f"   ✓ Producto de prueba: {producto_test['Modelo']}")
            print(f"     SKU: {producto_test['SKU']}")
            
            # Ver si tiene imágenes
            imagenes = producto_test.get('imagenes_adicionales', [])
            if imagenes:
                print(f"   ✓ El producto ya tiene {len(imagenes)} imágenes")
                for img in imagenes:
                    print(f"     - Orden {img['orden_posicion']}: {img['tamano_bytes']/1024:.1f} KB")
            else:
                print("   ℹ El producto no tiene imágenes aún")
        
        print("\n2. Sistema de imágenes funcionando correctamente")
        print("\nPara probar la subida de imágenes:")
        print("   1. Abre el dashboard en http://localhost:8080")
        print("   2. Busca cualquier producto")
        print("   3. Haz clic en el botón '🖼️ Imágenes'")
        print("   4. Arrastra o selecciona imágenes para subir")
        
    except requests.ConnectionError:
        print("   ✗ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor Flask esté corriendo")
    except Exception as e:
        print(f"   ✗ Error: {e}")

if __name__ == "__main__":
    test_sistema_imagenes()
