# Requerimientos de Conexión y Arquitectura

Este documento detalla la arquitectura de conexión de la aplicación del dashboard. Es un requerimiento obligatorio consultar este archivo antes de realizar modificaciones para asegurar la funcionalidad.

## 1. Arquitectura General

La aplicación tiene una arquitectura dual:

-   **Visualización de Productos:** Se realiza a través de una API (Google Cloud Function) que centraliza el acceso a los datos. El frontend **no debe** conectarse directamente a la base de datos para esta función.
-   **Funciones de Administración:** Tareas como la subida de archivos HTML o la gestión de imágenes pueden requerir una conexión directa a la base de datos y a Google Cloud Storage.

## 2. API de Productos (Visualización)

La carga principal de productos en el dashboard se realiza a través de una API.

-   **URL de la API:** `https://southamerica-east1-lista-precios-2025.cloudfunctions.net/actualizar-precios-v2`
-   **Método:** `GET`
-   **Implementación en Backend:** La ruta `/api/productos` en `dashboard.py` es la encargada de llamar a esta API y servir los datos al frontend.

### Código Relevante (`dashboard.py`):
```python
@app.route('/api/productos')
def get_productos():
    """
    Obtiene los productos desde la Cloud Function, que es la fuente de datos
    principal de la aplicación, en lugar de la base de datos directa.
    """
    try:
        response = requests.get(CONFIG["api_url"], timeout=20)
        response.raise_for_status()
        productos_api = response.json()
        
        # Estandarizar claves para el frontend
        # ...
            
        return jsonify(productos_estandarizados)
    except requests.exceptions.RequestException as e:
        # ...
```

## 3. Conexión Directa (Administración)

Para funciones administrativas que modifican datos (ej. subir HTMLs, gestionar imágenes), el backend se conecta directamente a los siguientes servicios:

### 3.1. Base de Datos MySQL

-   **Host:** `34.39.159.70`
-   **Usuario:** `admin-2025`
-   **Base de Datos:** `lista_precios_kor`
-   **Credenciales:** La contraseña está almacenada en el diccionario `CONFIG` en `dashboard.py`.
-   **Importante:** El acceso a esta base de datos está restringido por un firewall. Para conectar desde un nuevo entorno, se debe añadir la IP pública a la lista de redes autorizadas en la consola de Google Cloud SQL.

### 3.2. Google Cloud Storage

-   **Bucket:** `imagenes_tienda_kor`
-   **Project ID:** `lista-precios-2025`
-   **Autenticación:** La aplicación utiliza las "Application Default Credentials" (ADC). Esto requiere que la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS` esté configurada y apunte al archivo JSON de una cuenta de servicio con los permisos necesarios para acceder al bucket. **Este archivo JSON es una credencial crítica y no debe ser versionado en el repositorio.**
