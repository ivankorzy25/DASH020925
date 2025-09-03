import requests
import json

# URL base del servidor
BASE_URL = "http://localhost:8080"

print("=== Test de Corrección de Visualización de Imágenes ===\n")

# 1. Primero obtener todos los productos
print("1. Obteniendo productos...")
response = requests.get(f"{BASE_URL}/api/productos")
productos = response.json()

# Buscar productos con imágenes
productos_con_imagenes = [p for p in productos if p.get('imagenes_adicionales')]

if productos_con_imagenes:
    print(f"   ✓ Encontrados {len(productos_con_imagenes)} productos con imágenes\n")
    
    # Probar con cada producto que tiene imágenes
    for producto in productos_con_imagenes[:3]:  # Probar con los primeros 3
        sku = producto['SKU']
        modelo = producto['Modelo']
        imagenes_en_productos = producto.get('imagenes_adicionales', [])
        
        print(f"2. Probando endpoint /api/imagenes/{sku}")
        print(f"   Producto: {modelo}")
        print(f"   SKU: {sku}")
        print(f"   Imágenes según /api/productos: {len(imagenes_en_productos)}")
        
        # Probar el endpoint específico de imágenes
        response_imagenes = requests.get(f"{BASE_URL}/api/imagenes/{sku}")
        imagenes_endpoint = response_imagenes.json()
        
        print(f"   Imágenes según /api/imagenes/{sku}: {len(imagenes_endpoint)}")
        
        if len(imagenes_endpoint) == len(imagenes_en_productos):
            print("   ✅ CORRECTO: Ambos endpoints devuelven la misma cantidad de imágenes")
        else:
            print("   ❌ ERROR: Los endpoints devuelven cantidades diferentes")
        
        # Mostrar las URLs de las imágenes
        if imagenes_endpoint:
            print("   URLs de imágenes encontradas:")
            for img in imagenes_endpoint:
                print(f"     - Orden #{img['orden_posicion']}: {img['url_imagen']}")
                print(f"       Tamaño: {img['tamano_bytes']:,} bytes")
        
        print("-" * 60)
else:
    print("   ⚠️  No hay productos con imágenes en el sistema")
    print("   Sube algunas imágenes primero para probar")

print("\n=== RESUMEN ===")
print("Si ves las imágenes correctamente en ambos endpoints,")
print("el problema ha sido resuelto y las imágenes deberían")
print("mostrarse correctamente en el modal del dashboard.")
