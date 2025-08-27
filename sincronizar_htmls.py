#!/usr/bin/env python3
import os
import mysql.connector
from google.cloud import storage
import json
from datetime import datetime

# Configuración
CONFIG = {
    "bucket_name": "imagenes_tienda_kor",
    "project_id": "lista-precios-2025",
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",  # PON TU CONTRASEÑA AQUÍ
    "sql_db": "lista_precios_kor",
    "local_html_path": "/home/ivankorzy/htmls_locales"
}

def subir_html(archivo_local, modelo):
    """Sube HTML al bucket y retorna URL pública"""
    client = storage.Client(project=CONFIG["project_id"])
    bucket = client.bucket(CONFIG["bucket_name"])
    
    nombre_archivo = os.path.basename(archivo_local)
    blob_path = f"GAUCHO/{modelo}/web/{nombre_archivo}"
    
    blob = bucket.blob(blob_path)
    
    # Verificar si ya existe
    if blob.exists():
        print(f"  ⚠️  Reemplazando HTML existente para {modelo}")
    else:
        print(f"  ✨ Subiendo nuevo HTML para {modelo}")
    
    blob.upload_from_filename(archivo_local)
    
    url = f"https://storage.googleapis.com/{CONFIG['bucket_name']}/{blob_path}"
    return url

def actualizar_url_en_db(modelo, url_html):
    """Actualiza la URL del HTML en la base de datos"""
    conn = mysql.connector.connect(
        host=CONFIG["sql_host"],
        user=CONFIG["sql_user"],
        password=CONFIG["sql_pass"],
        database=CONFIG["sql_db"]
    )
    
    cursor = conn.cursor()
    
    # Verificar si la columna existe
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE table_name = 'shop_master_gaucho_completo' 
        AND column_name = 'url_ficha_html'
        AND table_schema = %s
    """, (CONFIG["sql_db"],))
    
    columna_existe = cursor.fetchone()[0] > 0
    
    # Si no existe, crearla
    if not columna_existe:
        cursor.execute("""
            ALTER TABLE shop_master_gaucho_completo 
            ADD COLUMN url_ficha_html VARCHAR(500)
        """)
        print("  ✓ Columna url_ficha_html creada")
    
    # Verificar si el producto ya tiene URL
    cursor.execute("""
        SELECT url_ficha_html 
        FROM shop_master_gaucho_completo 
        WHERE Modelo = %s
    """, (modelo,))
    
    resultado = cursor.fetchone()
    tiene_url = resultado and resultado[0] and resultado[0].strip()
    
    # Actualizar URL
    query = """
        UPDATE shop_master_gaucho_completo 
        SET url_ficha_html = %s 
        WHERE Modelo = %s
    """
    cursor.execute(query, (url_html, modelo))
    
    filas_actualizadas = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    
    if tiene_url:
        print(f"  ✓ URL actualizada (reemplazada) para {modelo}")
    else:
        print(f"  ✓ URL agregada por primera vez para {modelo}")
    
    return filas_actualizadas

def sincronizar():
    """Proceso principal"""
    ruta_local = CONFIG["local_html_path"]
    
    if not os.path.exists(ruta_local):
        print(f"❌ Error: No existe la carpeta {ruta_local}")
        print("Crea la carpeta y coloca tus HTMLs ahí")
        return
    
    archivos_html = [f for f in os.listdir(ruta_local) if f.endswith('.html')]
    
    if not archivos_html:
        print(f"⚠️  No se encontraron archivos HTML en {ruta_local}")
        return
    
    print(f"\n{'='*60}")
    print(f"SINCRONIZACIÓN DE HTMLs - KOR GENERADORES")
    print(f"{'='*60}")
    print(f"📁 Carpeta: {ruta_local}")
    print(f"📄 Archivos encontrados: {len(archivos_html)}")
    print(f"{'='*60}\n")
    
    reporte = []
    exitosos = 0
    errores = 0
    reemplazados = 0
    nuevos = 0
    
    for archivo in archivos_html:
        # Extraer modelo del nombre del archivo
        modelo = archivo.replace('.html', '')
        archivo_completo = os.path.join(ruta_local, archivo)
        
        print(f"📄 Procesando: {archivo}")
        print(f"   Modelo: {modelo}")
        
        try:
            # Verificar si es reemplazo o nuevo
            client = storage.Client(project=CONFIG["project_id"])
            bucket = client.bucket(CONFIG["bucket_name"])
            blob_path = f"GAUCHO/{modelo}/web/{archivo}"
            blob = bucket.blob(blob_path)
            es_reemplazo = blob.exists()
            
            # Subir al bucket
            url = subir_html(archivo_completo, modelo)
            print(f"  ✓ URL: {url}")
            
            # Actualizar DB
            filas = actualizar_url_en_db(modelo, url)
            
            if filas > 0:
                exitosos += 1
                if es_reemplazo:
                    reemplazados += 1
                else:
                    nuevos += 1
                print(f"  ✅ Completado exitosamente\n")
            else:
                print(f"  ⚠️  Producto no encontrado en la base de datos\n")
            
            reporte.append({
                "archivo": archivo,
                "modelo": modelo,
                "url": url,
                "db_actualizada": filas > 0,
                "es_reemplazo": es_reemplazo,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            errores += 1
            print(f"  ❌ Error: {str(e)}\n")
            reporte.append({
                "archivo": archivo,
                "modelo": modelo,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    # Guardar reporte
    with open("reporte_sincronizacion.json", "w") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    # Mostrar resumen
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DE SINCRONIZACIÓN")
    print(f"{'='*60}")
    print(f"✅ Exitosos: {exitosos}")
    print(f"   • Nuevos: {nuevos}")
    print(f"   • Reemplazados: {reemplazados}")
    print(f"❌ Errores: {errores}")
    print(f"📄 Total procesados: {len(reporte)}")
    print(f"📝 Reporte guardado en: reporte_sincronizacion.json")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    sincronizar()