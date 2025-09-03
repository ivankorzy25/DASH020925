# Información de Conexión y Credenciales

Este documento contiene los detalles de las API y los métodos de conexión utilizados en la aplicación `LISTA_PRECIOS_KOR_V3`. Es un requerimiento obligatorio consultar este archivo antes de realizar cualquier modificación para no perder la funcionalidad de conexión.

## 1. API de Actualización de Precios de Productos

El catálogo obtiene los datos de los productos directamente desde una base de datos a través de una Cloud Function de Google.

- **URL de la API:** `https://southamerica-east1-lista-precios-2025.cloudfunctions.net/actualizar-precios-v2`
- **Método:** `GET`
- **Autenticación:** No se requiere autenticación explícita en el frontend. La seguridad probablemente está gestionada en el lado del servidor (CORS, etc.).
- **Función en el código:** `cargarProductosDesdeAPI()`

### Código Relevante:
```javascript
// ==== NUEVA CONFIGURACIÓN DE API ====
const API_URL = "https://southamerica-east1-lista-precios-2025.cloudfunctions.net/actualizar-precios-v2";

async function cargarProductosDesdeAPI() {
    mostrarCargando();
    try {
        const response = await fetch(API_URL);
        if (!response.ok) {
            throw new Error(`Error de red: ${response.status} - ${response.statusText}`);
        }
        const datosSQL = await response.json();

        if (!Array.isArray(datosSQL)) {
            throw new Error("La respuesta de la API no es un formato válido.");
        }

        productos = processImportedData(datosSQL);
        saveProducts();
        finalizeDataLoading();

    } catch (error) {
        console.error("Error al cargar productos desde la API:", error);
        mostrarNotificacion(`No se pudieron cargar los datos desde la base de datos. Verifique la conexión y el servicio.`, 'danger');
        ocultarCargando();
    }
}
```

## 2. APIs de Cotización del Dólar

La aplicación utiliza dos fuentes para obtener las cotizaciones del dólar.

### 2.1. Bluelytics API (para datos históricos)

- **URL de la API:** `https://api.bluelytics.com.ar/v2/evolution.json`
- **Propósito:** Obtener la evolución histórica del dólar para permitir al usuario seleccionar una cotización de una fecha específica.
- **Función en el código:** `cargarDatosEvolucion()`

### 2.2. DolarAPI (para cotizaciones en vivo en el dashboard)

- **URL de la API:** `https://dolarapi.com/v1/dolares`
- **Propósito:** Alimentar el "Dashboard Dólar Avanzado" con cotizaciones en tiempo real de diferentes tipos de dólar.
- **Función en el código:** `obtenerCotizaciones()`

### Código Relevante (Bluelytics):
```javascript
// ==== Sistema de Cotización con Bluelytics ====
async function cargarDatosEvolucion() {
    try {
        const response = await fetch('https://api.bluelytics.com.ar/v2/evolution.json');
        // ...
    }
    // ...
}
```

### Código Relevante (DolarAPI):
```javascript
// SCRIPT DEL DASHBOARD DE DOLAR (dolar_avanzado.html)
async function obtenerCotizaciones() {
    try {
        const response = await fetchWithTimeout('https://dolarapi.com/v1/dolares', { timeout: 12000, retries: 2 });
        // ...
    }
    // ...
}
