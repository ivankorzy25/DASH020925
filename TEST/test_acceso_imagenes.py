import requests

# URL de una imagen que sabemos que existe en el bucket
url = "https://storage.googleapis.com/imagenes_tienda_kor/GAUCHO/152_F/images/152_F_1.png"

try:
    response = requests.get(url)
    print(f"Estado HTTP: {response.status_code}")
    print(f"Tamaño de imagen: {len(response.content):,} bytes")
    print(f"Tipo de contenido: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        print("✓ La imagen es accesible públicamente")
    else:
        print("✗ Error al acceder a la imagen")
except Exception as e:
    print(f"Error al verificar imagen: {e}")
