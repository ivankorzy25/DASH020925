import streamlit as st
from typing import Optional, Callable
from app.models import MediaType

def file_uploader(
    allowed_types: list,
    max_size_mb: int = 100,
    on_upload: Optional[Callable] = None,
    **kwargs
) -> Optional[bytes]:
    """
    Render a file uploader with validation
    
    Args:
        allowed_types: List of allowed file extensions (e.g., ['.jpg', '.png'])
        max_size_mb: Maximum file size in MB
        on_upload: Callback function when a file is uploaded
        **kwargs: Additional arguments to pass to st.file_uploader
    
    Returns:
        Uploaded file bytes or None
    """
    uploaded_file = st.file_uploader(
        "Seleccione un archivo",
        type=allowed_types,
        **kwargs
    )
    
    if uploaded_file is not None:
        # Check file size
        max_size_bytes = max_size_mb * 1024 * 1024
        if uploaded_file.size > max_size_bytes:
            st.error(f"El archivo es demasiado grande. Tamaño máximo: {max_size_mb}MB")
            return None
        
        # Check file type
        file_ext = f".{uploaded_file.name.split('.')[-1].lower()}"
        if file_ext not in allowed_types:
            st.error(f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(allowed_types)}")
            return None
        
        # Call callback if provided
        if on_upload:
            on_upload(uploaded_file)
        
        return uploaded_file.getvalue()
    
    return None

def media_type_selector() -> MediaType:
    """Render a media type selector"""
    media_types = {
        "Imagen": MediaType.IMAGE,
        "Video": MediaType.VIDEO,
        "Audio": MediaType.AUDIO,
        "PDF": MediaType.PDF,
        "HTML": MediaType.HTML,
        "Otro": MediaType.OTHER
    }
    
    selected = st.selectbox(
        "Tipo de contenido",
        list(media_types.keys())
    )
    
    return media_types[selected]

def product_selector(db, allow_none: bool = True):
    """Render a product selector"""
    from app.services.product_service import ProductService
    product_service = ProductService(db)
    products = product_service.get_all_products()
    
    options = ["Ninguno"] if allow_none else []
    product_map = {}
    
    for product in products:
        options.append(f"{product.sku} - {product.name}")
        product_map[f"{product.sku} - {product.name}"] = product.id
    
    selected = st.selectbox("Asociar a producto", options)
    
    if selected == "Ninguno":
        return None
    
    return product_map[selected]
