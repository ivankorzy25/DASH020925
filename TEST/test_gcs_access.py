import os
import sys
from google.cloud import storage
from google.auth import exceptions

CONFIG = {
    "bucket_name": "imagenes_tienda_kor",
    "project_id": "lista-precios-2025"
}

def test_gcs_access():
    print("=== Diagnóstico de acceso a Google Cloud Storage ===\n")
    
    # 1. Verificar credenciales (ADC o variable de entorno)
    print("1. Verificando credenciales...")
    creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if creds_path:
        print(f"   ✓ Variable GOOGLE_APPLICATION_CREDENTIALS configurada: {creds_path}")
        if os.path.exists(creds_path):
            print(f"   ✓ El archivo de credenciales existe")
        else:
            print(f"   ✗ ERROR: El archivo de credenciales NO existe en la ruta especificada")
            return False
    else:
        print("   ℹ Variable GOOGLE_APPLICATION_CREDENTIALS no configurada")
        print("   Verificando Application Default Credentials (gcloud)...")
        
        # Verificar si existe el archivo de credenciales de gcloud
        import platform
        if platform.system() == 'Windows':
            adc_path = os.path.expanduser('~\\AppData\\Roaming\\gcloud\\application_default_credentials.json')
        else:
            adc_path = os.path.expanduser('~/.config/gcloud/application_default_credentials.json')
        
        if os.path.exists(adc_path):
            print(f"   ✓ Application Default Credentials encontradas en: {adc_path}")
        else:
            print("   ✗ No se encontraron Application Default Credentials")
            print("\n   SOLUCIÓN: Necesitas configurar las credenciales de Google Cloud.")
            print("   Opción 1: Usar archivo de credenciales JSON:")
            print("      - Descarga el archivo de credenciales desde Google Cloud Console")
            print("      - Configura la variable de entorno:")
            print("        set GOOGLE_APPLICATION_CREDENTIALS=ruta\\a\\tu\\archivo.json")
            print("\n   Opción 2: Usar gcloud CLI:")
            print("      - Instala gcloud SDK")
            print("      - Ejecuta: gcloud auth application-default login")
            return False
    
    # 2. Intentar crear el cliente
    print("\n2. Intentando conectar con Google Cloud Storage...")
    try:
        client = storage.Client(project=CONFIG["project_id"])
        print(f"   ✓ Cliente creado exitosamente para el proyecto: {CONFIG['project_id']}")
    except exceptions.DefaultCredentialsError as e:
        print(f"   ✗ ERROR de credenciales: {e}")
        return False
    except Exception as e:
        print(f"   ✗ ERROR al crear cliente: {e}")
        return False
    
    # 3. Verificar acceso al bucket
    print(f"\n3. Verificando acceso al bucket '{CONFIG['bucket_name']}'...")
    try:
        bucket = client.bucket(CONFIG["bucket_name"])
        
        # Intentar listar algunos archivos para verificar permisos de lectura
        blobs = list(bucket.list_blobs(max_results=1))
        print(f"   ✓ Permisos de lectura confirmados")
        
        # Intentar subir un archivo de prueba para verificar permisos de escritura
        test_blob_name = "_test_access_check.txt"
        blob = bucket.blob(test_blob_name)
        
        try:
            blob.upload_from_string("Test de acceso", content_type='text/plain')
            print(f"   ✓ Permisos de escritura confirmados")
            
            # Limpiar archivo de prueba
            blob.delete()
            print(f"   ✓ Permisos de eliminación confirmados")
            
        except Exception as e:
            print(f"   ✗ ERROR al escribir en el bucket: {e}")
            print("\n   POSIBLES CAUSAS:")
            print("   - La cuenta no tiene permisos de escritura en el bucket")
            print("   - El bucket tiene restricciones de acceso")
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR al acceder al bucket: {e}")
        print("\n   POSIBLES CAUSAS:")
        print("   - El bucket no existe")
        print("   - La cuenta no tiene permisos para acceder al bucket")
        print("   - Error en el nombre del bucket o proyecto")
        return False
    
    print("\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("El sistema está correctamente configurado para subir imágenes.")
    return True

if __name__ == "__main__":
    success = test_gcs_access()
    sys.exit(0 if success else 1)
