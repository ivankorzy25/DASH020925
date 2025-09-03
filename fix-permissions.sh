#!/bin/bash

# Script para verificar y corregir problemas de permisos con archivos multimedia.

echo "--- Verificador de Permisos para DASH020925 ---"
echo ""

# En este proyecto, los archivos se suben a Google Cloud Storage (GCS),
# por lo que los permisos de sistema de archivos local no son la causa
# principal de problemas de acceso una vez que el archivo está subido.
#
# Los problemas de acceso suelen estar relacionados con:
# 1. Permisos de la cuenta de servicio en Google Cloud IAM.
# 2. Reglas de acceso a nivel del bucket de GCS.
# 3. Configuración de CORS en el bucket si se accede desde un navegador.

echo "Plataforma detectada: $OSTYPE"
echo ""

if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    echo "Plataforma tipo Unix detectada."
    echo "Si tuvieras un directorio de subida local (ej: ./public/uploads), estos comandos ayudarían:"
    
    UPLOAD_DIR="./public/uploads" # Ajusta esta ruta si existiera un directorio local temporal.
    
    if [ -d "$UPLOAD_DIR" ]; then
        echo "Aplicando permisos recomendados para un directorio local..."
        # find $UPLOAD_DIR -type f -exec chmod 644 {} \;
        # find $UPLOAD_DIR -type d -exec chmod 755 {} \;
        echo "Comandos de ejemplo (comentados):"
        echo "# find $UPLOAD_DIR -type f -exec chmod 644 {} \;"
        echo "# find $UPLOAD_DIR -type d -exec chmod 755 {} \;"
        echo ""
        # echo "Cambiando propietario (ejemplo para servidores web):"
        # chown -R www-data:www-data $UPLOAD_DIR
        echo "# chown -R www-data:www-data $UPLOAD_DIR"
    else
        echo "El directorio local de ejemplo '$UPLOAD_DIR' no existe. No se aplican cambios."
    fi

elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Plataforma Windows detectada."
    echo "Los comandos 'chmod' y 'chown' no son aplicables de la misma manera."
    echo "Para verificar permisos en Windows, puedes usar 'icacls' desde la terminal:"
    echo "Ejemplo: icacls \"ruta\\a\\tu\\carpeta\""
    echo ""
    echo "Sin embargo, el problema principal probablemente esté en la configuración de Google Cloud."

else
    echo "Plataforma no reconocida."
fi

echo ""
echo "--- Pasos recomendados para solucionar problemas de acceso ---"
echo "1. Ve a la consola de Google Cloud -> IAM y Admin: Asegúrate de que la cuenta de servicio que usa la aplicación tenga el rol 'Storage Object Admin'."
echo "2. Ve a Cloud Storage -> Buckets -> [nombre-del-bucket] -> Permisos: Verifica que el acceso público esté configurado como 'Sujeto a listas de control de acceso (LCA) de objetos'."
echo "3. Si las imágenes no se muestran en el navegador, configura CORS en tu bucket. Crea un archivo cors.json con el siguiente contenido:"
echo "   [{\"origin\": [\"*\"], \"method\": [\"GET\"], \"maxAgeSeconds\": 3600}]"
echo "   Y luego ejecuta en la terminal de gcloud:"
echo "   gcloud storage buckets update gs://[nombre-del-bucket] --cors-file=cors.json"
echo ""
echo "¡Verificación completada!"
