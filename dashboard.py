from flask import Flask, render_template, request, jsonify, send_file
import mysql.connector
from google.cloud import storage
import os
import re
import json
from difflib import SequenceMatcher
from werkzeug.utils import secure_filename
from pathlib import Path
import mimetypes

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CONFIG = {
    "bucket_name": "imagenes_tienda_kor",
    "project_id": "lista-precios-2025",
    "sql_host": "34.39.159.70",
    "sql_user": "admin-2025",
    "sql_pass": "Alvlgeddl2025@@@@@",
    "sql_db": "lista_precios_kor"
}

def get_db_connection():
    return mysql.connector.connect(
        host=CONFIG["sql_host"],
        user=CONFIG["sql_user"],
        password=CONFIG["sql_pass"],
        database=CONFIG["sql_db"]
    )

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/productos')
def get_productos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT SKU, Modelo, Marca, Familia, Precio_USD_con_IVA, Stock, url_ficha_html, URL_PDF,
               Web_Generica_URL_1, MercadoLibre_URL_1, Instagram_Feed_URL_1
        FROM shop_master_gaucho_completo
        ORDER BY Modelo
    """)
    productos = cursor.fetchall()
    
    # Obtener imágenes adicionales para cada producto
    for producto in productos:
        cursor.execute("""
            SELECT url_imagen, tamano_bytes, orden_posicion
            FROM producto_imagenes
            WHERE producto_sku = %s OR producto_modelo = %s
            ORDER BY orden_posicion
        """, (producto['SKU'], producto['Modelo']))
        
        imagenes = cursor.fetchall()
        producto['imagenes_adicionales'] = imagenes
    
    cursor.close()
    conn.close()
    return jsonify(productos)

@app.route('/api/escanear-carpeta', methods=['POST'])
def escanear_carpeta():
    data = request.json
    files_data = data.get('files', [])
    carpeta = data.get('carpeta', '')
    
    htmls = []
    
    # Si se enviaron archivos directamente
    if files_data:
        for file_info in files_data:
            path = file_info['path']
            folder_name = path.split('/')[-2] if '/' in path else "Raíz"
            
            htmls.append({
                'archivo': file_info['name'],
                'path': path,
                'carpeta': folder_name,
                'size': file_info['size']
            })
    # Si se envió una ruta de carpeta
    elif carpeta and os.path.exists(carpeta):
        # Buscar HTMLs recursivamente
        for root, dirs, files in os.walk(carpeta):
            for file in files:
                file_lower = file.lower()
                if file_lower.endswith('.html') or file_lower.endswith('.htm'):
                    path_completo = os.path.join(root, file)
                    htmls.append({
                        'archivo': file,
                        'path': path_completo,
                        'carpeta': os.path.basename(root),
                        'size': os.path.getsize(path_completo)
                    })
    else:
        return jsonify({'error': 'No se proporcionaron archivos ni carpeta válida'}), 400
    
    # Obtener productos sin HTML pero que SÍ tienen PDF
    # Solo consideramos productos con PDF ya que los HTML se generan del PDF
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Modelo, Marca, SKU, URL_PDF
        FROM shop_master_gaucho_completo
        WHERE (url_ficha_html IS NULL OR url_ficha_html = '')
          AND URL_PDF IS NOT NULL 
          AND URL_PDF != ''
        ORDER BY Modelo
    """)
    productos_sin_html = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Mejorar algoritmo de similitud
    asociaciones = []
    for producto in productos_sin_html:
        modelo = producto['Modelo']
        sugerencias = []
        
        for html in htmls:
            # Calcular similitud mejorada
            similitud = calcular_similitud_mejorada(modelo, html)
            if similitud['puntaje'] > 25:  # Umbral más bajo para más coincidencias
                sugerencias.append({
                    'html': html,
                    'similitud': similitud
                })
        
        # Ordenar y tomar las mejores 5
        sugerencias.sort(key=lambda x: x['similitud']['puntaje'], reverse=True)
        if sugerencias:
            asociaciones.append({
                'producto': producto,
                'sugerencias': sugerencias[:5]  # Mostrar más sugerencias
            })
    
    return jsonify({
        'htmls_encontrados': len(htmls),
        'productos_sin_html': len(productos_sin_html),
        'asociaciones': asociaciones
    })

# Nuevo algoritmo de similitud mejorado
def calcular_similitud_mejorada(modelo, html):
    """Calcula similitud mejorada entre modelo y archivo HTML"""
    def normalizar(texto):
        return re.sub(r'[^\w\s]', '', texto.lower()).strip()
    
    def extraer_numeros(texto):
        return re.findall(r'\d+', texto)
    
    def calcular_coincidencia(numeros1, numeros2):
        if not numeros1 or not numeros2:
            return 0
        return len(set(numeros1) & set(numeros2)) / max(len(numeros1), len(numeros2)) * 100
    
    modelo_norm = normalizar(modelo)
    archivo_norm = normalizar(html['archivo'])
    carpeta_norm = normalizar(html['carpeta'])
    
    # Similitud de texto
    similitud_nombre = SequenceMatcher(None, modelo_norm, archivo_norm).ratio() * 100
    similitud_carpeta = SequenceMatcher(None, modelo_norm, carpeta_norm).ratio() * 100
    
    # Coincidencia de números
    numeros_modelo = extraer_numeros(modelo)
    numeros_archivo = extraer_numeros(html['archivo'])
    coincidencia_numeros = calcular_coincidencia(numeros_modelo, numeros_archivo)
    
    # Coincidencia de palabras clave
    palabras_modelo = set(modelo_norm.split())
    palabras_archivo = set(archivo_norm.split())
    coincidencia_palabras = len(palabras_modelo & palabras_archivo) / len(palabras_modelo) * 100 if palabras_modelo else 0
    
    # Puntaje combinado (ponderado)
    puntaje = (
        similitud_nombre * 0.4 + 
        similitud_carpeta * 0.2 + 
        coincidencia_numeros * 0.3 +
        coincidencia_palabras * 0.1
    )
    
    return {
        'puntaje': puntaje,
        'detalles': f"Nombre: {similitud_nombre:.0f}%, Carpeta: {similitud_carpeta:.0f}%, Números: {coincidencia_numeros:.0f}%, Palabras: {coincidencia_palabras:.0f}%"
    }

@app.route('/api/upload', methods=['POST'])
def upload_html():
    if 'file' not in request.files:
        return jsonify({'error': 'No se proporcionó archivo'}), 400
    
    file = request.files['file']
    modelo = request.form.get('modelo')
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó archivo'}), 400
    
    # Validación más flexible de extensiones
    filename = file.filename.lower()
    allowed_extensions = ['.html', '.htm']
    
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        # Verificar si es un archivo HTML aunque no tenga la extensión correcta
        try:
            content = file.read(1024)
            file.seek(0)  # Rebobinar para luego leer completo
            if b'<!DOCTYPE html' in content or b'<html' in content:
                # Es HTML aunque la extensión no coincida
                pass
            else:
                return jsonify({'error': 'Solo se permiten archivos HTML'}), 400
        except:
            return jsonify({'error': 'No se pudo verificar el tipo de archivo'}), 400
    
    try:
        client = storage.Client(project=CONFIG["project_id"])
        bucket = client.bucket(CONFIG["bucket_name"])
        
        # Limpiar el nombre del modelo para evitar problemas con caracteres especiales
        modelo_limpio = re.sub(r'[^\w\s-]', '', modelo).strip().replace(' ', '_')
        
        blob_path = f"GAUCHO/{modelo_limpio}/web/{modelo_limpio}.html"
        blob = bucket.blob(blob_path)
        
        file_content = file.read()
        blob.upload_from_string(file_content, content_type='text/html')
        
        url = f"https://storage.googleapis.com/{CONFIG['bucket_name']}/{blob_path}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si existe la columna
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE table_name = 'shop_master_gaucho_completo' 
            AND column_name = 'url_ficha_html'
            AND table_schema = %s
        """, (CONFIG["sql_db"],))
        
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE shop_master_gaucho_completo 
                ADD COLUMN url_ficha_html VARCHAR(500)
            """)
        
        # Actualizar la URL en la base de datos
        cursor.execute("""
            UPDATE shop_master_gaucho_completo 
            SET url_ficha_html = %s 
            WHERE Modelo = %s
        """, (url, modelo))
        
        filas_actualizadas = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'url': url,
            'modelo': modelo,
            'filas_actualizadas': filas_actualizadas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-images', methods=['POST'])
def upload_images():
    """Endpoint para subir múltiples imágenes de un producto"""
    
    print(f"[DEBUG] Recibida petición POST a /api/upload-images")
    print(f"[DEBUG] Form data: {dict(request.form)}")
    print(f"[DEBUG] Files: {request.files}")
    
    if 'images' not in request.files:
        return jsonify({'error': 'No se proporcionaron imágenes'}), 400
    
    files = request.files.getlist('images')
    modelo = request.form.get('modelo')
    sku = request.form.get('sku')
    modo = request.form.get('modo', 'agregar')  # 'agregar' o 'reemplazar'
    
    print(f"[DEBUG] Modelo: {modelo}, SKU: {sku}, Modo: {modo}")
    print(f"[DEBUG] Número de archivos: {len(files)}")
    
    if not modelo or not sku:
        return jsonify({'error': 'Modelo y SKU son requeridos'}), 400
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'No se seleccionaron archivos'}), 400
    
    # Validar que todos sean archivos de imagen
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    for file in files:
        ext = os.path.splitext(file.filename.lower())[1]
        if ext not in allowed_extensions:
            # Verificar por tipo MIME también
            mimetype = file.content_type
            if not mimetype or not mimetype.startswith('image/'):
                return jsonify({'error': f'Archivo {file.filename} no es una imagen válida'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Si es modo reemplazar, eliminar imágenes anteriores
        if modo == 'reemplazar':
            # Obtener URLs actuales para eliminar del bucket
            cursor.execute("""
                SELECT url_imagen FROM producto_imagenes
                WHERE producto_sku = %s OR producto_modelo = %s
            """, (sku, modelo))
            
            urls_actuales = cursor.fetchall()
            
            # Eliminar registros de la BD
            cursor.execute("""
                DELETE FROM producto_imagenes
                WHERE producto_sku = %s OR producto_modelo = %s
            """, (sku, modelo))
            
            # Eliminar archivos del bucket (opcional, por espacio)
            # client = storage.Client(project=CONFIG["project_id"])
            # bucket = client.bucket(CONFIG["bucket_name"])
            # for url_row in urls_actuales:
            #     # Extraer el path del blob desde la URL
            #     blob_path = url_row[0].replace(f"https://storage.googleapis.com/{CONFIG['bucket_name']}/", "")
            #     blob = bucket.blob(blob_path)
            #     blob.delete()
        
        # Obtener el orden máximo actual si es modo agregar
        orden_inicio = 1
        if modo == 'agregar':
            cursor.execute("""
                SELECT COALESCE(MAX(orden_posicion), 0) + 1
                FROM producto_imagenes
                WHERE producto_sku = %s OR producto_modelo = %s
            """, (sku, modelo))
            orden_inicio = cursor.fetchone()[0]
        
        # Procesar y ordenar archivos por tamaño
        archivos_con_tamano = []
        for file in files:
            # Leer contenido del archivo
            content = file.read()
            tamano = len(content)
            file.seek(0)  # Rebobinar para poder subirlo
            
            archivos_con_tamano.append({
                'file': file,
                'tamano': tamano,
                'content': content
            })
        
        # Ordenar de mayor a menor tamaño
        archivos_con_tamano.sort(key=lambda x: x['tamano'], reverse=True)
        
        # Subir archivos al bucket
        client = storage.Client(project=CONFIG["project_id"])
        bucket = client.bucket(CONFIG["bucket_name"])
        
        modelo_limpio = re.sub(r'[^\w\s-]', '', modelo).strip().replace(' ', '_')
        urls_subidas = []
        
        for idx, archivo_info in enumerate(archivos_con_tamano):
            file = archivo_info['file']
            tamano = archivo_info['tamano']
            content = archivo_info['content']
            
            # Generar nombre único para la imagen
            ext = os.path.splitext(file.filename)[1]
            nombre_archivo = f"{modelo_limpio}_{idx+1}{ext}"
            blob_path = f"GAUCHO/{modelo_limpio}/images/{nombre_archivo}"
            
            blob = bucket.blob(blob_path)
            
            # Determinar el content-type
            content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'image/jpeg'
            
            blob.upload_from_string(content, content_type=content_type)
            
            # Nota: No se usa make_public() porque el bucket tiene "Uniform bucket-level access" habilitado
            # Las imágenes serán accesibles si el bucket está configurado para acceso público
            
            url = f"https://storage.googleapis.com/{CONFIG['bucket_name']}/{blob_path}"
            
            # Guardar en la base de datos
            cursor.execute("""
                INSERT INTO producto_imagenes 
                (producto_sku, producto_modelo, url_imagen, tamano_bytes, orden_posicion)
                VALUES (%s, %s, %s, %s, %s)
            """, (sku, modelo, url, tamano, orden_inicio + idx))
            
            urls_subidas.append({
                'url': url,
                'tamano': tamano,
                'orden': orden_inicio + idx,
                'nombre': nombre_archivo
            })
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'imagenes_subidas': len(urls_subidas),
            'urls': urls_subidas,
            'modelo': modelo,
            'sku': sku
        })
        
    except Exception as e:
        print(f"[ERROR] Error en upload-images: {str(e)}")
        print(f"[ERROR] Tipo de error: {type(e).__name__}")
        import traceback
        print(f"[ERROR] Stack trace:\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/imagenes/<sku>')
def get_imagenes_producto(sku):
    """Obtener todas las imágenes de un producto"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Primero obtener el modelo asociado al SKU
    cursor.execute("""
        SELECT Modelo FROM shop_master_gaucho_completo
        WHERE SKU = %s
    """, (sku,))
    
    producto = cursor.fetchone()
    modelo = producto['Modelo'] if producto else None
    
    # Buscar imágenes por SKU O por modelo
    if modelo:
        cursor.execute("""
            SELECT url_imagen, tamano_bytes, orden_posicion, fecha_subida
            FROM producto_imagenes
            WHERE producto_sku = %s OR producto_modelo = %s
            ORDER BY orden_posicion
        """, (sku, modelo))
    else:
        cursor.execute("""
            SELECT url_imagen, tamano_bytes, orden_posicion, fecha_subida
            FROM producto_imagenes
            WHERE producto_sku = %s
            ORDER BY orden_posicion
        """, (sku,))
    
    imagenes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(imagenes)

@app.route('/api/eliminar-imagen', methods=['POST'])
def eliminar_imagen():
    """Eliminar una imagen específica"""
    data = request.json
    url_imagen = data.get('url')
    
    if not url_imagen:
        return jsonify({'error': 'URL de imagen requerida'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM producto_imagenes
            WHERE url_imagen = %s
        """, (url_imagen,))
        
        filas_eliminadas = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Opcional: eliminar del bucket
        # blob_path = url_imagen.replace(f"https://storage.googleapis.com/{CONFIG['bucket_name']}/", "")
        # client = storage.Client(project=CONFIG["project_id"])
        # bucket = client.bucket(CONFIG["bucket_name"])
        # blob = bucket.blob(blob_path)
        # blob.delete()
        
        return jsonify({
            'success': True,
            'filas_eliminadas': filas_eliminadas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
